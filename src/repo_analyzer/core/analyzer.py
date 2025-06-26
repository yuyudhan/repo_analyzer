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

        self.logger.info(f"Initialized analyzer with {llm_provider} ({model})")

    def analyze_repository(
        self, repo_path: str, branch: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Perform comprehensive repository analysis.

        Args:
            repo_path: Local directory path or remote repository URL
            branch: Git branch to analyze (optional)

        Returns:
            Dictionary containing analysis results
        """
        self.logger.info(f"Starting analysis of repository: {repo_path}")

        try:
            # Handle repository setup (clone if remote, checkout branch)
            local_repo_path = self._setup_repository(repo_path, branch)
            repo_name = local_repo_path.name

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

            # Perform analysis
            analysis_result = self._perform_analysis(
                local_repo_path, prioritized_files, env_configs, git_info
            )

            return {
                "Repository Analysis": analysis_result,
                "Environment Configurations": env_configs,
                "Git Information": git_info,
                "Files Analyzed": len(all_files),
                "Repository Path": str(local_repo_path),
                "Analysis Model": self.model,
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
        self, question: str, repo_path: str, branch: Optional[str] = None
    ) -> str:
        """Answer a specific question about the repository."""
        try:
            # This would implement a more targeted analysis based on the question
            # For now, it's a placeholder for conversation mode
            return f"I'd analyze the repository to answer: {question}"
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

    def _perform_analysis(
        self,
        repo_path: Path,
        prioritized_files: List[Path],
        env_configs: Dict,
        git_info: Dict,
    ) -> str:
        """Perform the detailed analysis using LLM."""
        repo_name = repo_path.name

        # Split files into chunks
        file_chunks = [
            prioritized_files[i : i + Settings.FILES_PER_CHUNK]
            for i in range(0, len(prioritized_files), Settings.FILES_PER_CHUNK)
        ]

        self.logger.info(f"Analyzing {len(file_chunks)} chunks independently")

        chunk_analyses = []

        # Analyze each chunk independently
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
            chunk_analysis = self._analyze_chunk_independently(
                repo_name, chunk_content, i, len(file_chunks)
            )

            chunk_analyses.append(chunk_analysis)
            self.logger.info(f"Completed chunk {i}")

        # Generate final synthesis
        self.logger.info("Creating final synthesis...")
        return self._generate_final_analysis(
            repo_name, chunk_analyses, git_info, env_configs
        )

    def _analyze_chunk_independently(
        self, repo_name: str, chunk_content: str, chunk_num: int, total_chunks: int
    ) -> str:
        """Analyze a single chunk of code independently."""
        prompt = f"""
        Analyze this code chunk from repository "{repo_name}" (chunk {chunk_num}/{total_chunks}).

        EXTRACT COMPREHENSIVE CODE DETAILS:

        **TECHNOLOGY IDENTIFICATION:**
        - Exact programming languages, versions, and frameworks used
        - Specific libraries, dependencies, and their versions from imports/includes
        - Database technologies, ORM frameworks, and data access patterns
        - Build tools, package managers, and configuration files
        - Testing frameworks, CI/CD configurations, and deployment setups

        **CODE STRUCTURE ANALYSIS:**
        - Complete function/method signatures with parameters and return types
        - Class definitions, inheritance hierarchies, and interface implementations
        - Module organization, namespace structures, and import patterns
        - Data structures, enums, constants, and type definitions
        - Design patterns, architectural patterns, and coding conventions

        **FUNCTIONAL IMPLEMENTATION:**
        - API endpoints with exact routes, HTTP methods, and handlers
        - Database schemas, table structures, relationships, and queries
        - Business logic implementations, algorithms, and data processing
        - Configuration management, environment variables, and settings
        - Error handling, logging, validation, and security implementations

        **INFRASTRUCTURE & DEPLOYMENT:**
        - Containerization (Docker), orchestration, and deployment configurations
        - Service definitions, ports, volumes, and network configurations
        - Build processes, compilation steps, and optimization strategies
        - Monitoring, health checks, and observability implementations

        **SECURITY & PERFORMANCE:**
        - Authentication mechanisms, authorization patterns, and security headers
        - Input validation, sanitization, and data protection measures
        - Caching strategies, performance optimizations, and resource management
        - Rate limiting, throttling, and scalability considerations

        CODE CHUNK:
        {chunk_content}

        REQUIREMENTS:
        - State EXACTLY what you see in the code - be definitive and specific
        - Include complete code signatures, exact file paths, and specific values
        - Extract actual configuration keys, API endpoints, and database fields
        - Identify specific technologies by name and version where visible
        - Focus on concrete implementation details, not theoretical possibilities
        - Use technical terminology appropriate for senior developers
        """

        try:
            return self.llm.generate_response(prompt)
        except Exception as e:
            self.logger.error(f"Error analyzing chunk {chunk_num}: {str(e)}")
            return f"Error analyzing chunk {chunk_num}: {str(e)}"

    def _generate_final_analysis(
        self,
        repo_name: str,
        chunk_analyses: List[str],
        git_info: Dict,
        env_configs: Dict,
    ) -> str:
        """Generate the final comprehensive analysis."""
        # Combine all chunk analyses
        combined_analysis = "\n\n---\n\n".join(
            [
                f"## CHUNK {i + 1} ANALYSIS:\n{analysis}"
                for i, analysis in enumerate(chunk_analyses)
            ]
        )

        # Generate environment and git sections
        env_section = self._generate_env_section(env_configs)
        git_section = self._generate_git_section(git_info)

        # Create synthesis prompt
        synthesis_prompt = f"""
        Create a comprehensive technical analysis for repository "{repo_name}".

        Generate a detailed 10-section analysis covering:
        1. Repository Overview & Metrics
        2. Technology Stack Analysis
        3. Architectural Analysis
        4. Business Domain & Functionality
        5. Implementation Deep Dive
        6. Infrastructure & Deployment
        7. Development Workflow
        8. Security & Compliance
        9. Performance & Optimization
        10. Maintenance & Evolution

        {git_section}
        {env_section}

        CODE ANALYSIS DATA:
        {combined_analysis}

        Create a comprehensive, well-structured analysis that a CTO or senior developer
        would find valuable for understanding this codebase completely.
        """

        try:
            rate_limit_manager.wait_if_needed(self.llm_provider)
            return self.llm.generate_response(synthesis_prompt)
        except Exception as e:
            self.logger.error(f"Error generating final analysis: {str(e)}")
            return f"Error generating final analysis: {str(e)}"

    def _generate_env_section(self, env_configs: Dict) -> str:
        """Generate environment configuration section."""
        if not env_configs:
            return "## Environment Configuration Analysis\n\nNo environment configuration files found.\n\n"

        return self.env_extractor.generate_env_table(env_configs)

    def _generate_git_section(self, git_info: Dict) -> str:
        """Generate Git information section."""
        return self.git_handler.generate_git_info_section(git_info)
