# Skill source review

Checked September 29, 2026. Repository star counts below are a point-in-time GitHub API snapshot, not install counts or a benchmark of effectiveness. This is a practical shortlist of prominent collections, not an exhaustive global popularity ranking. No comparative evaluation here establishes a universal state-of-the-art skill set.

## What was already on this PC

- Codex's global `~/.codex/AGENTS.md` existed but was zero bytes. No global override was found.
- No `~/.claude/CLAUDE.md` or user-level Cursor rules directory was found during the initial inspection.
- The inspected roots contained 26 SKILL.md files under `~/.agents/skills`, 6 under Codex's system skill root, 25 under Cursor's `skills-cursor`, and 127 in the Codex plugin cache. These are file counts, not distinct active skills; there is substantial overlap.
- Codex already exposed Humanizer 2.5.1 through its Anthropic-skills plugin, plus document, PDF, spreadsheet, presentation, browser, Vercel, and other domain skills.
- Existing plugins/settings were preserved. The current roboarm repository has substantial existing changes and was not used as the home of this personal system.

## Reviewed sources

| Source | Stars at inspection | Repository push date (UTC) | Assessment and decision |
| --- | ---: | --- | --- |
| [obra/superpowers](https://github.com/obra/superpowers) | 292,767 | 2026-09-27 | Broad, prescriptive development process with planning, TDD, debugging, and subagent workflows. Useful optional process pack; not enabled globally because it would impose more workflow than this foundation needs. |
| [mattpocock/skills](https://github.com/mattpocock/skills) | 271,891 | 2026-09-29 | Maintainer-authored, composable engineering skills. Good next source for targeted additions such as TDD, design interrogation, and architecture work. No bulk installation. |
| [affaan-m/ECC](https://github.com/affaan-m/ECC) | 269,436 | 2026-09-28 | Large harness collection, formerly everything-claude-code. Worth studying for a deeper agent operating environment; too broad for the initial personal baseline. |
| [multica-ai/andrej-karpathy-skills](https://github.com/multica-ai/andrej-karpathy-skills) | 215,837 | 2026-04-20 | The former forrestchang URL redirects here. Small, understandable coding guidance. Installed with a narrow local change to clarification behavior and trigger text. Community-authored, not an official Karpathy skill. |
| [anthropics/skills](https://github.com/anthropics/skills) | 178,964 | 2026-09-29 | Official Anthropic public skills. Selected Frontend Design; existing Codex document capabilities already cover many other use cases. Check each skill's license rather than assuming one repo-wide license. |
| [blader/humanizer](https://github.com/blader/humanizer) | 52,845 | 2026-09-28 | Installed upstream 3.1.0 with a concise description and final-rewrite default. Preserves facts and supports voice matching, file editing, and embedded use. Kept the existing plugin intact. |
| [vercel-labs/agent-skills](https://github.com/vercel-labs/agent-skills) | 31,712 | 2026-08-28 | Official Vercel collection for React, Next.js, web UI, and platform work. The current Codex Vercel plugin already provides related skills, so not duplicated globally. Consider selected skills for Claude/Cursor when a project needs them. |
| [openai/skills](https://github.com/openai/skills) | 27,807 | 2026-09-08 | Historical official collection. Its current README explicitly marks the repository deprecated and points to openai/plugins. The locally bundled Skill Installer still references the old catalog, so its default source should not be treated as a freshness guarantee. |
| [trailofbits/skills](https://github.com/trailofbits/skills) | 7,289 | 2026-09-28 | Security analysis and testing workflows from Trail of Bits. Good task-specific extension for audits; not a general coding baseline. Review each package's requirements and licensing. |
| [openai/plugins](https://github.com/openai/plugins) | 7,230 | 2026-09-28 | Current official OpenAI distribution/example repository, including skill bundles and third-party plugins. Public availability in this repository does not mean every plugin is authored by OpenAI. Consult per-plugin metadata and dependencies. |

Repository push dates can reflect work outside the selected skill or default branch. Exact downloaded commits and hashes are recorded in `../manifest.json`; the pinned file contents, rather than a mutable README or search snippet, determine what was installed.

## Why this shape

[OpenAI's September 11 guidance](https://developers.openai.com/blog/rethinking-skills-and-prompts-for-gpt-6-astra) recommends concise descriptions, useful scope boundaries, and progressive disclosure. Overlapping broad skills can make selection less reliable. The baseline therefore holds personal defaults; focused skills hold the reusable workflows; project templates hold repository-specific facts.

The installed third-party instructions were read before activation. Only the selected Markdown, license notices, and UI metadata were promoted into skill discovery. Humanizer's repository also includes plugin packaging and a validation script; these remain in the inactive staging snapshot and are not installed as executable hooks or plugins.

Local changes are explicit: Karpathy's trigger is narrower and questions are reserved for material uncertainty; Humanizer's trigger is shorter and its default returns the final rewrite. Frontend Design's instruction body is unchanged. Added Codex UI metadata is local except for Humanizer's upstream metadata. The manifest distinguishes these edits from the pinned upstream snapshots.

## X/Twitter provenance

The Karpathy skill links to [Karpathy's original observations](https://x.com/karpathy/status/2015883857489522876). Direct retrieval of that X page failed during this review, so the attribution here is based on the repository's explicit statement. No claims about current X engagement or a Twitter-wide popularity ranking were used. GitHub source files and metadata were the verifiable basis for selection.

## Next additions by demonstrated need

- For a sustained engineering process, compare selected Matt Pocock skills with Superpowers on a disposable representative task before adopting a whole process pack.
- For security work, select a relevant Trail of Bits package and inspect its tool requirements.
- For React/Next.js outside Codex, install only the relevant Vercel skills; existing Codex plugins are not automatically available in Claude Code or Cursor.
- For other lab capabilities, consult the current OpenAI plugins and Anthropic skills repositories. Inspect ownership, per-skill licensing, and dependencies before importing them.

Keep additions driven by a repeated task or an observed failure. Record whether a new skill improved actual results, not just whether its description sounds comprehensive.
