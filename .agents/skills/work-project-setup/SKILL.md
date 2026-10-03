---
name: work-project-setup
description: Start substantial projects or work in unfamiliar repositories with the shared work standard, a focused kickoff, verified project guidance, and the appropriate implementation or improvement loop.
---

# Project setup

Use automatically at the start of a substantial project or the first substantive work in an unfamiliar repository. The global standard is standing authorization for this setup; the user need not name the skill or approve the same workflow again. Routine questions, small edits, and resumed work with adequate guidance do not need a new kickoff.

## Kickoff and routing

Read applicable project instructions and any relevant handoff before asking questions. Establish the intended result, constraints, and an observable success check from the request and local evidence. State the result and chosen workflow briefly in the first useful progress update. Ask one focused question only if a material decision is still missing; suggest the best-supported default and continue independent work. Do not repeat facts the user already supplied or print a setup checklist.

Apply the shared personal standard automatically. For substantial implementation, use `karpathy-guidelines` and verify the changed behavior. For measured optimization or a requested rollout experiment, read and use `work-improvement-loop` without requiring another invocation. Use `work-research` for research and `humanizer` for substantive prose; retain appropriate domain skills. Select the workflows that actually help rather than loading the entire library.

A new project without a working baseline starts by building and checking the first useful behavior. Add the full measured improvement loop when there is an actual metric and baseline to improve. Preserve its limits and release authorization requirements. Do not manufacture benchmarks, deployment access, or production evidence just to complete onboarding.

For non-code projects, use the relevant brief, source register, or deliverable success criteria. Do not impose repository files or coding stages on a writing or research task. For an existing project with adequate guidance, reuse it and move directly to the requested work.

## Repository inspection

Inspect the repository before writing its instructions: existing instruction files, working-tree state, README, dependency manifests, CI configuration, and relevant source boundaries. Preserve instructions and local work that already exist.

Use the templates in `~/.agents/harness/templates/` as outlines, not as facts. If that directory is unavailable, write the same concise information directly.

During authorized project creation or substantial development, fill missing or materially incomplete project guidance as part of setup. Merge useful additions into existing files. Record only what has been verified so far; improve the guide when new project facts are established. A setup-only or read-only request retains its own scope.

## Project instructions

Keep a root `AGENTS.md` focused on facts the next agent would otherwise have to rediscover:

- What the project does and the important source boundaries.
- The actual setup, development, build, lint, and test commands, including the directory in which each runs.
- Environment requirements and secret variable names, never secret values.
- Non-obvious invariants, generated files, data constraints, or operational hazards.
- What demonstrates that a typical change is complete.

Derive commands from maintained project files. Execute safe relevant checks when feasible; distinguish commands inspected from commands successfully run. Do not invent a stack, a test suite, or a CI requirement. Remove unused template sections and all placeholders before installing a project file.

Put detailed or area-specific instructions near the area they govern. Avoid copying the personal global standard into every project. For Claude Code compatibility, a project `CLAUDE.md` can import `@AGENTS.md`; merge with an existing file instead of replacing it. Cursor can use the root AGENTS.md directly.

## Continuity

For a project that needs measured optimization, identify its actual benchmark command, stable workload, correctness checks, revision identity, and any release/flag/telemetry tools. Route that work to `work-improvement-loop`. Keep a run's contract and changing evidence under `.agent-work/loops/`, not in the always-loaded AGENTS.md. Do not install dummy benchmarks, invent production access, or impose the loop on routine edits.

For work spanning sessions, add or update a concise handoff only when it would help: current goal, decisions, changed files, validation evidence, unresolved issues, and next action. Keep volatile task status out of the always-loaded project standard.

Finish by identifying the installed files and verified commands. Setting up a project does not authorize changing the application's architecture, pushing commits, or configuring unrelated repositories.
