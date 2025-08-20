from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime

class WebhookConfig(BaseModel):
    """Dynamic webhook configuration model"""
    id: str = Field(..., description="Unique identifier for webhook config")
    name: str = Field(..., description="Webhook configuration name")
    url: str = Field(..., description="Webhook endpoint URL")
    enabled: bool = Field(True, description="Whether webhook is active")
    method: str = Field("POST", description="HTTP method (POST, PUT, etc.)")
    headers: Dict[str, str] = Field(default_factory=dict, description="Custom headers")
    timeout: int = Field(30, description="Request timeout in seconds")
    retry_attempts: int = Field(3, description="Number of retry attempts")
    retry_delay: int = Field(1, description="Delay between retries in seconds")
    payload_template: Dict[str, Any] = Field(default_factory=dict, description="Custom payload template")
    filters: Dict[str, Any] = Field(default_factory=dict, description="Filtering conditions")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")

class WebhookConfigCreate(BaseModel):
    """Model for creating new webhook configuration"""
    name: str = Field(..., description="Webhook configuration name")
    url: str = Field(..., description="Webhook endpoint URL")
    enabled: bool = Field(True, description="Whether webhook is active")
    method: str = Field("POST", description="HTTP method")
    headers: Dict[str, str] = Field(default_factory=dict, description="Custom headers")
    timeout: int = Field(30, description="Request timeout in seconds")
    retry_attempts: int = Field(3, description="Number of retry attempts")
    retry_delay: int = Field(1, description="Delay between retries in seconds")
    payload_template: Dict[str, Any] = Field(default_factory=dict, description="Custom payload template")
    filters: Dict[str, Any] = Field(default_factory=dict, description="Filtering conditions")

class WebhookConfigUpdate(BaseModel):
    """Model for updating webhook configuration"""
    name: Optional[str] = Field(None, description="Webhook configuration name")
    url: Optional[str] = Field(None, description="Webhook endpoint URL")
    enabled: Optional[bool] = Field(None, description="Whether webhook is active")
    method: Optional[str] = Field(None, description="HTTP method")
    headers: Optional[Dict[str, str]] = Field(None, description="Custom headers")
    timeout: Optional[int] = Field(None, description="Request timeout in seconds")
    retry_attempts: Optional[int] = Field(None, description="Number of retry attempts")
    retry_delay: Optional[int] = Field(None, description="Delay between retries in seconds")
    payload_template: Optional[Dict[str, Any]] = Field(None, description="Custom payload template")
    filters: Optional[Dict[str, Any]] = Field(None, description="Filtering conditions")

class WebhookResponse(BaseModel):
    """Response model for webhook operations"""
    success: bool = Field(..., description="Operation success status")
    message: str = Field(..., description="Response message")
    data: Optional[Dict[str, Any]] = Field(None, description="Response data")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")
