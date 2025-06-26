# FilePath: config/languages.py

from typing import Dict, Set, List
from pathlib import Path


class LanguageConfig:
    """Configuration for supported languages and file types."""

    # Source file extensions for different languages
    SOURCE_EXTENSIONS: Set[str] = {
        ".py",
        ".pyi",
        ".pyx",
        ".js",
        ".jsx",
        ".ts",
        ".tsx",
        ".mjs",
        ".cjs",
        ".go",
        ".mod",
        ".rs",
        ".toml",
        ".java",
        ".kt",
        ".scala",
        ".groovy",
        ".clj",
        ".c",
        ".cpp",
        ".cc",
        ".cxx",
        ".h",
        ".hpp",
        ".hxx",
        ".cs",
        ".vb",
        ".fs",
        ".fsx",
        ".php",
        ".rb",
        ".swift",
        ".dart",
        ".lua",
        ".sql",
        ".psql",
        ".mysql",
        ".sqlite",
        ".pl",
        ".pm",
        ".prolog",
        ".d",
        ".m",
        ".mm",
        ".json",
        ".yaml",
        ".yml",
        ".ini",
        ".cfg",
        ".conf",
        ".xml",
        ".properties",
        ".env.example",
        ".plist",
        ".html",
        ".htm",
        ".css",
        ".scss",
        ".sass",
        ".less",
        ".styl",
        ".md",
        ".txt",
        ".rst",
        ".org",
        ".adoc",
        ".tex",
        ".dockerfile",
        ".sh",
        ".bash",
        ".zsh",
        ".fish",
        ".ps1",
        ".bat",
        ".cmd",
        ".makefile",
        ".tf",
        ".tfvars",
        ".hcl",
        ".nomad",
        ".cmake",
        ".in",
    }

    # High priority file names
    HIGH_PRIORITY_NAMES: Set[str] = {
        "main.py",
        "app.py",
        "server.py",
        "wsgi.py",
        "asgi.py",
        "manage.py",
        "setup.py",
        "pyproject.toml",
        "requirements.txt",
        "pipfile",
        "main.js",
        "app.js",
        "server.js",
        "index.js",
        "package.json",
        "main.ts",
        "app.ts",
        "server.ts",
        "index.ts",
        "main.go",
        "app.go",
        "server.go",
        "go.mod",
        "go.sum",
        "main.rs",
        "lib.rs",
        "server.rs",
        "cargo.toml",
        "cargo.lock",
        "main.java",
        "app.java",
        "application.java",
        "pom.xml",
        "build.gradle",
        "settings.gradle",
        "main.c",
        "main.cpp",
        "main.cc",
        "cmakelists.txt",
        "makefile",
        "appdelegate.swift",
        "mainactivity.java",
        "mainactivity.kt",
        "info.plist",
        "androidmanifest.xml",
        "dockerfile",
        "docker-compose.yml",
        "docker-compose.yaml",
        "webpack.config.js",
        "vite.config.js",
        "rollup.config.js",
        "tsconfig.json",
        "babel.config.js",
        ".babelrc",
        "readme.md",
        "readme.txt",
        "readme.rst",
        "changelog.md",
        "contributing.md",
        "license",
    }

    # High priority path patterns
    HIGH_PRIORITY_PATHS: Set[str] = {
        "main",
        "app",
        "server",
        "index",
        "entry",
        "bootstrap",
        "config",
        "configuration",
        "settings",
        "environment",
        "route",
        "router",
        "routes",
        "routing",
        "handler",
        "handlers",
        "controller",
        "controllers",
        "api",
        "apis",
        "endpoint",
        "endpoints",
        "service",
        "services",
        "model",
        "models",
        "schema",
        "schemas",
        "entity",
        "entities",
        "provider",
        "providers",
        "middleware",
        "interceptor",
        "core",
        "base",
        "common",
        "shared",
        "utils",
        "helpers",
    }

    # Important configuration files (no extension)
    IMPORTANT_NO_EXT: Set[str] = {
        "dockerfile",
        "makefile",
        "jenkinsfile",
        "procfile",
        "rakefile",
        "gulpfile",
        "gruntfile",
        "webpack",
        "license",
        "changelog",
        "authors",
        "contributors",
        "cmakelists.txt",
    }

    # Syntax highlighting mappings
    SYNTAX_HIGHLIGHTING: Dict[str, str] = {
        # Specific filenames
        "dockerfile": "dockerfile",
        "docker-compose.yml": "yaml",
        "docker-compose.yaml": "yaml",
        "makefile": "makefile",
        "jenkinsfile": "groovy",
        "procfile": "text",
        "package.json": "json",
        "tsconfig.json": "json",
        "webpack.config.js": "javascript",
        "jest.config.js": "javascript",
        ".eslintrc.json": "json",
        ".eslintrc.js": "javascript",
        "cargo.toml": "toml",
        "pyproject.toml": "toml",
        "go.mod": "go",
        "pom.xml": "xml",
        "build.gradle": "gradle",
        # Extensions
        ".rs": "rust",
        ".go": "go",
        ".py": "python",
        ".js": "javascript",
        ".mjs": "javascript",
        ".cjs": "javascript",
        ".ts": "typescript",
        ".jsx": "jsx",
        ".tsx": "tsx",
        ".java": "java",
        ".kt": "kotlin",
        ".scala": "scala",
        ".cpp": "cpp",
        ".cc": "cpp",
        ".cxx": "cpp",
        ".c": "c",
        ".h": "c",
        ".hpp": "cpp",
        ".cs": "csharp",
        ".php": "php",
        ".rb": "ruby",
        ".swift": "swift",
        ".dart": "dart",
        ".html": "html",
        ".css": "css",
        ".scss": "scss",
        ".sass": "sass",
        ".less": "less",
        ".vue": "vue",
        ".svelte": "svelte",
        ".json": "json",
        ".yaml": "yaml",
        ".yml": "yaml",
        ".toml": "toml",
        ".xml": "xml",
        ".sql": "sql",
        ".psql": "sql",
        ".mysql": "sql",
        ".sh": "bash",
        ".bash": "bash",
        ".zsh": "bash",
        ".fish": "fish",
        ".ps1": "powershell",
        ".bat": "batch",
        ".md": "markdown",
        ".rst": "rst",
        ".tex": "latex",
        ".ini": "ini",
        ".conf": "ini",
        ".env": "bash",
    }

    # File type descriptions
    FILE_TYPE_DESCRIPTIONS: Dict[str, str] = {
        # Configuration files
        "dockerfile": "Container build configuration",
        "docker-compose.yml": "Multi-container application definition",
        "docker-compose.yaml": "Multi-container application definition",
        "package.json": "Node.js project configuration and dependencies",
        "cargo.toml": "Rust project configuration and dependencies",
        "pyproject.toml": "Python project configuration and dependencies",
        "requirements.txt": "Python dependencies specification",
        "go.mod": "Go module definition and dependencies",
        "pom.xml": "Maven project configuration",
        "build.gradle": "Gradle build configuration",
        ".env.example": "Environment variables template",
        "tsconfig.json": "TypeScript compiler configuration",
        "webpack.config.js": "Webpack build configuration",
        "jest.config.js": "Jest testing framework configuration",
        ".eslintrc.json": "ESLint code quality configuration",
        ".prettierrc": "Prettier code formatting configuration",
        "makefile": "Build automation script",
        # Source code by extension
        ".rs": "Rust source code",
        ".go": "Go source code",
        ".py": "Python source code",
        ".js": "JavaScript source code",
        ".ts": "TypeScript source code",
        ".jsx": "React JavaScript component",
        ".tsx": "React TypeScript component",
        ".java": "Java source code",
        ".kt": "Kotlin source code",
        ".cpp": "C++ source code",
        ".c": "C source code",
        ".cs": "C# source code",
        ".php": "PHP source code",
        ".rb": "Ruby source code",
        ".swift": "Swift source code",
        ".dart": "Dart source code",
        ".scala": "Scala source code",
        # Web and markup
        ".html": "HTML markup",
        ".css": "CSS stylesheet",
        ".scss": "SASS stylesheet",
        ".sass": "SASS stylesheet",
        ".less": "LESS stylesheet",
        ".vue": "Vue.js component",
        ".svelte": "Svelte component",
        # Data and configuration
        ".json": "JSON data/configuration",
        ".yaml": "YAML configuration",
        ".yml": "YAML configuration",
        ".toml": "TOML configuration",
        ".xml": "XML data/configuration",
        ".ini": "INI configuration",
        ".conf": "Configuration file",
        ".env": "Environment variables",
        # Documentation
        ".md": "Markdown documentation",
        ".rst": "reStructuredText documentation",
        ".txt": "Plain text documentation",
        # Database and schema
        ".sql": "SQL database script",
        ".psql": "PostgreSQL script",
        ".mysql": "MySQL script",
        # Scripts and automation
        ".sh": "Shell script",
        ".bash": "Bash script",
        ".ps1": "PowerShell script",
        ".bat": "Batch script",
    }

    @classmethod
    def get_syntax_highlighting(cls, file_path: Path) -> str:
        """Get appropriate syntax highlighting for code blocks."""
        name = file_path.name.lower()
        suffix = file_path.suffix.lower()

        # Check specific filenames first
        if name in cls.SYNTAX_HIGHLIGHTING:
            return cls.SYNTAX_HIGHLIGHTING[name]

        # Check file extensions
        return cls.SYNTAX_HIGHLIGHTING.get(suffix, "text")

    @classmethod
    def get_file_type_description(cls, file_path: Path) -> str:
        """Get descriptive file type for better analysis context."""
        name = file_path.name.lower()
        suffix = file_path.suffix.lower()

        # Check specific filenames first
        if name in cls.FILE_TYPE_DESCRIPTIONS:
            return cls.FILE_TYPE_DESCRIPTIONS[name]

        # Check file extensions
        if suffix in cls.FILE_TYPE_DESCRIPTIONS:
            return cls.FILE_TYPE_DESCRIPTIONS[suffix]

        # Special patterns
        if "test" in name or "spec" in name:
            lang = suffix[1:] if suffix else "unknown"
            return f"Test file ({lang} language)"
        elif "config" in name or "conf" in name:
            fmt = suffix[1:] if suffix else "unknown"
            return f"Configuration file ({fmt} format)"
        elif name.startswith("."):
            fmt = suffix[1:] if suffix else "dotfile"
            return f"Hidden configuration file ({fmt})"

        lang = suffix[1:] if suffix else "no extension"
        return f"Source file ({lang})"

    @classmethod
    def is_priority_file(cls, file_path: Path) -> bool:
        """Check if a file should be prioritized."""
        file_name = file_path.name.lower()
        path_str = str(file_path).lower()

        return (
            file_name in cls.HIGH_PRIORITY_NAMES
            or any(pattern in path_str for pattern in cls.HIGH_PRIORITY_PATHS)
            or any(pattern in file_name for pattern in cls.HIGH_PRIORITY_PATHS)
        )
