# src/repo_analyzer/cli.py

import click
import subprocess
import sys
from typing import Optional

from config.settings import Settings
from .core.analyzer import RepositoryAnalyzer
from .utils.logging_utils import setup_logging, get_logger


@click.group()
def main():
    """Repository Analyzer - AI-powered codebase analysis tool."""
    pass


@main.command()  # Changed from @click.command() to @main.command()
@click.option(
    "--repo",
    required=True,
    help="Repository path (local directory) or URL (remote repository to clone)",
)
@click.option(
    "--branch",
    default=None,
    help="Git branch to checkout (default: current/main branch)",
)
@click.option(
    "--llm",
    default="claude",
    type=click.Choice(["claude"], case_sensitive=False),
    help="LLM provider to use for analysis (default: claude)",
)
@click.option(
    "--model",
    default=None,
    help="Specific model to use (default: claude-3-5-sonnet-20241022 for Claude)",
)
@click.option(
    "--output-dir",
    default=None,
    help="Output directory for analysis results (default: ./repo_analysis)",
)
@click.option(
    "--files-per-chunk",
    default=8,
    type=int,
    help="Number of files to process per chunk (default: 8)",
)
@click.option(
    "--use-compression/--no-compression",
    default=True,
    help="Enable/disable smart code compression (default: enabled)",
)
@click.option(
    "--max-indentation",
    default=3,
    type=int,
    help="Maximum indentation level to preserve during compression (default: 3)",
)
@click.option(
    "--processing-delay",
    default=2.0,
    type=float,
    help="Delay between API calls in seconds (default: 2.0)",
)
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose logging")
@click.option(
    "--conversation-mode",
    is_flag=True,
    help="Enable conversation mode for interactive analysis",
)
def analyze(
    repo: str,
    branch: Optional[str],
    llm: str,
    model: Optional[str],
    output_dir: Optional[str],
    files_per_chunk: int,
    use_compression: bool,
    max_indentation: int,
    processing_delay: float,
    verbose: bool,
    conversation_mode: bool,
):
    """
    Analyze a repository using AI to generate comprehensive technical analysis.

    REPO can be either:
    - Local directory path: /path/to/local/repo
    - Remote repository URL: https://github.com/user/repo.git
    """

    # Setup logging
    log_level = "DEBUG" if verbose else "INFO"
    setup_logging(log_level)
    logger = get_logger(__name__)

    # Update settings from CLI arguments
    settings_updates = {
        "files_per_chunk": files_per_chunk,
        "use_smart_compression": use_compression,
        "max_indentation_level": max_indentation,
        "processing_delay": processing_delay,
        "default_llm": llm,
    }

    if model:
        settings_updates["default_model"] = model

    if output_dir:
        settings_updates["output_dir"] = output_dir

    Settings.update_from_dict(settings_updates)

    # Validate API keys
    if llm == "claude" and not Settings.ANTHROPIC_API_KEY:
        logger.error("ANTHROPIC_API_KEY environment variable is required for Claude")
        click.echo("❌ Please set ANTHROPIC_API_KEY environment variable")
        raise click.ClickException("Missing required API key")

    try:
        logger.info(f"Starting repository analysis with {llm}")
        logger.info(f"Repository: {repo}")
        if branch:
            logger.info(f"Branch: {branch}")

        # Initialize analyzer
        analyzer = RepositoryAnalyzer(
            llm_provider=llm, model=model or Settings.DEFAULT_MODEL
        )

        # Start analysis
        if conversation_mode:
            click.echo("🗣️  Conversation mode enabled - interactive analysis")
            _run_conversation_mode(analyzer, repo, branch)
        else:
            click.echo("🚀 Starting comprehensive repository analysis...")
            _run_analysis(analyzer, repo, branch)

    except KeyboardInterrupt:
        logger.info("Analysis interrupted by user")
        click.echo("\n⏹️  Analysis interrupted by user")
    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}", exc_info=True)
        click.echo(f"❌ Analysis failed: {str(e)}")


def _run_analysis(analyzer: RepositoryAnalyzer, repo_path: str, branch: Optional[str]):
    """Run the standard analysis workflow."""
    try:
        # Analyze repository
        results = analyzer.analyze_repository(repo_path, branch)

        if results and "Repository Analysis" in results:
            output_file = analyzer.save_analysis(results, repo_path)

            if output_file:
                click.echo("\n" + "=" * 70)
                click.echo("🎉 COMPREHENSIVE TECHNICAL ANALYSIS COMPLETE!")
                click.echo("=" * 70)
                click.echo(
                    f"📊 Files analyzed: {results.get('Files Analyzed', 'Unknown')}"
                )
                click.echo(
                    f"🔧 Environment configs: {len(results.get('Environment Configurations', {}))}"
                )
                click.echo(f"📄 Complete analysis: {output_file}")
                click.echo("=" * 70)
            else:
                click.echo("❌ Failed to save analysis results")
        else:
            click.echo("❌ Analysis process failed")

    except Exception as e:
        click.echo(f"❌ Error during analysis: {str(e)}")


def _run_conversation_mode(
    analyzer: RepositoryAnalyzer, repo_path: str, branch: Optional[str]
):
    """Run interactive conversation mode."""
    click.echo("🎯 Conversation Mode - Ask questions about the repository")
    click.echo("Type 'quit' or 'exit' to stop, 'analyze' for full analysis")
    click.echo("-" * 50)

    # First, do a lightweight scan to understand the repository
    try:
        click.echo("📋 Performing initial repository scan...")
        repo_info = analyzer.get_repository_overview(repo_path, branch)
        click.echo(f"✅ Repository loaded: {repo_info.get('name', 'Unknown')}")
        click.echo(f"📁 Files found: {repo_info.get('file_count', 0)}")
        click.echo(f"🌿 Current branch: {repo_info.get('current_branch', 'Unknown')}")
        click.echo("-" * 50)

        while True:
            user_input = click.prompt(
                "\n🤔 What would you like to know about this repository?"
            ).strip()

            if user_input.lower() in ["quit", "exit", "q"]:
                click.echo("👋 Goodbye!")
                break
            elif user_input.lower() == "analyze":
                click.echo("🚀 Starting full analysis...")
                _run_analysis(analyzer, repo_path, branch)
                continue
            elif not user_input:
                continue

            try:
                click.echo("🤖 Analyzing...")
                response = analyzer.answer_question(user_input, repo_path, branch)
                click.echo(f"\n💡 {response}")
            except Exception as e:
                click.echo(f"❌ Error: {str(e)}")

    except Exception as e:
        click.echo(f"❌ Failed to initialize conversation mode: {str(e)}")


@main.command()
def version():
    """Show version information."""
    click.echo("Repository Analyzer v1.0.0")
    click.echo("AI-powered repository analysis tool")


@main.command()
@click.option("--check-all", is_flag=True, help="Check all dependencies")
def check(check_all: bool):
    """Check system requirements and API connectivity."""
    click.echo("🔍 Checking system requirements...")

    # Check Python version
    if sys.version_info < (3, 8):
        click.echo("❌ Python 3.8+ required")
        return
    else:
        click.echo(f"✅ Python {sys.version.split()[0]}")

    # Check Git
    try:
        result = subprocess.run(["git", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            click.echo(f"✅ {result.stdout.strip()}")
        else:
            click.echo("❌ Git not found")
    except FileNotFoundError:
        click.echo("❌ Git not installed")

    # Check API keys
    if Settings.ANTHROPIC_API_KEY:
        click.echo("✅ Anthropic API key configured")

        if check_all:
            # Test API connectivity
            try:
                from .llm.claude import ClaudeProvider

                click.echo("🔗 Testing API connectivity...")
                provider = ClaudeProvider()
                if provider.validate_configuration():
                    click.echo("✅ API connection successful")
                else:
                    click.echo("❌ API configuration validation failed")
            except Exception as e:
                click.echo(f"❌ API test failed: {str(e)}")
    else:
        click.echo("⚠️  Anthropic API key not configured")

    click.echo("✅ System check complete")


if __name__ == "__main__":
    main()
