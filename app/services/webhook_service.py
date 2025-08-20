import logging
import asyncio
import aiohttp
from typing import Dict, Any, Optional, List
from datetime import datetime
from app.services.webhook_config_service import WebhookConfigService

logger = logging.getLogger(__name__)

class WebhookService:
    """Service for sending webhooks using dynamic configurations"""
    
    def __init__(self):
        self.config_service = WebhookConfigService()
    
    async def send_ocr_result(self, ocr_data: Dict[str, Any], filename: Optional[str] = None) -> List[Dict[str, Any]]:
        """Send OCR results to all active webhook configurations"""
        logger.info(f"Starting webhook process for file: {filename}")
        logger.info(f"OCR data keys: {list(ocr_data.keys())}")
        
        active_configs = self.config_service.get_active_configs()
        logger.info(f"Found {len(active_configs)} active webhook configurations")
        
        if not active_configs:
            logger.warning("No active webhook configurations found")
            return []
        
        results = []
        
        for config in active_configs:
            logger.info(f"Processing webhook config: {config.name} -> {config.url}")
            try:
                success = await self._send_webhook_with_config(config, ocr_data, filename)
                results.append({
                    "config_id": config.id,
                    "config_name": config.name,
                    "url": config.url,
                    "success": success,
                    "timestamp": datetime.utcnow().isoformat()
                })
                
                if success:
                    logger.info(f"Webhook sent successfully to {config.name} ({config.url})")
                else:
                    logger.warning(f"Failed to send webhook to {config.name}")
                    
            except Exception as e:
                logger.error(f"Error sending webhook to {config.name}: {e}")
                results.append({
                    "config_id": config.id,
                    "config_name": config.name,
                    "url": config.url,
                    "success": False,
                    "error": str(e),
                    "timestamp": datetime.utcnow().isoformat()
                })
        
        logger.info(f"Webhook process completed. Results: {results}")
        return results
    
    async def _send_webhook_with_config(self, config: Any, ocr_data: Dict[str, Any], filename: Optional[str] = None) -> bool:
        """Send webhook using specific configuration"""
        if not config.enabled or not config.url:
            return False
        
        # Prepare webhook payload
        payload = self._prepare_payload(config, ocr_data, filename)
        
        # Send webhook with retry logic
        for attempt in range(config.retry_attempts):
            try:
                success = await self._send_webhook_request(config, payload)
                if success:
                    return True
                else:
                    logger.warning(f"Webhook attempt {attempt + 1} failed for {config.name}")
            except Exception as e:
                logger.error(f"Webhook attempt {attempt + 1} error for {config.name}: {e}")
            
            # Wait before retry (exponential backoff)
            if attempt < config.retry_attempts - 1:
                wait_time = config.retry_delay * (2 ** attempt)
                logger.info(f"Waiting {wait_time} seconds before retry for {config.name}...")
                await asyncio.sleep(wait_time)
        
        logger.error(f"Failed to send webhook to {config.name} after {config.retry_attempts} attempts")
        return False
    
    def _prepare_payload(self, config: Any, ocr_data: Dict[str, Any], filename: Optional[str] = None) -> Dict[str, Any]:
        """Prepare webhook payload based on configuration template"""
        # Extract all text content and combine into a single string
        full_text_content = ""
        
        # Handle different data structures (OCR results vs PDF results)
        if "results" in ocr_data and ocr_data["results"]:
            text_parts = []
            for result in ocr_data["results"]:
                if isinstance(result, dict):
                    # For OCR results
                    if "text" in result:
                        text_parts.append(result["text"])
                    # For PDF results
                    elif "text" in result and result.get("text"):
                        text_parts.append(result["text"])
            
            full_text_content = " ".join(text_parts)
        
        # If full_text_content is already provided (e.g., from PDF service)
        if not full_text_content and "full_text_content" in ocr_data:
            full_text_content = ocr_data["full_text_content"]
        
        # Start with default payload
        default_payload = {
            "timestamp": datetime.utcnow().isoformat(),
            "source": "paddleocr-microservice",
            "filename": filename,
            "ocr_result": ocr_data,
            "full_text_content": full_text_content,  # Combined text content
            "metadata": {
                "text_count": ocr_data.get("text_count", 0),
                "config_name": config.name,
                "processing_method": ocr_data.get("processing_method", "unknown"),
                "file_type": "pdf" if filename and filename.lower().endswith('.pdf') else "image"
            }
        }
        
        # Apply custom payload template if configured
        if config.payload_template:
            # Merge custom template with default payload
            # Custom template can override or add fields
            payload = default_payload.copy()
            payload.update(config.payload_template)
            
            # Replace placeholders in custom template
            payload = self._replace_placeholders(payload, ocr_data, filename, config)
        else:
            payload = default_payload
        
        return payload
    
    def _replace_placeholders(self, payload: Dict[str, Any], ocr_data: Dict[str, Any], filename: Optional[str], config: Any) -> Dict[str, Any]:
        """Replace placeholders in payload template with actual values"""
        import json
        
        # Extract full text content for placeholder replacement
        full_text_content = ""
        if "results" in ocr_data and ocr_data["results"]:
            text_parts = []
            for result in ocr_data["results"]:
                if isinstance(result, dict) and "text" in result:
                    text_parts.append(result["text"])
            full_text_content = " ".join(text_parts)
        
        # Convert to string for replacement
        payload_str = json.dumps(payload)
        
        # Replace common placeholders
        replacements = {
            "{{filename}}": filename or "unknown",
            "{{text_count}}": str(ocr_data.get("text_count", 0)),
            "{{config_name}}": config.name,
            "{{timestamp}}": datetime.utcnow().isoformat(),
            "{{ocr_data}}": json.dumps(ocr_data),
            "{{full_text_content}}": full_text_content  # New placeholder for combined text
        }
        
        for placeholder, value in replacements.items():
            payload_str = payload_str.replace(placeholder, value)
        
        # Convert back to dict
        try:
            return json.loads(payload_str)
        except:
            return payload
    
    async def _send_webhook_request(self, config: Any, payload: Dict[str, Any]) -> bool:
        """Send webhook request with configuration settings"""
        try:
            timeout = aiohttp.ClientTimeout(total=config.timeout)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                # Prepare headers
                headers = config.headers.copy()
                if "Content-Type" not in headers:
                    headers["Content-Type"] = "application/json"
                
                # Send request
                async with session.request(
                    method=config.method,
                    url=config.url,
                    json=payload,
                    headers=headers
                ) as response:
                    if response.status in [200, 201, 202]:
                        logger.info(f"Webhook sent successfully to {config.name}. Status: {response.status}")
                        return True
                    else:
                        logger.error(f"Webhook failed for {config.name} with status: {response.status}")
                        return False
                        
        except asyncio.TimeoutError:
            logger.error(f"Webhook timeout for {config.name} after {config.timeout} seconds")
            return False
        except Exception as e:
            logger.error(f"Webhook error for {config.name}: {e}")
            return False
    
    def get_webhook_status(self) -> Dict[str, Any]:
        """Get webhook service status"""
        summary = self.config_service.get_config_summary()
        active_configs = self.config_service.get_active_configs()
        
        return {
            "enabled": summary["active_configurations"] > 0,
            "total_configurations": summary["total_configurations"],
            "active_configurations": summary["active_configurations"],
            "disabled_configurations": summary["disabled_configurations"],
            "last_updated": summary["last_updated"],
            "active_urls": [config.url for config in active_configs if config.url]
        }
    
    def is_configured(self) -> bool:
        """Check if any webhook is properly configured"""
        active_configs = self.config_service.get_active_configs()
        return any(config.enabled and config.url for config in active_configs)
