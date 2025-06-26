# FilePath: src/repo_analyzer/core/conversation_analyzer.py

import time
from typing import Dict, List
from config.settings import Settings
from config.rate_limits import rate_limit_manager
from ..utils.logging_utils import get_logger


class ConversationAnalyzer:
    """
    Generates comprehensive repository analysis through conversational prompts.
    Each section is analyzed separately for deeper insights.
    """

    def __init__(self, llm_provider):
        self.logger = get_logger(__name__)
        self.llm = llm_provider
        self.conversation_context = []

    def generate_comprehensive_analysis(
        self,
        repo_name: str,
        chunk_analyses: List[str],
        git_info: Dict,
        env_configs: Dict,
    ) -> str:
        """
        Generate comprehensive analysis through conversational approach.
        Each section is analyzed separately for deeper insights.
        """
        self.logger.info("Starting conversational analysis generation...")

        # Build base context
        base_context = self._build_base_context(
            repo_name, chunk_analyses, git_info, env_configs
        )

        # Define analysis sections
        sections = [
            ("purpose", "Purpose of this repository"),
            ("overview", "Repository Overview & Metrics"),
            ("technology", "Technology Stack Analysis"),
            ("architecture", "Architectural Analysis"),
            ("business", "Business Domain & Functionality"),
            ("implementation", "Implementation Deep Dive"),
            ("infrastructure", "Infrastructure & Deployment"),
            ("workflow", "Development Workflow"),
            ("security", "Security & Compliance"),
            ("performance", "Performance & Optimization"),
            ("maintenance", "Maintenance & Evolution"),
        ]

        # Generate each section through conversation
        section_results = {}
        for section_key, section_title in sections:
            self.logger.info(f"Analyzing section: {section_title}")

            try:
                # Apply rate limiting
                rate_limit_manager.wait_if_needed("claude")

                section_analysis = self._analyze_section(
                    section_key, section_title, base_context
                )
                section_results[section_key] = section_analysis

                # Add small delay between sections
                time.sleep(Settings.PROCESSING_DELAY)

            except Exception as e:
                self.logger.error(f"Error analyzing {section_title}: {str(e)}")
                section_results[section_key] = (
                    f"Error analyzing {section_title}: {str(e)}"
                )

        # Generate final synthesis
        return self._synthesize_final_report(repo_name, section_results)

    def _build_base_context(
        self,
        repo_name: str,
        chunk_analyses: List[str],
        git_info: Dict,
        env_configs: Dict,
    ) -> str:
        """Build the base context that will be used across all section analyses."""

        # Combine chunk analyses
        combined_analysis = "\n\n---CHUNK SEPARATOR---\n\n".join(
            [f"CHUNK {i + 1}:\n{analysis}" for i, analysis in enumerate(chunk_analyses)]
        )

        # Environment summary
        env_summary = self._summarize_env_configs(env_configs)

        # Git summary
        git_summary = self._summarize_git_info(git_info)

        base_context = f"""
REPOSITORY: {repo_name}

GIT INFORMATION:
{git_summary}

ENVIRONMENT CONFIGURATION:
{env_summary}

DETAILED CODE ANALYSIS:
{combined_analysis}
"""
        return base_context

    def _analyze_section(
        self, section_key: str, section_title: str, base_context: str
    ) -> str:
        """Analyze a specific section with targeted prompts."""

        section_prompts = {
            "purpose": self._get_purpose_prompt(),
            "overview": self._get_overview_prompt(),
            "technology": self._get_technology_prompt(),
            "architecture": self._get_architecture_prompt(),
            "business": self._get_business_prompt(),
            "implementation": self._get_implementation_prompt(),
            "infrastructure": self._get_infrastructure_prompt(),
            "workflow": self._get_workflow_prompt(),
            "security": self._get_security_prompt(),
            "performance": self._get_performance_prompt(),
            "maintenance": self._get_maintenance_prompt(),
        }

        section_prompt = section_prompts.get(section_key, "")

        full_prompt = f"""
{base_context}

ANALYSIS TASK: {section_title}

{section_prompt}

REQUIREMENTS:
- Provide specific, actionable insights based on actual code evidence
- Use technical terminology appropriate for CTOs and senior developers
- Include concrete examples with file names, functions, or configurations
- Identify specific opportunities, risks, or recommendations
- Keep response detailed but focused (not verbose)
- Structure with clear subheadings for readability
"""

        return self.llm.generate_response(full_prompt)

    def _get_purpose_prompt(self) -> str:
        return """
Analyze the PURPOSE and CORE MISSION of this repository:

**Core Questions to Answer:**
- What is the primary business purpose this codebase serves?
- What problems does it solve and for whom?
- Is this a service, library, application, or infrastructure component?
- What are the key value propositions and unique features?
- How does this fit into a larger ecosystem or business strategy?

**Evidence to Look For:**
- README files, documentation, and project descriptions
- API endpoints and their business functions
- Database schemas and data models that reveal business logic
- Integration points with external services
- Configuration files that show deployment contexts

**Deliverable:**
Provide a clear, executive-level summary of what this repository does and why it exists.
"""

    def _get_overview_prompt(self) -> str:
        return """
Create a comprehensive REPOSITORY OVERVIEW & METRICS analysis:

**Metrics to Calculate:**
- Total lines of code by language
- Number of files, modules, and packages
- Complexity indicators (number of classes, functions, endpoints)
- Configuration files and their purposes
- External dependencies and integrations

**Structure Analysis:**
- Project organization and folder hierarchy
- Naming conventions and code organization patterns
- Entry points and main execution flows
- Build and deployment artifacts

**Health Indicators:**
- Code organization quality
- Documentation coverage
- Configuration management approach
- Development setup complexity

**Deliverable:**
Provide quantitative metrics and qualitative assessment of repository health and organization.
"""

    def _get_technology_prompt(self) -> str:
        return """
Conduct deep TECHNOLOGY STACK ANALYSIS:

**Technology Identification:**
- Programming languages with versions and usage patterns
- Frameworks and libraries with specific versions
- Database technologies and data storage solutions
- Message queues, caching, and middleware technologies
- Build tools, package managers, and development tools

**Technology Choices Assessment:**
- Why these technologies were likely chosen
- How technologies integrate and work together
- Modern vs legacy technology usage
- Technology stack maturity and ecosystem support

**Dependency Analysis:**
- Critical dependencies and their purposes
- Potential security vulnerabilities in dependencies
- Update strategies and dependency management approach
- License implications and compliance considerations

**Deliverable:**
Comprehensive technology inventory with strategic assessment of choices and implications.
"""

    def _get_architecture_prompt(self) -> str:
        return """
Perform detailed ARCHITECTURAL ANALYSIS:

**System Architecture:**
- Overall system design patterns (microservices, monolith, modular, etc.)
- Component interactions and data flow
- Service boundaries and responsibility separation
- Integration patterns and communication protocols

**Code Architecture:**
- Design patterns implementation (MVC, Repository, Factory, etc.)
- Abstraction layers and separation of concerns
- Module dependencies and coupling analysis
- Error handling and logging strategies

**Data Architecture:**
- Database design and schema patterns
- Data access patterns and ORM usage
- Caching strategies and data flow
- Data validation and transformation approaches

**Scalability & Extensibility:**
- How the architecture supports scaling
- Extension points and plugin mechanisms
- Configuration and customization capabilities

**Deliverable:**
Architectural assessment with strengths, weaknesses, and evolution recommendations.
"""

    def _get_business_prompt(self) -> str:
        return """
Analyze BUSINESS DOMAIN & FUNCTIONALITY:

**Business Logic Analysis:**
- Core business processes and workflows
- Domain models and business entities
- Business rules and validation logic
- User roles and permission systems

**Functional Capabilities:**
- Key features and user journeys
- API capabilities and external interfaces
- Data processing and transformation functions
- Reporting and analytics capabilities

**Business Value:**
- Revenue generation or cost savings mechanisms
- Competitive advantages in implementation
- User experience and interface quality
- Business process automation and efficiency

**Domain Knowledge:**
- Industry-specific requirements and compliance
- Business terminology and concepts in code
- Integration with business systems and processes

**Deliverable:**
Business-focused analysis showing how technology supports business objectives.
"""

    def _get_implementation_prompt(self) -> str:
        return """
Conduct IMPLEMENTATION DEEP DIVE:

**Code Quality Analysis:**
- Coding standards and consistency
- Error handling and edge case management
- Input validation and data sanitization
- Code reusability and modularity

**Algorithm & Logic Analysis:**
- Key algorithms and their efficiency
- Complex business logic implementations
- Data processing and transformation logic
- Performance-critical code sections

**Integration Implementation:**
- External API integrations and error handling
- Database interaction patterns
- Message queue and async processing
- File and data import/export mechanisms

**Testing & Quality Assurance:**
- Test coverage and testing strategies
- Quality gates and validation processes
- Debugging and monitoring capabilities

**Deliverable:**
Technical assessment of implementation quality with specific improvement opportunities.
"""

    def _get_infrastructure_prompt(self) -> str:
        return """
Analyze INFRASTRUCTURE & DEPLOYMENT:

**Deployment Strategy:**
- Containerization and orchestration setup
- Environment configuration management
- Deployment pipelines and automation
- Rollback and recovery mechanisms

**Infrastructure as Code:**
- Infrastructure definition and management
- Environment provisioning and scaling
- Resource allocation and optimization
- Cost management and efficiency

**Operational Concerns:**
- Monitoring and observability setup
- Logging and debugging capabilities
- Health checks and service discovery
- Backup and disaster recovery

**Cloud & Platform Strategy:**
- Cloud provider usage and services
- Platform-specific optimizations
- Vendor lock-in considerations
- Multi-environment management

**Deliverable:**
Infrastructure assessment with deployment, scaling, and operational recommendations.
"""

    def _get_workflow_prompt(self) -> str:
        return """
Evaluate DEVELOPMENT WORKFLOW:

**Development Process:**
- Code organization and development patterns
- Build and compilation processes
- Testing and quality assurance workflows
- Code review and collaboration practices

**CI/CD Pipeline:**
- Continuous integration setup and stages
- Deployment automation and strategies
- Environment promotion and gating
- Release management and versioning

**Development Tools:**
- Development environment setup
- Build tools and automation
- Code generation and scaffolding
- Development productivity tools

**Team Collaboration:**
- Code sharing and modularity
- Documentation and knowledge management
- Developer onboarding considerations
- Maintenance and support workflows

**Deliverable:**
Development workflow analysis with productivity and quality improvement recommendations.
"""

    def _get_security_prompt(self) -> str:
        return """
Conduct SECURITY & COMPLIANCE analysis:

**Security Implementation:**
- Authentication and authorization mechanisms
- Input validation and sanitization
- SQL injection and XSS prevention
- Secure communication and data protection

**Access Control:**
- User management and role-based access
- API security and rate limiting
- Session management and token handling
- Privilege escalation prevention

**Data Protection:**
- Sensitive data handling and encryption
- Privacy and data retention policies
- Audit trails and compliance logging
- Backup security and access controls

**Vulnerability Assessment:**
- Common security vulnerabilities present
- Dependency security and update strategy
- Configuration security and hardening
- Potential attack vectors and mitigations

**Deliverable:**
Security assessment with specific vulnerabilities, compliance gaps, and remediation priorities.
"""

    def _get_performance_prompt(self) -> str:
        return """
Analyze PERFORMANCE & OPTIMIZATION:

**Performance Characteristics:**
- Response time and throughput analysis
- Resource utilization patterns
- Bottleneck identification and analysis
- Scalability limitations and constraints

**Optimization Strategies:**
- Caching implementation and effectiveness
- Database query optimization
- Memory management and garbage collection
- Network and I/O optimization

**Monitoring & Metrics:**
- Performance monitoring and alerting
- Key performance indicators tracking
- Resource usage monitoring
- Performance testing and benchmarking

**Scalability Planning:**
- Horizontal and vertical scaling capabilities
- Load balancing and distribution strategies
- Performance under high load scenarios
- Resource allocation and auto-scaling

**Deliverable:**
Performance analysis with specific bottlenecks, optimization opportunities, and scaling recommendations.
"""

    def _get_maintenance_prompt(self) -> str:
        return """
Evaluate MAINTENANCE & EVOLUTION:

**Code Maintainability:**
- Code complexity and readability
- Documentation quality and completeness
- Refactoring opportunities and technical debt
- Legacy code and modernization needs

**Evolution Strategy:**
- Extensibility and modification ease
- Technology upgrade paths and migration strategies
- Feature addition and enhancement capabilities
- Backward compatibility considerations

**Operational Maintenance:**
- Monitoring and debugging capabilities
- Issue resolution and troubleshooting
- Performance tuning and optimization
- Regular maintenance tasks and automation

**Long-term Strategy:**
- Technology roadmap and future planning
- Resource allocation for maintenance
- Skills and knowledge transfer requirements
- Risk management and mitigation strategies

**Deliverable:**
Maintenance analysis with technical debt assessment, evolution roadmap, and resource planning recommendations.
"""

    def _synthesize_final_report(
        self, repo_name: str, section_results: Dict[str, str]
    ) -> str:
        """Create the final synthesized report from all section analyses."""

        report_sections = [
            ("purpose", "Purpose of this Repository"),
            ("overview", "Repository Overview & Metrics"),
            ("technology", "Technology Stack Analysis"),
            ("architecture", "Architectural Analysis"),
            ("business", "Business Domain & Functionality"),
            ("implementation", "Implementation Deep Dive"),
            ("infrastructure", "Infrastructure & Deployment"),
            ("workflow", "Development Workflow"),
            ("security", "Security & Compliance"),
            ("performance", "Performance & Optimization"),
            ("maintenance", "Maintenance & Evolution"),
        ]

        # Build the final report
        final_report = f"""# Comprehensive Technical Analysis: {repo_name}

*Generated on: {time.strftime("%Y-%m-%d %H:%M:%S")}*

---

"""

        for section_key, section_title in report_sections:
            section_content = section_results.get(section_key, "Analysis not available")
            final_report += f"""## {section_title}

{section_content}

---

"""

        return final_report

    def _summarize_env_configs(self, env_configs: Dict) -> str:
        """Create a concise summary of environment configurations."""
        if not env_configs:
            return "No environment configuration files found."

        summary = []
        for config_type, files in env_configs.items():
            if files:
                summary.append(f"- {config_type}: {len(files)} files")

        return (
            "\n".join(summary) if summary else "No environment configurations detected."
        )

    def _summarize_git_info(self, git_info: Dict) -> str:
        """Create a concise summary of Git information."""
        if not git_info:
            return "No Git information available."

        summary = []
        if git_info.get("is_git_repo"):
            summary.append(
                f"- Repository: {git_info.get('repository_url', 'Local repository')}"
            )
            summary.append(
                f"- Current branch: {git_info.get('current_branch', 'Unknown')}"
            )
            summary.append(
                f"- Total commits: {git_info.get('commit_count', 'Unknown')}"
            )
            if git_info.get("contributors"):
                summary.append(f"- Contributors: {len(git_info['contributors'])}")
        else:
            summary.append("- Not a Git repository")

        return "\n".join(summary)
