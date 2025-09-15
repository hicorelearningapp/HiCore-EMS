from pydantic import BaseModel, Field
from typing import Optional, Dict, List, Literal
from datetime import datetime

class AIRequest(BaseModel):
    user_id: str
    record_ids: Optional[List[str]] = []
    prompt: Optional[str] = None
    inputs: Optional[Dict] = None

class AIResponse(BaseModel):
    id: str
    user_id: str
    result: Optional[Dict] = {}
    explanation: Optional[str] = None
    created_at: datetime = None

    class Config:
        orm_mode = True

class TrainingMetrics(BaseModel):
    accuracy: Optional[float] = None
    precision: Optional[float] = None
    recall: Optional[float] = None
    f1_score: Optional[float] = None
    loss: Optional[float] = None
    training_time_seconds: Optional[float] = None

class TrainingRequest(BaseModel):
    model_name: str
    training_data: Dict  # Could be paths to data or actual data
    parameters: Dict  # Hyperparameters for training
    description: Optional[str] = None

class TrainingResponse(BaseModel):
    training_id: str
    model_name: str
    status: str  # e.g., 'pending', 'training', 'completed', 'failed'
    metrics: Optional[TrainingMetrics] = None
    created_at: datetime = None
    completed_at: Optional[datetime] = None
    error: Optional[str] = None

    class Config:
        orm_mode = True

class WebSearchRequest(BaseModel):
    """Request model for web search and summarization"""
    query: str
    max_results: int = 3
    summary_length: str = "medium"  # short, medium, or long

class WebSearchResponse(BaseModel):
    """Response model for web search and summarization"""
    query: str
    summary: str
    sources: List[Dict[str, str]]
    timestamp: datetime = None
    error: Optional[str] = None

    model_config = {
        "json_schema_extra": {
            "example": {
                "query": "latest treatments for diabetes",
                "summary": "Recent treatments for diabetes include...",
                "sources": [
                    {"title": "Diabetes Treatment Advances", "url": "https://example.com/diabetes"},
                    {"title": "New Diabetes Research", "url": "https://example.com/research"}
                ],
                "timestamp": "2023-01-01T12:00:00.000Z"
            }
        },
        "from_attributes": True
    }

class PDFAnalysisRequest(BaseModel):
    """Request model for PDF analysis and summarization"""
    pdf_id: str = Field(..., description="ID of the PDF file to analyze (must exist in uploads folder)")
    summary_length: Literal["short", "medium", "detailed"] = Field(
        default="medium",
        description="Desired length of the summary: 'short' (1-2 paragraphs), 'medium' (3-5 paragraphs), or 'detailed' (comprehensive)"
    )
    include_key_points: bool = Field(
        default=True,
        description="Whether to include key points in the response"
    )

class PDFAnalysisResponse(BaseModel):
    """Response model for PDF analysis and summarization"""
    pdf_id: str
    title: str
    page_count: int
    summary: str
    key_points: Optional[List[str]] = None
    created_at: datetime = None
    error: Optional[str] = None

    model_config = {
        "json_schema_extra": {
            "example": {
                "pdf_id": "123e4567-e89b-12d3-a456-426614174000",
                "title": "Medical Research Paper",
                "page_count": 12,
                "summary": "This research paper discusses...",
                "key_points": [
                    "Key finding 1...",
                    "Key finding 2...",
                    "Key finding 3..."
                ],
                "created_at": "2023-01-01T12:00:00.000Z"
            }
        },
        "from_attributes": True
    }
