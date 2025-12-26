#!/usr/bin/env python3
"""
Example: Integrating Teams Planner with Financial Engineering Project
Shows how to automate task creation based on project events
"""

import os
import sys
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from api_clients.teams_planner import TeamsPlannerClient


def create_analysis_task(client: TeamsPlannerClient, symbol: str, plan_id: str, bucket_id: str):
    """Create a task for analyzing a stock symbol"""
    task = client.create_task(
        plan_id=plan_id,
        bucket_id=bucket_id,
        title=f"Analyze {symbol}",
        notes=f"Perform full analysis including risk metrics, portfolio impact, and recommendations",
        due_date=(datetime.now() + timedelta(days=3)).isoformat(),
        priority=1,  # Important
        percent_complete=0
    )
    print(f"✓ Created task: {task['title']}")
    return task


def create_portfolio_review_task(client: TeamsPlannerClient, plan_id: str, bucket_id: str):
    """Create a recurring portfolio review task"""
    task = client.create_task(
        plan_id=plan_id,
        bucket_id=bucket_id,
        title="Weekly Portfolio Review",
        notes="Review portfolio performance, risk metrics, and rebalancing opportunities",
        due_date=(datetime.now() + timedelta(days=7)).isoformat(),
        priority=1,
        percent_complete=0
    )
    print(f"✓ Created task: {task['title']}")
    return task


def sync_project_goals(client: TeamsPlannerClient, plan_id: str, bucket_id: str):
    """Sync goals from ai_goals.md to Teams Planner"""
    goals_path = os.path.join(
        os.path.dirname(__file__),
        "..",
        "..",
        "ai_goals.md"
    )
    
    tasks = client.sync_goals_to_planner(
        plan_id=plan_id,
        bucket_id=bucket_id,
        goals_file_path=goals_path
    )
    
    print(f"✓ Synced {len(tasks)} tasks from goals file")
    return tasks


def update_task_progress(client: TeamsPlannerClient, task_id: str, progress: int):
    """Update task completion percentage"""
    client.update_task(
        task_id=task_id,
        percent_complete=progress
    )
    print(f"✓ Updated task {task_id} to {progress}% complete")


def main():
    """Example integration workflow"""
    print("Teams Planner Integration Example")
    print("=" * 50)
    
    # Initialize client
    client = TeamsPlannerClient()
    
    # Get IDs from environment (set these in .env)
    plan_id = os.getenv("MS_PLAN_ID")
    bucket_id = os.getenv("MS_BUCKET_ID")
    
    if not plan_id or not bucket_id:
        print("⚠️  Set MS_PLAN_ID and MS_BUCKET_ID in .env to run examples")
        return
    
    # Example 1: Create analysis tasks for symbols
    print("\n1. Creating analysis tasks...")
    symbols = ["AAPL", "GOOGL", "MSFT"]
    for symbol in symbols:
        create_analysis_task(client, symbol, plan_id, bucket_id)
    
    # Example 2: Create recurring review task
    print("\n2. Creating portfolio review task...")
    create_portfolio_review_task(client, plan_id, bucket_id)
    
    # Example 3: Sync goals from ai_goals.md
    print("\n3. Syncing project goals...")
    sync_project_goals(client, plan_id, bucket_id)
    
    # Example 4: List all tasks
    print("\n4. Listing all tasks...")
    tasks = client.get_tasks(plan_id=plan_id)
    print(f"Total tasks: {len(tasks)}")
    for task in tasks[:5]:  # Show first 5
        print(f"  - {task['title']} ({task.get('percentComplete', 0)}%)")
    
    print("\n" + "=" * 50)
    print("Integration examples completed!")


if __name__ == "__main__":
    main()











