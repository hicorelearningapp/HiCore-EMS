from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional
import os
import uuid
from pathlib import Path

# Import existing functions from ml_agent_llm_summarizer
from ml_agent_llm_summarizer import search_tool, summarize_tool, template_tool

# Initialize FastAPI app
app = FastAPI(
    title="Research Report Generator API",
    description="API for generating research reports using AI",
    version="1.0.0"
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for request/response
class ReportRequest(BaseModel):
    topic: str
    output_format: str = "docx"  # Could be extended to support other formats

class ReportResponse(BaseModel):
    status: str
    message: str
    report_path: Optional[str] = None
    download_url: Optional[str] = None

# Configuration
REPORTS_DIR = "reports"
os.makedirs(REPORTS_DIR, exist_ok=True)
BASE_URL = "http://localhost:8000"  # Update this in production

@app.post("/api/generate-report", response_model=ReportResponse)
async def generate_report(request: ReportRequest):
    """
    Generate a research report for the given topic.
    
    Args:
        request (ReportRequest): The request containing the topic and output format
    
    Returns:
        ReportResponse: The response containing the status and download URL
    """
    try:
        # Generate a unique filename
        report_id = str(uuid.uuid4())
        safe_topic = "".join(c if c.isalnum() or c in ' _-' else '_' for c in request.topic)
        filename = f"{safe_topic}_{report_id[:8]}.docx"
        filepath = os.path.join(REPORTS_DIR, filename)
        
        # Generate the report using existing functions
        raw_results = search_tool(request.topic)
        summary = summarize_tool(raw_results)
        
        # Save the report
        template_tool({
            "topic": request.topic,
            "summary": summary,
            "output_path": filepath  # Modified template_tool to accept output_path
        })
        
        download_url = f"{BASE_URL}/api/download/{filename}"
        
        return {
            "status": "success",
            "message": "Report generated successfully",
            "report_path": filepath,
            "download_url": download_url
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating report: {str(e)}"
        )

@app.get("/api/download/{filename}")
async def download_report(filename: str):
    """Download the generated report."""
    filepath = os.path.join(REPORTS_DIR, filename)
    
    if not os.path.exists(filepath):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )
    
    return FileResponse(
        filepath,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        filename=filename
    )

@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "message": "API is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
