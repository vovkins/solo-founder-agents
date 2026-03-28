"""Tests for GitHub tools."""

import pytest
from unittest.mock import Mock, patch

from src.tools.github_client import GitHubClient


class TestGitHubClient:
    """Tests for GitHubClient."""

    @patch("src.tools.github_client.Github")
    def test_get_issue(self, mock_github):
        """Test getting an issue by number."""
        client = GitHubClient()
        client._repo = Mock()

        mock_issue = Mock()
        mock_issue.number = 1
        mock_issue.title = "Test Issue"
        client.repo.get_issue.return_value = mock_issue

        result = client.get_issue(1)

        assert result.number == 1
        assert result.title == "Test Issue"
        client.repo.get_issue.assert_called_once_with(1)

    @patch("src.tools.github_client.Github")
    def test_create_issue(self, mock_github):
        """Test creating an issue."""
        client = GitHubClient()
        client._repo = Mock()

        mock_issue = Mock()
        mock_issue.number = 2
        mock_issue.html_url = "https://github.com/test/test/issues/2"
        client.repo.create_issue.return_value = mock_issue

        result = client.create_issue(
            title="New Issue",
            body="Issue body",
            labels=["bug"],
        )

        assert result.number == 2
        client.repo.create_issue.assert_called_once()


class TestGitHubTools:
    """Tests for GitHub tools."""

    @patch("src.tools.github_tools.github_client")
    def test_create_github_issue(self, mock_client):
        """Test create_github_issue tool."""
        from src.tools.github_tools import create_github_issue

        mock_issue = Mock()
        mock_issue.html_url = "https://github.com/test/test/issues/1"
        mock_client.create_issue.return_value = mock_issue

        result = create_github_issue("Title", "Body", ["bug"])

        assert result == "https://github.com/test/test/issues/1"

    @patch("src.tools.github_tools.github_client")
    def test_close_issue(self, mock_client):
        """Test close_issue tool."""
        from src.tools.github_tools import close_issue

        mock_issue = Mock()
        mock_issue.html_url = "https://github.com/test/test/issues/1"
        mock_client.update_issue.return_value = mock_issue

        result = close_issue(1)

        mock_client.update_issue.assert_called_once_with(1, state="closed")
