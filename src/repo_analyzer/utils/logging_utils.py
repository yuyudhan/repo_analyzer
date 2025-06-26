# FilePath: src/repo_analyzer/utils/logging_utils.py

import logging
import sys
from pathlib import Path
from typing import Optional

from config.settings import Settings


def setup_logging(log_level: str = "INFO", log_file: Optional[Path] = None) -> None:
    """
    Setup logging configuration for the application.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        log_file: Optional file path for logging output
    """
    # Convert string level to logging constant
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)

    # Create formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Setup console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(numeric_level)
    console_handler.setFormatter(formatter)

    # Setup root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    root_logger.handlers.clear()  # Clear any existing handlers
    root_logger.addHandler(console_handler)

    # Setup file handler if specified
    if log_file:
        try:
            log_file.parent.mkdir(parents=True, exist_ok=True)
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(numeric_level)
            file_handler.setFormatter(formatter)
            root_logger.addHandler(file_handler)
        except Exception as e:
            root_logger.warning(f"Failed to setup file logging: {e}")

    # Reduce noise from external libraries
    logging.getLogger("anthropic").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger with the specified name.

    Args:
        name: Logger name (typically __name__)

    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)


class ProgressLogger:
    """Logger for tracking analysis progress."""

    def __init__(self, total_steps: int, description: str = "Processing"):
        self.total_steps = total_steps
        self.current_step = 0
        self.description = description
        self.logger = get_logger(__name__)

    def step(self, message: str = "") -> None:
        """Advance progress by one step."""
        self.current_step += 1
        progress = (self.current_step / self.total_steps) * 100

        log_message = f"{self.description}: {self.current_step}/{self.total_steps} ({progress:.1f}%)"
        if message:
            log_message += f" - {message}"

        self.logger.info(log_message)

    def finish(self, message: str = "Complete") -> None:
        """Mark progress as finished."""
        self.logger.info(f"{self.description}: {message}")


class AnalysisLogger:
    """Specialized logger for analysis operations."""

    def __init__(self, repo_name: str):
        self.repo_name = repo_name
        self.logger = get_logger(f"analyzer.{repo_name}")
        self.start_time = None

    def start_analysis(self, total_files: int) -> None:
        """Log the start of analysis."""
        import time

        self.start_time = time.time()
        self.logger.info(f"Starting analysis of {self.repo_name} ({total_files} files)")

    def log_chunk_progress(
        self, chunk_num: int, total_chunks: int, files_in_chunk: int
    ) -> None:
        """Log progress for chunk processing."""
        progress = (chunk_num / total_chunks) * 100
        self.logger.info(
            f"Processing chunk {chunk_num}/{total_chunks} ({progress:.1f}%) - "
            f"{files_in_chunk} files"
        )

    def log_section_progress(self, section_num: int, section_name: str) -> None:
        """Log progress for section generation."""
        self.logger.info(f"Generating section {section_num}: {section_name}")

    def finish_analysis(self, output_file: Optional[str] = None) -> None:
        """Log the completion of analysis."""
        import time

        if self.start_time:
            duration = time.time() - self.start_time
            self.logger.info(
                f"Analysis of {self.repo_name} completed in {duration:.1f} seconds"
            )
        else:
            self.logger.info(f"Analysis of {self.repo_name} completed")

        if output_file:
            self.logger.info(f"Results saved to: {output_file}")

    def log_error(self, error: Exception, context: str = "") -> None:
        """Log an error with context."""
        error_msg = f"Error in {self.repo_name} analysis"
        if context:
            error_msg += f" ({context})"
        error_msg += f": {str(error)}"

        self.logger.error(error_msg, exc_info=True)
