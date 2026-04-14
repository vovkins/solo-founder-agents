"""Tasks for Business Analyst agent."""

from crewai import Task

from src.agents import get_analyst_agent


def create_analyze_backlog_task(backlog_path: str = "docs/requirements/backlog.md") -> Task:
    """Create task for analyzing the PM's epic-level backlog.

    Args:
        backlog_path: Path to the backlog document created by PM

    Returns:
        Task for backlog analysis
    """
    return Task(
        description=f"""
        Analyze the product backlog created by the Product Manager.

        Backlog location: {backlog_path}

        Your job is to:
        1. Read the backlog document
        2. Extract all epics and their acceptance criteria
        3. Read the PRD (docs/requirements/prd.md) for additional context if needed
        4. Identify edge cases, error scenarios, and technical constraints
        5. Note integration points between epics

        Create a structured analysis with:
        - Epic name and scope
        - Key acceptance criteria
        - Technical constraints
        - Dependencies between epics
        - Suggested task breakdown areas
        """,
        expected_output="Structured analysis of all epics with acceptance criteria and dependencies",
        agent=get_analyst_agent(),
    )


def create_decompose_epics_task(epics_analysis: str) -> Task:
    """Create task for decomposing epics into implementable tasks.

    Args:
        epics_analysis: Structured epic analysis from previous step

    Returns:
        Task for epic decomposition
    """
    return Task(
        description=f"""
        Decompose each EPIC from the PM's backlog into detailed, implementable tasks.

        Epic analysis:
        {epics_analysis}

        For each epic:
        1. Break it down into individual tasks (2-5 days each)
        2. Ensure each task is independent (INVEST criteria)
        3. Add detailed acceptance criteria for each task
        4. Estimate size (XS: <1d, S: 1-2d, M: 2-3d, L: 3-5d, XL: >5d → split)
        5. Identify dependencies between tasks
        6. Link each task to its parent epic

        ⚠️ IMPORTANT: This is where the DETAILED decomposition happens.
        The PM created high-level epics. You break them into concrete,
        implementable tasks that a developer can pick up.

        Split any XL tasks into smaller ones.
        """,
        expected_output="List of detailed tasks with sizes, dependencies, and parent epic links",
        agent=get_analyst_agent(),
    )


def create_task_specs_task(tasks: str) -> Task:
    """Create task for generating task specifications.

    Args:
        tasks: Decomposed task list

    Returns:
        Task for specification creation
    """
    return Task(
        description=f"""
        Create detailed specifications for each task.
        
        Tasks to specify:
        {tasks}
        
        For each task, create a GitHub Issue with:
        - Clear title
        - Description of work
        - Acceptance criteria (numbered list)
        - Technical notes
        - Size estimate
        - Dependencies
        - Link to parent feature
        
        Use the template from templates/github-issue-feature.md
        Apply appropriate labels (task, size, priority).
        
        After creating all issues, save the combined task specifications document
        using save_artifact with artifact_type="task-specs".
        
        ⚠️ IMPORTANT: Use ONLY artifact_type="task-specs" for saving specs.
        NEVER use "backlog" or "prd" — those belong to PM role.
        """,
        expected_output="List of created GitHub Issue URLs for tasks",
        agent=get_analyst_agent(),
    )


def create_dependency_map_task(task_urls: list) -> Task:
    """Create task for mapping dependencies between tasks.

    Args:
        task_urls: List of GitHub Issue URLs for tasks

    Returns:
        Task for dependency mapping
    """
    tasks_str = "\n".join(f"- {url}" for url in task_urls)

    return Task(
        description=f"""
        Map dependencies between tasks.
        
        Tasks created:
        {tasks_str}
        
        Your job is to:
        1. Identify which tasks depend on others
        2. Create a dependency graph
        3. Recommend execution order
        4. Flag any blocking tasks
        5. Suggest parallel work streams
        
        Save the dependency map using save_artifact with artifact_type="dep-map".
        
        ⚠️ IMPORTANT: Use ONLY artifact_type="dep-map" for saving the dependency map.
        NEVER use "backlog" or "prd" — those belong to PM role.
        
        Output format:
        - List tasks in recommended order
        - Mark dependencies for each task
        - Identify which tasks can be done in parallel
        """,
        expected_output="Dependency map with recommended execution order",
        agent=get_analyst_agent(),
    )


def create_sprint_recommendations_task(
    task_urls: list,
    team_capacity: int = 10,
) -> Task:
    """Create task for sprint planning recommendations.

    Args:
        task_urls: List of GitHub Issue URLs
        team_capacity: Story points capacity per sprint

    Returns:
        Task for sprint recommendations
    """
    tasks_str = "\n".join(f"- {url}" for url in task_urls)

    return Task(
        description=f"""
        Create sprint planning recommendations.
        
        Tasks:
        {tasks_str}
        
        Team capacity: {team_capacity} story points per sprint
        
        Your job is to:
        1. Assign story points to each task
           - XS: 1 point
           - S: 2 points
           - M: 3 points
           - L: 5 points
        2. Group tasks into sprints
        3. Respect dependencies
        4. Balance workload
        
        Output:
        - Sprint 1 tasks
        - Sprint 2 tasks (if needed)
        - Any blocked tasks
        """,
        expected_output="Sprint plan with task assignments",
        agent=get_analyst_agent(),
    )
