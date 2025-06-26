# FilePath: src/repo_analyzer/llm/claude.py

from typing import Dict, Any, Optional
import anthropic

from config.settings import Settings
from ..utils.logging_utils import get_logger
from .base import LLMProvider


class ClaudeProvider(LLMProvider):
    """Claude LLM provider implementation."""

    def __init__(self, model: Optional[str] = None, **kwargs):
        model = model or Settings.DEFAULT_MODEL
        super().__init__(model, **kwargs)

        self.logger = get_logger(__name__)
        self.client = None
        self._initialize_client()

    def _initialize_client(self):
        """Initialize the Anthropic client."""
        try:
            self.client = anthropic.Anthropic(
                api_key=Settings.ANTHROPIC_API_KEY, base_url=Settings.ANTHROPIC_BASE_URL
            )
            self.logger.info(f"Initialized Claude client with model: {self.model}")
        except Exception as e:
            self.logger.error(f"Failed to initialize Claude client: {str(e)}")
            raise

    def generate_response(self, prompt: str, **kwargs) -> str:
        """
        Generate a response using Claude.

        Args:
            prompt: The input prompt
            **kwargs: Additional parameters (temperature, max_tokens, etc.)

        Returns:
            Generated response text
        """
        if not self.client:
            raise RuntimeError("Claude client not initialized")

        # Merge default parameters with provided kwargs
        params = self.get_default_parameters()
        params.update(kwargs)

        try:
            self.logger.debug(f"Generating response with model: {self.model}")

            response_text = ""
            with self.client.messages.stream(
                model=self.model,
                max_tokens=params.get("max_tokens", Settings.MAX_TOKENS),
                temperature=params.get("temperature", Settings.TEMPERATURE),
                messages=[{"role": "user", "content": prompt}],
            ) as stream:
                for text in stream.text_stream:
                    response_text += text

            self.logger.debug(
                f"Generated response length: {len(response_text)} characters"
            )
            return response_text

        except Exception as e:
            self.logger.error(f"Error generating response: {str(e)}")
            raise

    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current Claude model."""
        return {
            "provider": "claude",
            "model": self.model,
            "base_url": Settings.ANTHROPIC_BASE_URL,
            "max_tokens": Settings.MAX_TOKENS,
            "temperature": Settings.TEMPERATURE,
        }

    def validate_configuration(self) -> bool:
        """Validate Claude configuration."""
        if not Settings.ANTHROPIC_API_KEY:
            self.logger.error("ANTHROPIC_API_KEY not configured")
            return False

        try:
            # Test the client initialization
            if not self.client:
                self._initialize_client()

            # Simple test to validate API key and connectivity
            # Note: In a real implementation, you might want to make a minimal API call
            self.logger.info("Claude configuration validated successfully")
            return True

        except Exception as e:
            self.logger.error(f"Claude configuration validation failed: {str(e)}")
            return False

    def get_default_parameters(self) -> Dict[str, Any]:
        """Get default parameters for Claude."""
        return {
            "temperature": Settings.TEMPERATURE,
            "max_tokens": Settings.MAX_TOKENS,
        }

    def get_available_models(self) -> list:
        """Get list of available Claude models."""
        return [
            "claude-3-5-sonnet-20241022",
            "claude-3-5-sonnet-20240620",
            "claude-3-opus-20240229",
            "claude-3-sonnet-20240229",
            "claude-3-haiku-20240307",
        ]

    def estimate_tokens(self, text: str) -> int:
        """
        Estimate the number of tokens in the given text.
        This is a rough estimation for Claude models.

        Args:
            text: Input text

        Returns:
            Estimated token count
        """
        # Rough estimation: ~4 characters per token for Claude
        return len(text) // 4

    def check_token_limit(self, prompt: str) -> bool:
        """
        Check if the prompt exceeds token limits.

        Args:
            prompt: Input prompt

        Returns:
            True if within limits, False otherwise
        """
        estimated_tokens = self.estimate_tokens(prompt)

        # Leave some buffer for response tokens
        max_input_tokens = (
            Settings.MAX_TOKENS * 0.7
        )  # Use 70% for input, 30% for output

        if estimated_tokens > max_input_tokens:
            self.logger.warning(
                f"Prompt may exceed token limits: {estimated_tokens} tokens "
                f"(limit: {max_input_tokens})"
            )
            return False

        return True
