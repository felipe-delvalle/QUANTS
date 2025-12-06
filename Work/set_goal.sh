#!/bin/bash

# ============================================================
# Set Goal for AI Collaboration
# ============================================================
# Quick script to add a new goal to ai_goals.md
#
# Usage:
#   ./set_goal.sh "Goal Title" "Description"
#   ./set_goal.sh "Goal Title" "Description" "Success criteria line 1|Success criteria line 2"
# ============================================================

GOALS_FILE="/Users/freedom/QUANTS/Work/ai_goals.md"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M')

if [ -z "$1" ] || [ -z "$2" ]; then
    echo "Usage: $0 \"Goal Title\" \"Description\" [\"Success criteria 1|Success criteria 2\"]"
    exit 1
fi

GOAL_TITLE="$1"
GOAL_DESC="$2"
SUCCESS_CRITERIA="${3:-}"

# Create success criteria list
CRITERIA_LIST=""
if [ -n "$SUCCESS_CRITERIA" ]; then
    IFS='|' read -ra CRITERIA <<< "$SUCCESS_CRITERIA"
    for criterion in "${CRITERIA[@]}"; do
        CRITERIA_LIST="${CRITERIA_LIST}- [ ] ${criterion}\n"
    done
else
    CRITERIA_LIST="- [ ] Goal completed successfully\n"
fi

# Create goal entry
GOAL_ENTRY="
## Goal: ${GOAL_TITLE}
**Status:** [NEW]
**Created:** ${TIMESTAMP}
**Owner:** User

**Description:**
${GOAL_DESC}

**Success Criteria:**
${CRITERIA_LIST}
**Breakdown:**
_To be determined by Codex after analysis_

**Progress Log:**
- [${TIMESTAMP}] User: Created goal

**Next Steps:**
Codex should analyze this goal and break it down into tasks.

---"

# Append to goals file
echo "$GOAL_ENTRY" >> "$GOALS_FILE"

echo "✅ Goal added to $GOALS_FILE"
echo ""
echo "📋 Next step: Ask Codex to analyze and break it down:"
echo "   @file Work/ai_goals.md Review the new goal \"${GOAL_TITLE}\" and break it down into tasks. Assign tasks to Cursor or Codex."
echo ""
echo "💡 Or ask Cursor:"
echo "   Check ai_goals.md and start working on the new goal"
