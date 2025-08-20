import logging
from typing import List, Dict, Any, Optional, Tuple
import cv2
import numpy as np
from PIL import Image
import io
import base64
from paddleocr import PaddleOCR
from app.config import settings
from app.services.webhook_service import WebhookService

logger = logging.getLogger(__name__)

class OCRService:
    """Service class for handling OCR operations using PaddleOCR"""
    
    def __init__(self):
        self.ocr: Optional[PaddleOCR] = None
        self.webhook_service = WebhookService()
        self._initialize_ocr()
    
    def _initialize_ocr(self) -> None:
        """Initialize PaddleOCR with configuration"""
        try:
            self.ocr = PaddleOCR(
                use_angle_cls=settings.PADDLE_OCR_USE_ANGLE_CLS,
                lang=settings.PADDLE_OCR_LANG,
                show_log=settings.PADDLE_OCR_SHOW_LOG
            )
            logger.info(f"PaddleOCR initialized successfully with language: {settings.PADDLE_OCR_LANG}")
        except Exception as e:
            logger.error(f"Failed to initialize PaddleOCR: {e}")
            self.ocr = None
            raise RuntimeError(f"PaddleOCR initialization failed: {e}")
    
    def is_initialized(self) -> bool:
        """Check if OCR service is properly initialized"""
        return self.ocr is not None
    
    def _validate_image_type(self, content_type: str) -> bool:
        """Validate if the uploaded file is a supported image type"""
        return content_type in settings.ALLOWED_IMAGE_TYPES
    
    def _validate_file_size(self, file_size: int) -> bool:
        """Validate if the uploaded file size is within limits"""
        return file_size <= settings.MAX_FILE_SIZE
    
    def _process_image(self, image_data: bytes) -> np.ndarray:
        """Process image data and convert to OpenCV format"""
        try:
            # Read image using PIL
            image = Image.open(io.BytesIO(image_data))
            
            # Convert PIL image to OpenCV format
            opencv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            
            return opencv_image
        except Exception as e:
            logger.error(f"Error processing image: {e}")
            raise ValueError(f"Invalid image format: {e}")
    
    def _extract_text_from_result(self, ocr_result: List) -> List[Dict[str, Any]]:
        """Extract and format text from OCR result"""
        extracted_text = []
        
        if ocr_result and ocr_result[0]:
            for line in ocr_result[0]:
                if line:
                    text = line[1][0]  # Extract text
                    confidence = line[1][1]  # Extract confidence score
                    bbox = line[0]  # Extract bounding box coordinates
                    
                    extracted_text.append({
                        "text": text,
                        "confidence": float(confidence),
                        "bbox": bbox
                    })
        
        return extracted_text
    
    async def process_image_file(self, file_data: bytes, filename: str, content_type: str, file_size: int) -> Dict[str, Any]:
        """Process uploaded image file and extract text"""
        # Validate file type and size
        if not self._validate_image_type(content_type):
            raise ValueError(f"Unsupported file type: {content_type}. Allowed types: {settings.ALLOWED_IMAGE_TYPES}")
        
        if not self._validate_file_size(file_size):
            raise ValueError(f"File size {file_size} bytes exceeds maximum allowed size of {settings.MAX_FILE_SIZE} bytes")
        
        # Process image
        opencv_image = self._process_image(file_data)
        
        # Perform OCR
        result = self.ocr.ocr(opencv_image, cls=True)
        
        # Extract text from result
        extracted_text = self._extract_text_from_result(result)
        
        # Prepare response
        response_data = {
            "success": True,
            "filename": filename,
            "text_count": len(extracted_text),
            "results": extracted_text
        }
        
        logger.info(f"Successfully processed image {filename}: {len(extracted_text)} text elements found")
        
        # Send webhook to n8n (non-blocking)
        try:
            await self.webhook_service.send_ocr_result(response_data, filename)
        except Exception as e:
            logger.error(f"Failed to send webhook: {e}")
            # Don't fail the main request if webhook fails
        
        return response_data
    
    async def process_base64_image(self, base64_string: str) -> Dict[str, Any]:
        """Process base64 encoded image and extract text"""
        try:
            # Remove data URL prefix if present
            if base64_string.startswith('data:image'):
                base64_string = base64_string.split(',')[1]
            
            # Decode base64 to image
            image_bytes = base64.b64decode(base64_string)
            
            # Process image
            opencv_image = self._process_image(image_bytes)
            
            # Perform OCR
            result = self.ocr.ocr(opencv_image, cls=True)
            
            # Extract text from result
            extracted_text = self._extract_text_from_result(result)
            
            # Prepare response
            response_data = {
                "success": True,
                "text_count": len(extracted_text),
                "results": extracted_text
            }
            
            logger.info(f"Successfully processed base64 image: {len(extracted_text)} text elements found")
            
            # Send webhook to n8n (non-blocking)
            try:
                await self.webhook_service.send_ocr_result(response_data)
            except Exception as e:
                logger.error(f"Failed to send webhook: {e}")
                # Don't fail the main request if webhook fails
            
            return response_data
            
        except Exception as e:
            logger.error(f"Error processing base64 image: {e}")
            raise ValueError(f"Invalid base64 image data: {e}")
    
    def get_supported_languages(self) -> Dict[str, Any]:
        """Get list of supported languages"""
        return {
            "supported_languages": [
                "en", "ch", "chinese_cht", "ko", "ja", "latin", "arabic", "cyrillic"
            ],
            "current_language": settings.PADDLE_OCR_LANG
        }
    
    def get_service_status(self) -> Dict[str, Any]:
        """Get current service status"""
        return {
            "status": "healthy" if self.is_initialized() else "unhealthy",
            "paddleocr_initialized": self.is_initialized(),
            "language": settings.PADDLE_OCR_LANG,
            "angle_classification": settings.PADDLE_OCR_USE_ANGLE_CLS,
            "webhook_status": self.webhook_service.get_webhook_status()
        }
