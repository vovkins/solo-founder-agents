"""Tasks for Product Manager agent."""

from crewai import Task

from .pm import pm_agent


def create_collect_requirements_task(user_input: str) -> Task:
    """Create task for collecting requirements from founder.

    Args:
        user_input: Initial input/vision from founder

    Returns:
        Task for requirement collection
    """
    return Task(
        description=f"""
        Collect and clarify product requirements from the founder.
        
        Initial input from founder:
        {user_input}
        
        Your job is to:
        1. Ask clarifying questions (one at a time) to understand the vision
        2. Identify target audience and problems to solve
        3. Determine key features and scope
        4. Apply MoSCoW prioritization (Must have, Should have, Could have, Won't have)
        
        Ask follow-up questions until you have enough information to create a PRD.
        """,
        expected_output="Structured requirements document with goals, personas, features, and priorities",
        agent=pm_agent,
    )


def create_prd_task(requirements: str) -> Task:
    """Create task for generating PRD document.

    Args:
        requirements: Structured requirements from collection phase

    Returns:
        Task for PRD creation
    """
    return Task(
        description=f"""
        Create a comprehensive Product Requirements Document (PRD).
        
        Use the following requirements:
        {requirements}
        
        Follow the PRD template from templates/prd.md and include:
        - Product overview and goals
        - Target personas
        - Functional requirements
        - Non-functional requirements
        - Success criteria
        - Out of scope items
        
        Save the PRD to docs/prd.md
        """,
        expected_output="Path to the created PRD document (docs/prd.md)",
        agent=pm_agent,
        output_file="data/artifacts/docs/prd.md",
    )


def create_backlog_task(prd_content: str) -> Task:
    """Create task for generating GitHub Issues backlog.

    Args:
        prd_content: Content of the PRD document

    Returns:
        Task for backlog generation
    """
    return Task(
        description=f"""
        Generate the product backlog from the PRD.
        
        PRD content:
        {prd_content}
        
        Your job is to:
        1. Decompose the PRD into features (epic-level)
        2. Create a GitHub Issue for each feature
        3. Apply appropriate labels (feature, priority)
        4. Add acceptance criteria to each issue
        
        Use the feature template from templates/github-issue-feature.md
        """,
        expected_output="List of created GitHub Issue URLs",
        agent=pm_agent,
    )


def create_prioritize_backlog_task(issue_urls: list) -> Task:
    """Create task for prioritizing the backlog.

    Args:
        issue_urls: List of GitHub Issue URLs

    Returns:
        Task for backlog prioritization
    """
    issues_str = "\n".join(f"- {url}" for url in issue_urls)

    return Task(
        description=f"""
        Prioritize the product backlog.
        
        Issues created:
        {issues_str}
        
        Apply priority labels to each issue:
        - P0: Critical (Must have for MVP)
        - P1: High (Should have)
        - P2: Medium (Could have)
        - P3: Low (Nice to have)
        
        Also add milestone assignments if applicable.
        """,
        expected_output="Updated list of issues with priorities",
        agent=pm_agent,
    )
