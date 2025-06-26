<!-- FilePath: README.md -->

# Repository Analyzer

An AI-powered repository analysis tool that provides comprehensive technical analysis of codebases using advanced language models.

## Features

🤖 **AI-Powered Analysis**: Uses Claude (and extensible to other LLMs) for intelligent code analysis
📊 **Comprehensive Reports**: Generates detailed 10-section technical analysis covering architecture, security, performance, and more
🌐 **Multi-Language Support**: Supports 50+ programming languages and frameworks
🔧 **Smart Compression**: Intelligently compresses code while preserving important context
📁 **Environment Analysis**: Automatically detects and analyzes configuration files
🏗️ **Git Integration**: Extracts repository metadata and supports branch-specific analysis
⚡ **Conversation Mode**: Interactive analysis for specific questions about your codebase
🎯 **Rate Limiting**: Built-in rate limiting to respect API constraints

## Installation

### Prerequisites

- Python 3.8 or higher
- Git (for repository cloning)
- Anthropic API key (for Claude)

### Install from Source

```bash
git clone https://github.com/yuyudhan/repo_analyser.git
cd repo_analyser
pip install -e .
```

### Environment Setup

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit `.env` and add your API key:

```env
ANTHROPIC_API_KEY=your_api_key_here
```

## Usage

### Basic Analysis

Analyze a local repository:

```bash
repo-analyzer --repo /path/to/your/repo
```

Analyze a remote repository:

```bash
repo-analyzer --repo https://github.com/user/repository.git
```

### Advanced Options

```bash
repo-analyzer \
  --repo https://github.com/user/repo.git \
  --branch develop \
  --model claude-3-5-sonnet-20241022 \
  --files-per-chunk 10 \
  --use-compression \
  --max-indentation 4 \
  --verbose
```

### Conversation Mode

Interactive analysis for specific questions:

```bash
repo-analyzer --repo /path/to/repo --conversation-mode
```

### Command Line Options

- `--repo`: Repository path (local) or URL (remote) **[Required]**
- `--branch`: Git branch to analyze (optional)
- `--llm`: LLM provider (`claude`) - extensible
- `--model`: Specific model to use (default: `claude-3-5-sonnet-20241022`)
- `--output-dir`: Custom output directory
- `--files-per-chunk`: Files to process per chunk (default: 8)
- `--use-compression / --no-compression`: Enable/disable smart code compression
- `--max-indentation`: Maximum indentation level to preserve (default: 3)
- `--processing-delay`: Delay between API calls in seconds (default: 2.0)
- `--conversation-mode`: Enable interactive mode
- `--verbose`: Enable detailed logging

## Configuration

### Settings

Key configuration options in `config/settings.py`:

```python
# File processing
USE_ENTIRE_FILES = True          # Process entire files vs chunks
USE_SMART_COMPRESSION = True     # Enable intelligent code compression
MAX_INDENTATION_LEVEL = 3        # Preserve code up to N indentation levels
FILES_PER_CHUNK = 8             # Files processed per API call

# LLM settings
DEFAULT_MODEL = "claude-3-5-sonnet-20241022"
MAX_TOKENS = 8000
TEMPERATURE = 0.1

# Rate limiting
PROCESSING_DELAY = 2.0          # Seconds between API calls
```

### Rate Limiting

Configure rate limits in `config/rate_limits.py`:

```python
RATE_LIMITS = {
    "claude": RateLimitConfig(
        requests_per_minute=50,
        burst_limit=5,
        retry_after=2.0,
        max_retries=3
    )
}
```

### Language Support

Supports 50+ languages including:

- **Web**: JavaScript, TypeScript, React, Vue, Angular
- **Backend**: Python, Java, Go, Rust, C++, C#, PHP, Ruby
- **Mobile**: Swift, Kotlin, Dart
- **Data**: SQL, Python (NumPy/Pandas), R
- **DevOps**: Docker, Kubernetes, Terraform
- **Configs**: JSON, YAML, TOML, XML, INI

## Output

### Generated Reports

The tool generates comprehensive reports in the `repo_analysis/{repo_name}/` directory:

- `{timestamp}_{repo_name}_analysis.md` - Timestamped full analysis
- `{repo_name}_latest.md` - Latest analysis (for easy access)
- `{timestamp}_{repo_name}_progress.md` - Analysis progress log
- `{timestamp}_{repo_name}_summary.json` - JSON summary for automation

### Report Sections

Each analysis includes 10 detailed sections:

1. **Repository Overview & Metrics** - Purpose, tech stack, architecture pattern
2. **Technology Stack Analysis** - Languages, frameworks, dependencies
3. **Architectural Analysis** - Design patterns, data flow, API design
4. **Business Domain & Functionality** - Core logic, features, workflows
5. **Implementation Deep Dive** - Entry points, modules, error handling
6. **Infrastructure & Deployment** - Build process, deployment, monitoring
7. **Development Workflow** - Code organization, quality, version control
8. **Security & Compliance** - Authentication, authorization, data protection
9. **Performance & Optimization** - Caching, scalability, resource management
10. **Maintenance & Evolution** - Technical debt, extensibility, upgrade paths

## System Check

Verify your setup:

```bash
repo-analyzer check --check-all
```

## Examples

### Analyze a Popular Open Source Project

```bash
repo-analyzer --repo https://github.com/microsoft/vscode.git --verbose
```

### Analyze Specific Branch

```bash
repo-analyzer --repo /local/project --branch feature/new-api
```

### Interactive Analysis

```bash
repo-analyzer --repo https://github.com/user/repo.git --conversation-mode
```

Example conversation:

```
🤔 What would you like to know about this repository?
> What security measures are implemented?

🤖 Analyzing...
💡 The repository implements several security measures including:
- JWT-based authentication with refresh tokens
- Input validation using Joi schemas
- SQL injection prevention through parameterized queries
- CORS configuration for cross-origin requests
...
```

## Architecture

```
repo_analyzer/
├── config/           # Configuration and settings
├── src/repo_analyzer/
│   ├── core/         # Core analysis logic
│   ├── llm/          # LLM provider abstractions
│   ├── utils/        # Utilities and helpers
│   └── output/       # Report generation
└── tests/            # Test suite
```

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Make your changes and add tests
4. Run tests: `python -m pytest`
5. Commit your changes: `git commit -am 'Add some feature'`
6. Push to the branch: `git push origin feature/your-feature`
7. Submit a pull request

## Development Setup

```bash
# Install in development mode
pip install -e ".[dev]"

# Run tests
python -m pytest

# Run linting
flake8 src/

# Type checking
mypy src/
```

## Troubleshooting

### Common Issues

**API Key Issues**

```bash
❌ Please set ANTHROPIC_API_KEY environment variable
```

Solution: Add your Anthropic API key to the `.env` file

**Git Not Found**

```bash
❌ Git not installed
```

Solution: Install Git and ensure it's in your system PATH

**Rate Limiting**

```bash
⚠️ Rate limit exceeded, waiting...
```

Solution: The tool automatically handles rate limiting. For faster processing, check your API plan limits.

### Debug Mode

Enable detailed logging:

```bash
repo-analyzer --repo /path/to/repo --verbose
```

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Changelog

### v1.0.0

- Initial release with Claude integration
- Comprehensive 10-section analysis
- Multi-language support
- Smart code compression
- Conversation mode
- Rate limiting and error handling

## Roadmap

- [ ] OpenAI GPT integration
- [ ] Web interface for analysis results
- [ ] API endpoint for programmatic access
- [ ] Integration with CI/CD pipelines
- [ ] Custom analysis templates
- [ ] Team collaboration features

