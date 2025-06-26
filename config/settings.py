# FilePath: config/settings.py

import os
from pathlib import Path
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Settings:
    """Global configuration settings for repo analyzer."""

    # File processing configuration
    CHUNK_LINES: int = 150
    FILES_PER_CHUNK: int = 8
    USE_ENTIRE_FILES: bool = True
    USE_SMART_COMPRESSION: bool = True
    MAX_FILE_SIZE: int = 15000
    MAX_INDENTATION_LEVEL: int = 3
    INDENTATION_SPACES: int = 4

    # LLM Configuration
    DEFAULT_LLM: str = "claude"
    DEFAULT_MODEL: str = "claude-3-5-sonnet-20241022"
    MAX_TOKENS: int = 8000
    TEMPERATURE: float = 0.1

    # API Configuration
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    ANTHROPIC_BASE_URL: str = "https://api.anthropic.com"

    # Output Configuration
    OUTPUT_DIR: str = "repo_analysis"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    SAVE_LOGS: bool = True

    # Git Configuration
    CLONE_TIMEOUT: int = 300  # 5 minutes
    GIT_COMMAND_TIMEOUT: int = 30

    # Processing Configuration
    PROCESSING_DELAY: float = 2.0
    MAX_CONCURRENT_REQUESTS: int = 3

    @classmethod
    def get_output_dir(cls, repo_name: str) -> Path:
        """Get output directory for a specific repository."""
        script_dir = Path(__file__).parent.parent
        return script_dir / cls.OUTPUT_DIR / repo_name

    @classmethod
    def update_from_dict(cls, config_dict: Dict[str, Any]) -> None:
        """Update settings from a dictionary."""
        for key, value in config_dict.items():
            if hasattr(cls, key.upper()):
                setattr(cls, key.upper(), value)

    @classmethod
    def to_dict(cls) -> Dict[str, Any]:
        """Convert settings to dictionary."""
        return {
            attr: getattr(cls, attr)
            for attr in dir(cls)
            if not attr.startswith("_") and not callable(getattr(cls, attr))
        }
