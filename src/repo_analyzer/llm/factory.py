# FilePath: src/repo_analyzer/llm/factory.py

from typing import Optional, Dict, Type

from ..utils.logging_utils import get_logger
from .base import LLMProvider
from .claude import ClaudeProvider


class LLMFactory:
    """Factory for creating LLM provider instances."""

    _providers: Dict[str, Type[LLMProvider]] = {
        "claude": ClaudeProvider,
    }

    @classmethod
    def create_provider(
        cls, provider_name: str, model: Optional[str] = None, **kwargs
    ) -> LLMProvider:
        """
        Create an LLM provider instance.

        Args:
            provider_name: Name of the provider (e.g., "claude")
            model: Model name (optional, uses provider default if not specified)
            **kwargs: Additional configuration parameters

        Returns:
            Configured LLM provider instance

        Raises:
            ValueError: If provider is not supported
            RuntimeError: If provider initialization fails
        """
        logger = get_logger(__name__)

        provider_name = provider_name.lower()

        if provider_name not in cls._providers:
            available = ", ".join(cls._providers.keys())
            raise ValueError(
                f"Unsupported LLM provider: {provider_name}. "
                f"Available providers: {available}"
            )

        provider_class = cls._providers[provider_name]

        try:
            logger.info(f"Creating {provider_name} provider with model: {model}")
            provider = provider_class(model=model, **kwargs)

            # Validate configuration
            if not provider.validate_configuration():
                raise RuntimeError(
                    f"Invalid configuration for {provider_name} provider"
                )

            logger.info(f"Successfully created {provider_name} provider")
            return provider

        except Exception as e:
            logger.error(f"Failed to create {provider_name} provider: {str(e)}")
            raise RuntimeError(
                f"Failed to initialize {provider_name} provider: {str(e)}"
            )

    @classmethod
    def get_available_providers(cls) -> list:
        """Get list of available provider names."""
        return list(cls._providers.keys())

    @classmethod
    def register_provider(cls, name: str, provider_class: Type[LLMProvider]) -> None:
        """
        Register a new LLM provider.

        Args:
            name: Provider name
            provider_class: Provider class that inherits from LLMProvider
        """
        logger = get_logger(__name__)

        if not issubclass(provider_class, LLMProvider):
            raise ValueError("Provider class must inherit from LLMProvider")

        cls._providers[name.lower()] = provider_class
        logger.info(f"Registered new LLM provider: {name}")

    @classmethod
    def get_provider_info(cls, provider_name: str) -> Dict:
        """
        Get information about a specific provider.

        Args:
            provider_name: Name of the provider

        Returns:
            Dictionary containing provider information
        """
        provider_name = provider_name.lower()

        if provider_name not in cls._providers:
            raise ValueError(f"Unknown provider: {provider_name}")

        provider_class = cls._providers[provider_name]

        # Create a temporary instance to get info (without full initialization)
        try:
            # This is a bit of a hack - we should improve this
            if provider_name == "claude":
                return {
                    "name": provider_name,
                    "class": provider_class.__name__,
                    "supported_models": [
                        "claude-3-5-sonnet-20241022",
                        "claude-3-5-sonnet-20240620",
                        "claude-3-opus-20240229",
                        "claude-3-sonnet-20240229",
                        "claude-3-haiku-20240307",
                    ],
                    "default_model": "claude-3-5-sonnet-20241022",
                }
        except Exception:
            pass

        return {
            "name": provider_name,
            "class": provider_class.__name__,
            "supported_models": ["Unknown"],
            "default_model": "Unknown",
        }
