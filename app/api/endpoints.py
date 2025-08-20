from fastapi import APIRouter, File, UploadFile, HTTPException, Depends
from fastapi.responses import JSONResponse
import logging
from typing import Dict, Any, List
from datetime import datetime

from app.services.ocr_service import OCRService
from app.services.webhook_service import WebhookService
from app.services.webhook_config_service import WebhookConfigService
from app.models.schemas import (
    Base64ImageRequest, OCRResponse, HealthResponse, 
    LanguagesResponse, ServiceInfo, ErrorResponse
)
from app.models.webhook_config import (
    WebhookConfig, WebhookConfigCreate, WebhookConfigUpdate, WebhookResponse
)
from app.config import settings

logger = logging.getLogger(__name__)

# Create router
router = APIRouter()

# Dependency to get OCR service
def get_ocr_service() -> OCRService:
    """Dependency to get OCR service instance"""
    return OCRService()

# Dependency to get webhook service
def get_webhook_service() -> WebhookService:
    """Dependency to get webhook service instance"""
    return WebhookService()

# Dependency to get webhook config service
def get_webhook_config_service() -> WebhookConfigService:
    """Dependency to get webhook config service instance"""
    return WebhookConfigService()

@router.get("/", response_model=ServiceInfo, tags=["Service Info"])
async def root():
    """Root endpoint - Service information"""
    return ServiceInfo(
        name=settings.APP_NAME,
        version=settings.APP_VERSION,
        description=settings.APP_DESCRIPTION,
        status="running"
    )

@router.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check(ocr_service: OCRService = Depends(get_ocr_service)):
    """Health check endpoint"""
    try:
        status = ocr_service.get_service_status()
        return HealthResponse(**status)
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail="Health check failed")

@router.post("/ocr/upload", response_model=OCRResponse, tags=["OCR"])
async def ocr_upload(
    file: UploadFile = File(...),
    ocr_service: OCRService = Depends(get_ocr_service)
):
    """Extract text from uploaded image file"""
    try:
        # Read file content
        contents = await file.read()
        file_size = len(contents)
        
        logger.info(f"Processing uploaded file: {file.filename}, size: {file_size} bytes")
        
        # Process image using OCR service
        result = await ocr_service.process_image_file(
            file_data=contents,
            filename=file.filename,
            content_type=file.content_type,
            file_size=file_size
        )
        
        return OCRResponse(**result)
        
    except ValueError as e:
        logger.warning(f"Validation error for file {file.filename}: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error processing uploaded file {file.filename}: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")

@router.post("/ocr/base64", response_model=OCRResponse, tags=["OCR"])
async def ocr_base64(
    image_data: Base64ImageRequest,
    ocr_service: OCRService = Depends(get_ocr_service)
):
    """Extract text from base64 encoded image"""
    try:
        logger.info("Processing base64 encoded image")
        
        # Process base64 image using OCR service
        result = await ocr_service.process_base64_image(image_data.image)
        
        return OCRResponse(**result)
        
    except ValueError as e:
        logger.warning(f"Validation error for base64 image: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error processing base64 image: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing base64 image: {str(e)}")

@router.get("/ocr/languages", response_model=LanguagesResponse, tags=["OCR"])
async def get_supported_languages(ocr_service: OCRService = Depends(get_ocr_service)):
    """Get list of supported languages"""
    try:
        languages = ocr_service.get_supported_languages()
        return LanguagesResponse(**languages)
    except Exception as e:
        logger.error(f"Error getting supported languages: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving supported languages")

# Webhook Configuration Management Endpoints
@router.get("/webhook/configs", response_model=List[WebhookConfig], tags=["Webhook Config"])
async def get_all_webhook_configs(
    config_service: WebhookConfigService = Depends(get_webhook_config_service)
):
    """Get all webhook configurations"""
    try:
        configs = config_service.get_all_configs()
        return configs
    except Exception as e:
        logger.error(f"Error getting webhook configs: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving webhook configurations")

@router.get("/webhook/configs/{config_id}", response_model=WebhookConfig, tags=["Webhook Config"])
async def get_webhook_config(
    config_id: str,
    config_service: WebhookConfigService = Depends(get_webhook_config_service)
):
    """Get specific webhook configuration by ID"""
    try:
        config = config_service.get_config(config_id)
        if not config:
            raise HTTPException(status_code=404, detail="Webhook configuration not found")
        return config
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting webhook config {config_id}: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving webhook configuration")

@router.post("/webhook/configs", response_model=WebhookConfig, tags=["Webhook Config"])
async def create_webhook_config(
    config_data: WebhookConfigCreate,
    config_service: WebhookConfigService = Depends(get_webhook_config_service)
):
    """Create a new webhook configuration"""
    try:
        config = config_service.create_config(config_data)
        return config
    except Exception as e:
        logger.error(f"Error creating webhook config: {e}")
        raise HTTPException(status_code=500, detail="Error creating webhook configuration")

@router.put("/webhook/configs/{config_id}", response_model=WebhookConfig, tags=["Webhook Config"])
async def update_webhook_config(
    config_id: str,
    config_data: WebhookConfigUpdate,
    config_service: WebhookConfigService = Depends(get_webhook_config_service)
):
    """Update webhook configuration"""
    try:
        config = config_service.update_config(config_id, config_data)
        if not config:
            raise HTTPException(status_code=404, detail="Webhook configuration not found")
        return config
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating webhook config {config_id}: {e}")
        raise HTTPException(status_code=500, detail="Error updating webhook configuration")

@router.delete("/webhook/configs/{config_id}", tags=["Webhook Config"])
async def delete_webhook_config(
    config_id: str,
    config_service: WebhookConfigService = Depends(get_webhook_config_service)
):
    """Delete webhook configuration"""
    try:
        success = config_service.delete_config(config_id)
        if not success:
            raise HTTPException(status_code=404, detail="Webhook configuration not found")
        return {"message": "Webhook configuration deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting webhook config {config_id}: {e}")
        raise HTTPException(status_code=500, detail="Error deleting webhook configuration")

@router.post("/webhook/configs/{config_id}/enable", tags=["Webhook Config"])
async def enable_webhook_config(
    config_id: str,
    config_service: WebhookConfigService = Depends(get_webhook_config_service)
):
    """Enable webhook configuration"""
    try:
        success = config_service.enable_config(config_id)
        if not success:
            raise HTTPException(status_code=404, detail="Webhook configuration not found")
        return {"message": "Webhook configuration enabled successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error enabling webhook config {config_id}: {e}")
        raise HTTPException(status_code=500, detail="Error enabling webhook configuration")

@router.post("/webhook/configs/{config_id}/disable", tags=["Webhook Config"])
async def disable_webhook_config(
    config_id: str,
    config_service: WebhookConfigService = Depends(get_webhook_config_service)
):
    """Disable webhook configuration"""
    try:
        success = config_service.disable_config(config_id)
        if not success:
            raise HTTPException(status_code=404, detail="Webhook configuration not found")
        return {"message": "Webhook configuration disabled successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error disabling webhook config {config_id}: {e}")
        raise HTTPException(status_code=500, detail="Error disabling webhook configuration")

@router.post("/webhook/configs/{config_id}/test", tags=["Webhook Config"])
async def test_webhook_config(
    config_id: str,
    config_service: WebhookConfigService = Depends(get_webhook_config_service)
):
    """Test webhook configuration"""
    try:
        result = config_service.test_config(config_id)
        return result
    except Exception as e:
        logger.error(f"Error testing webhook config {config_id}: {e}")
        raise HTTPException(status_code=500, detail="Error testing webhook configuration")

@router.get("/webhook/configs/summary", tags=["Webhook Config"])
async def get_webhook_config_summary(
    config_service: WebhookConfigService = Depends(get_webhook_config_service)
):
    """Get webhook configuration summary"""
    try:
        summary = config_service.get_config_summary()
        return summary
    except Exception as e:
        logger.error(f"Error getting webhook config summary: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving webhook configuration summary")

@router.get("/webhook/environment", tags=["Webhook Config"])
async def get_webhook_environment_info(
    config_service: WebhookConfigService = Depends(get_webhook_config_service)
):
    """Get webhook environment configuration information"""
    try:
        env_info = config_service.get_environment_info()
        return env_info
    except Exception as e:
        logger.error(f"Error getting webhook environment info: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving webhook environment information")

# Webhook Service Endpoints
@router.get("/webhook/status", tags=["Webhook"])
async def get_webhook_status(webhook_service: WebhookService = Depends(get_webhook_service)):
    """Get webhook service status and configuration"""
    try:
        status = webhook_service.get_webhook_status()
        return {
            "webhook_status": status,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting webhook status: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving webhook status")

@router.post("/webhook/test", tags=["Webhook"])
async def test_webhook(webhook_service: WebhookService = Depends(get_webhook_service)):
    """Test webhook by sending a sample payload"""
    try:
        if not webhook_service.is_configured():
            raise HTTPException(status_code=400, detail="No webhook configurations found")
        
        # Send test payload
        test_data = {
            "success": True,
            "filename": "test_sample.jpg",
            "text_count": 2,
            "results": [
                {
                    "text": "Test OCR Result",
                    "confidence": 0.95,
                    "bbox": [[[0, 0], [100, 0], [100, 20], [0, 20]]]
                },
                {
                    "text": "Sample Text",
                    "confidence": 0.87,
                    "bbox": [[[0, 30], [80, 30], [80, 50], [0, 50]]]
                }
            ]
        }
        
        results = await webhook_service.send_ocr_result(test_data, "test_sample.jpg")
        
        return {
            "message": "Test webhook sent",
            "results": results,
            "total_configs": len(results)
        }
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error testing webhook: {e}")
        raise HTTPException(status_code=500, detail=f"Error testing webhook: {str(e)}")

@router.get("/metrics", tags=["Monitoring"])
async def get_metrics():
    """Get service metrics (placeholder for monitoring)"""
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "operational"
    }
