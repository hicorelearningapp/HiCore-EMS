import os
from typing import Optional
from fastapi import UploadFile, HTTPException, status
from PIL import Image
import pytesseract
from pytesseract import Output
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import io
import uuid

class DocumentProcessor:
    """
    Service for processing documents including OCR functionality
    """
    
    @staticmethod
    def get_ocr_text(image_path: str) -> str:
        """Extract text from an image using OCR"""
        try:
            img = Image.open(image_path)
            return pytesseract.image_to_string(img)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error processing image with OCR: {str(e)}"
            )
    
    @staticmethod
    def image_to_searchable_pdf(
        image_file: UploadFile, 
        output_dir: str = "uploads/processed"
    ) -> str:
        """
        Convert an image to a searchable PDF with OCR text layer
        
        Args:
            image_file: Uploaded image file
            output_dir: Directory to save the processed PDF
            
        Returns:
            str: Path to the generated PDF file
        """
        try:
            # Create output directory if it doesn't exist
            os.makedirs(output_dir, exist_ok=True)
            
            # Generate unique filename
            file_ext = os.path.splitext(image_file.filename)[1] if image_file.filename else '.pdf'
            output_filename = f"{uuid.uuid4()}.pdf"
            output_path = os.path.join(output_dir, output_filename)
            
            # Save the uploaded file temporarily
            temp_img_path = f"temp_{uuid.uuid4()}.png"
            with open(temp_img_path, "wb") as buffer:
                buffer.write(image_file.file.read())
            
            # Load image
            img = Image.open(temp_img_path)

            # Run OCR with bounding box data
            data = pytesseract.image_to_data(img, output_type=Output.DICT)

            # Create a PDF
            pdf = canvas.Canvas(output_path, pagesize=letter)
            page_width, page_height = letter

            # Scale image size to PDF page
            img_width, img_height = img.size
            scale_x = page_width / img_width
            scale_y = page_height / img_height
            scale = min(scale_x, scale_y)

            # Draw original image as background
            pdf.drawInlineImage(temp_img_path, 0, 0, img_width * scale, img_height * scale)

            # Make text transparent but selectable
            pdf.setFillColorRGB(0, 0, 0, alpha=0.01)  # Almost transparent black
            pdf.setStrokeColorRGB(0, 0, 0, alpha=0)    # Invisible stroke
            
            # Set a small font size that won't be visible but will be searchable
            pdf.setFont("Helvetica", 1)
            
            # Place recognized text
            n_boxes = len(data['text'])
            for i in range(n_boxes):
                if int(data['conf'][i]) > 50:  # only take words with >50% confidence
                    (x, y, w, h) = (data['left'][i], data['top'][i], 
                                 data['width'][i], data['height'][i])
                    text = data['text'][i].strip()
                    
                    if not text:  # Skip empty text
                        continue
                        
                    # Map OCR coords to PDF coords
                    pdf_x = x * scale
                    pdf_y = page_height - (y * scale)  # invert y-axis for PDF
                    
                    # Add text to PDF (invisible but searchable)
                    text_obj = pdf.beginText(pdf_x, pdf_y)
                    text_obj.textLine(text)
                    pdf.drawText(text_obj)

            pdf.save()
            
            # Clean up temporary file
            os.remove(temp_img_path)
            
            return output_path
            
        except Exception as e:
            # Clean up in case of error
            if 'temp_img_path' in locals() and os.path.exists(temp_img_path):
                os.remove(temp_img_path)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error creating searchable PDF: {str(e)}"
            )
