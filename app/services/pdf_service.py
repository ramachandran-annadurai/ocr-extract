import logging
import fitz  # PyMuPDF
import io
from typing import Dict, Any, List, Optional, Tuple
from PIL import Image
import numpy as np
import cv2
from app.services.ocr_service import OCRService
from app.services.webhook_service import WebhookService

logger = logging.getLogger(__name__)

class PDFService:
    """Service for processing PDF files with text extraction and OCR capabilities"""
    
    def __init__(self):
        self.ocr_service = OCRService()
        self.webhook_service = WebhookService()
    
    async def process_pdf(self, file_data: bytes, filename: str) -> Dict[str, Any]:
        """Process PDF file with comprehensive text extraction"""
        try:
            logger.info(f"Processing PDF: {filename}")
            
            # Open PDF with PyMuPDF
            pdf_document = fitz.open(stream=file_data, filetype="pdf")
            total_pages = len(pdf_document)
            
            all_text_results = []
            pages_processed = 0
            text_extracted = False
            ocr_used = False
            
            for page_num in range(total_pages):
                page = pdf_document[page_num]
                page_result = await self._process_page(page, page_num + 1)
                
                if page_result:
                    all_text_results.append(page_result)
                    pages_processed += 1
                    
                    if page_result.get("text_type") == "native":
                        text_extracted = True
                    elif page_result.get("text_type") == "ocr":
                        ocr_used = True
            
            pdf_document.close()
            
            # Combine all text for webhook
            full_text_content = self._combine_text_results(all_text_results)
            
            result = {
                "success": True,
                "filename": filename,
                "file_size": len(file_data),
                "pdf_pages": total_pages,
                "pages_processed": pages_processed,
                "text_extracted": text_extracted,
                "ocr_used": ocr_used,
                "text_count": len(all_text_results),
                "results": all_text_results,
                "full_text_content": full_text_content,
                "processing_method": "pdf_comprehensive",
                "message": f"PDF processed successfully: {pages_processed}/{total_pages} pages"
            }
            
            logger.info(f"PDF {filename} processed: {pages_processed} pages, text extracted: {text_extracted}, OCR used: {ocr_used}")
            
            # Send webhook to n8n (non-blocking)
            logger.info(f"Attempting to send webhook for PDF: {filename}")
            try:
                webhook_results = await self.webhook_service.send_ocr_result(result, filename)
                logger.info(f"Webhook sent successfully for PDF: {filename}. Results: {webhook_results}")
            except Exception as e:
                logger.error(f"Failed to send webhook for PDF {filename}: {e}")
                import traceback
                logger.error(f"Webhook error traceback: {traceback.format_exc()}")
                # Don't fail the main request if webhook fails
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing PDF {filename}: {e}")
            raise ValueError(f"PDF processing failed: {str(e)}")
    
    async def _process_page(self, page, page_num: int) -> Optional[Dict[str, Any]]:
        """Process individual PDF page"""
        try:
            # Try to extract native text first
            native_text = page.get_text()
            
            if native_text and native_text.strip():
                # Native text found
                return {
                    "page": page_num,
                    "text": native_text.strip(),
                    "text_type": "native",
                    "confidence": 1.0,
                    "bbox": None
                }
            else:
                # No native text, try OCR
                return await self._ocr_page(page, page_num)
                
        except Exception as e:
            logger.warning(f"Error processing page {page_num}: {e}")
            # Try OCR as fallback
            return await self._ocr_page(page, page_num)
    
    async def _ocr_page(self, page, page_num: int) -> Optional[Dict[str, Any]]:
        """Extract text from page using OCR"""
        try:
            # Convert page to image
            mat = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # 2x zoom for better OCR
            img_data = mat.tobytes("png")
            
            # Convert to PIL Image then to OpenCV format
            pil_image = Image.open(io.BytesIO(img_data))
            opencv_image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
            
            # Perform OCR
            ocr_result = self.ocr_service.ocr.ocr(opencv_image, cls=True)
            
            if ocr_result and ocr_result[0]:
                # Extract text from OCR result
                page_texts = []
                for line in ocr_result[0]:
                    if line:
                        text = line[1][0]  # Extract text
                        confidence = line[1][1]  # Extract confidence
                        bbox = line[0]  # Extract bounding box
                        
                        page_texts.append({
                            "text": text,
                            "confidence": float(confidence),
                            "bbox": bbox
                        })
                
                if page_texts:
                    # Combine all text from the page
                    combined_text = " ".join([item["text"] for item in page_texts])
                    
                    return {
                        "page": page_num,
                        "text": combined_text,
                        "text_type": "ocr",
                        "confidence": sum([item["confidence"] for item in page_texts]) / len(page_texts),
                        "bbox": None,
                        "ocr_details": page_texts
                    }
            
            # No text found
            return {
                "page": page_num,
                "text": "",
                "text_type": "no_text",
                "confidence": 0.0,
                "bbox": None
            }
            
        except Exception as e:
            logger.error(f"OCR failed for page {page_num}: {e}")
            return {
                "page": page_num,
                "text": "",
                "text_type": "error",
                "confidence": 0.0,
                "bbox": None,
                "error": str(e)
            }
    
    def _combine_text_results(self, text_results: List[Dict[str, Any]]) -> str:
        """Combine all text results into a single string"""
        text_parts = []
        
        for result in text_results:
            if result.get("text") and result.get("text").strip():
                text_parts.append(result["text"].strip())
        
        return " ".join(text_parts)
    
    def get_supported_formats(self) -> List[str]:
        """Get supported PDF formats"""
        return [".pdf"]
    
    def get_processing_capabilities(self) -> Dict[str, Any]:
        """Get PDF processing capabilities"""
        return {
            "native_text_extraction": True,
            "ocr_for_scanned_pages": True,
            "page_by_page_processing": True,
            "text_confidence_scoring": True,
            "bbox_extraction": True,
            "supported_pdf_versions": ["PDF 1.0", "PDF 1.1", "PDF 1.2", "PDF 1.3", "PDF 1.4", "PDF 1.5", "PDF 1.6", "PDF 1.7", "PDF 2.0"]
        }
