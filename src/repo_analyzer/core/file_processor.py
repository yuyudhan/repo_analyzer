# FilePath: src/repo_analyzer/core/file_processor.py

import os
from pathlib import Path
from typing import List, Set

from config.settings import Settings
from config.languages import LanguageConfig
from ..utils.logging_utils import get_logger
from ..utils.compression import SmartCompressor


class FileProcessor:
    """Handles file scanning, filtering, and content processing."""

    def __init__(self):
        self.logger = get_logger(__name__)
        self.compressor = SmartCompressor()

    def get_all_source_files(self, repo_path: Path) -> List[Path]:
        """
        Get all source files with comprehensive language support.

        Args:
            repo_path: Path to the repository

        Returns:
            List of relative paths to source files
        """
        repo_path = Path(repo_path)
        all_files = []

        self.logger.info(f"Scanning directory: {repo_path}")

        total_scanned = 0
        for root, dirs, files in os.walk(repo_path):
            # Filter out ignored directories
            dirs[:] = [d for d in dirs if not self._should_ignore_file(Path(root) / d)]

            for file in files:
                total_scanned += 1
                file_path = Path(root) / file

                if self._should_ignore_file(file_path):
                    continue

                if self._is_source_file(file_path):
                    relative_path = file_path.relative_to(repo_path)
                    all_files.append(relative_path)

        all_files.sort()
        self.logger.info(
            f"Found {len(all_files)} source files out of {total_scanned} total files"
        )
        return all_files

    def prioritize_files(self, all_files: List[Path]) -> List[Path]:
        """
        Prioritize files for analysis based on importance.

        Args:
            all_files: List of all source files

        Returns:
            List of prioritized files (priority files first)
        """
        priority_files = []
        regular_files = []

        for file_path in all_files:
            if LanguageConfig.is_priority_file(file_path):
                priority_files.append(file_path)
            else:
                regular_files.append(file_path)

        self.logger.info(
            f"Prioritized: {len(priority_files)} priority files, "
            f"{len(regular_files)} regular files"
        )
        return priority_files + regular_files

    def create_file_chunk_content(
        self, repo_path: Path, files_chunk: List[Path], chunk_num: int
    ) -> str:
        """
        Create content for a chunk of files with enhanced context.

        Args:
            repo_path: Path to the repository
            files_chunk: List of files in this chunk
            chunk_num: Chunk number

        Returns:
            Formatted content string for the chunk
        """
        files_content = (
            f"## Code Analysis Chunk {chunk_num} ({len(files_chunk)} files):\n"
            f"**Processing Mode**: {'Entire Files' if Settings.USE_ENTIRE_FILES else 'Chunked Files'}"
            f"{' with Smart Compression' if Settings.USE_SMART_COMPRESSION else ''}\n\n"
        )

        total_original_size = 0
        total_processed_size = 0

        for file_path in files_chunk:
            full_path = repo_path / file_path

            # Get original size for statistics
            try:
                original_size = full_path.stat().st_size
                total_original_size += original_size
            except:
                original_size = 0

            file_chunks = self._read_file_content_enhanced(full_path)

            # Add enhanced file context and metadata
            files_content += f"### File: {file_path}\n"
            files_content += (
                f"**Type**: {LanguageConfig.get_file_type_description(file_path)}\n"
            )
            files_content += f"**Size**: {original_size:,} bytes"

            if Settings.USE_SMART_COMPRESSION:
                processed_size = sum(len(chunk) for chunk in file_chunks)
                total_processed_size += processed_size
                if processed_size < original_size * 0.95:  # If compressed
                    compression = (
                        (1 - processed_size / original_size) * 100
                        if original_size > 0
                        else 0
                    )
                    files_content += (
                        f" → {processed_size:,} bytes (compressed {compression:.1f}%)"
                    )

            if len(file_chunks) > 1:
                files_content += f", **Chunks**: {len(file_chunks)}"

            files_content += "\n\n"

            for i, chunk_content in enumerate(file_chunks):
                if len(file_chunks) > 1:
                    files_content += f"#### Part {i + 1}/{len(file_chunks)}\n"

                # Enhanced syntax highlighting and context
                syntax = LanguageConfig.get_syntax_highlighting(file_path)
                files_content += f"```{syntax}\n{chunk_content}\n```\n\n"

        # Add processing summary
        if Settings.USE_SMART_COMPRESSION and total_original_size > 0:
            overall_compression = (1 - total_processed_size / total_original_size) * 100
            files_content += f"**Chunk Processing Summary**: {total_original_size:,} → {total_processed_size:,} chars"
            if overall_compression > 5:
                files_content += f" ({overall_compression:.1f}% compression)"
            files_content += "\n\n"

        return files_content

    def _should_ignore_file(self, file_path: Path) -> bool:
        """
        Check if a file or directory should be ignored.

        Args:
            file_path: Path to check

        Returns:
            True if the file should be ignored
        """
        name = file_path.name.lower()

        # Ignore patterns for directories and files
        ignore_patterns = {
            "dirs": {
                "node_modules",
                "__pycache__",
                ".git",
                "target",
                "dist",
                "build",
                "vendor",
                ".cargo",
                "bin",
                "obj",
                "out",
                "debug",
                "release",
                ".vscode",
                ".idea",
                ".vs",
                ".atom",
                ".sublime-text",
                ".eclipse",
                "temp",
                "tmp",
                ".tmp",
                "cache",
                ".cache",
                ".pytest_cache",
                "coverage",
                ".coverage",
                ".nyc_output",
                ".jest",
                ".next",
                ".nuxt",
                ".angular",
                ".svelte-kit",
                "platforms",
                "xcuserdata",
                "project.xcworkspace",
                "pods",
                "carthage",
                "derived_data",
                "build_products",
                "logs",
                "log",
                ".log",
                ".terraform",
                ".vagrant",
                ".docker",
                "k8s-temp",
                ".ds_store",
                "thumbs.db",
            },
            "extensions": {
                ".pyc",
                ".pyo",
                ".pyd",
                ".class",
                ".o",
                ".obj",
                ".so",
                ".dll",
                ".dylib",
                ".exe",
                ".bin",
                ".deb",
                ".rpm",
                ".msi",
                ".dmg",
                ".pkg",
                ".a",
                ".lib",
                ".exp",
                ".pdb",
                ".ilk",
                ".idb",
                ".zip",
                ".tar",
                ".gz",
                ".bz2",
                ".xz",
                ".rar",
                ".7z",
                ".war",
                ".ear",
                ".jar",
                ".png",
                ".jpg",
                ".jpeg",
                ".gif",
                ".bmp",
                ".svg",
                ".ico",
                ".webp",
                ".mp3",
                ".mp4",
                ".avi",
                ".mov",
                ".wav",
                ".flv",
                ".wmv",
                ".webm",
                ".tiff",
                ".eps",
                ".ai",
                ".sketch",
                ".pdf",
                ".doc",
                ".docx",
                ".xls",
                ".xlsx",
                ".ppt",
                ".pptx",
                ".log",
                ".tmp",
                ".temp",
                ".cache",
                ".swp",
                ".swo",
                ".bak",
                ".orig",
                ".rej",
                ".patch",
                ".lock",
                ".pid",
                ".seed",
                ".coverage",
                ".map",
            },
            "files": {
                "package-lock.json",
                "yarn.lock",
                "pnpm-lock.yaml",
                "cargo.lock",
                "composer.lock",
                "pipfile.lock",
                "poetry.lock",
                "gemfile.lock",
                "go.sum",
                "mix.lock",
                ".ds_store",
                "thumbs.db",
                "desktop.ini",
                ".project",
                ".classpath",
                ".settings",
                "webpack-stats.json",
                "bundle-stats.json",
                "stats.json",
            },
        }

        # Special handling for .env files
        if name.startswith(".env") and name != ".env.example":
            return True

        # Check directory patterns
        for part in file_path.parts:
            if part.lower() in ignore_patterns["dirs"]:
                return True

        # Check file extensions
        if file_path.suffix.lower() in ignore_patterns["extensions"]:
            return True

        # Check specific file names
        if name in ignore_patterns["files"]:
            return True

        # Important configuration files (don't ignore)
        important_configs = {
            ".env.example",
            ".env.sample",
            ".env.template",
            ".env.local.example",
            ".gitignore",
            ".gitattributes",
            ".dockerignore",
            ".editorconfig",
            ".eslintrc.js",
            ".eslintrc.json",
            ".eslintrc.yaml",
            ".eslintrc.yml",
            ".prettierrc",
            ".prettierrc.json",
            ".prettierrc.yaml",
            ".prettierrc.yml",
            ".babelrc",
            ".babelrc.json",
            ".swcrc",
            ".browserslistrc",
            ".nvmrc",
            ".ruby-version",
            ".python-version",
            ".node-version",
            ".golangci.yml",
            ".golangci.yaml",
            ".clang-format",
            ".clang-tidy",
        }

        # Don't ignore important dotfiles
        if name.startswith(".") and name not in important_configs:
            return True

        return False

    def _is_source_file(self, file_path: Path) -> bool:
        """
        Check if a file is a source file that should be analyzed.

        Args:
            file_path: Path to check

        Returns:
            True if the file is a source file
        """
        name = file_path.name.lower()
        suffix = file_path.suffix.lower()

        # Check if it's in our source extensions
        if suffix in LanguageConfig.SOURCE_EXTENSIONS:
            return True

        # Check if it's an important file without extension
        if name in LanguageConfig.IMPORTANT_NO_EXT:
            return True

        return False

    def _read_file_content_enhanced(self, file_path: Path) -> List[str]:
        """
        Read file content with enhanced processing options.

        Args:
            file_path: Path to the file

        Returns:
            List of content chunks
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Apply smart compression if enabled
            if Settings.USE_SMART_COMPRESSION:
                content = self.compressor.smart_compress_code(content, file_path)

            # Decide whether to use entire files or chunks
            if Settings.USE_ENTIRE_FILES and len(content) <= Settings.MAX_FILE_SIZE:
                # Return entire file as single chunk
                return [content]
            else:
                # Fall back to chunking for very large files
                lines = content.split("\n")

                if len(lines) <= Settings.CHUNK_LINES:
                    return [content]

                # Split into chunks with better context preservation
                chunks = []
                for i in range(0, len(lines), Settings.CHUNK_LINES):
                    chunk_lines = lines[i : i + Settings.CHUNK_LINES]
                    chunk_content = "\n".join(chunk_lines)

                    # Add chunk header with context info
                    chunk_num = (i // Settings.CHUNK_LINES) + 1
                    total_chunks = (
                        len(lines) + Settings.CHUNK_LINES - 1
                    ) // Settings.CHUNK_LINES

                    # Try to preserve context by including some overlap
                    context_info = ""
                    if i > 0:
                        # Look for imports/function definitions in previous chunks
                        prev_lines = lines[max(0, i - 10) : i]
                        imports = [
                            line
                            for line in prev_lines
                            if any(
                                pattern in line
                                for pattern in [
                                    "import ",
                                    "from ",
                                    "def ",
                                    "class ",
                                    "function ",
                                ]
                            )
                        ]
                        if imports:
                            context_info = (
                                f"\n// Context from previous sections:\n"
                                + "\n".join(
                                    f"// {line.strip()}" for line in imports[-3:]
                                )
                                + "\n"
                            )

                    header = f"[CHUNK {chunk_num}/{total_chunks} - Lines {i + 1}-{i + len(chunk_lines)}]{context_info}\n"
                    chunks.append(header + chunk_content)

                return chunks

        except UnicodeDecodeError:
            return ["[Binary file - content not readable]"]
        except Exception as e:
            self.logger.warning(f"Error reading file {file_path}: {str(e)}")
            return [f"[Error reading file: {e}]"]
