"""
GitHub API Client
Manages GitHub repository operations and project management
"""

try:
    from github import Github
    GITHUB_AVAILABLE = True
except ImportError:
    GITHUB_AVAILABLE = False
    Github = None

from typing import Dict, Any, Optional, List
import logging

logger = logging.getLogger(__name__)


class GitHubAPIClient:
    """Client for GitHub API using PyGithub"""

    def __init__(self, token: str):
        """
        Initialize GitHub API client

        Args:
            token: GitHub personal access token
        """
        if not GITHUB_AVAILABLE:
            raise ImportError("PyGithub not installed. Install with: pip install PyGithub")
        self.github = Github(token)
        self.user = self.github.get_user()

    def create_issue(
        self, repo_name: str, title: str, body: str, labels: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Create a GitHub issue

        Args:
            repo_name: Repository name (owner/repo)
            title: Issue title
            body: Issue body
            labels: Optional labels

        Returns:
            Created issue data
        """
        try:
            repo = self.github.get_repo(repo_name)
            issue = repo.create_issue(title=title, body=body, labels=labels or [])

            return {
                "number": issue.number,
                "title": issue.title,
                "state": issue.state,
                "url": issue.html_url,
                "created_at": issue.created_at.isoformat(),
            }
        except Exception as e:
            logger.error(f"Error creating issue: {e}")
            raise

    def get_repository_info(self, repo_name: str) -> Dict[str, Any]:
        """
        Get repository information

        Args:
            repo_name: Repository name (owner/repo)

        Returns:
            Repository information
        """
        try:
            repo = self.github.get_repo(repo_name)

            return {
                "name": repo.name,
                "full_name": repo.full_name,
                "description": repo.description,
                "stars": repo.stargazers_count,
                "forks": repo.forks_count,
                "language": repo.language,
                "created_at": repo.created_at.isoformat(),
                "updated_at": repo.updated_at.isoformat(),
                "url": repo.html_url,
            }
        except Exception as e:
            logger.error(f"Error fetching repo info: {e}")
            raise

    def create_file(
        self, repo_name: str, path: str, content: str, message: str
    ) -> Dict[str, Any]:
        """
        Create a file in repository

        Args:
            repo_name: Repository name
            path: File path
            content: File content
            message: Commit message

        Returns:
            Created file information
        """
        try:
            repo = self.github.get_repo(repo_name)
            repo.create_file(path, message, content)

            return {
                "path": path,
                "message": message,
                "status": "created",
            }
        except Exception as e:
            logger.error(f"Error creating file: {e}")
            raise

    def get_commits(self, repo_name: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent commits

        Args:
            repo_name: Repository name
            limit: Number of commits to retrieve

        Returns:
            List of commit information
        """
        try:
            repo = self.github.get_repo(repo_name)
            commits = list(repo.get_commits()[:limit])

            return [
                {
                    "sha": commit.sha,
                    "message": commit.commit.message,
                    "author": commit.commit.author.name,
                    "date": commit.commit.author.date.isoformat(),
                    "url": commit.html_url,
                }
                for commit in commits
            ]
        except Exception as e:
            logger.error(f"Error fetching commits: {e}")
            raise

    def create_release(
        self, repo_name: str, tag: str, name: str, body: str
    ) -> Dict[str, Any]:
        """
        Create a GitHub release

        Args:
            repo_name: Repository name
            tag: Release tag
            name: Release name
            body: Release notes

        Returns:
            Release information
        """
        try:
            repo = self.github.get_repo(repo_name)
            release = repo.create_git_release(tag, name, body)

            return {
                "tag": release.tag_name,
                "name": release.title,
                "url": release.html_url,
                "created_at": release.created_at.isoformat(),
            }
        except Exception as e:
            logger.error(f"Error creating release: {e}")
            raise
