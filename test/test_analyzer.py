# FilePath: test/test_analyzer.py

import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch

from repo_analyzer.core.analyzer import RepositoryAnalyzer
from repo_analyzer.llm.factory import LLMFactory


class TestRepositoryAnalyzer:
    """Test cases for RepositoryAnalyzer."""

    @pytest.fixture
    def temp_repo(self):
        """Create a temporary repository for testing."""
        temp_dir = Path(tempfile.mkdtemp())

        # Create some test files
        (temp_dir / "main.py").write_text("""
# FilePath: main.py

def hello_world():
    print("Hello, World!")

if __name__ == "__main__":
    hello_world()
""")

        (temp_dir / "requirements.txt").write_text("""
# FilePath: requirements.txt

flask==2.0.1
requests==2.25.1
""")

        (temp_dir / ".env.example").write_text("""
# FilePath: .env.example

DATABASE_URL=postgresql://localhost/myapp
SECRET_KEY=your_secret_key_here
DEBUG=True
""")

        yield temp_dir

        # Cleanup
        shutil.rmtree(temp_dir)

    def test_analyzer_initialization(self):
        """Test analyzer initialization."""
        with patch("config.settings.Settings.ANTHROPIC_API_KEY", "test_key"):
            analyzer = RepositoryAnalyzer(llm_provider="claude")
            assert analyzer.llm_provider == "claude"
            assert analyzer.model is not None

    def test_get_repository_overview(self, temp_repo):
        """Test getting repository overview."""
        with patch("config.settings.Settings.ANTHROPIC_API_KEY", "test_key"):
            analyzer = RepositoryAnalyzer(llm_provider="claude")

            overview = analyzer.get_repository_overview(str(temp_repo))

            assert overview["name"] == temp_repo.name
            assert overview["file_count"] > 0
            assert "path" in overview

    @patch("repo_analyzer.llm.claude.ClaudeProvider.generate_response")
    def test_analyze_chunk_independently(self, mock_generate, temp_repo):
        """Test independent chunk analysis."""
        mock_generate.return_value = "Test analysis result"

        with patch("config.settings.Settings.ANTHROPIC_API_KEY", "test_key"):
            analyzer = RepositoryAnalyzer(llm_provider="claude")

            result = analyzer._analyze_chunk_independently(
                "test_repo", "test content", 1, 1
            )

            assert result == "Test analysis result"
            mock_generate.assert_called_once()


# FilePath: tests/test_file_processor.py

import pytest
import tempfile
import shutil
from pathlib import Path

from repo_analyzer.core.file_processor import FileProcessor
from config.languages import LanguageConfig


class TestFileProcessor:
    """Test cases for FileProcessor."""

    @pytest.fixture
    def temp_repo(self):
        """Create a temporary repository with various file types."""
        temp_dir = Path(tempfile.mkdtemp())

        # Create various file types
        (temp_dir / "main.py").write_text("print('Hello')")
        (temp_dir / "app.js").write_text("console.log('Hello');")
        (temp_dir / "README.md").write_text("# Test Repo")
        (temp_dir / "package.json").write_text('{"name": "test"}')
        (temp_dir / ".gitignore").write_text("*.pyc")

        # Create a subdirectory with files
        sub_dir = temp_dir / "src"
        sub_dir.mkdir()
        (sub_dir / "utils.py").write_text("def helper(): pass")

        # Create files that should be ignored
        (temp_dir / "node_modules").mkdir()
        (temp_dir / "node_modules" / "package.js").write_text("ignored")

        yield temp_dir
        shutil.rmtree(temp_dir)

    def test_get_all_source_files(self, temp_repo):
        """Test getting all source files."""
        processor = FileProcessor()
        files = processor.get_all_source_files(temp_repo)

        # Should find Python, JS, MD, and JSON files
        file_names = [f.name for f in files]
        assert "main.py" in file_names
        assert "app.js" in file_names
        assert "README.md" in file_names
        assert "package.json" in file_names

        # Should ignore files in node_modules
        assert "package.js" not in file_names

    def test_prioritize_files(self, temp_repo):
        """Test file prioritization."""
        processor = FileProcessor()
        all_files = processor.get_all_source_files(temp_repo)
        prioritized = processor.prioritize_files(all_files)

        # Priority files should come first
        priority_names = {f.name for f in prioritized[:3]}
        assert "main.py" in priority_names or "package.json" in priority_names

    def test_should_ignore_file(self, temp_repo):
        """Test file ignoring logic."""
        processor = FileProcessor()

        assert processor._should_ignore_file(temp_repo / "node_modules" / "test.js")
        assert processor._should_ignore_file(temp_repo / "test.pyc")
        assert not processor._should_ignore_file(temp_repo / "main.py")
        assert not processor._should_ignore_file(temp_repo / ".env.example")


# FilePath: tests/conftest.py

import pytest
import os
from pathlib import Path


@pytest.fixture(scope="session")
def test_env():
    """Setup test environment variables."""
    os.environ["ANTHROPIC_API_KEY"] = "test_key_for_testing"
    yield
    # Cleanup if needed


@pytest.fixture
def sample_code():
    """Sample code content for testing."""
    return '''
def calculate_fibonacci(n):
    """Calculate fibonacci number."""
    if n <= 1:
        return n
    return calculate_fibonacci(n-1) + calculate_fibonacci(n-2)

class MathUtils:
    @staticmethod
    def add(a, b):
        return a + b

    @staticmethod
    def multiply(a, b):
        return a * b
'''


@pytest.fixture
def sample_env_content():
    """Sample .env file content for testing."""
    return """
# Database configuration
DATABASE_URL=postgresql://localhost:5432/testdb
DB_HOST=localhost
DB_PORT=5432
DB_NAME=testdb

# API keys
SECRET_KEY=super_secret_key_here
JWT_SECRET=jwt_secret_key
API_KEY=test_api_key

# Application settings
DEBUG=True
LOG_LEVEL=INFO
PORT=8000
"""
