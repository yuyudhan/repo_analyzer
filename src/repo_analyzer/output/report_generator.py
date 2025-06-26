# FilePath: src/repo_analyzer/output/report_generator.py

import time
from pathlib import Path
from typing import Dict, Any, Optional

from config.settings import Settings
from ..utils.logging_utils import get_logger
from .formatters import MarkdownFormatter


class ReportGenerator:
    """Handles generation and saving of analysis reports."""

    def __init__(self):
        self.logger = get_logger(__name__)
        self.formatter = MarkdownFormatter()

    def save_analysis(
        self, results: Dict[str, Any], repo_path: str, timestamp: str
    ) -> Optional[str]:
        """
        Save comprehensive analysis to markdown file.

        Args:
            results: Analysis results dictionary
            repo_path: Path to the repository
            timestamp: Timestamp for the analysis

        Returns:
            Path to the saved file, or None if saving failed
        """
        try:
            repo_name = Path(repo_path).name

            # Create output directory
            output_dir = Settings.get_output_dir(repo_name)
            output_dir.mkdir(parents=True, exist_ok=True)

            # Generate file paths
            timestamped_file = output_dir / f"{timestamp}_{repo_name}_analysis.md"
            latest_file = output_dir / f"{repo_name}_latest.md"

            # Generate report content
            content = self._generate_report_content(results, repo_path, timestamp)

            # Save timestamped version
            with open(timestamped_file, "w", encoding="utf-8") as f:
                f.write(content)

            # Save latest version (without timestamp in filename)
            latest_content = self._generate_latest_content(content)
            with open(latest_file, "w", encoding="utf-8") as f:
                f.write(latest_content)

            self.logger.info(f"Analysis saved to: {timestamped_file}")
            self.logger.info(f"Latest version: {latest_file}")

            # Generate additional formats if requested
            self._save_additional_formats(results, output_dir, repo_name, timestamp)

            return str(timestamped_file)

        except Exception as e:
            self.logger.error(f"Failed to save analysis: {str(e)}", exc_info=True)
            return None

    def save_progress_log(
        self, content: str, repo_name: str, timestamp: str, log_type: str = "progress"
    ) -> None:
        """
        Save progress logs during analysis.

        Args:
            content: Log content
            repo_name: Repository name
            timestamp: Timestamp
            log_type: Type of log (progress, analysis, etc.)
        """
        try:
            output_dir = Settings.get_output_dir(repo_name)
            output_dir.mkdir(parents=True, exist_ok=True)

            log_file = output_dir / f"{timestamp}_{repo_name}_{log_type}.md"

            # Initialize log file if it doesn't exist
            if not log_file.exists():
                header = f"# FilePath: {timestamp}_{repo_name}_{log_type}.md\n\n"
                header += f"# {log_type.title()} Log: {repo_name}\n\n"
                with open(log_file, "w", encoding="utf-8") as f:
                    f.write(header)

            # Append log entry
            log_timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            log_entry = f"\n## {log_timestamp}\n\n{content}\n\n---\n\n"

            with open(log_file, "a", encoding="utf-8") as f:
                f.write(log_entry)

        except Exception as e:
            self.logger.warning(f"Failed to save progress log: {str(e)}")

    def _generate_report_content(
        self, results: Dict[str, Any], repo_path: str, timestamp: str
    ) -> str:
        """Generate the complete report content."""
        repo_name = Path(repo_path).name

        content = f"# FilePath: {timestamp}_{repo_name}_analysis.md\n\n"
        content += self.formatter.format_header(repo_name, results)

        # Add Git information if available
        if results.get("Git Information"):
            content += self.formatter.format_git_section(results["Git Information"])

        # Add environment configuration if available
        if results.get("Environment Configurations"):
            content += self.formatter.format_env_section(
                results["Environment Configurations"]
            )

        # Add main analysis
        content += results.get("Repository Analysis", "Analysis not available")

        # Add footer
        content += self.formatter.format_footer(results)

        return content

    def _generate_latest_content(self, content: str) -> str:
        """Generate content for the latest file (without timestamp in filepath)."""
        # Extract content after the filepath comment
        lines = content.split("\n")
        start_index = 0

        for i, line in enumerate(lines):
            if line.startswith("# Technical Analysis:"):
                start_index = i
                break

        if start_index > 0:
            # Add new filepath comment
            latest_content = "# FilePath: {repo_name}_latest.md\n\n"
            latest_content += "\n".join(lines[start_index:])
            return latest_content

        return content

    def _save_additional_formats(
        self, results: Dict[str, Any], output_dir: Path, repo_name: str, timestamp: str
    ) -> None:
        """Save analysis in additional formats if requested."""
        try:
            # Save JSON summary for programmatic access
            summary = {
                "repository_name": repo_name,
                "analysis_timestamp": timestamp,
                "files_analyzed": results.get("Files Analyzed", 0),
                "model_used": results.get("Analysis Model", "Unknown"),
                "git_info": results.get("Git Information", {}),
                "env_files_count": len(results.get("Environment Configurations", {})),
                "has_git_repo": results.get("Git Information", {}).get(
                    "is_git_repo", False
                ),
                "repository_url": results.get("Git Information", {}).get(
                    "repository_url"
                ),
                "current_branch": results.get("Git Information", {}).get(
                    "current_branch"
                ),
            }

            json_file = output_dir / f"{timestamp}_{repo_name}_summary.json"
            import json

            with open(json_file, "w", encoding="utf-8") as f:
                json.dump(summary, f, indent=2, default=str)

            self.logger.debug(f"Saved JSON summary: {json_file}")

        except Exception as e:
            self.logger.warning(f"Failed to save additional formats: {str(e)}")

    def get_analysis_history(self, repo_name: str) -> list:
        """
        Get list of previous analyses for a repository.

        Args:
            repo_name: Repository name

        Returns:
            List of analysis file information
        """
        try:
            output_dir = Settings.get_output_dir(repo_name)
            if not output_dir.exists():
                return []

            analysis_files = []
            for file_path in output_dir.glob(f"*_{repo_name}_analysis.md"):
                try:
                    stat = file_path.stat()
                    timestamp_str = file_path.stem.split("_")[0]

                    analysis_files.append(
                        {
                            "file_path": str(file_path),
                            "timestamp": timestamp_str,
                            "size": stat.st_size,
                            "modified": stat.st_mtime,
                        }
                    )
                except Exception:
                    continue

            # Sort by timestamp (newest first)
            analysis_files.sort(key=lambda x: x["timestamp"], reverse=True)
            return analysis_files

        except Exception as e:
            self.logger.warning(f"Failed to get analysis history: {str(e)}")
            return []
