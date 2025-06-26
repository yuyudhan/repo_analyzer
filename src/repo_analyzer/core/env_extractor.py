# FilePath: src/repo_analyzer/core/env_extractor.py

from pathlib import Path
from typing import Dict, List

from ..utils.logging_utils import get_logger


class EnvExtractor:
    """Handles extraction and analysis of environment configuration files."""

    def __init__(self):
        self.logger = get_logger(__name__)

    def extract_env_config(self, repo_path: Path) -> Dict:
        """
        Extract and analyze ALL .env configuration files comprehensively.

        Args:
            repo_path: Path to the repository

        Returns:
            Dictionary containing environment configurations
        """
        env_configs = {}

        # Comprehensive .env file patterns
        env_patterns = [
            ".env",
            ".env.example",
            ".env.sample",
            ".env.template",
            ".env.local",
            ".env.local.example",
            ".env.development",
            ".env.dev",
            ".env.staging",
            ".env.stage",
            ".env.production",
            ".env.prod",
            ".env.test",
            ".env.testing",
            ".environment",
            "env.example",
            "env.sample",
            "env.template",
        ]

        self.logger.info("Scanning for environment configuration files...")
        found_env_files = []

        for pattern in env_patterns:
            # Search in root directory
            env_file = repo_path / pattern
            if env_file.exists() and env_file.is_file():
                found_env_files.append(env_file)

            # Search recursively in subdirectories (but avoid common ignore dirs)
            for env_file in repo_path.rglob(pattern):
                if not self._should_ignore_file(env_file) and env_file.is_file():
                    found_env_files.append(env_file)

        # Remove duplicates
        found_env_files = list(set(found_env_files))

        for env_file in found_env_files:
            try:
                with open(env_file, "r", encoding="utf-8") as f:
                    content = f.read()

                # Parse environment variables with enhanced parsing
                env_vars = {}
                comments = []

                for line_num, line in enumerate(content.split("\n"), 1):
                    original_line = line
                    line = line.strip()

                    # Capture comments for context
                    if line.startswith("#") and line not in ["#", "# "]:
                        comments.append(f"Line {line_num}: {line}")

                    # Parse key=value pairs
                    elif line and not line.startswith("#") and "=" in line:
                        try:
                            # Handle quoted values and special characters
                            if line.count("=") == 1:
                                key, value = line.split("=", 1)
                            else:
                                # Handle cases like KEY=value=something
                                parts = line.split("=")
                                key = parts[0]
                                value = "=".join(parts[1:])

                            key = key.strip()
                            value = value.strip()

                            # Remove quotes if present
                            if value.startswith('"') and value.endswith('"'):
                                value = value[1:-1]
                            elif value.startswith("'") and value.endswith("'"):
                                value = value[1:-1]

                            if key:  # Only add non-empty keys
                                env_vars[key] = value

                        except Exception as e:
                            self.logger.warning(
                                f"Could not parse line {line_num} in {env_file}: {original_line}"
                            )

                if env_vars or comments:
                    relative_path = str(env_file.relative_to(repo_path))
                    env_configs[relative_path] = {
                        "variables": env_vars,
                        "comments": comments[:10],  # Limit comments to avoid bloat
                        "total_lines": len(content.split("\n")),
                        "variable_count": len(env_vars),
                    }
                    self.logger.info(
                        f"Parsed {relative_path}: {len(env_vars)} variables"
                    )

            except Exception as e:
                self.logger.warning(f"Error reading {env_file}: {str(e)}")

        if found_env_files:
            total_vars = sum(
                len(config["variables"]) for config in env_configs.values()
            )
            self.logger.info(
                f"Found {len(found_env_files)} environment files with {total_vars} total variables"
            )
        else:
            self.logger.info("No environment configuration files found")

        return env_configs

    def generate_env_table(self, env_configs: Dict) -> str:
        """
        Generate comprehensive formatted table for environment configurations.

        Args:
            env_configs: Dictionary of environment configurations

        Returns:
            Formatted markdown table string
        """
        if not env_configs:
            return "## Environment Configuration Analysis\n\nNo environment configuration files found.\n\n"

        env_table = "## Environment Configuration Analysis\n\n"
        total_vars = sum(config["variable_count"] for config in env_configs.values())
        env_table += f"**Summary**: {len(env_configs)} environment files with {total_vars} total variables\n\n"

        for file_path, config in env_configs.items():
            variables = config.get("variables", {})
            comments = config.get("comments", [])
            total_lines = config.get("total_lines", 0)
            variable_count = config.get("variable_count", 0)

            env_table += f"### {file_path}\n\n"
            env_table += f"**File Stats**: {variable_count} variables, {total_lines} total lines\n\n"

            if comments:
                env_table += "**Key Comments**:\n"
                for comment in comments[:5]:  # Show top 5 comments
                    env_table += f"- {comment}\n"
                env_table += "\n"

            if variables:
                env_table += "| Variable | Purpose/Description | Example Value |\n"
                env_table += "|----------|--------------------|--------------|\n"

                # Sort variables for better organization
                sorted_vars = sorted(variables.items())
                for var_name, var_value in sorted_vars:
                    description = self._get_env_var_description(var_name)
                    display_value = self._mask_sensitive_value(var_name, var_value)
                    env_table += (
                        f"| `{var_name}` | {description} | `{display_value}` |\n"
                    )

                env_table += "\n"
            else:
                env_table += "*No variables found (comments only)*\n\n"

        return env_table

    def _should_ignore_file(self, file_path: Path) -> bool:
        """Check if an environment file should be ignored."""
        ignore_dirs = {
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
            "temp",
            "tmp",
            ".tmp",
            "cache",
            ".cache",
        }

        for part in file_path.parts:
            if part.lower() in ignore_dirs:
                return True

        return False

    def _get_env_var_description(self, var_name: str) -> str:
        """
        Get description for common environment variables.

        Args:
            var_name: Environment variable name

        Returns:
            Description of the variable's purpose
        """
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
            "cors_origin": "CORS allowed origins",
            "session_secret": "Session encryption secret",
            "stripe_key": "Stripe payment API key",
            "aws_access_key": "AWS access credentials",
            "google_client_id": "Google OAuth client ID",
            "facebook_app_id": "Facebook app credentials",
            "smtp_host": "Email server configuration",
            "oauth_secret": "OAuth application secret",
            "encryption_key": "Data encryption key",
            "webhook_secret": "Webhook verification secret",
        }

        # Direct match
        for key, desc in descriptions.items():
            if key in var_lower:
                return desc

        # Pattern matching
        if "url" in var_lower or "uri" in var_lower:
            return "Service connection URL/URI"
        elif "key" in var_lower or "secret" in var_lower or "token" in var_lower:
            return "Authentication/encryption key"
        elif "host" in var_lower or "server" in var_lower:
            return "Server/service host address"
        elif "port" in var_lower:
            return "Service port number"
        elif "password" in var_lower or "pass" in var_lower:
            return "Authentication password"
        elif "user" in var_lower or "username" in var_lower:
            return "Authentication username"
        elif "email" in var_lower or "mail" in var_lower:
            return "Email configuration"
        elif "timeout" in var_lower:
            return "Timeout configuration (seconds)"
        elif "max" in var_lower or "limit" in var_lower:
            return "Limit/threshold configuration"
        elif "enable" in var_lower or "disable" in var_lower:
            return "Feature toggle flag"

        return "Configuration parameter"

    def _mask_sensitive_value(self, var_name: str, var_value: str) -> str:
        """
        Mask sensitive values in environment variables.

        Args:
            var_name: Variable name
            var_value: Variable value

        Returns:
            Masked value for display
        """
        var_lower = var_name.lower()
        sensitive_patterns = [
            "password",
            "secret",
            "key",
            "token",
            "auth",
            "credential",
            "private",
            "jwt",
            "oauth",
            "api_key",
            "access_key",
        ]

        if any(pattern in var_lower for pattern in sensitive_patterns):
            if len(var_value) > 4:
                return var_value[:2] + "*" * (len(var_value) - 4) + var_value[-2:]
            else:
                return "*" * len(var_value)

        # Show full value for non-sensitive variables
        return var_value
