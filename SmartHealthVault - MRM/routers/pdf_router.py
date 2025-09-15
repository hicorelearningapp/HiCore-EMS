from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Query
from fastapi.responses import JSONResponse
from typing import Optional, Literal, Dict, Any, List
import fitz  # PyMuPDF
import os
import tempfile
from openai import OpenAI
from dotenv import load_dotenv
from datetime import datetime
from sqlalchemy.orm import Session

from database.db_manager import get_db_session
from services.pdf_analyzer import PDFAnalyzer

# Load environment variables
load_dotenv()

router = APIRouter(prefix="/analyze", tags=["PDF Analysis"])

# Initialize OpenAI client
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract text from PDF file"""
    try:
        doc = fitz.open(pdf_path)
        text = ""
        for page in doc:
            text += page.get_text()
        return text.strip()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error reading PDF: {str(e)}")

def chunk_text(text: str, chunk_size: int = 4000) -> list[str]:
    """Split text into smaller chunks for processing"""
    words = text.split()
    chunks = []
    current_chunk = []
    current_length = 0
    
    for word in words:
        if current_length + len(word) + 1 > chunk_size:
            chunks.append(" ".join(current_chunk))
            current_chunk = []
            current_length = 0
        current_chunk.append(word)
        current_length += len(word) + 1
    
    if current_chunk:
        chunks.append(" ".join(current_chunk))
    
    return chunks

def generate_summary(text: str, length: str = "medium") -> Dict[str, Any]:
    """Generate summary using OpenAI"""
    try:
        # Define tokens based on length
        length_tokens = {
            "short": 150,
            "medium": 300,
            "long": 600
        }
        
        max_tokens = length_tokens.get(length.lower(), 300)
        
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that summarizes documents."},
                {"role": "user", "content": f"Please provide a {length} summary of the following text:\n\n{text}"}
            ],
            max_tokens=max_tokens,
            temperature=0.3
        )
        
        summary = response.choices[0].message.content.strip()
        
        # Generate key points
        key_points_response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Extract 3-5 key points from the following text:"},
                {"role": "user", "content": text}
            ],
            max_tokens=200,
            temperature=0.3
        )
        
        key_points = [point.strip() for point in key_points_response.choices[0].message.content.split("\n") if point.strip()]
        
        return {
            "summary": summary,
            "key_points": key_points,
            "summary_length": length,
            "tokens_used": response.usage.total_tokens if hasattr(response, 'usage') else None
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating summary: {str(e)}")

@router.post("/pdf", response_model=Dict[str, Any])
async def analyze_pdf(
    file: UploadFile = File(...),
    summary_length: str = "medium"
):
    """
    Analyze and summarize a PDF document
    
    - **file**: PDF file to analyze
    - **summary_length**: Length of the summary (short/medium/long)
    
    Returns:
        JSON with summary, key points, and metadata
    """
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
        content = await file.read()
        temp_file.write(content)
        temp_path = temp_file.name
    
    try:
        # Extract text from PDF
        text = extract_text_from_pdf(temp_path)
        
        if not text.strip():
            raise HTTPException(status_code=400, detail="No text could be extracted from the PDF")
        
        # Generate summary
        result = generate_summary(text, summary_length)
        
        # Add metadata
        result.update({
            "filename": file.filename,
            "pages": len(fitz.open(temp_path)),
            "processed_at": datetime.utcnow().isoformat(),
            "text_length": len(text)
        })
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        # Clean up temporary file
        try:
            os.unlink(temp_path)
        except:
            pass

@router.get("/pdf/{pdf_id}", response_model=Dict[str, Any])
async def analyze_pdf_id(
    pdf_id: str,
    length: str = Query(
        "medium",
        description="Desired summary length",
        regex="^(short|medium|long)$",
        example="medium"
    ),
    db: Session = Depends(get_db_session)
):
    """
    Analyze and summarize a PDF file
    
    - **pdf_id**: The ID of the PDF to analyze (without .pdf extension)
    - **length**: Desired summary length (short, medium, long)
    
    Returns:
    - Analysis results including summary and metrics
    """
    try:
        # Initialize PDF analyzer
        analyzer = PDFAnalyzer()
        
        # Analyze the PDF
        result = analyzer.analyze_pdf(pdf_id, length)
        
        # Check for errors
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
            
        return result
        
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")

@router.get("/pdfs/available", response_model=List[str])
async def list_available_pdfs():
    """
    List all available PDFs in the uploads directory
    
    Returns:
    - List of available PDF IDs (without .pdf extension)
    """
    try:
        uploads_dir = "uploads/raw"
        if not os.path.exists(uploads_dir):
            return []
            
        pdfs = [
            f[:-4]  # Remove .pdf extension
            for f in os.listdir(uploads_dir)
            if f.lower().endswith('.pdf')
        ]
        
        return pdfs
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing PDFs: {str(e)}")
