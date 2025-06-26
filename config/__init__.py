# FilePath: config/__init__.py

"""Configuration package for repo analyzer."""

from .settings import Settings
from .rate_limits import RateLimitManager, rate_limit_manager
from .languages import LanguageConfig

__all__ = ["Settings", "RateLimitManager", "rate_limit_manager", "LanguageConfig"]

# FilePath: src/repo_analyzer/__init__.py

"""Repository Analyzer - AI-powered codebase analysis tool."""

__version__ = "1.0.0"
__author__ = "Ankur"
__email__ = "ankur@signzy.com"
__description__ = (
    "AI-powered repository analysis tool with comprehensive tech stack analysis"
)

from .core.analyzer import RepositoryAnalyzer
from .llm.factory import LLMFactory

__all__ = ["RepositoryAnalyzer", "LLMFactory"]

# FilePath: src/repo_analyzer/core/__init__.py

"""Core analysis components."""

from .analyzer import RepositoryAnalyzer
from .git_handler import GitHandler
from .file_processor import FileProcessor
from .env_extractor import EnvExtractor

__all__ = ["RepositoryAnalyzer", "GitHandler", "FileProcessor", "EnvExtractor"]

# FilePath: src/repo_analyzer/llm/__init__.py

"""LLM provider abstractions."""

from .base import LLMProvider
from .claude import ClaudeProvider
from .factory import LLMFactory

__all__ = ["LLMProvider", "ClaudeProvider", "LLMFactory"]

# FilePath: src/repo_analyzer/utils/__init__.py

"""Utility modules."""

from .logging_utils import setup_logging, get_logger, ProgressLogger, AnalysisLogger
from .compression import SmartCompressor

__all__ = [
    "setup_logging",
    "get_logger",
    "ProgressLogger",
    "AnalysisLogger",
    "SmartCompressor",
]

# FilePath: src/repo_analyzer/output/__init__.py

"""Output generation and formatting."""

from .report_generator import ReportGenerator
from .formatters import MarkdownFormatter, JSONFormatter

__all__ = ["ReportGenerator", "MarkdownFormatter", "JSONFormatter"]

# FilePath: tests/__init__.py

"""Test package for repo analyzer."""
