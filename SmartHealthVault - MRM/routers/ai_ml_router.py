from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from sqlalchemy.orm import Session
from database.db_manager import get_db_session
from services.ai_ml_manager import AIManager
from parsers.ai_ml_parser import (
    AIRequest, AIResponse, TrainingRequest, TrainingResponse, 
    WebSearchRequest, WebSearchResponse, PDFAnalysisRequest, PDFAnalysisResponse
)

router = APIRouter(prefix="/ai", tags=["AI/ML"])

@router.post("/analyze/", response_model=AIResponse)
def analyze(req: AIRequest, db: Session = Depends(get_db_session)):
    return AIManager(db).analyze(req)

@router.post("/predict/", response_model=AIResponse)
def predict(req: AIRequest, db: Session = Depends(get_db_session)):
    return AIManager(db).predict(req)

@router.get("/models/", response_model=List[str])
def models(db: Session = Depends(get_db_session)):
    return AIManager(db).list_models()

@router.post("/train/", response_model=TrainingResponse, status_code=202)
def train_model(request: TrainingRequest, db: Session = Depends(get_db_session)):
    """
    Train a new AI/ML model with the provided data and parameters
    - **model_name**: Name of the model to train
    - **training_data**: Training data (can be file paths or direct data)
    - **parameters**: Hyperparameters for training
    - **description**: Optional description of the training run
    Returns:
        TrainingResponse with training status and metrics (once completed)
    """
    try:
        return AIManager(db).train_model(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/train/{training_id}", response_model=TrainingResponse)
def get_training_status(training_id: str, db: Session = Depends(get_db_session)):
    """
    Get the status of a training job
    
    - **training_id**: ID of the training job to check
    - Returns: Current status and metrics of the training job
    """
    try:
        return AIManager(db).get_training_status(training_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/search-and-summarize/", response_model=WebSearchResponse)
def search_and_summarize(
    request: WebSearchRequest,
    db: Session = Depends(get_db_session)
):
    """
    Perform a web search and generate an AI-powered summary of the results
    
    - **query**: The search query string
    - **max_results**: Maximum number of search results to include (1-10, default: 3)
    
    Returns:
        A summary of the search results with source references
    """
    try:
        # Ensure max_results is within valid range (1-10)
        max_results = max(1, min(10, request.max_results or 3))
        
        # Call the AIManager with the query and max_results
        result = AIManager(db).search_and_summarize(
            query=request.query,
            max_results=max_results
        )
        
        # Convert the result to a WebSearchResponse
        return WebSearchResponse(
            query=result['query'],
            summary=result['summary'],
            sources=result['sources'],
            timestamp=result['timestamp']
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error performing search and summarize: {str(e)}"
        )

@router.post("/analyze/pdf", response_model=PDFAnalysisResponse, status_code=200)
async def analyze_pdf(
    request: PDFAnalysisRequest,
    db: Session = Depends(get_db_session)
):
    """
    Analyze and summarize a PDF document
    
    This endpoint takes a PDF ID (from the uploads folder) and returns a summary
    with optional key points. The summary length can be customized.
    
    - **pdf_id**: ID of the PDF file to analyze (must exist in uploads/raw/pdfs/)
    - **summary_length**: Desired length of the summary (short/medium/detailed)
    - **include_key_points**: Whether to include key points in the response
    
    Returns:
        PDFAnalysisResponse with the document summary and metadata
    """
    try:
        return AIManager(db).analyze_pdf(request)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing PDF: {str(e)}"
        )
