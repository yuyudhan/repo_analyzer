# FilePath: src/repo_analyzer/core/analyzer.py

import time
from pathlib import Path
from typing import Dict, List, Optional, Any

from config.settings import Settings
from config.rate_limits import rate_limit_manager
from ..llm.factory import LLMFactory
from ..utils.logging_utils import get_logger
from .git_handler import GitHandler
from .file_processor import FileProcessor
from .env_extractor import EnvExtractor
from .conversation_analyzer import ConversationAnalyzer
from .developer_explanation import DeveloperExplanation
from ..output.report_generator import ReportGenerator


class RepositoryAnalyzer:
    """Main orchestrator for repository analysis."""

    def __init__(self, llm_provider: str = "claude", model: Optional[str] = None):
        self.logger = get_logger(__name__)
        self.llm_provider = llm_provider
        self.model = model or Settings.DEFAULT_MODEL
        self.timestamp = time.strftime("%Y%m%d_%H%M%S")

        # Initialize components
        self.llm = LLMFactory.create_provider(llm_provider, model)
        self.git_handler = GitHandler()
        self.file_processor = FileProcessor()
        self.env_extractor = EnvExtractor()
        self.report_generator = ReportGenerator()

        # Initialize both analysis approaches
        self.conversation_analyzer = ConversationAnalyzer(self.llm)
        self.developer_explanation = DeveloperExplanation(self.llm)

        self.logger.info(f"Initialized analyzer with {llm_provider} ({model})")

    def analyze_repository(
        self,
        repo_path: str,
        branch: Optional[str] = None,
        analysis_mode: str = "analysis",
        human_context: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Perform comprehensive repository analysis.

        Args:
            repo_path: Local directory path or remote repository URL
            branch: Git branch to analyze (optional)
            analysis_mode: "analysis" for third-party audit or "developer"
                          for insider explanation
            human_context: Additional context from human to enhance analysis
                          quality

        Returns:
            Dictionary containing analysis results
        """
        self.logger.info(
            f"Starting {analysis_mode} mode analysis of repository: {repo_path}"
        )

        if human_context:
            self.logger.info(f"Using human context: {human_context[:100]}...")

        try:
            # Handle repository setup (clone if remote, checkout branch)
            local_repo_path = self._setup_repository(repo_path, branch)

            self.logger.info(f"Analyzing local repository: {local_repo_path}")

            # Extract Git information
            self.logger.info("Extracting Git information...")
            git_info = self.git_handler.extract_git_info(local_repo_path)

            # Extract environment configurations
            self.logger.info("Extracting environment configurations...")
            env_configs = self.env_extractor.extract_env_config(local_repo_path)

            # Process source files
            self.logger.info("Processing source files...")
            all_files = self.file_processor.get_all_source_files(local_repo_path)
            prioritized_files = self.file_processor.prioritize_files(all_files)

            self.logger.info(f"Found {len(all_files)} source files")

            # Perform analysis based on selected mode
            if analysis_mode == "developer":
                analysis_result = self._perform_developer_explanation(
                    local_repo_path,
                    prioritized_files,
                    env_configs,
                    git_info,
                    human_context,
                )
                analysis_type = "Developer Explanation"
            else:
                analysis_result = self._perform_analysis_audit(
                    local_repo_path,
                    prioritized_files,
                    env_configs,
                    git_info,
                    human_context,
                )
                analysis_type = "Technical Analysis"

            return {
                "Repository Analysis": analysis_result,
                "Analysis Type": analysis_type,
                "Analysis Mode": analysis_mode,
                "Environment Configurations": env_configs,
                "Git Information": git_info,
                "Files Analyzed": len(all_files),
                "Repository Path": str(local_repo_path),
                "Analysis Model": self.model,
                "Human Context": human_context,
                "Timestamp": self.timestamp,
            }

        except Exception as e:
            self.logger.error(f"Analysis failed: {str(e)}", exc_info=True)
            raise

    def get_repository_overview(
        self, repo_path: str, branch: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get a quick overview of the repository for conversation mode."""
        try:
            local_repo_path = self._setup_repository(repo_path, branch)
            git_info = self.git_handler.extract_git_info(local_repo_path)
            all_files = self.file_processor.get_all_source_files(local_repo_path)

            return {
                "name": local_repo_path.name,
                "path": str(local_repo_path),
                "file_count": len(all_files),
                "current_branch": git_info.get("current_branch"),
                "repository_url": git_info.get("repository_url"),
                "is_git_repo": git_info.get("is_git_repo", False),
            }
        except Exception as e:
            self.logger.error(f"Failed to get repository overview: {str(e)}")
            raise

    def answer_question(
        self,
        question: str,
        repo_path: str,
        branch: Optional[str] = None,
        human_context: Optional[str] = None,
    ) -> str:
        """Answer a specific question about the repository."""
        try:
            # Get quick repository overview for context
            overview = self.get_repository_overview(repo_path, branch)

            # Create context-aware prompt for targeted analysis
            context_info = f"""
            You are analyzing the repository "{overview["name"]}" with
            {overview["file_count"]} files.
            Current branch: {overview.get("current_branch", "unknown")}
            """

            if human_context:
                context_info += f"\n\nAdditional Context: {human_context}"

            prompt = f"""
            {context_info}

            User Question: {question}

            Based on the repository structure, human context (if provided),
            and the user's question, provide a specific and helpful answer.
            If you need to examine specific files or patterns, mention what
            you would look for.
            """

            rate_limit_manager.wait_if_needed(self.llm_provider)
            response = self.llm.generate_response(prompt)

            return response

        except Exception as e:
            self.logger.error(f"Failed to answer question: {str(e)}")
            raise

    def save_analysis(self, results: Dict[str, Any], repo_path: str) -> Optional[str]:
        """Save analysis results to files."""
        try:
            return self.report_generator.save_analysis(
                results, repo_path, self.timestamp
            )
        except Exception as e:
            self.logger.error(f"Failed to save analysis: {str(e)}")
            return None

    def _setup_repository(self, repo_path: str, branch: Optional[str]) -> Path:
        """Setup repository (clone if remote, checkout branch if specified)."""
        # Check if it's a remote URL
        if self._is_remote_url(repo_path):
            self.logger.info(f"Cloning remote repository: {repo_path}")
            local_path = self.git_handler.clone_repository(repo_path)
        else:
            local_path = Path(repo_path)
            if not local_path.exists():
                raise ValueError(f"Repository path does not exist: {repo_path}")

        # Checkout specific branch if requested
        if branch:
            self.logger.info(f"Checking out branch: {branch}")
            self.git_handler.checkout_branch(local_path, branch)

        return local_path

    def _is_remote_url(self, path: str) -> bool:
        """Check if the path is a remote repository URL."""
        return (
            path.startswith("http://")
            or path.startswith("https://")
            or path.startswith("git@")
            or path.startswith("ssh://")
        )

    def _perform_analysis_audit(
        self,
        repo_path: Path,
        prioritized_files: List[Path],
        env_configs: Dict,
        git_info: Dict,
        human_context: Optional[str] = None,
    ) -> str:
        """Perform third-party technical analysis audit."""
        repo_name = repo_path.name

        # Get code analysis first
        chunk_analyses = self._get_code_analysis(repo_path, prioritized_files)

        # Generate comprehensive analysis using audit approach
        self.logger.info("Generating comprehensive technical analysis...")
        return self.conversation_analyzer.generate_comprehensive_analysis(
            repo_name, chunk_analyses, git_info, env_configs, human_context
        )

    def _perform_developer_explanation(
        self,
        repo_path: Path,
        prioritized_files: List[Path],
        env_configs: Dict,
        git_info: Dict,
        human_context: Optional[str] = None,
    ) -> str:
        """Perform developer perspective explanation."""
        repo_name = repo_path.name

        # Get code analysis first
        chunk_analyses = self._get_code_analysis(repo_path, prioritized_files)

        # Generate developer explanation
        self.logger.info("Generating developer perspective explanation...")
        return self.developer_explanation.generate_developer_explanation(
            repo_name, chunk_analyses, git_info, env_configs, human_context
        )

    def _get_code_analysis(
        self, repo_path: Path, prioritized_files: List[Path]
    ) -> List[str]:
        """Get code analysis from chunks (shared by both modes)."""

        # Split files into chunks for analysis
        file_chunks = [
            prioritized_files[i : i + Settings.FILES_PER_CHUNK]
            for i in range(0, len(prioritized_files), Settings.FILES_PER_CHUNK)
        ]

        self.logger.info(f"Processing {len(file_chunks)} chunks for code analysis")

        chunk_analyses = []

        # Process each chunk to analyze the code
        for i, chunk in enumerate(file_chunks, 1):
            self.logger.info(
                f"Analyzing chunk {i}/{len(file_chunks)} ({len(chunk)} files)"
            )

            # Apply rate limiting
            rate_limit_manager.wait_if_needed(self.llm_provider)

            chunk_content = self.file_processor.create_file_chunk_content(
                repo_path, chunk, i
            )

            # Small delay between chunks
            if i > 1:
                time.sleep(Settings.PROCESSING_DELAY)

            # Analyze this chunk
            chunk_analysis = self._analyze_code_chunk(
                chunk_content, i, len(file_chunks)
            )

            chunk_analyses.append(chunk_analysis)
            self.logger.info(f"Completed analysis of chunk {i}")

        return chunk_analyses

    def _analyze_code_chunk(
        self, chunk_content: str, chunk_num: int, total_chunks: int
    ) -> str:
        """Analyze code chunk content and provide insights."""
        prompt = f"""
        Analyze this code chunk ({chunk_num}/{total_chunks}) and provide
        comprehensive technical insights.

        **TECHNICAL ANALYSIS:**
        - Architecture patterns and design principles used
        - Code quality assessment (structure, maintainability, readability)
        - Performance implications and optimizations present
        - Security implementations and potential vulnerabilities
        - Error handling and resilience patterns

        **FUNCTIONAL ANALYSIS:**
        - Core business logic and functionality
        - API design and data flow patterns
        - Integration patterns and external dependencies
        - Database operations and data modeling approaches
        - Testing strategies and coverage visible

        **TECHNOLOGY ASSESSMENT:**
        - Framework usage and best practices adherence
        - Library choices and their appropriateness
        - Configuration management and environment handling
        - Deployment and infrastructure considerations
        - Monitoring, logging, and observability patterns

        **CODE INSIGHTS:**
        - Strengths and well-implemented patterns
        - Areas for improvement or refactoring
        - Technical debt indicators
        - Scalability considerations
        - Maintainability factors

        **DEVELOPMENT PRACTICES:**
        - Code organization and modularity
        - Documentation quality and completeness
        - Version control patterns visible
        - Development workflow indicators
        - Compliance and standards adherence

        CODE CHUNK:
        {chunk_content}

        REQUIREMENTS:
        - Provide actionable technical insights
        - Focus on both strengths and improvement areas
        - Consider enterprise-level concerns (security, scalability,
          maintainability)
        - Be specific with examples from the code when possible
        - Consider industry best practices and modern development standards
        """

        try:
            return self.llm.generate_response(prompt)
        except Exception as e:
            self.logger.error(f"Error analyzing chunk {chunk_num}: {str(e)}")
            return f"Error analyzing chunk {chunk_num}: {str(e)}"
