"""Tasks for Technical Writer agent."""

from crewai import Task

from src.agents import get_tech_writer_agent


def create_readme_task(project_name: str, project_description: str) -> Task:
    """Create task for generating README.md.

    Args:
        project_name: Name of the project
        project_description: Description of the project

    Returns:
        Task for README creation
    """
    return Task(
        description=f"""
        Create a comprehensive README.md for the project.
        
        Project: {project_name}
        Description: {project_description}
        
        Your job is to:
        
        1. **Project Overview**
           - What the project does
           - Key features
           - Target users
        
        2. **Quick Start**
           - Prerequisites
           - Installation steps
           - Basic usage example
        
        3. **Installation**
           - Dependencies
           - Setup instructions
           - Configuration
        
        4. **Usage**
           - Common use cases
           - Code examples
           - Configuration options
        
        5. **Documentation Links**
           - Link to API docs
           - Link to architecture
           - Link to contribution guide
        
        6. **Contributing**
           - How to contribute
           - Development setup
           - Code standards
        
        7. **License**
           - License type
        
        Save to README.md in project root.
        """,
        expected_output="Path to created README.md",
        agent=get_tech_writer_agent(),
    )


def create_api_docs_task(api_endpoints: list, base_url: str) -> Task:
    """Create task for API documentation.

    Args:
        api_endpoints: List of API endpoints to document
        base_url: Base URL for the API

    Returns:
        Task for API documentation
    """
    endpoints_str = "\n".join(f"- {e}" for e in api_endpoints)

    return Task(
        description=f"""
        Create API documentation for all endpoints.
        
        Base URL: {base_url}
        
        Endpoints:
        {endpoints_str}
        
        For each endpoint, document:
        
        1. **Endpoint**
           - HTTP method
           - Path
           - Description
        
        2. **Authentication**
           - Required auth
           - Token format
           - Headers
        
        3. **Request**
           - Path parameters
           - Query parameters
           - Request body schema
           - Example request
        
        4. **Response**
           - Success response schema
           - Response codes
           - Example response
        
        5. **Errors**
           - Error codes
           - Error response format
           - Common errors
        
        Save to docs/api/README.md with individual endpoint files.
        """,
        expected_output="Path to API documentation",
        agent=get_tech_writer_agent(),
    )


def create_component_docs_task(components: list) -> Task:
    """Create task for component documentation.

    Args:
        components: List of components to document

    Returns:
        Task for component documentation
    """
    components_str = "\n".join(f"- {c}" for c in components)

    return Task(
        description=f"""
        Create documentation for UI components.
        
        Components:
        {components_str}
        
        For each component, document:
        
        1. **Overview**
           - Component name
           - Purpose
           - When to use
        
        2. **Props**
           - Prop name
           - Type
           - Required/Optional
           - Default value
           - Description
        
        3. **Usage Examples**
           - Basic usage
           - With props
           - Common patterns
        
        4. **States**
           - Default
           - Hover
           - Focus
           - Disabled
           - Loading
        
        5. **Accessibility**
           - ARIA attributes
           - Keyboard navigation
        
        Save to docs/components/[ComponentName].md
        """,
        expected_output="List of created component documentation files",
        agent=get_tech_writer_agent(),
    )


def create_setup_guide_task(
    prerequisites: list,
    setup_steps: list,
) -> Task:
    """Create task for setup/Getting Started guide.

    Args:
        prerequisites: List of prerequisites
        setup_steps: List of setup steps

    Returns:
        Task for setup guide creation
    """
    prereqs_str = "\n".join(f"- {p}" for p in prerequisites)
    steps_str = "\n".join(f"{i+1}. {s}" for i, s in enumerate(setup_steps))

    return Task(
        description=f"""
        Create a comprehensive setup guide.
        
        Prerequisites:
        {prereqs_str}
        
        Setup Steps:
        {steps_str}
        
        Your job is to:
        
        1. **Environment Setup**
           - System requirements
           - Dependencies installation
           - Environment variables
        
        2. **Step-by-Step Instructions**
           - Clear numbered steps
           - Code blocks for commands
           - Expected output examples
        
        3. **Troubleshooting**
           - Common issues
           - Solutions
           - Where to get help
        
        4. **Verification**
           - How to verify setup
           - Test commands
           - Expected results
        
        Save to docs/getting-started.md
        """,
        expected_output="Path to created setup guide",
        agent=get_tech_writer_agent(),
    )


def create_changelog_task(
    version: str,
    changes: list,
    release_date: str,
) -> Task:
    """Create task for updating CHANGELOG.md.

    Args:
        version: Version number
        changes: List of changes
        release_date: Release date

    Returns:
        Task for changelog update
    """
    changes_str = "\n".join(f"- {c}" for c in changes)

    return Task(
        description=f"""
        Update CHANGELOG.md with new release.
        
        Version: {version}
        Date: {release_date}
        
        Changes:
        {changes_str}
        
        Your job is to:
        
        1. **Read Existing Changelog**
           - Get current content
           - Preserve history
        
        2. **Add New Section**
           - Version number
           - Release date
           - Categorize changes:
             - Added (new features)
             - Changed (modifications)
             - Fixed (bug fixes)
             - Removed
        
        3. **Format Properly**
           - Follow Keep a Changelog format
           - Consistent style
           - Clear descriptions
        
        Save to CHANGELOG.md
        """,
        expected_output="Path to updated CHANGELOG.md",
        agent=get_tech_writer_agent(),
    )


def create_architecture_doc_task(
    system_design_path: str,
    adrs_path: str,
) -> Task:
    """Create task for architecture documentation.

    Args:
        system_design_path: Path to system design doc
        adrs_path: Path to ADRs directory

    Returns:
        Task for architecture documentation
    """
    return Task(
        description=f"""
        Create architecture documentation for the project.
        
        System Design: {system_design_path}
        ADRs: {adrs_path}
        
        Your job is to:
        
        1. **System Overview**
           - High-level architecture
           - Key components
           - Data flow
        
        2. **Technology Stack**
           - Frontend stack
           - Backend stack
           - Database
           - External services
        
        3. **Key Decisions**
           - Summary of ADRs
           - Links to full ADRs
           - Rationale
        
        4. **Directory Structure**
           - Project organization
           - Key directories
           - Naming conventions
        
        5. **Deployment**
           - Infrastructure
           - CI/CD
           - Environments
        
        Save to docs/architecture.md
        """,
        expected_output="Path to created architecture documentation",
        agent=get_tech_writer_agent(),
    )
