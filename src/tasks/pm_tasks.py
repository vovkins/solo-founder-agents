"""Tasks for Product Manager agent."""

from crewai import Task

from src.agents import get_pm_agent


def create_collect_requirements_task(user_input: str) -> Task:
    """Create task for collecting requirements from founder."""
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
        agent=get_pm_agent(),
    )


def create_prd_task(requirements: str) -> Task:
    """Create task for generating PRD document."""
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
        
        Save the PRD to docs/requirements/prd.md
        
        IMPORTANT: This is the ONLY time you write to prd.md. Do NOT overwrite it later.
        """,
        expected_output="Path to the created PRD document (docs/requirements/prd.md)",
        agent=get_pm_agent(),
    )


def create_backlog_task(prd_content: str) -> Task:
    """Create task for generating product backlog."""
    return Task(
        description=f"""
        Generate the product backlog from the PRD.
        
        PRD content:
        {prd_content}
        
        Your job is to:
        1. Decompose the PRD into features and tasks (epic-level)
        2. Write each task with description and acceptance criteria
        3. Save the backlog to docs/requirements/backlog.md
        4. Create a GitHub Issue for each feature/task
        5. Apply appropriate labels (feature, priority)
        
        Use the feature template from templates/github-issue-feature.md
        
        CRITICAL: Write the backlog to docs/requirements/backlog.md — NOT to prd.md!
        The prd.md file must NOT be modified during this step.
        """,
        expected_output="Path to the created backlog (docs/requirements/backlog.md) and list of GitHub Issue URLs",
        agent=get_pm_agent(),
    )


def create_prioritize_backlog_task(issue_urls: list) -> Task:
    """Create task for prioritizing the backlog."""
    issues_str = "\n".join(f"- {{url}}" for url in issue_urls)

    return Task(
        description=f"""
        Prioritize the product backlog.
        
        Issues created:
        {issues_str}
        
        Your job is to:
        1. Read the current backlog from docs/requirements/backlog.md
        2. Apply priority labels to each backlog item:
           - P0: Critical (Must have for MVP)
           - P1: High (Should have)
           - P2: Medium (Could have)
           - P3: Low (Nice to have)
        3. Update docs/requirements/backlog.md with the priorities
        4. Add milestone assignments if applicable
        
        CRITICAL: Update docs/requirements/backlog.md only. 
        Do NOT modify docs/requirements/prd.md!
        """,
        expected_output="Updated docs/requirements/backlog.md with priorities",
        agent=get_pm_agent(),
    )
