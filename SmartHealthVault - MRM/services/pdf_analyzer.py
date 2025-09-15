import os
import fitz  # PyMuPDF
from typing import Optional, Dict, Any
from openai import OpenAI
from dotenv import load_dotenv
import re

# Load environment variables
load_dotenv()

class PDFAnalyzer:
    def __init__(self, uploads_dir: str = "uploads/raw"):
        """
        Initialize the PDF Analyzer with the uploads directory
        
        Args:
            uploads_dir: Path to the directory containing uploaded PDFs
        """
        self.uploads_dir = uploads_dir
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
    def extract_text_from_pdf(self, pdf_id: str) -> str:
        """
        Extract text from a PDF file
        
        Args:
            pdf_id: The ID of the PDF file (without .pdf extension)
            
        Returns:
            Extracted text from the PDF
            
        Raises:
            FileNotFoundError: If the PDF file doesn't exist
        """
        pdf_path = os.path.join(self.uploads_dir, f"{pdf_id}.pdf")
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF with ID {pdf_id} not found in {self.uploads_dir}")
        
        text = ""
        try:
            with fitz.open(pdf_path) as doc:
                for page in doc:
                    text += page.get_text()
        except Exception as e:
            raise Exception(f"Error extracting text from PDF: {str(e)}")
            
        return text.strip()
    
    def clean_text(self, text: str) -> str:
        """Clean and preprocess the extracted text"""
        # Remove excessive whitespace and newlines
        text = re.sub(r'\s+', ' ', text)
        # Remove non-printable characters
        text = ''.join(char for char in text if char.isprintable() or char.isspace())
        return text.strip()
    
    def chunk_text(self, text: str, chunk_size: int = 2000) -> list[str]:
        """Split text into chunks of specified size"""
        words = text.split()
        chunks = []
        current_chunk = []
        current_length = 0
        
        for word in words:
            if current_length + len(word) + 1 > chunk_size and current_chunk:
                chunks.append(' '.join(current_chunk))
                current_chunk = []
                current_length = 0
                
            current_chunk.append(word)
            current_length += len(word) + 1
            
        if current_chunk:
            chunks.append(' '.join(current_chunk))
            
        return chunks
    
    def summarize_text(self, text: str, length: str = "medium") -> str:
        """
        Generate a summary of the text using OpenAI
        
        Args:
            text: The text to summarize
            length: Desired length of summary (short, medium, or long)
            
        Returns:
            Generated summary
        """
        # Define tokens based on desired length
        length_map = {
            "short": 100,
            "medium": 250,
            "long": 500
        }
        
        max_tokens = length_map.get(length.lower(), 250)  # Default to medium
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that summarizes text concisely."},
                    {"role": "user", "content": f"Please provide a {length} summary of the following text:\n\n{text}"}
                ],
                max_tokens=max_tokens,
                temperature=0.3
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            raise Exception(f"Error generating summary: {str(e)}")
    
    def analyze_pdf(self, pdf_id: str, summary_length: str = "medium") -> Dict[str, Any]:
        """
        Analyze and summarize a PDF file
        
        Args:
            pdf_id: The ID of the PDF to analyze
            summary_length: Desired length of the summary (short, medium, long)
            
        Returns:
            Dictionary containing analysis results
        """
        try:
            # Extract and clean text
            text = self.extract_text_from_pdf(pdf_id)
            if not text:
                return {"error": "No text could be extracted from the PDF"}
                
            cleaned_text = self.clean_text(text)
            
            # Generate summary
            summary = self.summarize_text(cleaned_text, summary_length)
            
            # Get basic metrics
            word_count = len(cleaned_text.split())
            char_count = len(cleaned_text)
            
            return {
                "pdf_id": pdf_id,
                "summary": summary,
                "metrics": {
                    "word_count": word_count,
                    "character_count": char_count,
                    "summary_length": summary_length
                },
                "status": "completed"
            }
            
        except Exception as e:
            return {
                "error": str(e),
                "status": "failed"
            }
