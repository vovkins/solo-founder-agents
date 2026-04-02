"""Designer crew for UI/UX design tasks."""

from crewai import Crew, Process


def create_designer_crew(
    system_design_path: str = "data/artifacts/docs/design/system-design.md",
    task_description: str = "",
    verbose: bool = True,
) -> Crew:
    """Create a crew with only the Designer agent."""
    from src.agents import designer_agent
    from src.tasks import (
        create_design_system_task,
        create_ui_screen_task,
    )

    design_system = create_design_system_task(system_design_path)
    design_screen = create_ui_screen_task("TaskScreen", task_description)

    return Crew(
        agents=[designer_agent],
        tasks=[design_system, design_screen],
        process=Process.sequential,
        verbose=verbose,
    )


def run_designer_crew(
    system_design_path: str = "data/artifacts/docs/design/system-design.md",
    task_description: str = "",
) -> dict:
    """Run the designer crew."""
    from src.tools.file_permissions import set_current_role
    set_current_role("designer")

    crew = create_designer_crew(system_design_path, task_description)
    result = crew.kickoff()

    return {
        "status": "completed",
        "result": str(result),
    }
