"""
OpenRouter models configuration for RA.Aid.

This module defines free and cost-effective models available on OpenRouter
that are suitable for coding tasks.
"""

# Free models available on OpenRouter
FREE_MODELS = [
    {
        "id": "meta-llama/llama-3-8b-instruct:free",
        "name": "Llama 3 8B Instruct (Free)",
        "description": "Meta's 8B instruct-tuned model optimized for high performance at a small size.",
        "context_length": 8192,
        "supports_temperature": True,
        "default_temperature": 0.7,
        "is_free": True,
        "category": "coding"
    },
    {
        "id": "mistralai/mistral-7b-instruct-v0.2:free",
        "name": "Mistral 7B Instruct (Free)",
        "description": "Mistral's 7B parameter instruction-tuned model with strong performance for its size.",
        "context_length": 8192,
        "supports_temperature": True,
        "default_temperature": 0.7,
        "is_free": True,
        "category": "coding"
    },
    {
        "id": "google/gemma-7b-it:free",
        "name": "Gemma 7B Instruct (Free)",
        "description": "Google's lightweight 7B parameter instruction-tuned model.",
        "context_length": 8192,
        "supports_temperature": True,
        "default_temperature": 0.7,
        "is_free": True,
        "category": "general"
    }
]

# Cost-effective models available on OpenRouter
COST_EFFECTIVE_MODELS = [
    {
        "id": "meta-llama/llama-3-70b-instruct",
        "name": "Llama 3 70B Instruct",
        "description": "Meta's 70B parameter instruction-tuned model with excellent performance for coding tasks.",
        "context_length": 8192,
        "supports_temperature": True,
        "default_temperature": 0.7,
        "is_free": False,
        "category": "coding"
    },
    {
        "id": "mistralai/mistral-large-2411",
        "name": "Mistral Large 2411",
        "description": "Mistral's large model with strong performance for coding and reasoning tasks.",
        "context_length": 32768,
        "supports_temperature": True,
        "default_temperature": 0.7,
        "is_free": False,
        "category": "coding"
    },
    {
        "id": "qwen/qwen-2.5-coder-32b-instruct",
        "name": "Qwen 2.5 Coder 32B",
        "description": "Qwen's specialized coding model with excellent performance for programming tasks.",
        "context_length": 131072,
        "supports_temperature": True,
        "default_temperature": 0.4,
        "is_free": False,
        "category": "coding"
    },
    {
        "id": "deepseek/deepseek-r1",
        "name": "DeepSeek R1",
        "description": "DeepSeek's reasoning-focused model with strong performance for complex coding tasks.",
        "context_length": 163840,
        "supports_temperature": True,
        "default_temperature": 0.7,
        "is_free": False,
        "category": "coding"
    }
]

# All models combined
ALL_MODELS = FREE_MODELS + COST_EFFECTIVE_MODELS

def get_model_by_id(model_id):
    """Get model information by ID."""
    for model in ALL_MODELS:
        if model["id"] == model_id:
            return model
    return None

def get_free_models():
    """Get all free models."""
    return FREE_MODELS

def get_cost_effective_models():
    """Get all cost-effective models."""
    return COST_EFFECTIVE_MODELS

def get_coding_models():
    """Get all models suitable for coding tasks."""
    return [model for model in ALL_MODELS if model["category"] == "coding"]
