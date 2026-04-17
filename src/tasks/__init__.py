"""Tasks package for CrewAI agents."""

from .pm_tasks import (
    create_collect_requirements_task,
    create_prd_task,
    create_backlog_task,
    create_prioritize_backlog_task,
)
from .analyst_tasks import (
    create_analyze_backlog_task,
    create_decompose_epics_task,
    create_task_specs_task,
    create_dependency_map_task,
    create_sprint_recommendations_task,
)
from .architect_tasks import (
    create_analyze_requirements_task,
    create_design_architecture_task,
    create_adr_task,
    create_system_design_task,
    create_standards_task,
    create_api_spec_task,
)
from .designer_tasks import (
    create_design_system_task,
    create_ui_screen_task,
    create_user_flow_task,
    create_component_spec_task,
    create_all_screens_task,
)
from .developer_tasks import (
    create_analyze_task_task,
    create_feature_branch_task,
    create_implement_feature_task,
    create_write_tests_task,
    create_pull_request_task,
    create_fix_review_comments_task,
)
from .reviewer_tasks import (
    create_review_pr_task,
    create_check_standards_task,
    create_security_check_task,
    create_review_tests_task,
    create_approval_task,
)
from .qa_tasks import (
    create_test_plan_task,
    create_code_verification_task,
    create_qa_signoff_task,
)
from .tech_writer_tasks import (
    create_readme_task,
    create_changelog_task,
)

__all__ = [
    # PM Tasks
    "create_collect_requirements_task",
    "create_prd_task",
    "create_backlog_task",
    "create_prioritize_backlog_task",
    # Analyst Tasks
    "create_analyze_backlog_task",
    "create_decompose_epics_task",
    "create_task_specs_task",
    "create_dependency_map_task",
    "create_sprint_recommendations_task",
    # Architect Tasks
    "create_analyze_requirements_task",
    "create_design_architecture_task",
    "create_adr_task",
    "create_system_design_task",
    "create_standards_task",
    "create_api_spec_task",
    # Designer Tasks
    "create_design_system_task",
    "create_ui_screen_task",
    "create_user_flow_task",
    "create_component_spec_task",
    "create_all_screens_task",
    # Developer Tasks
    "create_analyze_task_task",
    "create_feature_branch_task",
    "create_implement_feature_task",
    "create_write_tests_task",
    "create_pull_request_task",
    "create_fix_review_comments_task",
    # Reviewer Tasks
    "create_review_pr_task",
    "create_check_standards_task",
    "create_security_check_task",
    "create_review_tests_task",
    "create_approval_task",
    # QA Tasks
    "create_test_plan_task",
    "create_code_verification_task",
    "create_qa_signoff_task",
    # Tech Writer Tasks
    "create_readme_task",
    "create_changelog_task",
]
