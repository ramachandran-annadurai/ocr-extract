from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class Base64ImageRequest(BaseModel):
    """Request model for base64 image processing"""
    image: str = Field(..., description="Base64 encoded image string")

class OCRResult(BaseModel):
    """Model for individual OCR result"""
    text: str = Field(..., description="Extracted text")
    confidence: float = Field(..., description="Confidence score (0.0 to 1.0)")
    bbox: List[List[float]] = Field(..., description="Bounding box coordinates")

class OCRResponse(BaseModel):
    """Response model for OCR operations"""
    success: bool = Field(..., description="Operation success status")
    filename: Optional[str] = Field(None, description="Original filename")
    text_count: int = Field(..., description="Number of text elements found")
    results: List[OCRResult] = Field(..., description="List of extracted text results")

class HealthResponse(BaseModel):
    """Health check response model"""
    status: str = Field(..., description="Service status")
    paddleocr_initialized: bool = Field(..., description="PaddleOCR initialization status")
    language: str = Field(..., description="Current OCR language")
    angle_classification: bool = Field(..., description="Angle classification status")

class LanguagesResponse(BaseModel):
    """Supported languages response model"""
    supported_languages: List[str] = Field(..., description="List of supported languages")
    current_language: str = Field(..., description="Currently active language")

class ErrorResponse(BaseModel):
    """Error response model"""
    detail: str = Field(..., description="Error description")
    error_code: Optional[str] = Field(None, description="Error code")
    timestamp: Optional[str] = Field(None, description="Error timestamp")

class ServiceInfo(BaseModel):
    """Service information model"""
    name: str = Field(..., description="Service name")
    version: str = Field(..., description="Service version")
    description: str = Field(..., description="Service description")
    status: str = Field(..., description="Service status")
