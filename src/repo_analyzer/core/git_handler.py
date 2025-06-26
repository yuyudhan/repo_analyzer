# FilePath: src/repo_analyzer/core/git_handler.py

import subprocess
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Optional
from urllib.parse import urlparse

from config.settings import Settings
from ..utils.logging_utils import get_logger


class GitHandler:
    """Handles Git operations for repository analysis."""

    def __init__(self):
        self.logger = get_logger(__name__)
        self._temp_dirs = []  # Track temporary directories for cleanup

    def clone_repository(
        self, repo_url: str, target_dir: Optional[Path] = None
    ) -> Path:
        """
        Clone a remote repository to a local directory.

        Args:
            repo_url: URL of the remote repository
            target_dir: Optional target directory (creates temp dir if None)

        Returns:
            Path to the cloned repository
        """
        if target_dir is None:
            # Create temporary directory
            temp_dir = Path(tempfile.mkdtemp(prefix="repo_analyzer_"))
            self._temp_dirs.append(temp_dir)
            target_dir = temp_dir / self._extract_repo_name(repo_url)

        target_dir = Path(target_dir)

        try:
            self.logger.info(f"Cloning {repo_url} to {target_dir}")

            # Clone repository
            result = subprocess.run(
                ["git", "clone", repo_url, str(target_dir)],
                capture_output=True,
                text=True,
                timeout=Settings.CLONE_TIMEOUT,
            )

            if result.returncode != 0:
                raise RuntimeError(f"Git clone failed: {result.stderr}")

            self.logger.info(f"Successfully cloned repository to {target_dir}")
            return target_dir

        except subprocess.TimeoutExpired:
            self.logger.error(
                f"Clone operation timed out after {Settings.CLONE_TIMEOUT}s"
            )
            raise RuntimeError(f"Clone operation timed out")
        except FileNotFoundError:
            self.logger.error("Git not found in system PATH")
            raise RuntimeError("Git is not installed or not found in PATH")
        except Exception as e:
            self.logger.error(f"Clone operation failed: {str(e)}")
            raise

    def checkout_branch(self, repo_path: Path, branch: str) -> None:
        """
        Checkout a specific branch in the repository.

        Args:
            repo_path: Path to the local repository
            branch: Branch name to checkout
        """
        try:
            self.logger.info(f"Checking out branch '{branch}' in {repo_path}")

            # First, try to checkout existing branch
            result = subprocess.run(
                ["git", "checkout", branch],
                cwd=repo_path,
                capture_output=True,
                text=True,
                timeout=Settings.GIT_COMMAND_TIMEOUT,
            )

            if result.returncode != 0:
                # If that fails, try to checkout remote branch
                self.logger.info(
                    f"Local branch not found, trying remote branch origin/{branch}"
                )
                result = subprocess.run(
                    ["git", "checkout", "-b", branch, f"origin/{branch}"],
                    cwd=repo_path,
                    capture_output=True,
                    text=True,
                    timeout=Settings.GIT_COMMAND_TIMEOUT,
                )

                if result.returncode != 0:
                    raise RuntimeError(
                        f"Failed to checkout branch '{branch}': {result.stderr}"
                    )

            self.logger.info(f"Successfully checked out branch '{branch}'")

        except subprocess.TimeoutExpired:
            self.logger.error(f"Checkout operation timed out")
            raise RuntimeError(f"Checkout operation timed out")
        except Exception as e:
            self.logger.error(f"Checkout failed: {str(e)}")
            raise

    def extract_git_info(self, repo_path: Path) -> Dict:
        """
        Extract comprehensive Git repository information.

        Args:
            repo_path: Path to the repository

        Returns:
            Dictionary containing Git information
        """
        git_info = {
            "is_git_repo": False,
            "remote_urls": {},
            "current_branch": None,
            "all_branches": [],
            "total_commits": None,
            "last_commit": {},
            "repository_url": None,
            "error": None,
        }

        try:
            # Check if it's a Git repository
            result = subprocess.run(
                ["git", "rev-parse", "--git-dir"],
                cwd=repo_path,
                capture_output=True,
                text=True,
                timeout=Settings.GIT_COMMAND_TIMEOUT,
            )

            if result.returncode != 0:
                git_info["error"] = "Not a git repository"
                return git_info

            git_info["is_git_repo"] = True

            # Extract remote URLs
            self._extract_remote_urls(repo_path, git_info)

            # Extract branch information
            self._extract_branch_info(repo_path, git_info)

            # Extract commit information
            self._extract_commit_info(repo_path, git_info)

        except subprocess.TimeoutExpired:
            git_info["error"] = "Git command timed out"
        except FileNotFoundError:
            git_info["error"] = "Git not found in system PATH"
        except Exception as e:
            git_info["error"] = f"Error accessing git repository: {str(e)}"

        return git_info

    def generate_git_info_section(self, git_info: Dict) -> str:
        """Generate formatted Git repository information section."""
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

    def cleanup(self):
        """Clean up temporary directories."""
        for temp_dir in self._temp_dirs:
            try:
                if temp_dir.exists():
                    shutil.rmtree(temp_dir)
                    self.logger.info(f"Cleaned up temporary directory: {temp_dir}")
            except Exception as e:
                self.logger.warning(f"Failed to clean up {temp_dir}: {str(e)}")

        self._temp_dirs.clear()

    def _extract_repo_name(self, repo_url: str) -> str:
        """Extract repository name from URL."""
        try:
            if repo_url.endswith(".git"):
                repo_url = repo_url[:-4]

            # Handle different URL formats
            if repo_url.startswith("git@"):
                # SSH format: git@github.com:user/repo
                return repo_url.split(":")[-1].split("/")[-1]
            else:
                # HTTP(S) format
                parsed = urlparse(repo_url)
                return parsed.path.strip("/").split("/")[-1]
        except Exception:
            return "repository"

    def _extract_remote_urls(self, repo_path: Path, git_info: Dict) -> None:
        """Extract remote URLs from repository."""
        try:
            result = subprocess.run(
                ["git", "remote", "-v"],
                cwd=repo_path,
                capture_output=True,
                text=True,
                timeout=Settings.GIT_COMMAND_TIMEOUT,
            )

            if result.returncode == 0 and result.stdout.strip():
                remotes = {}
                for line in result.stdout.strip().split("\n"):
                    if line.strip():
                        parts = line.split()
                        if len(parts) >= 2:
                            remote_name = parts[0]
                            remote_url = parts[1]
                            operation = parts[2] if len(parts) > 2 else ""

                            if remote_name not in remotes:
                                remotes[remote_name] = {}

                            if "(fetch)" in operation:
                                remotes[remote_name]["fetch"] = remote_url
                            elif "(push)" in operation:
                                remotes[remote_name]["push"] = remote_url
                            else:
                                remotes[remote_name]["url"] = remote_url

                git_info["remote_urls"] = remotes

                # Set primary repository URL
                if "origin" in remotes:
                    git_info["repository_url"] = remotes["origin"].get(
                        "fetch"
                    ) or remotes["origin"].get("url")
                elif remotes:
                    first_remote = next(iter(remotes.values()))
                    git_info["repository_url"] = first_remote.get(
                        "fetch"
                    ) or first_remote.get("url")

        except Exception as e:
            self.logger.warning(f"Failed to extract remote URLs: {str(e)}")

    def _extract_branch_info(self, repo_path: Path, git_info: Dict) -> None:
        """Extract branch information from repository."""
        try:
            # Get current branch
            result = subprocess.run(
                ["git", "branch", "--show-current"],
                cwd=repo_path,
                capture_output=True,
                text=True,
                timeout=Settings.GIT_COMMAND_TIMEOUT,
            )

            if result.returncode == 0 and result.stdout.strip():
                git_info["current_branch"] = result.stdout.strip()

            # Get all branches
            result = subprocess.run(
                ["git", "branch", "-a"],
                cwd=repo_path,
                capture_output=True,
                text=True,
                timeout=Settings.GIT_COMMAND_TIMEOUT,
            )

            if result.returncode == 0 and result.stdout.strip():
                branches = []
                for line in result.stdout.strip().split("\n"):
                    branch = line.strip()
                    if branch and not branch.startswith("remotes/origin/HEAD"):
                        # Clean up branch name
                        branch = branch.replace("* ", "").replace("remotes/origin/", "")
                        if branch not in branches:
                            branches.append(branch)
                git_info["all_branches"] = sorted(branches)

        except Exception as e:
            self.logger.warning(f"Failed to extract branch info: {str(e)}")

    def _extract_commit_info(self, repo_path: Path, git_info: Dict) -> None:
        """Extract commit information from repository."""
        try:
            # Get total commit count
            result = subprocess.run(
                ["git", "rev-list", "--count", "HEAD"],
                cwd=repo_path,
                capture_output=True,
                text=True,
                timeout=Settings.GIT_COMMAND_TIMEOUT,
            )

            if result.returncode == 0 and result.stdout.strip():
                git_info["total_commits"] = int(result.stdout.strip())

            # Get last commit info
            result = subprocess.run(
                ["git", "log", "-1", "--pretty=format:%H|%an|%ae|%ad|%s", "--date=iso"],
                cwd=repo_path,
                capture_output=True,
                text=True,
                timeout=Settings.GIT_COMMAND_TIMEOUT,
            )

            if result.returncode == 0 and result.stdout.strip():
                commit_parts = result.stdout.strip().split("|")
                if len(commit_parts) >= 5:
                    git_info["last_commit"] = {
                        "hash": commit_parts[0],
                        "author_name": commit_parts[1],
                        "author_email": commit_parts[2],
                        "date": commit_parts[3],
                        "message": commit_parts[4],
                    }

        except Exception as e:
            self.logger.warning(f"Failed to extract commit info: {str(e)}")

    def __del__(self):
        """Ensure cleanup on object destruction."""
        self.cleanup()
