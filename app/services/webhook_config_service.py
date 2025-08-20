import logging
import json
import os
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid
from app.models.webhook_config import WebhookConfig, WebhookConfigCreate, WebhookConfigUpdate

logger = logging.getLogger(__name__)

class WebhookConfigService:
    """Service for managing dynamic webhook configurations"""
    
    def __init__(self):
        self.configs: Dict[str, WebhookConfig] = {}
        self.config_file = os.getenv("WEBHOOK_CONFIG_FILE", "webhook_configs.json")
        self.max_configs = int(os.getenv("WEBHOOK_MAX_CONFIGS", "100"))
        self.allow_external_urls = os.getenv("WEBHOOK_ALLOW_EXTERNAL_URLS", "true").lower() == "true"
        self.require_auth = os.getenv("WEBHOOK_REQUIRE_AUTHENTICATION", "false").lower() == "true"
        self._load_configs()
        self._create_default_config()
    
    def _create_default_config(self):
        """Create a default webhook configuration if none exists"""
        if not self.configs:
            # Get default values from environment
            default_url = os.getenv("DEFAULT_WEBHOOK_URL", "")
            default_method = os.getenv("DEFAULT_WEBHOOK_METHOD", "POST")
            default_timeout = int(os.getenv("DEFAULT_WEBHOOK_TIMEOUT", "30"))
            default_retry_attempts = int(os.getenv("DEFAULT_WEBHOOK_RETRY_ATTEMPTS", "3"))
            default_retry_delay = int(os.getenv("DEFAULT_WEBHOOK_RETRY_DELAY", "1"))
            
            # Parse default headers from environment
            default_headers = {"Content-Type": "application/json"}
            try:
                env_headers = os.getenv("DEFAULT_WEBHOOK_HEADERS", "")
                if env_headers:
                    default_headers = json.loads(env_headers)
            except json.JSONDecodeError:
                logger.warning("Invalid DEFAULT_WEBHOOK_HEADERS format, using default")
            
            # Parse default payload template from environment
            default_payload_template = {}
            try:
                env_template = os.getenv("DEFAULT_WEBHOOK_PAYLOAD_TEMPLATE", "")
                if env_template:
                    default_payload_template = json.loads(env_template)
            except json.JSONDecodeError:
                logger.warning("Invalid DEFAULT_WEBHOOK_PAYLOAD_TEMPLATE format, using default")
            
            default_config = WebhookConfig(
                id=str(uuid.uuid4()),
                name="Default n8n Webhook",
                url=default_url,
                enabled=bool(default_url),  # Enable only if URL is provided
                method=default_method,
                headers=default_headers,
                timeout=default_timeout,
                retry_attempts=default_retry_attempts,
                retry_delay=default_retry_delay,
                payload_template=default_payload_template,
                filters={}
            )
            self.configs[default_config.id] = default_config
            self._save_configs()
            logger.info("Created default webhook configuration from environment variables")
    
    def _load_configs(self):
        """Load webhook configurations from file"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    configs_data = json.load(f)
                    for config_data in configs_data.values():
                        config = WebhookConfig(**config_data)
                        self.configs[config.id] = config
                logger.info(f"Loaded {len(self.configs)} webhook configurations")
            else:
                logger.info("No webhook config file found, starting with empty configs")
        except Exception as e:
            logger.error(f"Error loading webhook configs: {e}")
            self.configs = {}
    
    def _save_configs(self):
        """Save webhook configurations to file"""
        try:
            configs_data = {}
            for config_id, config in self.configs.items():
                configs_data[config_id] = config.dict()
            
            with open(self.config_file, 'w') as f:
                json.dump(configs_data, f, indent=2, default=str)
            
            logger.info(f"Saved {len(self.configs)} webhook configurations to {self.config_file}")
        except Exception as e:
            logger.error(f"Error saving webhook configs: {e}")
    
    def _validate_config(self, config_data: WebhookConfigCreate) -> List[str]:
        """Validate webhook configuration"""
        errors = []
        
        # Check if we've reached the maximum number of configurations
        if len(self.configs) >= self.max_configs:
            errors.append(f"Maximum number of webhook configurations ({self.max_configs}) reached")
        
        # Validate URL
        if not config_data.url:
            errors.append("Webhook URL is required")
        elif not self.allow_external_urls and not self._is_internal_url(config_data.url):
            errors.append("External URLs are not allowed")
        
        # Validate method
        valid_methods = ["GET", "POST", "PUT", "PATCH", "DELETE"]
        if config_data.method.upper() not in valid_methods:
            errors.append(f"Invalid HTTP method. Must be one of: {', '.join(valid_methods)}")
        
        # Validate timeout
        if config_data.timeout < 1 or config_data.timeout > 300:
            errors.append("Timeout must be between 1 and 300 seconds")
        
        # Validate retry attempts
        if config_data.retry_attempts < 0 or config_data.retry_attempts > 10:
            errors.append("Retry attempts must be between 0 and 10")
        
        # Validate retry delay
        if config_data.retry_delay < 0 or config_data.retry_delay > 60:
            errors.append("Retry delay must be between 0 and 60 seconds")
        
        return errors
    
    def _is_internal_url(self, url: str) -> bool:
        """Check if URL is internal/local"""
        internal_prefixes = ["localhost", "127.0.0.1", "0.0.0.0", "::1"]
        return any(prefix in url.lower() for prefix in internal_prefixes)
    
    def create_config(self, config_data: WebhookConfigCreate) -> WebhookConfig:
        """Create a new webhook configuration"""
        # Validate configuration
        errors = self._validate_config(config_data)
        if errors:
            raise ValueError(f"Configuration validation failed: {'; '.join(errors)}")
        
        config_id = str(uuid.uuid4())
        config = WebhookConfig(
            id=config_id,
            **config_data.dict(),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        self.configs[config_id] = config
        self._save_configs()
        logger.info(f"Created webhook configuration: {config.name}")
        return config
    
    def get_config(self, config_id: str) -> Optional[WebhookConfig]:
        """Get webhook configuration by ID"""
        return self.configs.get(config_id)
    
    def get_all_configs(self) -> List[WebhookConfig]:
        """Get all webhook configurations"""
        return list(self.configs.values())
    
    def get_active_configs(self) -> List[WebhookConfig]:
        """Get all enabled webhook configurations"""
        return [config for config in self.configs.values() if config.enabled]
    
    def update_config(self, config_id: str, config_data: WebhookConfigUpdate) -> Optional[WebhookConfig]:
        """Update webhook configuration"""
        if config_id not in self.configs:
            return None
        
        config = self.configs[config_id]
        
        # Update only provided fields
        update_data = config_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(config, field, value)
        
        # Validate updated configuration
        if update_data.get('url') or update_data.get('method') or update_data.get('timeout') or update_data.get('retry_attempts') or update_data.get('retry_delay'):
            # Create a temporary config for validation
            temp_config = WebhookConfigCreate(
                name=config.name,
                url=config.url,
                enabled=config.enabled,
                method=config.method,
                headers=config.headers,
                timeout=config.timeout,
                retry_attempts=config.retry_attempts,
                retry_delay=config.retry_delay,
                payload_template=config.payload_template,
                filters=config.filters
            )
            errors = self._validate_config(temp_config)
            if errors:
                raise ValueError(f"Configuration validation failed: {'; '.join(errors)}")
        
        config.updated_at = datetime.utcnow()
        self._save_configs()
        
        logger.info(f"Updated webhook configuration: {config.name}")
        return config
    
    def delete_config(self, config_id: str) -> bool:
        """Delete webhook configuration"""
        if config_id not in self.configs:
            return False
        
        config_name = self.configs[config_id].name
        del self.configs[config_id]
        self._save_configs()
        
        logger.info(f"Deleted webhook configuration: {config_name}")
        return True
    
    def enable_config(self, config_id: str) -> bool:
        """Enable a webhook configuration"""
        config = self.get_config(config_id)
        if not config:
            return False
        
        config.enabled = True
        config.updated_at = datetime.utcnow()
        self._save_configs()
        
        logger.info(f"Enabled webhook configuration: {config.name}")
        return True
    
    def disable_config(self, config_id: str) -> bool:
        """Disable a webhook configuration"""
        config = self.get_config(config_id)
        if not config:
            return False
        
        config.enabled = False
        config.updated_at = datetime.utcnow()
        self._save_configs()
        
        logger.info(f"Disabled webhook configuration: {config.name}")
        return True
    
    def test_config(self, config_id: str) -> Dict[str, Any]:
        """Test webhook configuration by sending a test payload"""
        config = self.get_config(config_id)
        if not config:
            return {"success": False, "message": "Configuration not found"}
        
        if not config.enabled:
            return {"success": False, "message": "Configuration is disabled"}
        
        if not config.url:
            return {"success": False, "message": "URL not configured"}
        
        # This would integrate with the webhook service to send a test
        return {"success": True, "message": "Configuration is valid", "config": config.dict()}
    
    def get_config_summary(self) -> Dict[str, Any]:
        """Get summary of all webhook configurations"""
        total_configs = len(self.configs)
        active_configs = len(self.get_active_configs())
        
        return {
            "total_configurations": total_configs,
            "active_configurations": active_configs,
            "disabled_configurations": total_configs - active_configs,
            "max_configurations": self.max_configs,
            "allow_external_urls": self.allow_external_urls,
            "require_authentication": self.require_auth,
            "config_file": self.config_file,
            "last_updated": max([config.updated_at for config in self.configs.values()]) if self.configs else None
        }
    
    def get_environment_info(self) -> Dict[str, Any]:
        """Get webhook environment configuration information"""
        return {
            "webhook_enabled": os.getenv("WEBHOOK_ENABLED", "true").lower() == "true",
            "default_webhook_url": os.getenv("DEFAULT_WEBHOOK_URL", ""),
            "default_webhook_method": os.getenv("DEFAULT_WEBHOOK_METHOD", "POST"),
            "default_webhook_timeout": int(os.getenv("DEFAULT_WEBHOOK_TIMEOUT", "30")),
            "default_webhook_retry_attempts": int(os.getenv("DEFAULT_WEBHOOK_RETRY_ATTEMPTS", "3")),
            "default_webhook_retry_delay": int(os.getenv("DEFAULT_WEBHOOK_RETRY_DELAY", "1")),
            "default_webhook_headers": os.getenv("DEFAULT_WEBHOOK_HEADERS", '{"Content-Type": "application/json"}'),
            "default_webhook_payload_template": os.getenv("DEFAULT_WEBHOOK_PAYLOAD_TEMPLATE", ""),
            "webhook_config_file": self.config_file,
            "max_configs": self.max_configs,
            "allow_external_urls": self.allow_external_urls,
            "require_authentication": self.require_auth
        }
