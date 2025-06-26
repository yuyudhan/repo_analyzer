# FilePath: src/repo_analyzer/llm/base.py

from abc import ABC, abstractmethod
from typing import Dict, Any


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""

    def __init__(self, model: str, **kwargs):
        self.model = model
        self.config = kwargs

    @abstractmethod
    def generate_response(self, prompt: str, **kwargs) -> str:
        """
        Generate a response from the LLM.

        Args:
            prompt: The input prompt
            **kwargs: Additional parameters specific to the provider

        Returns:
            Generated response text
        """
        pass

    @abstractmethod
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the current model.

        Returns:
            Dictionary containing model information
        """
        pass

    @abstractmethod
    def validate_configuration(self) -> bool:
        """
        Validate that the provider is properly configured.

        Returns:
            True if configuration is valid
        """
        pass

    def get_provider_name(self) -> str:
        """Get the name of this provider."""
        return self.__class__.__name__.replace("Provider", "").lower()

    def get_default_parameters(self) -> Dict[str, Any]:
        """Get default parameters for this provider."""
        return {
            "temperature": 0.1,
            "max_tokens": 8000,
        }
