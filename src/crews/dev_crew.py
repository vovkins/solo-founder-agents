"""Development crew for implementing features."""

from typing import Optional
from crewai import Crew, Process


def create_dev_crew(
    issue_number: int,
    task_description: str,
    system_design_path: str = "data/artifacts/docs/system-design.md",
    verbose: bool = True,
) -> Crew:
    """Create a crew for developing a single task/feature."""
    # Lazy imports to avoid circular dependency
    from src.agents import (
        designer_agent,
        developer_agent,
        reviewer_agent,
        qa_agent,
        tech_writer_agent,
    )
    from src.tasks import (
        create_design_system_task,
        create_ui_screen_task,
        create_analyze_task_task,
        create_feature_branch_task,
        create_implement_feature_task,
        create_write_tests_task,
        create_pull_request_task,
        create_review_pr_task,
        create_qa_signoff_task,
        create_readme_task,
    )

    # Designer tasks
    design_system = create_design_system_task(system_design_path)
    design_screen = create_ui_screen_task("TaskScreen", task_description)

    # Developer tasks
    analyze_task = create_analyze_task_task(issue_number)
    create_branch = create_feature_branch_task(issue_number, "feature")
    implement = create_implement_feature_task("{{implementation_plan}}", "{{branch_name}}")
    write_tests = create_write_tests_task(["{{files_modified}}"], issue_number)
    create_pr = create_pull_request_task(issue_number, "{{branch_name}}", "{{changes_summary}}")

    # Reviewer tasks
    review_pr = create_review_pr_task("{{pr_url}}", "{{pr_description}}")

    # QA tasks
    qa_signoff = create_qa_signoff_task("{{pr_url}}", "{{test_results}}", "{{acceptance_status}}")

    # Tech Writer tasks
    update_readme = create_readme_task("Project", "{{project_description}}")

    return Crew(
        agents=[
            designer_agent,
            developer_agent,
            reviewer_agent,
            qa_agent,
            tech_writer_agent,
        ],
        tasks=[
            design_system,
            design_screen,
            analyze_task,
            create_branch,
            implement,
            write_tests,
            create_pr,
            review_pr,
            qa_signoff,
            update_readme,
        ],
        process=Process.sequential,
        verbose=verbose,
    )


def run_dev_crew(issue_number: int, task_description: str) -> dict:
    """Run the development crew for a task."""
    from src.tools.file_permissions import set_current_role
    set_current_role("developer")
    
    crew = create_dev_crew(issue_number, task_description)
    result = crew.kickoff()

    return {
        "status": "completed",
        "result": str(result),
        "issue_number": issue_number,
    }


def create_review_cycle_crew(
    pr_url: str,
    review_comments: str,
    verbose: bool = True,
) -> Crew:
    """Create a crew for addressing review comments."""
    from src.agents import developer_agent, qa_agent, reviewer_agent
    from src.tasks import (
        create_fix_review_comments_task,
        create_regression_test_task,
        create_review_pr_task,
    )

    fix_comments = create_fix_review_comments_task(pr_url, review_comments)
    regression = create_regression_test_task(pr_url, ["{{fixed_issues}}"])
    final_review = create_review_pr_task(pr_url, "Updated based on review comments")

    return Crew(
        agents=[developer_agent, qa_agent, reviewer_agent],
        tasks=[fix_comments, regression, final_review],
        process=Process.sequential,
        verbose=verbose,
    )


def create_qa_cycle_crew(
    pr_url: str,
    test_cases: list,
    acceptance_criteria: list,
    verbose: bool = True,
) -> Crew:
    """Create a crew for QA testing cycle."""
    from src.agents import qa_agent
    from src.tasks import (
        create_test_plan_task,
        create_e2e_tests_task,
        create_acceptance_verification_task,
    )

    test_plan = create_test_plan_task(pr_url, acceptance_criteria)
    e2e_tests = create_e2e_tests_task(test_cases, "Feature")
    acceptance = create_acceptance_verification_task(pr_url, acceptance_criteria, "{{test_results}}")

    return Crew(
        agents=[qa_agent],
        tasks=[test_plan, e2e_tests, acceptance],
        process=Process.sequential,
        verbose=verbose,
    )
