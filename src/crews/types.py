"""Standard types for crew results.

FIX: Standardized return types across all crews.
"""

from typing import TypedDict, Optional, Dict, List, Any


class CrewResult(TypedDict, total=False):
    """Standard return type for all crew runners.
    
    Required fields:
        - status: completed or error
    
    Optional fields:
        - result: String representation of crew output
        - error: Error message if status == error
        - artifacts: Dict of artifact_name -> path
        - metadata: Additional metadata (issue_number, pr_url, etc.)
    """
    status: str
    result: Optional[str]
    error: Optional[str]
    artifacts: Optional[Dict[str, str]]
    metadata: Optional[Dict[str, Any]]


# Example usage:
# {
#     status: completed,
#     result: PRD created successfully,
#     artifacts: {
#         prd: docs/requirements/prd.md,
#         backlog: docs/requirements/backlog.md
#     },
#     metadata: {
#         issues_created: 5,
#         duration_seconds: 120
#     }
# }
