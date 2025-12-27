#!/usr/bin/env python3
"""
Microsoft Teams Planner Automation Demo
Demonstrates creating tasks, plans, and syncing with project goals
"""

import os
import sys
import logging
from dotenv import load_dotenv
from datetime import datetime, timedelta

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from api_clients.teams_planner import TeamsPlannerClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()


def demo_list_plans():
    """List all available plans"""
    logger.info("=== Listing Plans ===")
    
    client = TeamsPlannerClient()
    
    try:
        plans = client.get_plans()
        logger.info(f"Found {len(plans)} plans:")
        for plan in plans:
            logger.info(f"  - {plan.get('title')} (ID: {plan.get('id')})")
        return plans
    except Exception as e:
        logger.error(f"Error listing plans: {e}")
        return []


def demo_create_plan():
    """Create a new plan"""
    logger.info("=== Creating Plan ===")
    
    client = TeamsPlannerClient()
    
    # You'll need to provide a group_id or owner_id
    # For demo purposes, we'll show the structure
    try:
        # Note: You need a Microsoft 365 Group ID for this
        group_id = os.getenv("MS_GROUP_ID")
        if not group_id:
            logger.warning(
                "MS_GROUP_ID not set. Skipping plan creation.\n"
                "To create a plan, you need a Microsoft 365 Group ID."
            )
            return None
        
        plan = client.create_plan(
            title="Financial Engineering Project",
            owner_id=group_id,
            group_id=group_id
        )
        logger.info(f"Created plan: {plan.get('title')} (ID: {plan.get('id')})")
        return plan
    except Exception as e:
        logger.error(f"Error creating plan: {e}")
        return None


def demo_create_bucket(plan_id: str):
    """Create a bucket in a plan"""
    logger.info("=== Creating Bucket ===")
    
    client = TeamsPlannerClient()
    
    try:
        bucket = client.create_bucket(
            plan_id=plan_id,
            name="Active Tasks"
        )
        logger.info(f"Created bucket: {bucket.get('name')} (ID: {bucket.get('id')})")
        return bucket
    except Exception as e:
        logger.error(f"Error creating bucket: {e}")
        return None


def demo_create_task(plan_id: str, bucket_id: str):
    """Create a task in a plan"""
    logger.info("=== Creating Task ===")
    
    client = TeamsPlannerClient()
    
    try:
        # Create a task with due date
        due_date = (datetime.now() + timedelta(days=7)).isoformat()
        
        task = client.create_task(
            plan_id=plan_id,
            bucket_id=bucket_id,
            title="Implement Teams Planner Integration",
            notes="Automate task creation from project goals",
            due_date=due_date,
            priority=1,  # Important
            percent_complete=0
        )
        logger.info(f"Created task: {task.get('title')} (ID: {task.get('id')})")
        return task
    except Exception as e:
        logger.error(f"Error creating task: {e}")
        return None


def demo_sync_goals(plan_id: str, bucket_id: str):
    """Sync goals from ai_goals.md to Teams Planner"""
    logger.info("=== Syncing Goals to Planner ===")
    
    client = TeamsPlannerClient()
    
    try:
        # Path to ai_goals.md (adjust as needed)
        goals_path = os.path.join(
            os.path.dirname(__file__),
            "..",
            "ai_goals.md"
        )
        
        tasks = client.sync_goals_to_planner(
            plan_id=plan_id,
            bucket_id=bucket_id,
            goals_file_path=goals_path
        )
        
        logger.info(f"Synced {len(tasks)} tasks from goals file")
        for task in tasks:
            logger.info(f"  - {task.get('title')}")
        
        return tasks
    except Exception as e:
        logger.error(f"Error syncing goals: {e}")
        return []


def demo_list_tasks(plan_id: str = None):
    """List all tasks, optionally filtered by plan"""
    logger.info("=== Listing Tasks ===")
    
    client = TeamsPlannerClient()
    
    try:
        tasks = client.get_tasks(plan_id=plan_id)
        logger.info(f"Found {len(tasks)} tasks:")
        for task in tasks:
            status = "✓" if task.get('percentComplete', 0) == 100 else "○"
            logger.info(
                f"  {status} {task.get('title')} "
                f"({task.get('percentComplete', 0)}% complete)"
            )
        return tasks
    except Exception as e:
        logger.error(f"Error listing tasks: {e}")
        return []


def main():
    """Main demo function"""
    logger.info("Microsoft Teams Planner Automation Demo")
    logger.info("=" * 50)
    
    # Check if credentials are set
    if not all([
        os.getenv("MS_CLIENT_ID"),
        os.getenv("MS_CLIENT_SECRET"),
        os.getenv("MS_TENANT_ID")
    ]):
        logger.warning(
            "Microsoft credentials not set in .env file.\n"
            "Required: MS_CLIENT_ID, MS_CLIENT_SECRET, MS_TENANT_ID\n"
            "See TEAMS_PLANNER_SETUP.md for setup instructions."
        )
        return
    
    # List existing plans
    plans = demo_list_plans()
    
    # If you have a plan ID, you can use it for further operations
    plan_id = os.getenv("MS_PLAN_ID")
    bucket_id = os.getenv("MS_BUCKET_ID")
    
    if plan_id and bucket_id:
        # Create a sample task
        demo_create_task(plan_id, bucket_id)
        
        # Sync goals from ai_goals.md
        demo_sync_goals(plan_id, bucket_id)
        
        # List all tasks
        demo_list_tasks(plan_id=plan_id)
    else:
        logger.info(
            "\nTo run full demo, set in .env:\n"
            "  MS_PLAN_ID=your-plan-id\n"
            "  MS_BUCKET_ID=your-bucket-id\n"
            "\nOr create a new plan and bucket first."
        )
    
    logger.info("=" * 50)
    logger.info("Demo completed!")


if __name__ == "__main__":
    main()












