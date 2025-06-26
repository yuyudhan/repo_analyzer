# FilePath: src/repo_analyzer/main.py

import sys
import os
from pathlib import Path

# Add the config directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from .cli import main as cli_main
from .utils.logging_utils import setup_logging, get_logger
from config.settings import Settings


def main():
    """
    Main entry point for the repository analyzer application.
    """
    try:
        # Setup basic logging
        setup_logging(Settings.LOG_LEVEL)
        logger = get_logger(__name__)

        logger.info("Starting Repository Analyzer")
        logger.debug(f"Python version: {sys.version}")
        logger.debug(f"Working directory: {os.getcwd()}")

        # Run the CLI
        cli_main()

    except KeyboardInterrupt:
        print("\n⏹️  Application interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Application failed to start: {str(e)}")
        if "--debug" in sys.argv:
            import traceback

            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
