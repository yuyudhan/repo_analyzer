# FilePath: src/repo_analyzer/utils/compression.py

from pathlib import Path
from typing import List

from config.settings import Settings
from .logging_utils import get_logger


class SmartCompressor:
    """Intelligently compress code while preserving structure and context."""

    def __init__(self):
        self.logger = get_logger(__name__)

    def smart_compress_code(self, content: str, file_path: Path) -> str:
        """
        Intelligently compress code while preserving structure and context.

        Args:
            content: Original file content
            file_path: Path to the file being compressed

        Returns:
            Compressed content
        """
        if not Settings.USE_SMART_COMPRESSION:
            return content

        lines = content.split("\n")
        compressed_lines = []

        # Detect indentation style
        indentation_char, indent_size = self._detect_indentation(lines)

        consecutive_blank_lines = 0
        in_string_block = False
        string_delimiters = ['"""', "'''"]

        for i, line in enumerate(lines):
            stripped_line = line.strip()

            # Track multiline strings to preserve them
            for delimiter in string_delimiters:
                if delimiter in line:
                    in_string_block = not in_string_block

            # Skip completely empty lines (but allow one consecutive blank line)
            if not stripped_line:
                consecutive_blank_lines += 1
                if consecutive_blank_lines <= 1:
                    compressed_lines.append("")
                continue
            else:
                consecutive_blank_lines = 0

            # Calculate indentation level
            indent_level = self._calculate_indent_level(
                line, indentation_char, indent_size
            )

            # Always keep certain types of lines regardless of indentation
            is_important = self._is_important_line(line)

            # Keep line if it's important OR within acceptable indentation level
            if (
                is_important
                or indent_level <= Settings.MAX_INDENTATION_LEVEL
                or in_string_block
            ):
                compressed_lines.append(line)
            else:
                # For deeply nested code, add a comment indicating compression
                if i > 0 and not any(
                    "..." in prev_line for prev_line in compressed_lines[-3:]
                ):
                    base_indent = indentation_char * (
                        Settings.MAX_INDENTATION_LEVEL * indent_size
                    )
                    compressed_lines.append(
                        f"{base_indent}// ... [compressed: deeply nested code] ..."
                    )

        # Remove trailing empty lines
        while compressed_lines and not compressed_lines[-1].strip():
            compressed_lines.pop()

        compressed_content = "\n".join(compressed_lines)

        # Calculate and log compression ratio
        self._log_compression_stats(content, compressed_content, file_path)

        return compressed_content

    def _detect_indentation(self, lines: List[str]) -> tuple:
        """
        Detect indentation style from file content.

        Args:
            lines: List of lines from the file

        Returns:
            Tuple of (indentation_char, indent_size)
        """
        # Default values
        indentation_char = " "
        indent_size = Settings.INDENTATION_SPACES

        # Try to detect actual indentation from file
        for line in lines[:50]:  # Check first 50 lines
            if line.strip() and line.startswith((" ", "\t")):
                if line.startswith("\t"):
                    indentation_char = "\t"
                    indent_size = 1
                    break
                else:
                    # Count leading spaces
                    leading_spaces = len(line) - len(line.lstrip(" "))
                    if leading_spaces > 0:
                        # Common indentation sizes
                        for size in [2, 4, 8]:
                            if leading_spaces % size == 0:
                                indent_size = size
                                break
                        break

        return indentation_char, indent_size

    def _calculate_indent_level(
        self, line: str, indentation_char: str, indent_size: int
    ) -> int:
        """
        Calculate the indentation level of a line.

        Args:
            line: Line to analyze
            indentation_char: Character used for indentation
            indent_size: Size of one indentation level

        Returns:
            Indentation level
        """
        if indentation_char == "\t":
            return len(line) - len(line.lstrip("\t"))
        else:
            return (len(line) - len(line.lstrip(" "))) // indent_size

    def _is_important_line(self, line: str) -> bool:
        """
        Check if a line should be preserved regardless of indentation.

        Args:
            line: Line to check

        Returns:
            True if the line is important
        """
        important_patterns = [
            # Imports and exports
            "import ",
            "from ",
            "export ",
            "require(",
            "include ",
            # Function/class definitions
            "def ",
            "class ",
            "function ",
            "async def",
            "fn ",
            "pub fn",
            "interface ",
            "trait ",
            "impl ",
            "struct ",
            "enum ",
            # Type definitions
            "type ",
            "typedef ",
            "using ",
            "@interface",
            "protocol ",
            # Decorators and annotations
            "@",
            "#[",
            "/*",
            "//",
            "#",
            # Important keywords
            "return ",
            "yield ",
            "throw ",
            "raise ",
            "panic!",
            # Route definitions and endpoints
            "app.",
            "router.",
            "@app.route",
            "@router.",
            "app.use",
            # Database and model definitions
            "CREATE TABLE",
            "ALTER TABLE",
            "SELECT ",
            "INSERT ",
            "UPDATE ",
            # Configuration and constants
            "const ",
            "let ",
            "var ",
            "final ",
            "static ",
            # Package and module info
            "package ",
            "module ",
            "namespace ",
            # Error handling
            "try ",
            "catch ",
            "except ",
            "finally ",
            "rescue ",
            # Control flow
            "if ",
            "else ",
            "elif ",
            "while ",
            "for ",
            "switch ",
            "case ",
            # Async/await patterns
            "async ",
            "await ",
            "Promise",
            "Future",
        ]

        return any(pattern in line for pattern in important_patterns)

    def _log_compression_stats(
        self, original: str, compressed: str, file_path: Path
    ) -> None:
        """
        Log compression statistics.

        Args:
            original: Original content
            compressed: Compressed content
            file_path: Path to the file
        """
        original_size = len(original)
        compressed_size = len(compressed)

        if original_size > 0:
            compression_ratio = (1 - compressed_size / original_size) * 100

            if compression_ratio > 5:  # Only log if significant compression
                self.logger.debug(
                    f"Compressed {file_path.name}: {compression_ratio:.1f}% reduction "
                    f"({original_size} → {compressed_size} chars)"
                )
