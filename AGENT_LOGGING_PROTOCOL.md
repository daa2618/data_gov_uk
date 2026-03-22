# Agent Logging & Traceability Protocol

## Purpose

This document defines a **mandatory logging protocol** for any autonomous or semi-autonomous agent operating inside this repository or workspace.

The goals are:

- Full **traceability** of agent actions  
- Persistent **institutional memory** of bugs, fixes, and decisions  
- Prevention of repeated mistakes  
- Clear documentation for future agents or human reviewers  

Failure to comply with this protocol is considered a task failure.

---

## Scope

This protocol applies to **any agent** that:

- Writes or modifies code
- Changes configuration
- Installs dependencies
- Runs experiments
- Performs refactors
- Debugging or troubleshooting
- Generates documentation
- Alters data or directory structures

---

## Mandatory Directory Structure

### 1. Agent Logs Directory

The agent **must ensure** the following directory exists at repository root:

```text
agent_logs/
```

#### Creation Rules

- If `agent_logs/` **does not exist**, the agent **must ask for permission** before creating it.
- If permission is granted, the agent must create it.
- If permission is denied, the agent must halt and report inability to proceed.

---

## Log File Naming Convention

Each agent **must write to its own log file**, organized by date.

### Required Format (Date-Based)

```text
agent_<agent_name>_<YYYY-MM-DD>.logs
```

### Examples

```text
agent_claude_code_2026-01-28.logs
agent_claude_code_2026-01-29.logs
agent_copilot_2026-01-28.logs
agent_antigravity_2026-01-30.logs
```

### Naming Rules

- `<agent_name>` must be lowercase, snake_case, ASCII only.
- `<YYYY-MM-DD>` is the date of the first entry in UTC.
- One log file per agent per day.
- Logs must be **append-only** (never overwrite).
- At session start, check current UTC date and use/create appropriate file.

### Directory Structure

```text
agent_logs/
├── INDEX.md                              # Master index of all sessions
├── agent_claude_code_2026-01-28.logs     # Current day's logs
├── agent_claude_code_2026-01-29.logs
├── agent_copilot_2026-01-28.logs
└── archive/                              # Archived logs (older than 30 days)
    └── 2026-01/
        ├── agent_claude_code_2026-01-01.logs
        └── agent_claude_code_2026-01-02.logs
```

---

## Index File (INDEX.md)

The agent **should maintain** an index file at `agent_logs/INDEX.md` for quick navigation.

### Index Format

```markdown
# Agent Logs Index

## 2026-01-29
| Agent | File | Summary |
|-------|------|---------|
| claude_code | agent_claude_code_2026-01-29.logs | Entropy threshold analysis, log organization |

## 2026-01-28
| Agent | File | Summary |
|-------|------|---------|
| claude_code | agent_claude_code_2026-01-28.logs | TenCrop TTA analysis, OOD documentation |
```

### Index Update Rules

- Update index at **session end** (not start) with a brief summary.
- If index doesn't exist, create it on first session.
- Keep most recent dates at the top.

---

## Log Rotation & Archival Policy

To prevent log directory clutter:

### Daily Rotation (Automatic)

- Each new UTC day automatically starts a new log file.
- No manual rotation needed for date-based naming.

### Monthly Archival

1. **Trigger**: Logs older than **30 days**.
2. **Archival Location**: `agent_logs/archive/<YYYY-MM>/`
3. **Process**:
   - Move old log files to archive directory.
   - Update INDEX.md to reflect new locations.
   - Log an "Archival" event in the current day's log.

### Size-Based Emergency Rotation

If a single day's log exceeds **5MB**:

1. Rename current file: `agent_<name>_<YYYY-MM-DD>_part1.logs`
2. Create continuation: `agent_<name>_<YYYY-MM-DD>_part2.logs`
3. Log a "Size Rotation" event as first entry in new part.

## Logging Trigger Rules (Non-Negotiable)

The agent **must log** when **any** of the following occurs:

- A task begins
- A task ends
- A file is created, modified, or deleted
- A command is executed
- A dependency is installed or removed
- A bug or error is encountered
- A workaround or fix is applied
- A design decision is made
- An assumption is introduced
- A limitation is discovered
- A new tool, library, or technology is used

If unsure whether to log something → **log it**.

---

## Log Entry Structure (Strict)

Each log entry **must follow this structure**:

### Session Delimiter (Start of Conversation)

At the very beginning of a new conversation or session, append a high-level header:

```markdown
# [SESSION START] YYYY-MM-DD - Conversation ID: <UUID_OR_NAME>
```

### Standard Log Entry

```markdown
---

## [YYYY-MM-DD HH:MM:SS UTC] <ACTION_TITLE>

### Context
- What the agent was trying to achieve
- Relevant files, modules, or subsystems involved

### Action Taken
- Exact steps performed
- Commands executed (verbatim)
- Files touched (full relative paths)

### Outcome
- What happened as a result
- Success / Partial / Failure

### Bugs / Errors Encountered
- Error messages (exact)
- Stack traces if applicable
- Unexpected behavior

### Fix or Mitigation
- How the issue was resolved
- Why this fix works
- Trade-offs introduced

### Pitfalls & Future Risks
- What could go wrong next time
- Conditions under which this may break
- Environment-specific concerns

### Best Practices & Lessons Learned
- Patterns to repeat
- Anti-patterns to avoid
- Naming, structure, or workflow improvements

### New Technologies / Tools Used
- Libraries, frameworks, CLIs, APIs
- Versions (if known)
- Why they were chosen

### Follow-ups / TODOs
- Deferred work
- Validation steps required
- Recommendations for future agents

---
```

All sections are **mandatory**.  
If a section is not applicable, explicitly write:

```text
N/A
```

---

## Logging Quality Rules

- Be **precise**, not verbose
- Avoid vague language (“it worked”, “seems fine”)
- Prefer factual descriptions over speculation
- Do not omit failures or mistakes
- Do not sanitize errors — raw messages are required
- Logs must be understandable **without chat history**

---

## Enforcement Rules

- If the agent performs work **without logging**, the work is invalid.
- If logs are incomplete, the agent must retroactively document actions.
- Human reviewers may reject outputs lacking sufficient logs.

---

## Final Instruction to the Agent

Before starting **any task**:

1. Check for `agent_logs/` directory
2. Ask permission if creation is required
3. Determine current UTC date
4. Check if log file exists for today: `agent_<name>_<YYYY-MM-DD>.logs`
5. Create new file if needed, or append to existing
6. Write "Session Start / Preflight" entry immediately
7. Proceed with task

At **session end** (if possible):

1. Write final log entry summarizing session
2. Update `INDEX.md` with session summary

### Quick Reference: File Selection Logic

```
current_date = UTC date (YYYY-MM-DD)
log_file = f"agent_logs/agent_{agent_name}_{current_date}.logs"

if not exists(log_file):
    create(log_file)

append(log_file, session_start_entry)
```

---

**End of Protocol**
