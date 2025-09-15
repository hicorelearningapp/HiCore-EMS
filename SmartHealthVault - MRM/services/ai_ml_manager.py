from database.db_manager import DatabaseManager
from database.enums import DBType
from schemas.ai_ml_schema import AIParser
from parsers.ai_ml_parser import AIRequest, TrainingRequest, TrainingResponse, TrainingMetrics, WebSearchResponse, PDFAnalysisRequest, PDFAnalysisResponse
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from datetime import datetime
from openai import OpenAI
from ddgs import DDGS
import os
import json
import fitz  # PyMuPDF
from pathlib import Path

class AIManager:
    def __init__(self, db_session: Session):
        self.db = DatabaseManager(db_session).get_database(DBType.AI_ML_DB)
        self.training_jobs: Dict[str, Dict[str, Any]] = {}
        
        # Initialize OpenAI client with API key from environment variable
        self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY", "your-openai-api-key-here"))
        
        # Verify OpenAI API key is set
        if not self.openai_client.api_key or self.openai_client.api_key == "your-openai-api-key-here":
            print("WARNING: OpenAI API key not set. Please set the OPENAI_API_KEY environment variable.")

    def analyze(self, payload: AIRequest):
        result = {"summary": "placeholder summary", "risk_scores": {"diabetes": 0.1}}
        model = AIParser.parse_result(payload.user_id, result, explanation="placeholder")
        created = self.db.insert(model)
        return AIParser.to_response(created)

    def predict(self, payload: AIRequest):
        return self.analyze(payload)

    def get_result(self, result_id: str):
        m = self.db.get_by_id(result_id)
        return AIParser.to_response(m) if m else None

    def list_models(self) -> List[str]:
        return ["diagnosis-risk-model", "treatment-suggestion-model"]

    def train_model(self, request: TrainingRequest) -> TrainingResponse:
        """
        Train a new model with the provided data and parameters
        
        Args:
            request: TrainingRequest containing model details, data, and parameters
            
        Returns:
            TrainingResponse with training status and metrics
        """
        import uuid
        
        # Generate a unique training ID
        training_id = str(uuid.uuid4())
        
        # Create initial training job
        training_job = {
            'id': training_id,
            'model_name': request.model_name,
            'status': 'pending',
            'created_at': datetime.utcnow(),
            'request': request.dict()
        }
        
        # Store the training job
        self.training_jobs[training_id] = training_job
        
        # In a real implementation, you would start an async training process here
        # For now, we'll simulate a simple training process
        self._start_training(training_id)
        
        return TrainingResponse(
            training_id=training_id,
            model_name=request.model_name,
            status='pending',
            created_at=training_job['created_at']
        )
    
    def _start_training(self, training_id: str):
        import time
        from random import random
        
        # Simulate training delay
        time.sleep(2)
        
        job = self.training_jobs.get(training_id)
        if not job:
            return
            
        try:
            job['status'] = 'training'
            
            # Simulate training time
            time.sleep(5)
            
            # Generate some mock metrics
            metrics = TrainingMetrics(
                accuracy=0.85 + (random() * 0.1),  # 85-95%
                precision=0.82 + (random() * 0.1),
                recall=0.83 + (random() * 0.1),
                f1_score=0.84 + (random() * 0.1),
                loss=0.2 + (random() * 0.1),
                training_time_seconds=5.0 + (random() * 2.0)
            )
            
            # Update job status
            job.update({
                'status': 'completed',
                'completed_at': datetime.utcnow(),
                'metrics': metrics.dict()
            })
            
        except Exception as e:
            job.update({
                'status': 'failed',
                'completed_at': datetime.utcnow(),
                'error': str(e)
            })
    
    def get_training_status(self, training_id: str) -> TrainingResponse:

        job = self.training_jobs.get(training_id)
        if not job:
            raise ValueError(f"No training job found with ID: {training_id}")
            
        return TrainingResponse(
            training_id=job['id'],
            model_name=job['model_name'],
            status=job['status'],
            metrics=job.get('metrics'),
            created_at=job['created_at'],
            completed_at=job.get('completed_at'),
            error=job.get('error')
        )

    def search_and_summarize(self, query: str, max_results: int = 3) -> Dict[str, Any]:
        """
        Perform a web search and generate an AI-powered summary of the results
        
        Args:
            query: The search query string
            max_results: Maximum number of search results to include (1-10)
            
        Returns:
            Dictionary containing the query, summary, sources, and timestamp
        """
        # Ensure max_results is within valid range
        max_results = max(1, min(10, max_results))
        
        # Step 1: Perform web search
        search_results = []
        try:
            with DDGS() as ddgs:
                search_results = [
                    {
                        'title': result.get('title', 'No title'),
                        'url': result.get('href', ''),
                        'snippet': result.get('body', '')
                    }
                    for result in ddgs.text(query, max_results=max_results)
                ]
        except Exception as e:
            raise Exception(f"Error performing web search: {str(e)}")
        
        if not search_results:
            return {
                'query': query,
                'summary': "No results found for the given query.",
                'sources': [],
                'timestamp': datetime.utcnow().isoformat()
            }
        
        # Step 2: Generate summary using OpenAI
        try:
            # Prepare context for summarization
            context = "\n\n".join(
                f"Source {i+1}: {res['title']}\n{res['snippet']}"
                for i, res in enumerate(search_results)
            )
            
            # Call OpenAI API
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant that summarizes search results. Provide a concise and informative summary based on the following sources:"
                    },
                    {
                        "role": "user",
                        "content": f"Query: {query}\n\nSources:\n{context}"
                    }
                ],
                max_tokens=500,
                temperature=0.3
            )
            
            summary = response.choices[0].message.content.strip()
            
            # Prepare response
            return {
                'query': query,
                'summary': summary,
                'sources': [
                    {
                        'title': res['title'],
                        'url': res['url']
                    }
                    for res in search_results
                ],
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            # Fallback to a simple summary if OpenAI fails
            return {
                'query': query,
                'summary': f"Search results for '{query}':\n" + 
                         "\n".join(f"- {res['title']}: {res['snippet']}" for res in search_results[:3]),
                'sources': [
                    {
                        'title': res['title'],
                        'url': res['url']
                    }
                    for res in search_results
                ],
                'timestamp': datetime.utcnow().isoformat(),
                'error': str(e) if str(e) else 'Unknown error occurred'
            }

    def analyze_pdf(self, request: PDFAnalysisRequest) -> PDFAnalysisResponse:
        """
        Analyze and summarize a PDF document
        
        Args:
            request: PDFAnalysisRequest containing pdf_id and analysis parameters
            
        Returns:
            PDFAnalysisResponse with the analysis results
        """
        try:
            # Construct the path to the PDF file
            pdf_path = Path("uploads") / "raw" / "pdfs" / f"{request.pdf_id}.pdf"
            
            if not pdf_path.exists():
                # Try with different extensions if needed
                pdf_path = pdf_path.with_suffix('.PDF')
                if not pdf_path.exists():
                    return PDFAnalysisResponse(
                        pdf_id=request.pdf_id,
                        title="",
                        page_count=0,
                        summary="",
                        error=f"PDF file with ID {request.pdf_id} not found in uploads",
                        created_at=datetime.utcnow()
                    )
            
            # Extract text from PDF
            text, page_count, title = self._extract_text_from_pdf(pdf_path)
            
            # Generate summary using OpenAI
            summary, key_points = self._generate_summary(
                text=text,
                summary_length=request.summary_length,
                include_key_points=request.include_key_points
            )
            
            return PDFAnalysisResponse(
                pdf_id=request.pdf_id,
                title=title or f"Document {request.pdf_id}",
                page_count=page_count,
                summary=summary,
                key_points=key_points if request.include_key_points else None,
                created_at=datetime.utcnow()
            )
            
        except Exception as e:
            return PDFAnalysisResponse(
                pdf_id=request.pdf_id,
                title="",
                page_count=0,
                summary="",
                error=f"Error processing PDF: {str(e)}",
                created_at=datetime.utcnow()
            )
    
    def _extract_text_from_pdf(self, pdf_path: Path) -> tuple[str, int, str]:
        """
        Extract text from a PDF file
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            tuple of (extracted_text, page_count, title)
        """
        text = ""
        title = ""
        
        try:
            with fitz.open(pdf_path) as doc:
                page_count = len(doc)
                
                # Try to get document title from metadata
                meta = doc.metadata
                title = meta.get('title', '').strip()
                
                # Extract text from each page
                for page_num in range(page_count):
                    page = doc.load_page(page_num)
                    text += page.get_text() + "\n\n"
                
                return text.strip(), page_count, title
                
        except Exception as e:
            raise Exception(f"Failed to extract text from PDF: {str(e)}")
    
    def _generate_summary(self, text: str, summary_length: str, include_key_points: bool) -> tuple[str, Optional[List[str]]]:
        """
        Generate a summary and key points using OpenAI
        
        Args:
            text: Text to summarize
            summary_length: Desired length of the summary (short/medium/detailed)
            include_key_points: Whether to include key points
            
        Returns:
            tuple of (summary, key_points)
        """
        try:
            # Determine token limits based on summary length
            max_tokens = {
                "short": 300,
                "medium": 600,
                "detailed": 1000
            }.get(summary_length, 600)
            
            # Prepare the prompt
            system_prompt = (
                "You are an AI assistant that analyzes and summarizes documents. "
                "Your task is to create a clear and concise summary of the provided text. "
                f"The summary should be {summary_length} in length."
            )
            
            if include_key_points:
                system_prompt += " Also extract 3-5 key points from the text."
            
            user_prompt = f"Text to summarize:\n\n{text[:12000]}"  # Limit context window
            
            # Call OpenAI API
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=max_tokens,
                temperature=0.3
            )
            
            result = response.choices[0].message.content
            
            # Parse the response to separate summary and key points if needed
            summary = result
            key_points = None
            
            if include_key_points:
                # Try to split summary and key points if they're in the response
                parts = result.split("\n\nKey Points:")
                if len(parts) > 1:
                    summary = parts[0].strip()
                    key_points = [point.strip() for point in parts[1].split("\n") if point.strip()]
            
            return summary, key_points
            
        except Exception as e:
            raise Exception(f"Failed to generate summary: {str(e)}")
