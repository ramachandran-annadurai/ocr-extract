from fastapi import FastAPI, File, UploadFile, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import time
import json
from typing import Dict, Any, List

# Import the real OCR service
from app.services.ocr_service import OCRService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize OCR service
ocr_service = OCRService()

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

# OCR Endpoints with real PaddleOCR functionality
@app.post("/api/v1/ocr/upload", tags=["OCR"])
async def ocr_upload(file: UploadFile = File(...)):
    """Process uploaded file for OCR using real PaddleOCR"""
    try:
        logger.info(f"Processing uploaded file: {file.filename}, type: {file.content_type}")
        
        # Read file content
        contents = await file.read()
        file_size = len(contents)
        
        # Use the real OCR service for image files
        logger.info(f"Using OCR service for {file.filename}")
        result = await ocr_service.process_image_file(
            file_data=contents,
            filename=file.filename,
            content_type=file.content_type,
            file_size=file_size
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error processing file {file.filename}: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

@app.post("/api/v1/ocr/base64", tags=["OCR"])
async def ocr_base64(request: Request):
    """Process base64 encoded image using real PaddleOCR"""
    try:
        data = await request.json()
        image_data = data.get("image")
        
        if not image_data:
            raise HTTPException(status_code=400, detail="Image data is required")
        
        # Use the real OCR service
        result = await ocr_service.process_base64_image(image_data)
        
        return result
        
    except Exception as e:
        logger.error(f"Error processing base64 image: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")

# Webhook endpoints
@app.get("/api/v1/webhook/configs", tags=["Webhooks"])
async def get_webhook_configs():
    """Get webhook configurations"""
    try:
        # Get webhook configs from OCR service
        configs = ocr_service.webhook_service.config_service.get_all_configs()
        return {
            "status": "success",
            "configs": configs,
            "timestamp": time.time()
        }
    except Exception as e:
        logger.error(f"Error getting webhook configs: {e}")
        return {
            "status": "error",
            "message": "Error getting webhook configs",
            "timestamp": time.time()
        }

@app.post("/api/v1/webhook/test", tags=["Webhooks"])
async def test_webhook():
    """Test webhook endpoint"""
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
        
        return {
            "message": "Test webhook sent",
            "webhook_results": webhook_results,
            "test_data": test_data
        }
        
    except Exception as e:
        logger.error(f"Test webhook error: {e}")
        raise HTTPException(status_code=500, detail=f"Test webhook error: {str(e)}")

@app.get("/api/v1/webhook/debug", tags=["Webhooks"])
async def webhook_debug():
    """Debug webhook configuration and status"""
    try:
        # Get webhook status from OCR service
        webhook_status = ocr_service.webhook_service.get_webhook_status()
        
        # Get active configurations
        active_configs = ocr_service.webhook_service.config_service.get_active_configs()
        
        return {
            "webhook_status": webhook_status,
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
            "webhook_enabled": ocr_service.webhook_service.is_configured()
        }
        
    except Exception as e:
        logger.error(f"Debug webhook error: {e}")
        raise HTTPException(status_code=500, detail=f"Debug webhook error: {str(e)}")

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "timestamp": time.time(),
            "path": str(request.url)
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions"""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "timestamp": time.time(),
            "path": str(request.url)
        }
    )
