"""Tasks for Business Analyst agent."""

from crewai import Task

from src.agents import get_analyst_agent


def create_analyze_prd_task(prd_path: str) -> Task:
    """Create task for analyzing PRD document.

    Args:
        prd_path: Path to the PRD document

    Returns:
        Task for PRD analysis
    """
    return Task(
        description=f"""
        Analyze the Product Requirements Document and extract all features.
        
        PRD location: {prd_path}
        
        Your job is to:
        1. Read the PRD document
        2. Extract all features and functional requirements
        3. Identify edge cases and error scenarios
        4. Note any technical constraints
        5. Identify integration points
        
        Create a structured feature list with:
        - Feature name
        - Description
        - Priority (from PRD)
        - Dependencies on other features
        """,
        expected_output="Structured feature list with all requirements",
        agent=get_analyst_agent(),
    )


def create_decompose_features_task(features: str) -> Task:
    """Create task for decomposing features into tasks.

    Args:
        features: Structured feature list from analysis

    Returns:
        Task for feature decomposition
    """
    return Task(
        description=f"""
        Decompose each feature into implementable tasks.
        
        Features to decompose:
        {features}
        
        For each feature:
        1. Break it down into 2-5 day tasks
        2. Ensure each task is independent
        3. Add acceptance criteria
        4. Estimate size (XS, S, M, L, XL)
        5. Identify dependencies
        
        Use INVEST criteria for task quality.
        Split any XL tasks into smaller ones.
        """,
        expected_output="List of decomposed tasks with sizes and dependencies",
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
