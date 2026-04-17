"""Tasks for Technical Writer agent."""

from crewai import Task

from src.agents import get_tech_writer_agent


def create_readme_task() -> Task:
    """Create task for generating README.md based on GitHub artifacts.

    Returns:
        Task for README creation
    """
    return Task(
        description="""
        Create a comprehensive README.md for the project by reading artifacts from GitHub.

        Your job is to:

        1. **Read Project Artifacts** (use read_artifact tool):
           - docs/requirements/prd.md — for project description, goals, features
           - docs/requirements/task-specs.md — for detailed feature list
           - docs/design/system-design.md — for architecture overview
           - docs/design/design-system.md — for tech stack info
           - docs/adr/ — for key architectural decisions

        2. **Create README.md** with the following sections:
           - Project Overview (from PRD goals and description)
           - Key Features (from task-specs / backlog)
           - Tech Stack (from system-design and design-system)
           - Architecture Overview (from system-design, keep high-level)
           - Getting Started (prerequisites, installation, basic usage)
           - Project Structure (directory layout)
           - Contributing guidelines
           - License

        3. **Save** using save_artifact with type="changelog" or write directly.

        The README should be thorough and useful for someone who has never seen the project.
        Base ALL content on what you read from GitHub artifacts — do not invent features.
        """,
        expected_output="Comprehensive README.md content based on project artifacts",
        output_key="readme_content",
        agent=get_tech_writer_agent(),
    )


def create_changelog_task() -> Task:
    """Create task for generating CHANGELOG based on GitHub artifacts.

    Returns:
        Task for changelog creation
    """
    return Task(
        description="""
        Create a CHANGELOG.md for the project by reading artifacts from GitHub.

        Your job is to:

        1. **Read Project Artifacts** (use read_artifact tool):
           - docs/requirements/prd.md — for planned features
           - docs/requirements/task-specs.md — for implemented task list
           - src/** — check which source files exist (implemented features)

        2. **Create CHANGELOG.md** in Keep a Changelog format:
           - ## [Unreleased] section
           - ### Added — features from task-specs that have source files in src/
           - ### Changed — modifications
           - ### Fixed — bug fixes (if any from QA reports)

        3. **Save** using save_artifact with type="changelog".

        Base the changelog on actual artifacts — cross-reference task-specs with existing source files.
        """,
        expected_output="CHANGELOG.md based on project artifacts",
        agent=get_tech_writer_agent(),
    )
