"""Tasks for Software Architect agent."""

from crewai import Task

from src.agents import get_architect_agent


def create_analyze_requirements_task(prd_path: str, tasks_summary: str) -> Task:
    """Create task for analyzing technical requirements.

    Args:
        prd_path: Path to the PRD document
        tasks_summary: Summary of tasks from Analyst

    Returns:
        Task for requirements analysis
    """
    return Task(
        description=f"""
        Analyze requirements from technical perspective.
        
        PRD location: {prd_path}
        
        Task summary:
        {tasks_summary}
        
        Your job is to:
        1. Review the PRD and tasks
        2. Identify technical requirements
        3. Determine performance and scale needs
        4. Identify integration points
        5. Note constraints and limitations
        
        Output:
        - Technical requirements summary
        - Performance requirements
        - Security considerations
        - Integration requirements
        """,
        expected_output="Technical requirements summary",
        agent=get_architect_agent(),
    )


def create_design_architecture_task(requirements: str) -> Task:
    """Create task for designing system architecture.

    Args:
        requirements: Technical requirements summary

    Returns:
        Task for architecture design
    """
    return Task(
        description=f"""
        Design the high-level system architecture.
        
        Technical requirements:
        {requirements}
        
        Your job is to:
        1. Choose architectural pattern (Clean Architecture, MVC, etc.)
        2. Define system layers
        3. Design component boundaries
        4. Plan data flow
        5. Choose state management approach
        
        Consider:
        - Scalability
        - Maintainability
        - Testability
        - Performance
        
        Create architecture diagrams using Mermaid syntax.
        """,
        expected_output="Architecture design with diagrams",
        agent=get_architect_agent(),
    )


def create_adr_task(decision_topic: str, context: str) -> Task:
    """Create task for generating an ADR.

    Args:
        decision_topic: Topic for the ADR (e.g., "Database Choice")
        context: Context for the decision

    Returns:
        Task for ADR creation
    """
    return Task(
        description=f"""
        Create an Architecture Decision Record (ADR).
        
        Decision topic: {decision_topic}
        
        Context:
        {context}
        
        Follow the ADR template from templates/ADR-item.md and include:
        - Title and number (sequential)
        - Status (Proposed, Accepted, etc.)
        - Context (background and problem)
        - Decision (the choice made)
        - Consequences (pros and cons)
        - Alternatives considered
        
        Save to docs/adr/ADR-XXX.md
        """,
        expected_output="Path to the created ADR document",
        agent=get_architect_agent(),
    )


def create_system_design_task(
    prd_path: str,
    architecture: str,
) -> Task:
    """Create task for generating System Design document.

    Args:
        prd_path: Path to the PRD document
        architecture: Architecture design summary

    Returns:
        Task for System Design creation
    """
    return Task(
        description=f"""
        Create comprehensive System Design document.
        
        PRD: {prd_path}
        
        Architecture:
        {architecture}
        
        Follow the template from templates/system-design.md and include:
        
        1. **Overview**
           - System purpose and goals
           - Key stakeholders
        
        2. **Architecture Diagrams** (C4 Model)
           - Context diagram (Mermaid)
           - Container diagram (Mermaid)
           - Component diagram (Mermaid)
        
        3. **Components**
           - Frontend (React Native)
           - Backend (Node.js)
           - Database
           - External services
        
        4. **Data Model**
           - Entities and relationships
           - ERD diagram
        
        5. **API Design**
           - Endpoints overview
           - Authentication
        
        6. **State Management**
           - Client state
           - Server state
        
        7. **Security**
           - Authentication/Authorization
           - Data protection
        
        8. **Deployment**
           - Environment overview
           - CI/CD considerations
        
        Save to docs/design/system-design.md
        """,
        expected_output="Path to the created System Design document",
        agent=get_architect_agent(),
    )


def create_standards_task(architecture: str) -> Task:
    """Create task for defining coding standards.

    Args:
        architecture: Architecture design summary

    Returns:
        Task for standards definition
    """
    return Task(
        description=f"""
        Define technical standards and conventions.
        
        Architecture context:
        {architecture}
        
        Create documentation for:
        
        1. **Coding Standards**
           - TypeScript/JavaScript conventions
           - React Native best practices
           - Node.js patterns
        
        2. **Naming Conventions**
           - Files and folders
           - Variables and functions
           - Components
           - API endpoints
        
        3. **Folder Structure**
           - Frontend structure
           - Backend structure
           - Shared code
        
        4. **Git Workflow**
           - Branch naming
           - Commit message format
           - PR guidelines
        
        5. **Testing Standards**
           - Unit test requirements
           - E2E test guidelines
           - Coverage minimums
        
        Save to docs/standards.md
        """,
        expected_output="Path to the created standards document",
        agent=get_architect_agent(),
    )


def create_api_spec_task(system_design_path: str) -> Task:
    """Create task for generating OpenAPI specification.

    Args:
        system_design_path: Path to System Design document

    Returns:
        Task for API spec creation
    """
    return Task(
        description=f"""
        Create OpenAPI specification for the API.
        
        System Design: {system_design_path}
        
        Your job is to:
        1. Define all API endpoints
        2. Specify request/response schemas
        3. Add authentication requirements
        4. Document error responses
        
        Create an OpenAPI 3.0 specification in YAML format.
        Save to docs/api/openapi.yaml
        """,
        expected_output="Path to the OpenAPI spec file",
        agent=get_architect_agent(),
    )
