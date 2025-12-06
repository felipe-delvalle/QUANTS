# 🎯 AI Collaboration Goals

Shared goal tracker for Cursor and Codex Max 5 to collaborate on tasks until completion.

## How to Use

1. **Add a new goal** at the bottom using the template
2. **Update status** as work progresses (use `[STATUS]` tags)
3. **Both AIs check this file** before starting work
4. **Mark complete** when goal is resolved

### Status Tags
- `[NEW]` - Goal just created, not started
- `[IN_PROGRESS]` - Currently being worked on
- `[CURSOR_TURN]` - Waiting for Cursor to execute
- `[CODEX_TURN]` - Waiting for Codex to analyze/review
- `[BLOCKED]` - Needs user input or clarification
- `[COMPLETE]` - Goal resolved
- `[CANCELLED]` - Goal abandoned

### Template
```markdown
## Goal: [Title]
**Status:** [NEW|IN_PROGRESS|CURSOR_TURN|CODEX_TURN|BLOCKED|COMPLETE|CANCELLED]
**Created:** [YYYY-MM-DD HH:MM]
**Owner:** [User/Cursor/Codex/Both]

**Description:**
[Clear description of what needs to be accomplished]

**Success Criteria:**
- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Criterion 3

**Breakdown:**
1. [Task 1] - [Assigned to: Cursor/Codex]
2. [Task 2] - [Assigned to: Cursor/Codex]
3. [Task 3] - [Assigned to: Cursor/Codex]

**Progress Log:**
- [YYYY-MM-DD HH:MM] [Cursor/Codex]: [What was done]
- [YYYY-MM-DD HH:MM] [Cursor/Codex]: [What was done]

**Next Steps:**
[What needs to happen next and who should do it]
```

---

## Active Goals

### Example Goal (Template)
**Status:** [NEW]
**Created:** 2025-12-06 00:00
**Owner:** User

**Description:**
This is an example goal to show the format. Replace with your actual goals.

**Success Criteria:**
- [ ] Example criterion 1
- [ ] Example criterion 2

**Breakdown:**
1. Analyze requirements - Assigned to: Codex
2. Implement solution - Assigned to: Cursor
3. Review and test - Assigned to: Codex

**Progress Log:**
- [2025-12-06 00:00] User: Created example goal

**Next Steps:**
Codex should analyze the requirements first.

---

## Completed Goals

_(Goals will be moved here when marked [COMPLETE])_

---

## How Cursor and Codex Collaborate

### Workflow Pattern:
1. **User sets goal** → Adds entry here
2. **Codex analyzes** → Reviews goal, breaks it down, suggests approach
3. **Cursor executes** → Implements code changes, file operations
4. **Codex reviews** → Validates implementation, suggests improvements
5. **Iterate** → Repeat steps 3-4 until complete
6. **Mark complete** → Update status to [COMPLETE]

### Communication:
- Use `Work/codex_cursor_channel.md` for real-time coordination
- Update this file for goal tracking and progress
- Both AIs check both files before starting work

### Assignment Guidelines:
- **Codex handles:** Analysis, code review, architecture decisions, complex reasoning
- **Cursor handles:** File operations, code implementation, terminal commands, multi-step execution
- **Both:** Update progress logs, check for conflicts, coordinate handoffs

## Goal: Automated Financial Model Report Generator
**Status:** [CURSOR_TURN]
**Created:** 2025-12-06 00:11
**Owner:** User

**Description:**
Create an automated system that generates comprehensive PDF reports from the financial model, including executive summary, risk analysis, performance metrics, and visualizations. This will save hours of manual work and ensure consistent, professional reporting.

**Success Criteria:**
- [ ] CLI/command generates a PDF report from sample model outputs without manual edits
- [ ] Report includes sections for executive summary, risk analysis, performance metrics, and at least 2 charts
- [ ] Configurable inputs (model outputs path, as-of date, output path/filename) via config/CLI flags
- [ ] Smoke test or unit test passes, confirming generation and key sections present
- [ ] README or usage guide documents setup and run instructions
**Breakdown:**
1. Clarify model outputs schema and choose report stack (e.g., pandas + Jinja + WeasyPrint/LaTeX); define sections and KPIs - Assigned to: Codex
2. Scaffold project structure with sample data, config, and CLI entry point stub - Assigned to: Cursor
3. Implement data ingestion/transform layer to compute KPIs and risk metrics from sample model outputs - Assigned to: Cursor
4. Build report templates (exec summary, risk, performance, charts) and PDF rendering pipeline - Assigned to: Cursor
5. Add tests/smoke check plus example command; wire configs/flags for paths and as-of date - Assigned to: Cursor
6. Review implementation, validate criteria, and suggest refinements - Assigned to: Codex

**Progress Log:**
- [2025-12-06 00:11] User: Created goal
- [2025-12-06 01:05] Codex: Analyzed goal, proposed breakdown, set success criteria, and marked status to [CODEX_TURN]
- [2025-12-06 01:15] Cursor: Status updated to [CURSOR_TURN]. Starting implementation with project scaffolding.

**Next Steps:**
Cursor: start with scaffolding (sample data, config, CLI stub) then implement ingestion, templates, PDF pipeline, and tests. Codex will review after initial implementation.

---
