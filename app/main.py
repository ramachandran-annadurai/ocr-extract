from fastapi import FastAPI, File, UploadFile, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import time
import json
from typing import Dict, Any, List

# Import the real OCR service
from app.services.ocr_service import OCRService
from app.services.pdf_service import PDFService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize services
ocr_service = OCRService()
pdf_service = PDFService()

# Create FastAPI app
app = FastAPI(
    title="PaddleOCR Microservice",
    description="A microservice for text recognition using PaddleOCR",
    version="1.0.0",
    debug=True
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add processing time header to responses"""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """Basic health check for load balancers"""
    return {
        "status": "healthy", 
        "service": "PaddleOCR Microservice",
        "timestamp": time.time(),
        "message": "Service is running",
        "version": "1.0.0"
    }

# Root endpoint for service information
@app.get("/", tags=["Service Info"])
async def root():
    """Root endpoint - Service information"""
    return {
        "name": "PaddleOCR Microservice",
        "version": "1.0.0",
        "description": "A microservice for text recognition using PaddleOCR",
        "status": "running",
        "endpoints": {
            "api_docs": "/docs",
            "health": "/health",
            "ocr_upload": "/api/v1/ocr/upload",
            "ocr_base64": "/api/v1/ocr/base64",
            "webhook_configs": "/api/v1/webhook/configs"
        }
    }

# OCR Endpoints
@app.post("/api/v1/ocr/upload", tags=["OCR"])
async def ocr_upload(file: UploadFile = File(...)):
    """Process uploaded file for OCR using real PaddleOCR or PDF service"""
    try:
        logger.info(f"Processing uploaded file: {file.filename}, type: {file.content_type}")
        
        # Read file content
        contents = await file.read()
        file_size = len(contents)
        
        # Check if it's a PDF
        if file.filename.lower().endswith('.pdf'):
            # Use PDF service for PDF files
            logger.info(f"PDF detected, using PDF service for {file.filename}")
            result = await pdf_service.process_pdf(
                file_data=contents,
                filename=file.filename
            )
        else:
            # Use OCR service for image files
            logger.info(f"Image detected, using OCR service for {file.filename}")
            result = await ocr_service.process_image_file(
                file_data=contents,
                filename=file.filename,
                content_type=file.content_type,
                file_size=file_size
            )
        
        return result
        
    except Exception as e:
        logger.error(f"Error processing file: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

@app.post("/api/v1/ocr/base64", tags=["OCR"])
async def ocr_base64(request: Request):
    """Process base64 encoded image using real PaddleOCR"""
    try:
        body = await request.json()
        image_data = body.get("image", "")
        
        if not image_data:
            raise HTTPException(status_code=400, detail="Base64 image data is required")
        
        # Use the real OCR service
        result = await ocr_service.process_base64_image(image_data)
        
        return result
        
    except Exception as e:
        logger.error(f"Error processing base64 image: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing base64 image: {str(e)}")

@app.get("/api/v1/ocr/languages", tags=["OCR"])
async def get_languages():
    """Get supported OCR languages"""
    return {
        "supported_languages": [
            "en", "ch", "chinese_cht", "ko", "ja", "latin", "arabic", "cyrillic"
        ],
        "current_language": "en",
        "default_language": "en"
    }

# Enhanced OCR endpoints for PDF and document processing
@app.post("/api/v1/ocr/enhanced/upload", tags=["Enhanced OCR"])
async def enhanced_ocr_upload(file: UploadFile = File(...)):
    """Enhanced OCR for multiple file types including PDFs"""
    try:
        logger.info(f"Enhanced OCR processing: {file.filename}, type: {file.content_type}")
        
        contents = await file.read()
        file_size = len(contents)
        
        # Use the real OCR service for enhanced processing
        result = await ocr_service.process_image_file(
            file_data=contents,
            filename=file.filename,
            content_type=file.content_type,
            file_size=file_size
        )
        
        # Add enhanced processing metadata
        result["processing_method"] = "enhanced_ocr"
        result["pages_processed"] = 1
        
        return result
        
    except Exception as e:
        logger.error(f"Enhanced OCR error: {e}")
        raise HTTPException(status_code=500, detail=f"Enhanced OCR error: {str(e)}")

# Webhook Management Endpoints
@app.get("/api/v1/webhook/configs", tags=["Webhook"])
async def list_webhooks():
    """List all webhook configurations"""
    # Mock webhook configurations
    mock_webhooks = [
        {
            "id": "webhook-001",
            "name": "Test Webhook",
            "url": "https://example.com/webhook",
            "enabled": True,
            "method": "POST",
            "created_at": "2024-01-01T00:00:00Z"
        }
    ]
    return mock_webhooks

@app.post("/api/v1/webhook/configs", tags=["Webhook"])
async def create_webhook(request: Request):
    """Create new webhook configuration"""
    try:
        body = await request.json()
        
        # Mock webhook creation
        mock_webhook = {
            "id": f"webhook-{int(time.time())}",
            "name": body.get("name", "New Webhook"),
            "url": body.get("url", ""),
            "enabled": body.get("enabled", True),
            "method": body.get("method", "POST"),
            "timeout": body.get("timeout", 30),
            "retry_attempts": body.get("retry_attempts", 3),
            "created_at": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "message": "Webhook created successfully (mock response)"
        }
        
        return mock_webhook
        
    except Exception as e:
        logger.error(f"Error creating webhook: {e}")
        raise HTTPException(status_code=500, detail=f"Error creating webhook: {str(e)}")

@app.get("/api/v1/webhook/configs/summary", tags=["Webhook"])
async def webhook_summary():
    """Get webhook configuration summary"""
    return {
        "total_configs": 1,
        "enabled_configs": 1,
        "disabled_configs": 0,
        "active_webhooks": 1,
        "last_updated": time.strftime("%Y-%m-%dT%H:%M:%SZ")
    }

@app.get("/api/v1/webhook/environment", tags=["Webhook"])
async def webhook_environment():
    """Get webhook environment settings"""
    return {
        "webhook_enabled": True,
        "max_configs": 100,
        "default_timeout": 30,
        "default_retry_attempts": 3,
        "default_retry_delay": 1,
        "allow_external_urls": True
    }

# Test webhook endpoint
@app.post("/api/v1/webhook/test", tags=["Webhook"])
async def test_webhook():
    """Test webhook functionality with sample data"""
    try:
        # Sample OCR data for testing
        test_data = {
            "success": True,
            "filename": "test_image.jpg",
            "text_count": 2,
            "results": [
                {
                    "text": "Test text for webhook",
                    "confidence": 0.95,
                    "bbox": [[100, 100], [300, 100], [300, 150], [100, 150]]
                },
                {
                    "text": "Another test line",
                    "confidence": 0.92,
                    "bbox": [[100, 200], [350, 200], [350, 250], [100, 250]]
                }
            ]
        }
        
        # Send test webhook
        webhook_results = await ocr_service.webhook_service.send_ocr_result(test_data, "test_image.jpg")
        
        # Show what will be sent in the webhook
        sample_payload = {
            "timestamp": "2024-01-01T00:00:00Z",
            "source": "paddleocr-microservice",
            "filename": "test_image.jpg",
            "ocr_result": test_data,
            "full_text_content": "Test text for webhook Another test line",  # Combined text
            "metadata": {
                "text_count": 2,
                "config_name": "Default n8n Webhook"
            }
        }
        
        return {
            "message": "Test webhook sent",
            "webhook_results": webhook_results,
            "test_data": test_data,
            "sample_webhook_payload": sample_payload
        }
        
    except Exception as e:
        logger.error(f"Test webhook error: {e}")
        raise HTTPException(status_code=500, detail=f"Test webhook error: {str(e)}")

@app.get("/api/v1/webhook/debug", tags=["Webhook"])
async def debug_webhook():
    """Debug webhook configuration and status"""
    try:
        # Get webhook status from OCR service
        ocr_webhook_status = ocr_service.webhook_service.get_webhook_status()
        
        # Get webhook status from PDF service
        pdf_webhook_status = pdf_service.webhook_service.get_webhook_status()
        
        # Get active configurations
        active_configs = ocr_service.webhook_service.config_service.get_active_configs()
        
        # Get config summary
        config_summary = ocr_service.webhook_service.config_service.get_config_summary()
        
        return {
            "ocr_webhook_status": ocr_webhook_status,
            "pdf_webhook_status": pdf_webhook_status,
            "active_configs_count": len(active_configs),
            "active_configs": [
                {
                    "id": config.id,
                    "name": config.name,
                    "url": config.url,
                    "enabled": config.enabled,
                    "method": config.method
                } for config in active_configs
            ],
            "config_summary": config_summary,
            "webhook_enabled": ocr_service.webhook_service.is_configured()
        }
        
    except Exception as e:
        logger.error(f"Debug webhook error: {e}")
        raise HTTPException(status_code=500, detail=f"Debug webhook error: {str(e)}")

# PDF-specific endpoints
@app.post("/api/v1/pdf/process", tags=["PDF"])
async def process_pdf(file: UploadFile = File(...)):
    """Process PDF file with specialized handling"""
    try:
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="File must be a PDF")
        
        contents = await file.read()
        file_size = len(contents)
        
        # Use the real PDF service
        result = await pdf_service.process_pdf(
            file_data=contents,
            filename=file.filename
        )
        
        return result
        
    except Exception as e:
        logger.error(f"PDF processing error: {e}")
        raise HTTPException(status_code=500, detail=f"PDF processing error: {str(e)}")

@app.get("/api/v1/pdf/capabilities", tags=["PDF"])
async def get_pdf_capabilities():
    """Get PDF processing capabilities"""
    return {
        "pdf_service_capabilities": pdf_service.get_processing_capabilities(),
        "supported_formats": pdf_service.get_supported_formats(),
        "processing_methods": [
            "Native text extraction (faster, higher accuracy)",
            "OCR for scanned pages (slower, works with images)",
            "Automatic detection and fallback",
            "Page-by-page analysis",
            "Text confidence scoring"
        ]
    }

# Utility endpoints
@app.get("/api/v1/formats", tags=["Utility"])
async def get_supported_formats():
    """Get supported file formats"""
    return {
        "supported_formats": {
            "images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".tif"],
            "documents": [".pdf", ".txt", ".doc", ".docx"],
            "ocr_supported": [".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".tif", ".pdf"],
            "text_extraction": [".pdf", ".txt", ".doc", ".docx"]
        },
        "max_file_size": "10MB",
        "processing_methods": ["OCR", "Text Extraction", "Enhanced Processing"]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
