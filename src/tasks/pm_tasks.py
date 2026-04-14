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

        ⚠️ DO NOT write any files during this step. Only ask questions and collect information.
        """,
        expected_output="Structured requirements document with goals, personas, features, and priorities. DO NOT save to file — just return the structured text.",
        agent=get_pm_agent(),
    )


def create_prd_task(requirements_hint: str) -> Task:
    """Create task for generating PRD document."""
    return Task(
        description="""
        Create a comprehensive Product Requirements Document (PRD).

        You will receive the collected requirements from the previous step as context.
        Use that context to create the PRD.

        Follow the PRD template and include:
        - Product overview and goals
        - Target personas
        - Functional requirements
        - Non-functional requirements
        - Success criteria
        - Out of scope items

        Save the PRD to docs/requirements/prd.md using the save_artifact tool
        with artifact_type="prd".

        ⛔ CRITICAL RULES:
        - This is the ONLY time you write to prd.md.
        - Write ONLY the PRD (requirements document), NOT a backlog or task list.
        - After saving prd.md, you must NEVER call save_artifact with type "prd" again.
        - The next steps will use docs/requirements/backlog.md for tasks.
        """,
        expected_output="Confirmation that PRD was saved to docs/requirements/prd.md",
        agent=get_pm_agent(),
    )


def create_backlog_task(prd_hint: str) -> Task:
    """Create task for generating EPIC-level product backlog from PRD.

    The PM creates EPIC-level items (features/user stories).
    The Analyst will later decompose these epics into detailed tasks.
    """
    return Task(
        description="""
        Generate the EPIC-LEVEL product backlog from the PRD.

        You will receive the PRD from the previous step as context.
        Use that context to create the backlog.

        Your job is to:
        1. Decompose the PRD into EPICS (major features / user stories)
           — Each epic should represent a cohesive feature area
           — Each epic should be describable in 1-2 sentences
           — Do NOT break epics into individual implementation tasks
        2. Write each epic with:
           — Epic title and description
           — High-level acceptance criteria (2-4 bullet points)
           — Priority (P0-P3, MoSCoW)
           — Dependencies on other epics (if any)
        3. Save the backlog to docs/requirements/backlog.md using save_artifact
        4. Create ONE GitHub Issue per epic with appropriate labels (feature, priority)

        ⚠️ IMPORTANT: Stay at EPIC level. Do NOT create detailed task breakdowns.
        The Business Analyst will decompose each epic into implementable tasks later.
        Example: "Chat System" is an epic. "Implement WebSocket connection", "Build message UI"
        are tasks — those belong to the Analyst, NOT here.

        ⛔ CRITICAL RULES:
        - Write to docs/requirements/backlog.md ONLY.
        - NEVER call save_artifact with type "prd" — the PRD is already created.
        - NEVER write to or modify docs/requirements/prd.md.
        - If you need to reference the PRD, read it but do NOT overwrite it.
        """,
        expected_output="Path to the created backlog (docs/requirements/backlog.md) with epic-level items and list of GitHub Issue URLs",
        agent=get_pm_agent(),
    )


def create_prioritize_backlog_task(issue_urls: list) -> Task:
    """Create task for prioritizing the backlog."""
    issues_str = "\n".join(f"- {url}" for url in issue_urls) if issue_urls else "See context from previous step for issue URLs."

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

        ⛔ CRITICAL RULES:
        - Update docs/requirements/backlog.md ONLY.
        - NEVER call save_artifact with type "prd".
        - NEVER write to or modify docs/requirements/prd.md.
        """,
        expected_output="Updated docs/requirements/backlog.md with priorities",
        agent=get_pm_agent(),
    )
