"""
API endpoints for settings management.

This module provides API endpoints for managing settings, including model configuration.
"""

import logging
import os
from typing import Dict, List, Optional, Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from ra_aid.database.repositories.config_repository import ConfigRepository, get_config_repository
from ra_aid.config import VALID_PROVIDERS
from ra_aid.openrouter_models import get_free_models, get_cost_effective_models, get_model_by_id
from ra_aid.models_params import models_params

# Create logger
logger = logging.getLogger(__name__)

# Create API router
router = APIRouter(
    prefix="/v1/settings",
    tags=["settings"],
    responses={
        status.HTTP_422_UNPROCESSABLE_ENTITY: {"description": "Validation error"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Server error"},
    },
)

class ModelInfo(BaseModel):
    """Model information."""
    id: str = Field(description="Model ID")
    name: str = Field(description="Display name")
    description: str = Field(description="Model description")
    context_length: int = Field(description="Context length in tokens")
    supports_temperature: bool = Field(description="Whether the model supports temperature")
    default_temperature: float = Field(description="Default temperature value")
    is_free: bool = Field(description="Whether the model is free to use")
    category: str = Field(description="Model category (e.g., coding, general)")

class ModelSettings(BaseModel):
    """Model settings."""
    provider: str = Field(description="Provider name")
    model: str = Field(description="Model name")
    temperature: Optional[float] = Field(None, description="Temperature value")
    expert_enabled: bool = Field(True, description="Whether expert mode is enabled")
    web_research_enabled: bool = Field(False, description="Whether web research is enabled")

class ModelSettingsResponse(BaseModel):
    """Response model for model settings."""
    settings: ModelSettings = Field(description="Current model settings")
    available_providers: List[str] = Field(description="List of available providers")
    available_models: Dict[str, List[ModelInfo]] = Field(description="Available models by provider")

@router.get(
    "",
    response_model=ModelSettingsResponse,
    summary="Get model settings",
    description="Get current model settings and available options",
)
async def get_settings(
    config_repo: ConfigRepository = Depends(get_config_repository),
) -> ModelSettingsResponse:
    """
    Get current model settings and available options.

    Args:
        config_repo: Configuration repository

    Returns:
        ModelSettingsResponse: Current settings and available options
    """
    # Get current settings
    provider = config_repo.get("provider", "anthropic")
    model = config_repo.get("model", "claude-3-7-sonnet-20250219")
    temperature = config_repo.get("temperature")
    expert_enabled = config_repo.get("expert_enabled", True)
    web_research_enabled = config_repo.get("web_research_enabled", False)

    # Create settings object
    settings = ModelSettings(
        provider=provider,
        model=model,
        temperature=temperature,
        expert_enabled=expert_enabled,
        web_research_enabled=web_research_enabled,
    )

    # Get available providers
    available_providers = VALID_PROVIDERS

    # Get available models by provider
    available_models = {}

    # Add OpenRouter models
    openrouter_models = []

    # Add free models
    for model_data in get_free_models():
        openrouter_models.append(ModelInfo(**model_data))

    # Add cost-effective models
    for model_data in get_cost_effective_models():
        openrouter_models.append(ModelInfo(**model_data))

    available_models["openrouter"] = openrouter_models

    # Return response
    return ModelSettingsResponse(
        settings=settings,
        available_providers=available_providers,
        available_models=available_models,
    )

@router.post(
    "",
    response_model=ModelSettings,
    summary="Update model settings",
    description="Update model settings",
)
async def update_settings(
    settings: ModelSettings,
    config_repo: ConfigRepository = Depends(get_config_repository),
) -> ModelSettings:
    """
    Update model settings.

    Args:
        settings: New settings
        config_repo: Configuration repository

    Returns:
        ModelSettings: Updated settings

    Raises:
        HTTPException: If the provider or model is invalid
    """
    # Validate provider
    if settings.provider not in VALID_PROVIDERS:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid provider: {settings.provider}. Valid providers: {VALID_PROVIDERS}",
        )

    # Validate model if provider is OpenRouter
    if settings.provider == "openrouter":
        model_info = get_model_by_id(settings.model)
        if not model_info:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Invalid model: {settings.model} for provider: {settings.provider}",
            )

    # Update settings
    config_repo.set("provider", settings.provider)
    config_repo.set("model", settings.model)

    if settings.temperature is not None:
        config_repo.set("temperature", settings.temperature)

    # Handle expert mode
    config_repo.set("expert_enabled", settings.expert_enabled)

    # Log expert mode status
    if settings.expert_enabled:
        logger.info(f"Expert mode enabled for provider: {settings.provider}")
    else:
        logger.info(f"Expert mode disabled for provider: {settings.provider}")

    # Only enable web research if Tavily API key is available
    tavily_api_key = os.environ.get("TAVILY_API_KEY")
    if settings.web_research_enabled and not tavily_api_key:
        logger.warning("Web research enabled but TAVILY_API_KEY not found. Disabling web research.")
        config_repo.set("web_research_enabled", False)
    else:
        config_repo.set("web_research_enabled", settings.web_research_enabled)

    # Return updated settings
    return settings
