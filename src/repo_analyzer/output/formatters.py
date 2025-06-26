# FilePath: src/repo_analyzer/output/formatters.py

import time
from typing import Dict, Any

from ..utils.logging_utils import get_logger


class MarkdownFormatter:
    """Formats analysis results into markdown format."""

    def __init__(self):
        self.logger = get_logger(__name__)

    def format_header(self, repo_name: str, results: Dict[str, Any]) -> str:
        """
        Format the report header with metadata.

        Args:
            repo_name: Repository name
            results: Analysis results

        Returns:
            Formatted header string
        """
        header = f"# Technical Analysis: {repo_name}\n\n"
        header += f"*Analysis Date: {time.strftime('%Y-%m-%d %H:%M:%S')}*\n\n"

        if results.get("Repository Path"):
            header += f"*Repository Path: {results['Repository Path']}*\n\n"

        if results.get("Files Analyzed"):
            header += f"*Analysis Scope: {results['Files Analyzed']} files*\n\n"

        if results.get("Analysis Model"):
            header += f"*AI Model: {results['Analysis Model']}*\n\n"

        return header

    def format_git_section(self, git_info: Dict) -> str:
        """
        Format Git information section.

        Args:
            git_info: Git information dictionary

        Returns:
            Formatted Git section
        """
        if not git_info.get("is_git_repo"):
            if git_info.get("error"):
                return f"## Git Repository Information\n\n❌ {git_info['error']}\n\n"
            else:
                return "## Git Repository Information\n\n❌ Not a Git repository\n\n"

        git_section = "## Git Repository Information\n\n"

        if git_info.get("repository_url"):
            git_section += f"**Repository URL**: {git_info['repository_url']}\n\n"

        if git_info.get("current_branch"):
            git_section += f"**Current Branch**: `{git_info['current_branch']}`\n\n"

        if git_info.get("all_branches"):
            branches = git_info["all_branches"]
            git_section += (
                f"**All Branches**: {', '.join(f'`{b}`' for b in branches[:10])}"
            )
            if len(branches) > 10:
                git_section += f" (and {len(branches) - 10} more)"
            git_section += "\n\n"

        if git_info.get("total_commits"):
            git_section += f"**Total Commits**: {git_info['total_commits']}\n\n"

        if git_info.get("last_commit"):
            commit = git_info["last_commit"]
            git_section += "### Last Commit\n\n"
            git_section += f"- **Hash**: `{commit.get('hash', 'N/A')}`\n"
            git_section += (
                f"- **Author**: {commit.get('author_name', 'N/A')} "
                f"({commit.get('author_email', 'N/A')})\n"
            )
            git_section += f"- **Date**: {commit.get('date', 'N/A')}\n"
            git_section += f"- **Message**: {commit.get('message', 'N/A')}\n\n"

        return git_section

    def format_env_section(self, env_configs: Dict) -> str:
        """
        Format environment configuration section.

        Args:
            env_configs: Environment configurations dictionary

        Returns:
            Formatted environment section
        """
        if not env_configs:
            return "## Environment Configuration Analysis\n\nNo environment configuration files found.\n\n"

        env_section = "## Environment Configuration Analysis\n\n"
        total_vars = sum(
            config.get("variable_count", 0) for config in env_configs.values()
        )
        env_section += f"**Summary**: {len(env_configs)} environment files with {total_vars} total variables\n\n"

        for file_path, config in env_configs.items():
            variables = config.get("variables", {})
            comments = config.get("comments", [])
            total_lines = config.get("total_lines", 0)
            variable_count = config.get("variable_count", 0)

            env_section += f"### {file_path}\n\n"
            env_section += f"**File Stats**: {variable_count} variables, {total_lines} total lines\n\n"

            if comments:
                env_section += "**Key Comments**:\n"
                for comment in comments[:5]:  # Show top 5 comments
                    env_section += f"- {comment}\n"
                env_section += "\n"

            if variables:
                env_section += "| Variable | Purpose/Description | Example Value |\n"
                env_section += "|----------|--------------------|--------------|\n"

                # Sort variables for better organization
                sorted_vars = sorted(variables.items())
                for var_name, var_value in sorted_vars:
                    description = self._get_var_description(var_name)
                    display_value = self._mask_sensitive_value(var_name, var_value)
                    env_section += (
                        f"| `{var_name}` | {description} | `{display_value}` |\n"
                    )

                env_section += "\n"
            else:
                env_section += "*No variables found (comments only)*\n\n"

        return env_section

    def format_footer(self, results: Dict[str, Any]) -> str:
        """
        Format the report footer with analysis metadata.

        Args:
            results: Analysis results

        Returns:
            Formatted footer string
        """
        footer = "\n\n---\n\n"
        footer += "*Analysis completed using AI-powered repository analysis*\n"

        if results.get("Analysis Model"):
            footer += f"*Model: {results['Analysis Model']}*\n"

        if results.get("Files Analyzed"):
            footer += f"*Files processed: {results['Files Analyzed']}*\n"

        footer += f"*Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}*\n"

        return footer

    def format_section_header(self, section_num: int, title: str) -> str:
        """Format a section header."""
        return f"## {section_num}. {title.upper()}\n\n"

    def format_subsection_header(self, title: str) -> str:
        """Format a subsection header."""
        return f"### {title}\n\n"

    def format_code_block(self, content: str, language: str = "text") -> str:
        """Format a code block."""
        return f"```{language}\n{content}\n```\n\n"

    def format_table(self, headers: list, rows: list) -> str:
        """
        Format a markdown table.

        Args:
            headers: List of header strings
            rows: List of row data (each row is a list)

        Returns:
            Formatted table string
        """
        if not headers or not rows:
            return ""

        table = "| " + " | ".join(headers) + " |\n"
        table += "|" + "|".join(["-" * (len(h) + 2) for h in headers]) + "|\n"

        for row in rows:
            table += "| " + " | ".join(str(cell) for cell in row) + " |\n"

        return table + "\n"

    def format_list(self, items: list, ordered: bool = False) -> str:
        """
        Format a markdown list.

        Args:
            items: List of items
            ordered: Whether to create an ordered list

        Returns:
            Formatted list string
        """
        if not items:
            return ""

        list_str = ""
        for i, item in enumerate(items):
            if ordered:
                list_str += f"{i + 1}. {item}\n"
            else:
                list_str += f"- {item}\n"

        return list_str + "\n"

    def format_alert(self, message: str, alert_type: str = "info") -> str:
        """
        Format an alert/callout box.

        Args:
            message: Alert message
            alert_type: Type of alert (info, warning, error, success)

        Returns:
            Formatted alert string
        """
        icons = {"info": "ℹ️", "warning": "⚠️", "error": "❌", "success": "✅"}

        icon = icons.get(alert_type, "ℹ️")
        return f"> {icon} **{alert_type.title()}**: {message}\n\n"

    def _get_var_description(self, var_name: str) -> str:
        """Get description for environment variable."""
        var_lower = var_name.lower()

        descriptions = {
            "port": "Application server port",
            "host": "Server host address",
            "database_url": "Database connection string",
            "db_host": "Database host",
            "db_port": "Database port",
            "db_name": "Database name",
            "db_user": "Database username",
            "db_password": "Database password",
            "redis_url": "Redis connection string",
            "jwt_secret": "JWT signing secret",
            "api_key": "External API key",
            "secret_key": "Application secret key",
            "debug": "Debug mode flag",
            "env": "Environment (dev/staging/prod)",
            "log_level": "Logging level",
        }

        for key, desc in descriptions.items():
            if key in var_lower:
                return desc

        if "url" in var_lower or "uri" in var_lower:
            return "Service connection URL/URI"
        elif "key" in var_lower or "secret" in var_lower or "token" in var_lower:
            return "Authentication/encryption key"
        elif "host" in var_lower or "server" in var_lower:
            return "Server/service host address"
        elif "port" in var_lower:
            return "Service port number"

        return "Configuration parameter"

    def _mask_sensitive_value(self, var_name: str, var_value: str) -> str:
        """Mask sensitive values."""
        var_lower = var_name.lower()
        sensitive_patterns = ["password", "secret", "key", "token", "auth"]

        if any(pattern in var_lower for pattern in sensitive_patterns):
            if len(var_value) > 4:
                return var_value[:2] + "*" * (len(var_value) - 4) + var_value[-2:]
            else:
                return "*" * len(var_value)

        return var_value


class JSONFormatter:
    """Formats analysis results into JSON format."""

    def __init__(self):
        self.logger = get_logger(__name__)

    def format_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format results into a JSON summary.

        Args:
            results: Analysis results

        Returns:
            JSON-serializable summary dictionary
        """
        from pathlib import Path

        summary = {
            "analysis_metadata": {
                "timestamp": results.get("Timestamp", time.strftime("%Y%m%d_%H%M%S")),
                "model_used": results.get("Analysis Model", "Unknown"),
                "files_analyzed": results.get("Files Analyzed", 0),
                "repository_path": results.get("Repository Path", ""),
            },
            "repository_info": {
                "name": Path(results.get("Repository Path", "")).name
                if results.get("Repository Path")
                else "Unknown",
                "git_info": results.get("Git Information", {}),
                "environment_files": len(results.get("Environment Configurations", {})),
                "has_git_repo": results.get("Git Information", {}).get(
                    "is_git_repo", False
                ),
            },
            "analysis_summary": {
                "has_analysis": "Repository Analysis" in results,
                "analysis_length": len(results.get("Repository Analysis", ""))
                if results.get("Repository Analysis")
                else 0,
                "sections_identified": self._count_sections(
                    results.get("Repository Analysis", "")
                ),
            },
        }

        return summary

    def _count_sections(self, analysis_text: str) -> int:
        """Count the number of sections in the analysis."""
        if not analysis_text:
            return 0

        import re

        # Count markdown headers (## or ###)
        headers = re.findall(r"^#{2,3}\s+", analysis_text, re.MULTILINE)
        return len(headers)
