"""Tasks for Developer (Coder) agent."""

from crewai import Task

from src.agents import get_developer_agent


def create_analyze_task_task(issue_number: int) -> Task:
    """Create task for analyzing task specifications from GitHub.

    Args:
        issue_number: GitHub Issue number

    Returns:
        Task for issue analysis
    """
    return Task(
        description=f"""
        Analyze task specifications for implementation.

        Your job is to:
        1. Read task specifications from docs/requirements/task-specs.md in GitHub
        2. Read the related GitHub Issue #{issue_number} for context
        3. Review System Design (docs/design/system-design.md) and ADRs
        4. Read the Design System (docs/design/design-system.md) for UI guidance
        5. Identify dependencies and implementation order
        6. Plan which files need to be created

        To determine which task is not yet implemented:
        - Read existing files in src/ directory using read_artifact or list_my_files tool
        - A task is considered implemented if its main source files already exist in src/
        - Focus on the FIRST task that is NOT yet implemented
        - Prioritize tasks marked as P0 or P1
        - If you cannot determine which tasks are done, start with the first P0 task

        Output a detailed implementation plan including:
        - Which task you will implement
        - List of files to create with their paths
        - Implementation approach
        - Dependencies on other files/components
        """,
        expected_output="Detailed implementation plan: which task, files to create, approach",
        output_key="implementation_plan",
        agent=get_developer_agent(),
    )


def create_implement_feature_task() -> Task:
    """Create task for implementing a feature.

    The implementation_plan is passed from the previous task via output_key.

    Returns:
        Task for implementation
    """
    return Task(
        description="""
        Implement the feature according to the plan from the analysis step.

        Follow the implementation plan from the previous task.

        Your job is to:
        1. Create source code files using the save_artifact tool
        2. For TypeScript/JavaScript files, use artifact_type="source-code" with name parameter for the file path
        3. Follow coding standards (TypeScript strict, functional React, proper error handling)
        4. Include JSDoc comments for functions
        5. Handle errors appropriately
        6. Add logging where needed

        IMPORTANT: Save ALL code files to GitHub using save_artifact tool.
        Do NOT use git commands. The save_artifact tool handles file persistence.

        Example:
        save_artifact("source-code", "import React from 'react'...", name="components/LoginScreen.tsx")
        save_artifact("source-code", "export interface User {...}", name="types/User.ts")

        Ensure code is clean, readable, and maintainable.
        """,
        expected_output="List of files created and saved to GitHub",
        output_key="files_created",
        agent=get_developer_agent(),
    )


def create_write_tests_task() -> Task:
    """Create task for writing unit tests.

    The files_created is passed from the previous task via output_key.

    Returns:
        Task for test writing
    """
    return Task(
        description="""
        Write unit tests for the implemented feature.

        Based on the files created in the previous step, write corresponding tests.

        Your job is to:
        1. For each source file created, create a test file (e.g., Component.tsx -> Component.test.tsx)
        2. Use save_artifact with artifact_type="source-code" and name parameter for test files
        3. Test all functions and components
        4. Cover edge cases
        5. Test error handling
        6. Ensure tests are meaningful

        Testing Guidelines:
        - Use Jest and React Testing Library
        - Test behavior, not implementation
        - Use descriptive test names
        - Arrange-Act-Assert pattern
        - Mock external dependencies

        Example:
        save_artifact("source-code", "import { render } from '@testing-library/react'...", name="components/__tests__/LoginScreen.test.tsx")
        """,
        expected_output="List of test files created and saved to GitHub",
        agent=get_developer_agent(),
    )


def create_fix_review_comments_task(
    review_comments: str,
) -> Task:
    """Create task for addressing review comments.

    Args:
        review_comments: Comments from reviewer

    Returns:
        Task for fixing comments
    """
    return Task(
        description=f"""
        Address review comments.

        Review Comments:
        {review_comments}

        Your job is to:
        1. Read each comment
        2. Update files using save_artifact tool
        3. Do NOT use git commands — save_artifact handles persistence

        Guidelines:
        - Accept valid suggestions
        - Explain reasoning if you disagree
        - Keep changes minimal
        - Update tests if needed
        """,
        expected_output="Review comments addressed, files updated in GitHub",
        agent=get_developer_agent(),
    )
