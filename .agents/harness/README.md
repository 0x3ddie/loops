# Eddie's agent foundation

A shared working standard for local Codex, Claude Code, and Cursor, with nine focused skills and reusable project templates. Created September 29, 2026. The [improvement-loop design](LOOP-DESIGN.md) explains measured experiments, recovery, regression protection, and writing acceptance.

## What to use

The personal baseline asks agents to finish authorized work, make focused changes, verify results, preserve existing work, research uncertain claims, and write plainly. At the start of a substantial project or substantive work in an unfamiliar repository, it directs the agent to load `work-project-setup` automatically. The kickoff uses existing context and asks one focused question only when a material goal or success criterion is missing. Detailed workflows load when relevant.

| Skill | Purpose | Source |
| --- | --- | --- |
| `karpathy-guidelines` | Simple implementation, clear assumptions, focused changes | Community adaptation of Karpathy's observations, with a small local adjustment |
| `humanizer` | Plain prose with facts and voice preserved; mechanical writing checks | Local adaptation of blader/humanizer 3.1.0 with its pattern guide retained |
| `frontend-design` | Intentional visual design and usable interfaces | Anthropic; upstream instructions unchanged |
| `job-outreach` | Specific, conversational hiring replies, DMs, cover letters, and recruiting responses | Original local skill informed by attributed posts and user-supplied screenshots |
| `work-debugging` | Reproduction, cause analysis, focused fix, regression checks | Original local skill |
| `work-improvement-loop` | Baseline, bounded experiments, review, controlled release, field evidence, regression protection | Original local skill informed by published Anthropic engineering practices |
| `work-research` | Current primary sources, comparisons, provenance | Original local skill |
| `work-project-setup` | Automatic project kickoff, workflow selection, and guidance based on actual facts | Original local skill |
| `work-harness-maintenance` | Audit, reviewed updates, synchronization and recovery | Original local skill |

Example requests:

- "Use karpathy-guidelines to implement this feature."
- "Use humanizer to edit this in my voice and preserve every fact."
- "Use work-improvement-loop to improve this project's measured response time."
- "Use work-project-setup to set up this repository's agent instructions."
- "Use work-harness-maintenance to check for drift and review upstream updates."

Codex CLI/IDE supports `$skill-name`; Claude Code and Cursor expose skills through their command interfaces. Plain-language requests also work when the host matches the description. New Codex skills should be available on the next turn; restart if they do not appear. Start fresh chats to pick up the global standards consistently.

## Where everything lives

| Location | Role |
| --- | --- |
| `~/.agents/harness/CORE.md` | Canonical personal working standard; edit this first |
| `~/.agents/skills/<name>/` | Canonical skill files, discovered by local Codex and Cursor |
| `~/.codex/AGENTS.md` | Generated Codex global standard |
| `~/.claude/CLAUDE.md` | Generated Claude Code global standard |
| `~/.claude/skills/<name>/` | Generated copies of these nine skills for Claude Code |
| `~/.cursor/rules/00-work-standard.mdc` | Generated local Cursor rule with `alwaysApply: true` |
| `templates/` | Project AGENTS.md, Claude import, and handoff outlines |
| `manifest.json` | Installed files, source commits, upstream hashes, local adaptations |
| `research/SOURCES.md` | Source evaluation and shortlist, with dated popularity evidence |
| `research/ANTHROPIC-WORKFLOW.md` | Published engineering sources and our specific adaptations |
| `state.json` | Hashes of the last synchronized application copies |
| `backups/<timestamp>/receipt.json` | Every changed destination and its pre-change backup |
| `staging/2026-09-29/` | Original pinned third-party downloads, outside skill discovery |

`~` means the current user's home directory on Windows, macOS, or Linux. There is one canonical skill set and a small list of generated application copies. This installation does not bulk-edit project working trees. During future authorized project creation or substantial development, the setup skill can add or merge missing project guidance.

## Make a change

Edit `CORE.md` or a canonical skill. Then run these in PowerShell:

```powershell
py -3 "$env:USERPROFILE\.agents\harness\scripts\sync.py"
py -3 "$env:USERPROFILE\.agents\harness\scripts\sync.py" --apply
py -3 "$env:USERPROFILE\.agents\harness\scripts\sync.py"
```

The first and last commands only inspect files. Exit 0 means all generated copies match, exit 1 means changes or conflicts exist, and exit 2 means an invalid setup or read/write error. The script uses only Python's standard library and requires Python 3.10 or later. Verify the selected runtime is Python 3.10 or later. On macOS/Linux, use `python3` and `$HOME` in place of `py -3` and `$env:USERPROFILE`. A full Python executable path can also be used; in PowerShell prefix it with `&`.

Synchronization backs up changed destinations, refuses to overwrite independently edited destination files, and copies only the manifest's explicit inventory. It does not delete obsolete files. If a destination was edited directly, inspect and merge the useful changes into the canonical source, then restore the destination to its last recorded version before applying. Keep a separate backup of those edits. Never change the recorded hashes merely to bypass a conflict.

If adding a resource to a skill, add its relative path to that skill's `files` list in `manifest.json`. Upstream hashes describe the reviewed download. Initial-install hashes preserve historical local content; current canonical hashes describe reviewed local revisions. Change the source version only after reviewing an actual upstream update.

## Add a project

Start describing the project or the work you want done. The global standard directs the agent to use `work-project-setup` automatically for substantial new work. An explicit invocation remains available. It inspects existing guidance, identifies the outcome and success check, and selects the relevant skills without a repeated permission prompt. Missing project guidance is filled with real commands and invariants during authorized development. Existing guidance is preserved.

Measured optimization automatically selects `work-improvement-loop`; ordinary feature work uses a proportional implementation-and-verification cycle. Non-code projects use their relevant briefs and success criteria. Small edits and resumed work with adequate guidance skip onboarding. Startup does not auto-download skills, start a scheduler, or authorize deployment.

Keep detailed workflow guidance in skills and project facts in the project's AGENTS.md. The optional CLAUDE.md template imports the same AGENTS.md for compatibility with Claude Code versions/configurations that do not load it directly.

The templates intentionally contain placeholders; they are not active instruction files. Remove the placeholders when creating a real project guide.

## Update or recover

Third-party skills are pinned snapshots. Nothing auto-updates. Ask for a harness maintenance pass when you want to review newer releases. Review relevance, changed behavior, licensing, resources, and duplicates before updating.

To undo a synchronization, consult that run's `receipt.json`. For entries whose `existed` value is true, restore the backed-up file to the recorded path under your home directory. For entries that were newly created, first check for later edits, then remove only that exact generated file if you want to undo it. Preserve later user work and reconcile `state.json` afterward. An agent can perform this recovery from the receipt. Backups cover generated destinations; preserve separate copies before changing canonical sources.

The initial Codex AGENTS.md was empty and is backed up. Existing plugins and application settings were not changed. The older Codex plugin Humanizer 2.5.1 remains available; the personal baseline routes prose work to the local adaptation of `humanizer` 3.1.0. The original pattern guide and license remain available. This overlap is documented; plugin-cache files were not modified.

## Validation and limits

Run the preservation tests with:

```powershell
py -3 "$env:USERPROFILE\.agents\harness\validation\test_sync.py"
py -3 "$env:USERPROFILE\.agents\harness\validation\test_loop.py"
py -3 -X utf8 "$env:USERPROFILE\.agents\harness\validation\test_writing.py"
```

See `validation/RESULTS.md` for checks actually performed and `validation/SMOKE-PROMPTS.md` for fresh-chat behavioral checks. The format validator's PyYAML dependency is isolated under `.tools`; normal synchronization requires no third-party packages.

This setup concerns local application sessions. It does not install skills into remote machines, cloud workers, or Claude Cowork. File and format validation do not prove that a running application's current chat loaded the instructions. Restart or open a fresh chat and check the app's rules/skills interface. These are behavioral guidelines, not a security enforcement mechanism.

Discovery paths were checked against [Codex instructions](https://learn.chatgpt.com/docs/agent-configuration/agents-md), [Codex skills](https://learn.chatgpt.com/docs/build-skills), [Claude Code memory](https://code.claude.com/docs/en/memory), [Claude Code skills](https://code.claude.com/docs/en/skills), [Cursor rules](https://cursor.com/help/customization/rules), and [Cursor skills](https://cursor.com/docs/skills).

## Portable package and job outreach

The October 3, 2026 revision adds `job-outreach` with transcriptions of the two supplied screenshots, source links, and factual boundaries. Its description supports automatic selection; explicit invocation is `$job-outreach`. Provide the actual role and your relevant experience when asking for a draft.

The portable agent-kit repository contains an explicit inventory of this harness and its nine managed skills. Its root README describes the check/apply installer, updates, and recovery. The installer tracks installed source hashes separately from `state.json`, which remains the synchronizer's record of generated files. Backups and both state files stay local to each computer.

Edit the repository's source files for a release, update reviewed hashes in the manifest, validate, and apply the release on each machine. If you edit active files under `~/.agents` instead, merge those changes back into the repository before installing a conflicting version. Updates preserve independent changes and never delete removed inventory automatically. The improvement-loop helper records experiments; it does not schedule recurring updates or start background agents.
