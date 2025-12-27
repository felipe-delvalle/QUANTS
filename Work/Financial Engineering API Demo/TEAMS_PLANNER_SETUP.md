# Microsoft Teams Planner Automation Setup

This guide explains how to set up automation with Microsoft Teams Planner using the Microsoft Graph API.

## Overview

The Teams Planner integration allows you to:
- ✅ Create tasks, plans, and buckets programmatically
- ✅ Sync project goals from `ai_goals.md` to Teams Planner
- ✅ Automate task management workflows
- ✅ Integrate with your Financial Engineering API Demo project

## Prerequisites

1. **Microsoft 365 Account** with Teams access
2. **Azure AD Application** (App Registration)
3. **Python dependencies**: `msal` library

## Step 1: Create Azure AD Application

1. Go to [Azure Portal](https://portal.azure.com)
2. Navigate to **Azure Active Directory** → **App registrations**
3. Click **New registration**
4. Fill in:
   - **Name**: `Financial Engineering Teams Planner`
   - **Supported account types**: Your organization only
   - **Redirect URI**: Leave blank for now
5. Click **Register**

## Step 2: Configure API Permissions

1. In your app registration, go to **API permissions**
2. Click **Add a permission** → **Microsoft Graph** → **Application permissions**
3. Add these permissions:
   - `Group.ReadWrite.All` (Application)
   - `Tasks.ReadWrite` (Application)
   - `User.Read.All` (Application) - if needed
4. Click **Grant admin consent** (requires admin approval)

## Step 3: Create Client Secret

1. Go to **Certificates & secrets**
2. Click **New client secret**
3. Add description: `Teams Planner Automation`
4. Set expiration (recommend 24 months)
5. Click **Add**
6. **IMPORTANT**: Copy the secret value immediately (you won't see it again!)

## Step 4: Get Required IDs

You'll need:
- **Application (Client) ID**: Found on the app registration **Overview** page
- **Directory (Tenant) ID**: Found on the app registration **Overview** page
- **Client Secret**: From Step 3

## Step 5: Get Microsoft 365 Group ID

To create plans, you need a Microsoft 365 Group:

1. Go to [Microsoft 365 Admin Center](https://admin.microsoft.com)
2. Navigate to **Teams** → **Active teams and groups**
3. Find your team/group and note the **Group ID** (or Object ID)

Alternatively, use PowerShell:
```powershell
Get-MgGroup | Select-Object DisplayName, Id
```

## Step 6: Configure Environment Variables

Add to your `.env` file:

```env
# Microsoft Teams Planner / Graph API
MS_CLIENT_ID=your-application-client-id
MS_CLIENT_SECRET=your-client-secret-value
MS_TENANT_ID=your-tenant-id
MS_GROUP_ID=your-microsoft-365-group-id

# Optional: If you already have a plan and bucket
MS_PLAN_ID=your-plan-id
MS_BUCKET_ID=your-bucket-id
```

## Step 7: Install Dependencies

```bash
pip install msal
# Or install all requirements
pip install -r requirements.txt
```

## Step 8: Test the Integration

Run the demo script:

```bash
python demo_teams_planner.py
```

## Usage Examples

### Create a Task

```python
from api_clients.teams_planner import TeamsPlannerClient

client = TeamsPlannerClient()

task = client.create_task(
    plan_id="your-plan-id",
    bucket_id="your-bucket-id",
    title="Implement new feature",
    notes="Description of the task",
    priority=1,  # 0=urgent, 1=important, 3=medium, 5=low
    due_date="2024-12-31T23:59:59"
)
```

### Sync Goals from ai_goals.md

```python
client = TeamsPlannerClient()

tasks = client.sync_goals_to_planner(
    plan_id="your-plan-id",
    bucket_id="your-bucket-id",
    goals_file_path="../ai_goals.md"
)
```

### List All Plans

```python
client = TeamsPlannerClient()
plans = client.get_plans()
for plan in plans:
    print(f"{plan['title']}: {plan['id']}")
```

### Update Task Progress

```python
client = TeamsPlannerClient()
client.update_task(
    task_id="task-id",
    percent_complete=75,
    priority=3
)
```

## Authentication Methods

### Method 1: Client Credentials (Recommended for Automation)

Uses application permissions. Best for server-side automation.

```python
client = TeamsPlannerClient(
    client_id="...",
    client_secret="...",
    tenant_id="...",
    auth_mode="client_credentials"
)
```

### Method 2: Access Token (Direct)

If you already have an access token:

```python
client = TeamsPlannerClient(access_token="your-token")
```

## Troubleshooting

### Error: "Insufficient privileges"
- Ensure admin consent was granted for all permissions
- Check that permissions are **Application** permissions (not Delegated)

### Error: "Invalid client secret"
- Verify the secret value is correct (no extra spaces)
- Check if the secret has expired

### Error: "Group not found"
- Verify the Group ID is correct
- Ensure the app has `Group.ReadWrite.All` permission
- Check that admin consent was granted

### Error: "Plan creation failed"
- Ensure you're using a Microsoft 365 Group ID (not a regular group)
- Verify the group has Planner enabled

## Security Best Practices

1. **Never commit secrets** to version control
2. **Use environment variables** for all credentials
3. **Rotate secrets** regularly
4. **Use least privilege** - only grant necessary permissions
5. **Monitor API usage** in Azure Portal

## API Rate Limits

Microsoft Graph API has rate limits:
- **10,000 requests per 10 minutes** per app
- The client includes rate limiting, but be mindful of bulk operations

## Next Steps

- Integrate with your CI/CD pipeline
- Set up scheduled syncs from `ai_goals.md`
- Create automated workflows based on project events
- Build custom dashboards using Planner data

## Resources

- [Microsoft Graph API Documentation](https://learn.microsoft.com/en-us/graph/api/resources/planner-overview)
- [MSAL Python Documentation](https://msal-python.readthedocs.io/)
- [Planner API Reference](https://learn.microsoft.com/en-us/graph/api/resources/planner-overview)












