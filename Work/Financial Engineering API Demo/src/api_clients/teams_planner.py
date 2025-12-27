"""
Microsoft Teams Planner API Client
Manages tasks, plans, and buckets in Microsoft Teams Planner via Microsoft Graph API
"""

import os
import json
from typing import Dict, Any, Optional, List
import logging
import requests
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

try:
    from msal import ConfidentialClientApplication, PublicClientApplication
    MSAL_AVAILABLE = True
except ImportError:
    MSAL_AVAILABLE = False
    ConfidentialClientApplication = None
    PublicClientApplication = None


class TeamsPlannerClient:
    """Client for Microsoft Teams Planner using Microsoft Graph API"""

    GRAPH_API_BASE = "https://graph.microsoft.com/v1.0"
    
    # Required permissions for Teams Planner
    REQUIRED_SCOPES = [
        "Tasks.ReadWrite",
        "Group.ReadWrite.All",
        "User.Read"
    ]

    def __init__(
        self,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        tenant_id: Optional[str] = None,
        access_token: Optional[str] = None,
        auth_mode: str = "client_credentials"  # or "delegated"
    ):
        """
        Initialize Teams Planner API client

        Args:
            client_id: Azure AD Application (Client) ID
            client_secret: Azure AD Application Secret (for client_credentials)
            tenant_id: Azure AD Tenant ID
            access_token: Pre-obtained access token (optional)
            auth_mode: "client_credentials" or "delegated"
        """
        self.client_id = client_id or os.getenv("MS_CLIENT_ID")
        self.client_secret = client_secret or os.getenv("MS_CLIENT_SECRET")
        self.tenant_id = tenant_id or os.getenv("MS_TENANT_ID")
        self.auth_mode = auth_mode
        self.access_token = access_token
        self.token_expires_at = None
        
        if not MSAL_AVAILABLE and not access_token:
            logger.warning(
                "msal library not installed. Install with: pip install msal\n"
                "Or provide an access_token directly."
            )

    def _get_access_token(self) -> str:
        """Get or refresh access token"""
        if self.access_token and self.token_expires_at:
            if datetime.now() < self.token_expires_at:
                return self.access_token

        if not MSAL_AVAILABLE:
            raise ImportError(
                "msal library required for authentication. "
                "Install with: pip install msal"
            )

        if self.auth_mode == "client_credentials":
            return self._get_client_credentials_token()
        else:
            raise ValueError(
                "Delegated auth not yet implemented. "
                "Use client_credentials or provide access_token."
            )

    def _get_client_credentials_token(self) -> str:
        """Get access token using client credentials flow"""
        if not all([self.client_id, self.client_secret, self.tenant_id]):
            raise ValueError(
                "Missing required credentials: client_id, client_secret, tenant_id"
            )

        authority = f"https://login.microsoftonline.com/{self.tenant_id}"
        app = ConfidentialClientApplication(
            client_id=self.client_id,
            client_credential=self.client_secret,
            authority=authority
        )

        result = app.acquire_token_for_client(scopes=["https://graph.microsoft.com/.default"])
        
        if "access_token" not in result:
            raise ValueError(f"Failed to acquire token: {result.get('error_description', 'Unknown error')}")

        self.access_token = result["access_token"]
        expires_in = result.get("expires_in", 3600)
        self.token_expires_at = datetime.now() + timedelta(seconds=expires_in - 300)  # 5 min buffer
        
        return self.access_token

    def _get_headers(self) -> Dict[str, str]:
        """Get request headers with authentication"""
        token = self._get_access_token()
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None,
        params: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Make HTTP request to Microsoft Graph API"""
        url = f"{self.GRAPH_API_BASE}/{endpoint.lstrip('/')}"
        headers = self._get_headers()

        try:
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                json=data,
                params=params,
                timeout=30
            )
            response.raise_for_status()
            
            # Handle empty responses
            if response.status_code == 204 or not response.content:
                return {}
            
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Graph API request failed: {e}")
            if hasattr(e.response, 'text'):
                logger.error(f"Response: {e.response.text}")
            raise

    # Plan Operations
    def get_plans(self, group_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get all plans for a group or user

        Args:
            group_id: Microsoft 365 Group ID (optional, uses /me/planner/plans if not provided)

        Returns:
            List of plan dictionaries
        """
        if group_id:
            endpoint = f"groups/{group_id}/planner/plans"
        else:
            endpoint = "me/planner/plans"
        
        result = self._make_request("GET", endpoint)
        return result.get("value", [])

    def get_plan(self, plan_id: str) -> Dict[str, Any]:
        """Get a specific plan by ID"""
        return self._make_request("GET", f"planner/plans/{plan_id}")

    def create_plan(
        self,
        title: str,
        owner_id: str,
        group_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a new plan

        Args:
            title: Plan title
            owner_id: Owner ID (user or group)
            group_id: Microsoft 365 Group ID (optional)

        Returns:
            Created plan data
        """
        data = {
            "title": title,
            "owner": owner_id
        }
        
        if group_id:
            endpoint = f"groups/{group_id}/planner/plans"
        else:
            endpoint = "planner/plans"
        
        return self._make_request("POST", endpoint, data=data)

    # Bucket Operations
    def get_buckets(self, plan_id: str) -> List[Dict[str, Any]]:
        """Get all buckets for a plan"""
        result = self._make_request("GET", f"planner/plans/{plan_id}/buckets")
        return result.get("value", [])

    def create_bucket(
        self,
        plan_id: str,
        name: str,
        order_hint: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a new bucket in a plan

        Args:
            plan_id: Plan ID
            name: Bucket name
            order_hint: Order hint for positioning

        Returns:
            Created bucket data
        """
        data = {
            "name": name,
            "planId": plan_id
        }
        if order_hint:
            data["orderHint"] = order_hint

        return self._make_request("POST", "planner/buckets", data=data)

    # Task Operations
    def get_tasks(self, plan_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get all tasks, optionally filtered by plan

        Args:
            plan_id: Optional plan ID to filter tasks

        Returns:
            List of task dictionaries
        """
        if plan_id:
            endpoint = f"planner/plans/{plan_id}/tasks"
        else:
            endpoint = "me/planner/tasks"
        
        result = self._make_request("GET", endpoint)
        return result.get("value", [])

    def get_task(self, task_id: str) -> Dict[str, Any]:
        """Get a specific task by ID"""
        return self._make_request("GET", f"planner/tasks/{task_id}")

    def create_task(
        self,
        plan_id: str,
        bucket_id: str,
        title: str,
        due_date: Optional[str] = None,
        assigned_to: Optional[List[str]] = None,
        notes: Optional[str] = None,
        priority: int = 5,  # 0=urgent, 1=important, 3=medium, 5=low
        percent_complete: int = 0
    ) -> Dict[str, Any]:
        """
        Create a new task in a plan

        Args:
            plan_id: Plan ID
            bucket_id: Bucket ID
            title: Task title
            due_date: Due date in ISO format (YYYY-MM-DDTHH:MM:SS)
            assigned_to: List of user IDs to assign task to
            notes: Task notes/description
            priority: Priority (0=urgent, 1=important, 3=medium, 5=low)
            percent_complete: Completion percentage (0-100)

        Returns:
            Created task data
        """
        data = {
            "planId": plan_id,
            "bucketId": bucket_id,
            "title": title,
            "percentComplete": percent_complete,
            "priority": priority
        }

        if due_date:
            data["dueDateTime"] = due_date
        if notes:
            data["notes"] = notes
        if assigned_to:
            data["assignments"] = {
                user_id: {
                    "@odata.type": "microsoft.graph.plannerAssignment",
                    "orderHint": " !"
                }
                for user_id in assigned_to
            }

        return self._make_request("POST", "planner/tasks", data=data)

    def update_task(
        self,
        task_id: str,
        title: Optional[str] = None,
        due_date: Optional[str] = None,
        percent_complete: Optional[int] = None,
        priority: Optional[int] = None,
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """Update an existing task"""
        data = {}
        if title:
            data["title"] = title
        if due_date:
            data["dueDateTime"] = due_date
        if percent_complete is not None:
            data["percentComplete"] = percent_complete
        if priority is not None:
            data["priority"] = priority
        if notes:
            data["notes"] = notes

        if not data:
            raise ValueError("At least one field must be provided for update")

        return self._make_request("PATCH", f"planner/tasks/{task_id}", data=data)

    def delete_task(self, task_id: str) -> bool:
        """Delete a task"""
        try:
            self._make_request("DELETE", f"planner/tasks/{task_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete task: {e}")
            return False

    # Convenience Methods
    def sync_goals_to_planner(
        self,
        plan_id: str,
        bucket_id: str,
        goals_file_path: str = "../ai_goals.md"
    ) -> List[Dict[str, Any]]:
        """
        Sync goals from ai_goals.md to Teams Planner

        Args:
            plan_id: Plan ID to create tasks in
            bucket_id: Bucket ID to create tasks in
            goals_file_path: Path to ai_goals.md file

        Returns:
            List of created task dictionaries
        """
        import re
        from pathlib import Path

        goals_path = Path(goals_file_path)
        if not goals_path.exists():
            logger.warning(f"Goals file not found: {goals_path}")
            return []

        content = goals_path.read_text()
        created_tasks = []

        # Parse goals (simple markdown parsing)
        goal_pattern = r"## Goal: (.+?)\n\*\*Status:\*\* \[(.+?)\].*?\*\*Description:\*\*\n(.+?)(?=\n##|$)"
        goals = re.findall(goal_pattern, content, re.DOTALL)

        for title, status, description in goals:
            # Skip completed/cancelled goals
            if status in ["COMPLETE", "CANCELLED"]:
                continue

            # Determine priority based on status
            priority_map = {
                "IN_PROGRESS": 1,  # Important
                "CURSOR_TURN": 1,
                "CODEX_TURN": 3,  # Medium
                "BLOCKED": 5,  # Low
                "NEW": 3
            }
            priority = priority_map.get(status, 5)

            # Create task
            try:
                task = self.create_task(
                    plan_id=plan_id,
                    bucket_id=bucket_id,
                    title=title.strip(),
                    notes=description.strip()[:500],  # Limit notes length
                    priority=priority,
                    percent_complete=50 if status == "IN_PROGRESS" else 0
                )
                created_tasks.append(task)
                logger.info(f"Created task: {title}")
            except Exception as e:
                logger.error(f"Failed to create task '{title}': {e}")

        return created_tasks












