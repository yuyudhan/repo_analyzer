# FilePath: src/repo_analyzer/core/developer_explanation.py

import time
from typing import Dict, List, Optional
from config.settings import Settings
from config.rate_limits import rate_limit_manager
from ..utils.logging_utils import get_logger


class DeveloperExplanation:
    """
    Generates repository explanation from developer's perspective.
    Explains WHY decisions were made and HOW the system works from insider knowledge.
    """

    def __init__(self, llm_provider):
        self.logger = get_logger(__name__)
        self.llm = llm_provider

    def generate_developer_explanation(
        self,
        repo_name: str,
        chunk_analyses: List[str],
        git_info: Dict,
        env_configs: Dict,
        human_context: Optional[str] = None,
    ) -> str:
        """
        Generate repository explanation from developer's perspective.
        Focus on design decisions, implementation reasoning, and system context.
        """
        self.logger.info("Starting developer explanation generation...")

        if human_context:
            self.logger.info("Incorporating human context into developer explanation")

        # Build base context
        base_context = self._build_base_context(
            repo_name, chunk_analyses, git_info, env_configs, human_context
        )

        # Define explanation sections with developer perspective
        sections = [
            ("vision", "Project Vision & Technical Goals"),
            ("overview", "System Overview & Design Philosophy"),
            ("technology", "Technology Choices & Engineering Rationale"),
            ("architecture", "Architecture Decisions & Trade-offs"),
            ("implementation", "Implementation Strategy & Patterns"),
            ("features", "Core Features & Logic Implementation"),
            ("infrastructure", "Infrastructure & Deployment Strategy"),
            ("development", "Development Approach & Workflow"),
            ("challenges", "Technical Challenges & Solutions"),
            ("future", "Future Roadmap & Evolution"),
        ]

        # Generate each section through developer lens
        section_results = {}
        for section_key, section_title in sections:
            self.logger.info(f"Explaining section: {section_title}")

            try:
                # Apply rate limiting
                rate_limit_manager.wait_if_needed("claude")

                section_explanation = self._explain_section(
                    section_key, section_title, base_context
                )
                section_results[section_key] = section_explanation

                # Add small delay between sections
                time.sleep(Settings.PROCESSING_DELAY)

            except Exception as e:
                self.logger.error(f"Error explaining {section_title}: {str(e)}")
                section_results[section_key] = (
                    f"Error explaining {section_title}: {str(e)}"
                )

        # Generate final developer explanation
        return self._synthesize_developer_explanation(
            repo_name, section_results, human_context
        )

    def _build_base_context(
        self,
        repo_name: str,
        chunk_analyses: List[str],
        git_info: Dict,
        env_configs: Dict,
        human_context: Optional[str] = None,
    ) -> str:
        """Build context for developer explanation."""

        # Combine chunk analyses
        combined_analysis = "\n\n---CHUNK SEPARATOR---\n\n".join(
            [
                f"CODEBASE SECTION {i + 1}:\n{analysis}"
                for i, analysis in enumerate(chunk_analyses)
            ]
        )

        # Environment summary
        env_summary = self._summarize_env_configs(env_configs)

        # Git summary
        git_summary = self._summarize_git_info(git_info)

        # Build base context
        base_context = f"""
PROJECT: {repo_name}

REPOSITORY INFORMATION:
{git_summary}

ENVIRONMENT & CONFIGURATION:
{env_summary}"""

        # Add human context if provided
        if human_context:
            base_context += f"""

DEVELOPMENT CONTEXT:
{human_context}

IMPORTANT: Use this development context to provide more accurate explanations
of design decisions. Consider the specific technical requirements, constraints,
and implementation considerations mentioned when explaining the rationale
behind engineering choices.
"""

        base_context += f"""

CODEBASE ANALYSIS:
{combined_analysis}
"""
        return base_context

    def _explain_section(
        self, section_key: str, section_title: str, base_context: str
    ) -> str:
        """Explain a specific section from developer perspective."""

        section_prompts = {
            "vision": self._get_vision_prompt(),
            "overview": self._get_overview_prompt(),
            "technology": self._get_technology_prompt(),
            "architecture": self._get_architecture_prompt(),
            "implementation": self._get_implementation_prompt(),
            "features": self._get_features_prompt(),
            "infrastructure": self._get_infrastructure_prompt(),
            "development": self._get_development_prompt(),
            "challenges": self._get_challenges_prompt(),
            "future": self._get_future_prompt(),
        }

        section_prompt = section_prompts.get(section_key, "")

        full_prompt = f"""
{base_context}

EXPLANATION TASK: {section_title}

{section_prompt}

TECHNICAL PERSPECTIVE REQUIREMENTS:
- Write from the development team's perspective using technical language
- Explain WHY decisions were made, not just WHAT exists
- Provide context for technical choices and trade-offs
- Share implementation insights that only developers would know
- Focus on engineering reasoning and problem-solving approaches
- Include technical lessons learned and design rationale
- Use engineer-to-engineer communication style
- Mention specific technical challenges and how they were solved
- If development context is provided, incorporate those technical insights
- Consider the implementation constraints and requirements mentioned in context
"""

        return self.llm.generate_response(full_prompt)

    def _get_vision_prompt(self) -> str:
        return """
Explain the PROJECT VISION & TECHNICAL GOALS from the development perspective:

**Technical Problem Statement:**
- What technical problem this project was built to solve
- The system requirements and functional specifications
- Target performance characteristics and constraints
- How this implementation differs from existing solutions
- The key technical capabilities and features

**Development Context:**
- What triggered the initial development requirement
- The original technical scope and how it evolved during implementation
- Key stakeholders and their technical requirements
- Success criteria and performance metrics defined
- The broader technical ecosystem this project integrates with

**Implementation Goals:**
- How the current implementation addresses the original requirements
- Technical compromises made and their engineering rationale
- Features that exceeded initial technical specifications
- Areas where the technical requirements are still evolving

**Context Integration:**
- Use development context to explain the original technical requirements
- Consider any implementation constraints or system requirements mentioned
- Factor in technical goals and project objectives from context

**Deliverable:**
Provide technical explanation of why this system exists and what engineering goals it aims to achieve.
"""

    def _get_overview_prompt(self) -> str:
        return """
Explain the SYSTEM OVERVIEW & DESIGN PHILOSOPHY:

**System Design Approach:**
- The core architectural patterns and design principles followed
- How the system's structure supports its functional requirements
- The mental model developers need when working with this codebase
- Key design decisions that shaped the overall structure
- Trade-offs between complexity, performance, and maintainability

**Code Organization Strategy:**
- How the codebase is structured and why this organization was chosen
- The relationship between different modules and components
- Naming conventions and their technical reasoning
- File and folder organization methodology
- How developers navigate and understand the codebase structure

**Development Philosophy:**
- Coding standards and practices adopted by the team
- Quality gates and development practices
- Testing strategy and its integration with development workflow
- Documentation approach and code knowledge sharing methods

**Context Integration:**
- Consider team structure and technical expertise mentioned in context
- Factor in any design constraints or system requirements specified
- Align design philosophy with technical objectives from context

**Deliverable:**
Technical overview that helps developers understand the engineering thinking behind the system design and organization.
"""

    def _get_technology_prompt(self) -> str:
        return """
Explain TECHNOLOGY CHOICES & ENGINEERING RATIONALE:

**Technology Selection Process:**
- Why specific programming languages were chosen for different components
- Framework selection criteria and technical evaluation process
- Database technology decisions and their engineering reasoning
- Third-party library choices and alternatives considered
- Build tools and development environment decisions

**Technical Requirements:**
- Performance requirements that influenced technology choices
- Scalability considerations and their impact on the technology stack
- Team expertise and learning curve considerations
- Integration requirements with existing systems
- Licensing and technical cost considerations

**Technology Integration:**
- How different technologies work together in the system
- Compatibility decisions and version management strategy
- Migration strategies and technology evolution plans
- Technical lessons learned from technology choices made
- Areas where different technical choices might be made today

**Context Integration:**
- Consider any technology preferences or constraints mentioned
- Factor in team expertise and technical learning requirements from context
- Align technology choices with system requirements specified

**Deliverable:**
In-depth technical explanation of technology decisions with the engineering reasoning and context behind each major choice.
"""

    def _get_architecture_prompt(self) -> str:
        return """
Explain ARCHITECTURE DECISIONS & TRADE-OFFS:

**Architectural Philosophy:**
- The overall architectural pattern chosen and its technical reasoning
- How the architecture supports the system's primary use cases
- Design principles that guided architectural decisions
- Separation of concerns and responsibility allocation
- How the architecture enables or constrains system evolution

**Component Design:**
- How major components were designed and their interactions
- Data flow architecture and its technical reasoning
- Error handling and resilience strategies
- Security architecture and its integration with functionality
- Performance considerations built into the architecture

**Technical Trade-off Analysis:**
- Complexity vs maintainability decisions made
- Performance vs flexibility trade-offs
- Scalability vs simplicity considerations
- Development speed vs long-term maintainability
- Areas where architectural compromises were necessary

**Evolution Strategy:**
- How the architecture supports future changes and extensions
- Extension points and plugin mechanisms designed
- Refactoring strategies and technical debt management
- Migration paths for architectural changes

**Context Integration:**
- Consider any architectural requirements or constraints mentioned
- Factor in scalability and performance needs from context
- Align architectural decisions with technical objectives specified

**Deliverable:**
Deep architectural explanation focusing on the engineering reasoning behind design decisions and their technical implications.
"""

    def _get_implementation_prompt(self) -> str:
        return """
Explain IMPLEMENTATION STRATEGY & PATTERNS:

**Implementation Approach:**
- Development methodology and implementation strategy followed
- Code organization patterns and their technical benefits
- Error handling philosophy and implementation
- Testing strategy integration with implementation
- Code review practices and quality assurance

**Design Pattern Usage:**
- Specific design patterns implemented and why they were chosen
- Custom patterns developed for this project's unique technical needs
- How patterns improve maintainability and extensibility
- Anti-patterns avoided and their alternatives
- Pattern evolution as the system grew

**Quality Strategy:**
- Code quality standards and their enforcement
- Refactoring approach and technical debt management
- Performance optimization strategies implemented
- Security implementation patterns and practices
- Documentation and knowledge sharing within code

**Development Practices:**
- Coding conventions and their technical reasoning
- Debugging and troubleshooting approaches
- Integration and deployment strategies
- Monitoring and observability implementation

**Context Integration:**
- Consider any implementation challenges or priorities mentioned
- Factor in quality requirements and constraints from context
- Align implementation strategy with team capabilities specified

**Deliverable:**
Technical explanation of how the system was built, focusing on implementation wisdom and engineering practices.
"""

    def _get_features_prompt(self) -> str:
        return """
Explain CORE FEATURES & LOGIC IMPLEMENTATION:

**Feature Implementation Strategy:**
- How features were prioritized and developed
- The relationship between functional requirements and technical implementation
- System interface design considerations that influenced implementation
- Feature interaction design and dependency management
- How features evolved based on system feedback

**Logic Implementation:**
- How complex rules and workflows were translated into code
- Domain modeling approach and its evolution
- Data validation and rule enforcement
- Workflow implementation and state management
- Integration between logic components and system interfaces

**Feature Architecture:**
- How features are structured within the codebase
- Reusability and modularity in feature implementation
- Configuration and customization capabilities built in
- Feature flag and gradual rollout strategies
- Testing strategy for complex logic

**System Interface Design:**
- How system interfaces influenced technical implementation decisions
- Performance optimization for critical features
- Error handling and system feedback mechanisms
- Integration points and API design

**Context Integration:**
- Consider any feature priorities or functional requirements mentioned
- Factor in system interface goals and constraints from context
- Align feature implementation with technical objectives specified

**Deliverable:**
Feature-focused explanation that connects functional requirements to technical implementation decisions.
"""

    def _get_infrastructure_prompt(self) -> str:
        return """
Explain INFRASTRUCTURE & DEPLOYMENT STRATEGY:

**Infrastructure Philosophy:**
- The infrastructure approach chosen and its technical reasoning
- Cloud vs on-premise decisions and their engineering drivers
- Scalability and reliability requirements that shaped infrastructure
- Cost optimization strategies in infrastructure design
- Security and compliance considerations in infrastructure choices

**Deployment Strategy:**
- Deployment pipeline design and its evolution
- Environment management and promotion strategies
- Rollback and disaster recovery planning
- Monitoring and alerting strategy implementation
- Infrastructure as code approach and its technical benefits

**Operational Considerations:**
- How operational requirements influenced design decisions
- Maintenance and update strategies
- Performance monitoring and optimization approaches
- Resource allocation and capacity planning
- Documentation and runbook development

**Evolution and Scaling:**
- How the infrastructure supports system growth
- Planned improvements and infrastructure roadmap
- Technical lessons learned from operational challenges
- Cost management and optimization strategies

**Context Integration:**
- Consider any infrastructure requirements or constraints mentioned
- Factor in operational and compliance needs from context
- Align infrastructure strategy with system requirements specified

**Deliverable:**
Infrastructure explanation that covers both technical decisions and operational wisdom gained through experience.
"""

    def _get_development_prompt(self) -> str:
        return """
Explain DEVELOPMENT APPROACH & WORKFLOW:

**Development Methodology:**
- Development process chosen and its adaptation to the project
- Team collaboration strategies and tools
- Project management integration with development workflow
- Quality assurance integration throughout development
- Knowledge sharing and documentation practices

**Team Workflow:**
- Code collaboration and review processes
- Branch management and release strategies
- Integration and testing workflows
- Issue tracking and resolution processes
- Communication and coordination methods

**Developer Experience:**
- Tools and environments provided to developers
- Onboarding process and documentation for new team members
- Development environment setup and maintenance
- Debugging and troubleshooting support
- Productivity tools and automation implemented

**Continuous Improvement:**
- How the development process evolved over time
- Retrospectives and process improvement initiatives
- Technology and tool adoption strategies
- Skills development and team growth approaches

**Context Integration:**
- Consider any team structure or workflow preferences mentioned
- Factor in development constraints and requirements from context
- Align development approach with team capabilities specified

**Deliverable:**
Technical explanation of how the development team works and the engineering reasoning behind workflow decisions.
"""

    def _get_challenges_prompt(self) -> str:
        return """
Explain TECHNICAL CHALLENGES & SOLUTIONS:

**Major Technical Challenges:**
- Significant technical obstacles encountered during development
- Performance challenges and optimization solutions implemented
- Scalability challenges and architectural solutions
- Integration challenges with external systems
- Data management and consistency challenges

**Problem-Solving Approach:**
- How technical problems were analyzed and approached
- Research and evaluation processes for solutions
- Experimentation and proof-of-concept strategies
- Decision-making criteria for solution selection
- Risk assessment and mitigation strategies

**Technical Solutions:**
- Creative or unconventional solutions developed
- Custom implementations created for specific problems
- Performance optimizations and their impact
- Security challenges and mitigation strategies
- Legacy system integration solutions

**Engineering Lessons:**
- What worked well and what didn't in problem-solving
- Technical knowledge gained that could benefit similar projects
- Areas where different approaches might be taken
- Best practices developed through experience

**Context Integration:**
- Consider any specific challenges or constraints mentioned
- Factor in problem-solving constraints and requirements from context
- Align solutions with technical objectives and constraints specified

**Deliverable:**
Problem-solving focused explanation that shares engineering wisdom and technical insights gained through challenges.
"""

    def _get_future_prompt(self) -> str:
        return """
Explain FUTURE ROADMAP & EVOLUTION:

**Evolution Strategy:**
- Planned improvements and feature additions
- Technical debt reduction priorities
- Performance optimization roadmap
- Scalability enhancement plans
- Security and compliance improvement strategies

**Technology Roadmap:**
- Technology upgrades and migration plans
- New technology adoption strategies
- Legacy system modernization plans
- Integration and API evolution plans
- Infrastructure improvement roadmap

**Growth Preparation:**
- How the system is prepared for growth and scale
- Resource allocation and capacity planning
- Team growth and skill development plans
- Documentation and knowledge management improvements
- Process and workflow evolution plans

**Technical Innovation:**
- Areas identified for innovation and experimentation
- Emerging technologies being evaluated
- System improvement opportunities
- Automation and efficiency improvement potential
- Community and ecosystem development plans

**Context Integration:**
- Consider any future goals or constraints mentioned in context
- Factor in growth plans and requirements
- Align future planning with strategic objectives specified

**Deliverable:**
Forward-looking explanation that shows how the system is positioned for future growth and evolution.
"""

    def _synthesize_developer_explanation(
        self,
        repo_name: str,
        section_results: Dict[str, str],
        human_context: Optional[str] = None,
    ) -> str:
        """Create the final developer explanation from all sections."""

        explanation_sections = [
            ("vision", "Project Vision & Technical Goals"),
            ("overview", "System Overview & Design Philosophy"),
            ("technology", "Technology Choices & Engineering Rationale"),
            ("architecture", "Architecture Decisions & Trade-offs"),
            ("implementation", "Implementation Strategy & Patterns"),
            ("features", "Core Features & Logic Implementation"),
            ("infrastructure", "Infrastructure & Deployment Strategy"),
            ("development", "Development Approach & Workflow"),
            ("challenges", "Technical Challenges & Solutions"),
            ("future", "Future Roadmap & Evolution"),
        ]

        # Build the final explanation
        final_explanation = f"""# Developer's Guide to {repo_name}

*Technical perspective on design decisions, implementation choices, and engineering philosophy*

*Generated on: {time.strftime("%Y-%m-%d %H:%M:%S")}*

---

## Introduction

This guide provides technical context and reasoning behind the engineering decisions made in developing {repo_name}.
It explains not just what the system does, but why it was built this way and how the technical choices
support the project's requirements.

"""

        # Add development context section if provided
        if human_context:
            final_explanation += f"""## Development Context

**Context Provided:**
{human_context}

This explanation incorporates the provided development context to offer more accurate
insights into design decisions and implementation reasoning.

---

"""

        for section_key, section_title in explanation_sections:
            section_content = section_results.get(
                section_key, "Explanation not available"
            )
            final_explanation += f"""## {section_title}

{section_content}

---

"""

        final_explanation += f"""
## Conclusion

This guide represents the accumulated technical knowledge and experience from developing {repo_name}.
The decisions documented here reflect the balance between various technical, system, and
practical constraints at the time of development.

As the system continues to evolve, these insights serve as a foundation for future
development decisions and help maintain consistency with the original engineering vision.

"""

        return final_explanation

    def _summarize_env_configs(self, env_configs: Dict) -> str:
        """Create environment configuration summary for developer context."""
        if not env_configs:
            return "No environment configuration files found."

        summary = []
        total_vars = sum(
            len(config.get("variables", {})) for config in env_configs.values()
        )

        summary.append(
            f"Environment configuration includes {len(env_configs)} files with {total_vars} variables total."
        )

        for file_path, config in env_configs.items():
            var_count = len(config.get("variables", {}))
            if var_count > 0:
                summary.append(f"- {file_path}: {var_count} configuration variables")

        return "\n".join(summary)

    def _summarize_git_info(self, git_info: Dict) -> str:
        """Create Git information summary for developer context."""
        if not git_info or not git_info.get("is_git_repo"):
            return "No Git repository information available."

        summary = []

        if git_info.get("repository_url"):
            summary.append(f"Repository URL: {git_info['repository_url']}")

        if git_info.get("current_branch"):
            summary.append(f"Current branch: {git_info['current_branch']}")

        if git_info.get("total_commits"):
            summary.append(f"Total commits: {git_info['total_commits']}")

        if git_info.get("all_branches"):
            branch_count = len(git_info["all_branches"])
            summary.append(f"Total branches: {branch_count}")

        return (
            "\n".join(summary)
            if summary
            else "Git repository with limited information available."
        )
