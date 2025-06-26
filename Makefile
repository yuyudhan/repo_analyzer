# FilePath: Makefile

.PHONY: help install install-dev test lint format clean build upload

help:
	@echo "Available commands:"
	@echo "  install     - Install package in production mode"
	@echo "  install-dev - Install package in development mode with dev dependencies"
	@echo "  test        - Run test suite"
	@echo "  lint        - Run linting checks"
	@echo "  format      - Format code using black and isort"
	@echo "  clean       - Clean build artifacts"
	@echo "  build       - Build distribution packages"
	@echo "  check       - Run system compatibility check"

install:
	pip install -e .

install-dev:
	pip install -e ".[dev]"
	pip install pytest pytest-cov black isort flake8 mypy

test:
	python -m pytest tests/ -v --cov=src/repo_analyzer --cov-report=html

lint:
	flake8 src/ --max-line-length=88 --extend-ignore=E203,W503
	mypy src/ --ignore-missing-imports

format:
	black src/ tests/ --line-length=88
	isort src/ tests/ --profile=black

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/

build: clean
	python setup.py sdist bdist_wheel

check:
	repo-analyzer check --check-all

# Development shortcuts
dev-setup: install-dev
	@echo "Setting up development environment..."
	@echo "Creating .env file..."
	@cp .env.example .env
	@echo "Please edit .env file and add your API keys"

quick-test:
	python -m pytest tests/ -x --tb=short

# Example usage
example-local:
	repo-analyzer --repo . --verbose

example-remote:
	repo-analyzer --repo https://github.com/microsoft/vscode.git --verbose --conversation-mode

# FilePath: scripts/dev_setup.py

#!/usr/bin/env python3
"""
Development setup script for repo analyzer.
"""

import os
import sys
import subprocess
from pathlib import Path

def run_command(cmd, description):
    """Run a command and handle errors."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e.stderr}")
        return False

def main():
    """Main setup function."""
    print("🚀 Repository Analyzer Development Setup")
    print("=" * 50)

    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ required")
        sys.exit(1)

    print(f"✅ Python {sys.version.split()[0]} detected")

    # Create virtual environment if it doesn't exist
    if not Path("venv").exists():
        print("🔄 Creating virtual environment...")
        if not run_command("python -m venv venv", "Virtual environment creation"):
            sys.exit(1)
    else:
        print("✅ Virtual environment already exists")

    # Activate virtual environment and install dependencies
    activate_cmd = "source venv/bin/activate" if os.name != 'nt' else "venv\\Scripts\\activate"

    commands = [
        (f"{activate_cmd} && pip install --upgrade pip", "Upgrading pip"),
        (f"{activate_cmd} && pip install -e .", "Installing repo analyzer"),
        (f"{activate_cmd} && pip install pytest pytest-cov black isort flake8 mypy", "Installing dev dependencies"),
    ]

    for cmd, desc in commands:
        if not run_command(cmd, desc):
            print("❌ Setup failed")
            sys.exit(1)

    # Create .env file if it doesn't exist
    if not Path(".env").exists():
        print("🔄 Creating .env file...")
        try:
            with open(".env.example", "r") as src, open(".env", "w") as dst:
                dst.write(src.read())
            print("✅ .env file created from template")
            print("⚠️  Please edit .env file and add your API keys")
        except Exception as e:
            print(f"❌ Failed to create .env file: {e}")
    else:
        print("✅ .env file already exists")

    # Run system check
    check_cmd = f"{activate_cmd} && repo-analyzer check"
    run_command(check_cmd, "Running system check")

    print("\n🎉 Development setup complete!")
    print("\nNext steps:")
    print("1. Edit .env file and add your ANTHROPIC_API_KEY")
    print("2. Activate virtual environment:")
    if os.name == 'nt':
        print("   venv\\Scripts\\activate")
    else:
        print("   source venv/bin/activate")
    print("3. Run tests: make test")
    print("4. Try analysis: repo-analyzer --repo . --verbose")

if __name__ == "__main__":
    main()

# FilePath: scripts/install.sh

#!/bin/bash
# Installation script for repo analyzer

set -e

echo "🚀 Installing Repository Analyzer"
echo "=================================="

# Check if Python 3.8+ is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed"
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
REQUIRED_VERSION="3.8"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo "❌ Python $REQUIRED_VERSION or higher is required (found $PYTHON_VERSION)"
    exit 1
fi

echo "✅ Python $PYTHON_VERSION detected"

# Check if Git is available
if ! command -v git &> /dev/null; then
    echo "❌ Git is required but not installed"
    exit 1
fi

echo "✅ Git detected"

# Install the package
echo "🔄 Installing repo-analyzer..."
pip3 install -e .

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "🔄 Creating .env file..."
    cp .env.example .env
    echo "✅ .env file created"
    echo "⚠️  Please edit .env file and add your ANTHROPIC_API_KEY"
else
    echo "✅ .env file already exists"
fi

# Run system check
echo "🔄 Running system check..."
repo-analyzer check

echo ""
echo "🎉 Installation complete!"
echo ""
echo "Next steps:"
echo "1. Add your ANTHROPIC_API_KEY to the .env file"
echo "2. Try: repo-analyzer --repo /path/to/your/repo"
echo "3. Or run: repo-analyzer --help for more options"

# FilePath: requirements-dev.txt

# Development dependencies
pytest>=7.0.0
pytest-cov>=4.0.0
black>=22.0.0
isort>=5.10.0
flake8>=5.0.0
mypy>=0.991
pre-commit>=2.20.0

# Documentation
sphinx>=5.0.0
sphinx-rtd-theme>=1.0.0

# Testing utilities
factory-boy>=3.2.0
freezegun>=1.2.0

