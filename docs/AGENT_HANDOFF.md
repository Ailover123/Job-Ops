# AI Fresher Job Matcher - Agent Handoff Guide

## 1. Why This Exists

If you continue coding with Antigravity AI agents and later come back to Codex, the project needs a simple handoff pattern so context is not lost.

The goal is to make progress easy to understand without rereading the whole codebase.

## 2. Files To Keep Updated

Use these files as the project memory:

- `docs/BUILD_LOG.md`
- `docs/NEXT_STEPS.md`
- `docs/DECISIONS.md`
- `docs/KNOWN_ISSUES.md`

If these files do not exist yet, create them when development starts.

## 3. What To Ask Antigravity Agents To Do

At the end of every meaningful coding session, ask the agent:

```text
Update docs/BUILD_LOG.md, docs/NEXT_STEPS.md, docs/DECISIONS.md, and docs/KNOWN_ISSUES.md with a concise handoff for another AI agent.
Include changed files, commands run, what works, what is broken, and the next recommended task.
```

## 4. Build Log Format

Use this structure in `docs/BUILD_LOG.md`:

```md
## YYYY-MM-DD - Session Title

### Changed
- 

### Commands Run
- 

### Verified
- 

### Not Verified
- 

### Notes For Next Agent
- 
```

## 5. Next Steps Format

Use this structure in `docs/NEXT_STEPS.md`:

```md
# Next Steps

## Current Priority
- 

## Ready To Build
- 

## Blocked
- 

## Later
- 
```

## 6. Decisions Format

Use this structure in `docs/DECISIONS.md`:

```md
# Decisions

## YYYY-MM-DD - Decision Title

Decision:

Reason:

Alternatives considered:

Impact:
```

## 7. Known Issues Format

Use this structure in `docs/KNOWN_ISSUES.md`:

```md
# Known Issues

## Issue Title

Status:

Where:

Problem:

Temporary workaround:

Recommended fix:
```

## 8. Best Prompt To Bring Codex Back In

When returning to Codex after Antigravity work, use:

```text
Read docs/BUILD_LOG.md, docs/NEXT_STEPS.md, docs/DECISIONS.md, and docs/KNOWN_ISSUES.md.
Then inspect the current codebase and continue from the current priority.
Do not restart the project from scratch.
```

## 9. Best Prompt For Antigravity Before Ending A Session

Use:

```text
Before ending, write a handoff for Codex.
Update the project docs with:
1. What you changed.
2. What files matter.
3. What commands were run.
4. What works.
5. What is broken or unverified.
6. What should be done next.
Keep it concise and practical.
```

## 10. Rule For AI Agents

Every agent should leave the repo easier to continue than it found it.

