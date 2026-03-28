"""Utility functions for Solo Founder Agents."""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict


def save_json(data: Dict[str, Any], path: Path) -> None:
    """Save data to JSON file.

    Args:
        data: Dictionary to save
        path: File path
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def load_json(path: Path) -> Dict[str, Any]:
    """Load data from JSON file.

    Args:
        path: File path

    Returns:
        Loaded dictionary
    """
    if not path.exists():
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def format_datetime(dt: datetime) -> str:
    """Format datetime for display.

    Args:
        dt: Datetime object

    Returns:
        Formatted string
    """
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def truncate_text(text: str, max_length: int = 100) -> str:
    """Truncate text to max length.

    Args:
        text: Text to truncate
        max_length: Maximum length

    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."
