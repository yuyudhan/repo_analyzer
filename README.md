# Repository Analyzer

AI-powered codebase analysis tool providing comprehensive technical assessment using large language models.

## Quick Start

```bash
# Local repository analysis
repo-analyzer analyze --repo /path/to/repo

# Remote repository analysis
repo-analyzer analyze --repo https://github.com/user/repo.git

# Developer perspective analysis with context
repo-analyzer analyze --repo /path/to/repo --mode developer --human-context "Fintech payment processing API with strict compliance requirements"

# Interactive conversation mode
repo-analyzer analyze --repo /path/to/repo --conversation-mode
```

## Installation & Environment Setup

### Prerequisites

- Python 3.8+
- Git
- Anthropic API key

### Install

```bash
git clone https://github.com/yuyudhan/repo_analyzer.git
cd repo_analyzer
pip install -e .
```

### Environment Configuration

Create `.env` file:

```bash
cp .env.example .env
```

Required environment variables:

```bash
# Required
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Optional
LOG_LEVEL=INFO                    # DEBUG, INFO, WARNING, ERROR
```

### System Verification

```bash
repo-analyzer check --check-all
```

## Command Reference

### analyze

Primary analysis command with full parameter set:

```bash
repo-analyzer analyze [OPTIONS]
```

#### Required Parameters

| Parameter | Type   | Description                                                  |
| --------- | ------ | ------------------------------------------------------------ |
| `--repo`  | string | Repository path (local directory) or URL (remote repository) |

#### Optional Parameters

| Parameter             | Type    | Default                    | Description                                            |
| --------------------- | ------- | -------------------------- | ------------------------------------------------------ |
| `--branch`            | string  | current                    | Git branch to checkout and analyze                     |
| `--mode`              | choice  | analysis                   | Analysis perspective: `analysis` \| `developer`        |
| `--llm`               | choice  | claude                     | LLM provider: `claude`                                 |
| `--model`             | string  | claude-3-5-sonnet-20241022 | Specific model identifier                              |
| `--output-dir`        | string  | ./repo_analysis            | Output directory for analysis results                  |
| `--files-per-chunk`   | integer | 8                          | Files processed per LLM request                        |
| `--use-compression`   | flag    | enabled                    | Enable smart code compression                          |
| `--no-compression`    | flag    | disabled                   | Disable smart code compression                         |
| `--max-indentation`   | integer | 3                          | Maximum indentation level preserved during compression |
| `--processing-delay`  | float   | 2.0                        | Delay between API calls (seconds)                      |
| `--human-context`     | string  | none                       | Additional context for enhanced analysis quality       |
| `--conversation-mode` | flag    | disabled                   | Enable interactive analysis mode                       |
| `--verbose`           | flag    | disabled                   | Enable debug-level logging                             |

#### Analysis Modes

- **analysis**: Third-party technical assessment perspective
- **developer**: Internal team perspective explaining design decisions

#### Examples

```bash
# Full parameter analysis
repo-analyzer analyze \
  --repo https://github.com/microsoft/vscode.git \
  --branch main \
  --mode developer \
  --model claude-3-5-sonnet-20241022 \
  --files-per-chunk 10 \
  --use-compression \
  --max-indentation 4 \
  --processing-delay 1.5 \
  --human-context "Enterprise IDE with performance and extensibility requirements" \
  --output-dir ./analysis_results \
  --verbose

# Conversation mode analysis
repo-analyzer analyze \
  --repo /path/to/local/repo \
  --conversation-mode \
  --human-context "Legacy system migration with performance constraints"
```

### check

System verification command:

```bash
repo-analyzer check [OPTIONS]
```

| Parameter     | Type | Default  | Description                                             |
| ------------- | ---- | -------- | ------------------------------------------------------- |
| `--check-all` | flag | disabled | Perform comprehensive system and API connectivity tests |

### version

Display version information:

```bash
repo-analyzer version
```

## Configuration

### Core Settings

| Setting                 | Type | Default | Description                                    |
| ----------------------- | ---- | ------- | ---------------------------------------------- |
| `CHUNK_LINES`           | int  | 150     | Lines per code chunk for processing            |
| `FILES_PER_CHUNK`       | int  | 8       | Files processed per LLM request                |
| `USE_ENTIRE_FILES`      | bool | true    | Process complete files vs. chunked processing  |
| `USE_SMART_COMPRESSION` | bool | true    | Enable intelligent code compression            |
| `MAX_FILE_SIZE`         | int  | 15000   | Maximum file size for processing (lines)       |
| `MAX_INDENTATION_LEVEL` | int  | 3       | Indentation depth preserved during compression |
| `INDENTATION_SPACES`    | int  | 4       | Spaces per indentation level                   |

### LLM Configuration

| Setting         | Type   | Default                    | Description                              |
| --------------- | ------ | -------------------------- | ---------------------------------------- |
| `DEFAULT_LLM`   | string | claude                     | Primary LLM provider                     |
| `DEFAULT_MODEL` | string | claude-3-5-sonnet-20241022 | Default model identifier                 |
| `MAX_TOKENS`    | int    | 8000                       | Maximum tokens per request               |
| `TEMPERATURE`   | float  | 0.1                        | LLM temperature for deterministic output |

### Rate Limiting

| Provider  | Requests/Min | Burst Limit | Retry After | Max Retries |
| --------- | ------------ | ----------- | ----------- | ----------- |
| `claude`  | 50           | 5           | 2.0s        | 3           |
| `openai`  | 60           | 10          | 1.0s        | 3           |
| `default` | 30           | 3           | 3.0s        | 2           |

### Processing Configuration

| Setting                   | Type  | Default | Description                   |
| ------------------------- | ----- | ------- | ----------------------------- |
| `PROCESSING_DELAY`        | float | 2.0     | Inter-request delay (seconds) |
| `MAX_CONCURRENT_REQUESTS` | int   | 3       | Concurrent LLM requests       |
| `CLONE_TIMEOUT`           | int   | 300     | Git clone timeout (seconds)   |
| `GIT_COMMAND_TIMEOUT`     | int   | 30      | Git command timeout (seconds) |

## Language Support

### Supported File Extensions

**Programming Languages**: `.py`, `.js`, `.ts`, `.jsx`, `.tsx`, `.go`, `.rs`, `.java`, `.kt`, `.scala`, `.cpp`, `.c`, `.cs`, `.php`, `.rb`, `.swift`, `.dart`, `.lua`, `.sql`

**Web Technologies**: `.html`, `.css`, `.scss`, `.sass`, `.less`, `.vue`, `.svelte`

**Configuration**: `.json`, `.yaml`, `.yml`, `.toml`, `.xml`, `.ini`, `.conf`, `.env`

**Documentation**: `.md`, `.rst`, `.txt`, `.adoc`, `.tex`

**Build/Deploy**: `Dockerfile`, `docker-compose.yml`, `Makefile`, `.tf`, `.hcl`, `CMakeLists.txt`

**Scripts**: `.sh`, `.bash`, `.ps1`, `.bat`, `.fish`

### Priority File Detection

High-priority files automatically receive enhanced analysis:

**Entry Points**: `main.py`, `app.py`, `server.py`, `index.js`, `main.go`, `lib.rs`

**Configuration**: `package.json`, `pyproject.toml`, `go.mod`, `Cargo.toml`, `pom.xml`, `build.gradle`

**Documentation**: `README.md`, `CHANGELOG.md`, `CONTRIBUTING.md`

**Infrastructure**: `Dockerfile`, `docker-compose.yml`, `Makefile`, `webpack.config.js`

## Output Structure

### Generated Reports

```
repo_analysis/
└── {repository_name}/
    ├── {timestamp}_{repo_name}_analysis.md     # Complete technical analysis
    ├── {repo_name}_latest.md                   # Latest analysis (symlink)
    ├── {timestamp}_{repo_name}_progress.md     # Processing log
    └── {timestamp}_{repo_name}_summary.json    # Structured analysis data
```

### Analysis Sections

Each report contains 10-section technical analysis:

1. **Repository Purpose** - Technical goals, problem statement, system requirements
2. **Overview & Metrics** - Quantitative assessment, code organization, health indicators
3. **Technology Stack** - Language analysis, framework evaluation, dependency assessment
4. **Architecture** - Design patterns, component interactions, scalability analysis
5. **Business Domain** - Functional capabilities, domain logic, workflow implementation
6. **Implementation** - Code quality, algorithms, integration patterns, testing strategy
7. **Infrastructure** - Deployment strategy, environment management, operational considerations
8. **Development Workflow** - Process analysis, tooling, collaboration patterns
9. **Security & Compliance** - Security implementation, access control, vulnerability assessment
10. **Performance & Optimization** - Performance characteristics, bottleneck analysis, scaling strategy
11. **Maintenance & Evolution** - Technical debt, maintainability, future roadmap

## Architecture

```
repo_analyzer/
├── config/
│   ├── settings.py           # Core configuration management
│   ├── rate_limits.py        # LLM provider rate limiting
│   └── languages.py          # Language detection and prioritization
├── src/repo_analyzer/
│   ├── cli.py               # Command-line interface
│   ├── core/
│   │   ├── analyzer.py      # Main orchestration logic
│   │   ├── conversation_analyzer.py  # Technical analysis mode
│   │   ├── developer_explanation.py # Developer perspective mode
│   │   ├── file_processor.py        # Code processing and compression
│   │   ├── git_handler.py           # Repository management
│   │   └── env_extractor.py         # Environment configuration analysis
│   ├── llm/
│   │   ├── factory.py       # LLM provider abstraction
│   │   └── claude.py        # Anthropic Claude integration
│   ├── utils/
│   │   └── logging_utils.py # Logging configuration
│   └── output/
│       └── report_generator.py # Report formatting and output
└── tests/                    # Test suite
```

## Integration

### CI/CD Pipeline

```yaml
# GitHub Actions example
- name: Repository Analysis
  run: |
    repo-analyzer analyze \
      --repo ${{ github.workspace }} \
      --branch ${{ github.ref_name }} \
      --output-dir ./analysis \
      --human-context "CI/CD analysis for ${{ github.repository }}"
```

### Programmatic Usage

```python
from repo_analyzer.core.analyzer import RepositoryAnalyzer

analyzer = RepositoryAnalyzer(llm_provider="claude")
results = analyzer.analyze_repository(
    repo_path="/path/to/repo",
    analysis_mode="developer",
    human_context="API service with microservices architecture"
)
```

## Troubleshooting

### Rate Limiting

```
⚠️ Rate limit exceeded, waiting...
```

**Solution**: Tool automatically handles rate limiting. Check API plan limits for faster processing.

### API Authentication

```
❌ Please set ANTHROPIC_API_KEY environment variable
```

**Solution**: Configure API key in `.env` file.

### Git Repository Access

```
❌ Repository path does not exist: /path/to/repo
```

**Solution**: Verify repository path exists and is accessible.

### Memory Issues

```
❌ Analysis failed: Memory allocation error
```

**Solution**: Reduce `--files-per-chunk` parameter or enable `--use-compression`.

## License

MIT License - see [LICENSE](LICENSE) file for details.

