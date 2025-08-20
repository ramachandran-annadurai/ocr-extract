import os
from typing import List, Dict, Any

class Settings:
    """Application configuration settings"""
    
    def __init__(self):
        # Service Configuration
        self.APP_NAME = os.getenv("APP_NAME", "PaddleOCR Microservice")
        self.APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
        self.APP_DESCRIPTION = os.getenv("APP_DESCRIPTION", "A microservice for text recognition using PaddleOCR")
        
        # Server Configuration
        self.HOST = os.getenv("HOST", "0.0.0.0")
        self.PORT = int(os.getenv("PORT", "8000"))
        self.DEBUG = os.getenv("DEBUG", "false").lower() == "true"
        
        # PaddleOCR Configuration
        self.PADDLE_OCR_LANG = os.getenv("PADDLE_OCR_LANG", "en")
        self.PADDLE_OCR_USE_ANGLE_CLS = os.getenv("PADDLE_OCR_USE_ANGLE_CLS", "true").lower() == "true"
        self.PADDLE_OCR_SHOW_LOG = os.getenv("PADDLE_OCR_SHOW_LOG", "false").lower() == "true"
        
        # CORS Configuration
        cors_origins = os.getenv("CORS_ORIGINS", "*")
        self.CORS_ORIGINS = [cors_origins] if cors_origins != "*" else ["*"]
        self.CORS_ALLOW_CREDENTIALS = os.getenv("CORS_ALLOW_CREDENTIALS", "true").lower() == "true"
        cors_methods = os.getenv("CORS_ALLOW_METHODS", "*")
        self.CORS_ALLOW_METHODS = [cors_methods] if cors_methods != "*" else ["*"]
        cors_headers = os.getenv("CORS_ALLOW_HEADERS", "*")
        self.CORS_ALLOW_HEADERS = [cors_headers] if cors_headers != "*" else ["*"]
        
        # Logging Configuration
        self.LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
        self.LOG_FORMAT = os.getenv("LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        
        # Health Check Configuration
        self.HEALTH_CHECK_ENABLED = os.getenv("HEALTH_CHECK_ENABLED", "true").lower() == "true"
        
        # File Upload Configuration
        self.MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", str(10 * 1024 * 1024)))  # 10MB
        allowed_types = os.getenv("ALLOWED_IMAGE_TYPES", "image/jpeg,image/png,image/gif,image/bmp,image/tiff")
        self.ALLOWED_IMAGE_TYPES = [t.strip() for t in allowed_types.split(",")]
        
        # Webhook Configuration
        self.WEBHOOK_ENABLED = os.getenv("WEBHOOK_ENABLED", "true").lower() == "true"
        
        # Default webhook settings (these can be overridden via API)
        self.DEFAULT_WEBHOOK_URL = os.getenv("DEFAULT_WEBHOOK_URL", "")
        self.DEFAULT_WEBHOOK_METHOD = os.getenv("DEFAULT_WEBHOOK_METHOD", "POST")
        self.DEFAULT_WEBHOOK_TIMEOUT = int(os.getenv("DEFAULT_WEBHOOK_TIMEOUT", "30"))
        self.DEFAULT_WEBHOOK_RETRY_ATTEMPTS = int(os.getenv("DEFAULT_WEBHOOK_RETRY_ATTEMPTS", "3"))
        self.DEFAULT_WEBHOOK_RETRY_DELAY = int(os.getenv("DEFAULT_WEBHOOK_RETRY_DELAY", "1"))
        
        # Default webhook headers (JSON format)
        self.DEFAULT_WEBHOOK_HEADERS = os.getenv("DEFAULT_WEBHOOK_HEADERS", '{"Content-Type": "application/json"}')
        
        # Default webhook payload template (JSON format, leave empty for default)
        self.DEFAULT_WEBHOOK_PAYLOAD_TEMPLATE = os.getenv("DEFAULT_WEBHOOK_PAYLOAD_TEMPLATE", "")
        
        # Webhook configuration file path (relative to application root)
        self.WEBHOOK_CONFIG_FILE = os.getenv("WEBHOOK_CONFIG_FILE", "webhook_configs.json")
        
        # Webhook security settings
        self.WEBHOOK_MAX_CONFIGS = int(os.getenv("WEBHOOK_MAX_CONFIGS", "100"))
        self.WEBHOOK_ALLOW_EXTERNAL_URLS = os.getenv("WEBHOOK_ALLOW_EXTERNAL_URLS", "true").lower() == "true"
        self.WEBHOOK_REQUIRE_AUTHENTICATION = os.getenv("WEBHOOK_REQUIRE_AUTHENTICATION", "false").lower() == "true"
        
        # Legacy webhook settings (for backward compatibility)
        self.N8N_WEBHOOK_URL = os.getenv("N8N_WEBHOOK_URL", "")
        self.WEBHOOK_TIMEOUT = int(os.getenv("WEBHOOK_TIMEOUT", "30"))
        self.WEBHOOK_RETRY_ATTEMPTS = int(os.getenv("WEBHOOK_RETRY_ATTEMPTS", "3"))

# Global settings instance
settings = Settings()
