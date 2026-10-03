# Eddie's agent kit

A portable copy of Eddie's personal working standard, nine managed skills, and the measured improvement-loop helper. Prepared October 3, 2026 for installation on Eddie's computers. The source repository is [0x3ddie/loops](https://github.com/0x3ddie/loops).

The new `job-outreach` skill writes hiring-post replies, LinkedIn DMs, cover letters, and recruiting responses. Its language follows the supplied examples: a brief public reply, specific relevant work in the DM, and an ordinary invitation to talk. The [source notes](.agents/skills/job-outreach/references/source-examples.md) preserve the screenshot transcriptions and distinguish Brandon's experience from the user's.

## Install

You need Python 3.10 or later. Installation uses only the Python standard library. Keep this checkout in a normal project folder, separate from the active `~/.agents` folder. From the checkout root, preview the changes first.

Windows PowerShell:

```powershell
py -3 --version
py -3 -X utf8 scripts/install.py
py -3 -X utf8 scripts/install.py --apply
py -3 -X utf8 scripts/install.py
```

macOS or Linux:

```sh
git clone https://github.com/0x3ddie/loops.git
cd loops
python3 --version
python3 scripts/install.py
python3 scripts/install.py --apply
python3 scripts/install.py
```

The preview returns exit 1 when changes or conflicts exist, exit 0 when everything matches, and exit 2 for an invalid package or read/write error. Apply only after reviewing the reported changes. Conflicts block all installation writes. An explicit `--home PATH` installs into another home directory and is used for tests.

The installer places the canonical instructions and skills under `~/.agents`, generates Codex's `~/.codex/AGENTS.md`, Claude Code's `~/.claude/CLAUDE.md` and managed skill copies, and Cursor's `~/.cursor/rules/00-work-standard.mdc`. It creates these instruction files even if an application is not installed. It does not install the applications, connect accounts, migrate plugins, or configure permissions.

Open a fresh chat and check the application's skills interface. In Codex, ask: `Use $job-outreach to draft a DM for this opening using my experience below.` Installed files alone do not prove a running application loaded them. macOS and Linux runtime discovery have not been tested on a live machine in this work.

## What is included

| Part | Location |
| --- | --- |
| Shared working standard | `.agents/harness/CORE.md` |
| Managed skills and resources | `.agents/skills/` |
| Source provenance and reviewed hashes | `.agents/harness/manifest.json` |
| App synchronizer | `.agents/harness/scripts/sync.py` |
| Measured experiment workflow | `.agents/skills/work-improvement-loop/` |
| Installation and source checks | `scripts/` |
| Cross-platform CI definition | `.github/workflows/validate.yml` |

The other managed skills are `karpathy-guidelines`, `humanizer`, `frontend-design`, `work-debugging`, `work-research`, `work-project-setup`, and `work-harness-maintenance`.

The measured loop records baselines, candidate results, review, release evidence, recovery, and regression limits. It does not schedule agents or automatically improve the harness. Host-specific timer skills, active recurring jobs, and plugin installations are separate from this package.

## Repository

The user selected the public [0x3ddie/loops](https://github.com/0x3ddie/loops) repository for this package. Clone it to obtain the source files, including the hidden `.agents` and `.github` directories. Cloning alone does not install the global instructions or application skill copies; run the installer afterward.

The package omits credentials, application histories, installed plugin caches, machine state, backups, source images, and personal job-application materials. Original local files and upstream skill files have different provenance; see [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) before choosing any public redistribution license.

## Update your computers

Edit the release sources in this checkout, review the changes, and update the changed skills' `canonical_current_sha256` values in the manifest. Keep upstream and initial-install hashes intact. Run the checks below, commit the reviewed changes, and optionally tag a release. The package preserves the existing manual-review policy for third-party updates.

On another computer, pull the reviewed revision with `git pull --ff-only`, inspect the changes, then run the installer in preview and apply modes. Each machine keeps its own installation state. The installer refuses to overwrite independently edited installed sources or generated application files.

The supplied `.gitattributes` preserves file bytes across checkouts so Windows line-ending conversion does not invalidate the reviewed source hashes. Keep that file in the repository.

If you edit the active files under `~/.agents` instead, merge those edits back into the repository before installing another revision. A clone and an installation are separate copies; the installer does not provide automatic two-way synchronization. Do not alter recorded state hashes to bypass conflicts.

For active-source changes that do not involve a new repository release, use the existing harness synchronizer described in [.agents/harness/README.md](.agents/harness/README.md). Keep a source backup before editing. Ordinary synchronization backs up generated files, while package installation also backs up the canonical sources it changes.

## Preservation and recovery

Before changing files, the installer saves existing bytes and a receipt under `~/.agents/harness/backups/kit-TIMESTAMP/`. It records installed source hashes in `package-state.json` and generated-file hashes in `state.json`, both inside the local harness directory. These files are intentionally excluded from Git.

Removed inventory is reported as a conflict and is never deleted automatically. For recovery, inspect the exact receipt, preserve any work made afterward, and restore the recorded pre-change bytes. Entries marked `existed: false` identify newly created files; remove one only after checking for later work. Restore the corresponding state files from the same receipt when present. A write interrupted midway is recoverable from the receipt but is not a transaction across all files.

## Validate a release

In a development environment, install `requirements-dev.txt`; only metadata validation requires PyYAML. Use the selected Python executable for each command below (`py -3 -X utf8` on Windows, or `python3` on macOS/Linux).

```sh
python3 -m pip install -r requirements-dev.txt
python3 -B scripts/validate.py
python3 -B scripts/test_install.py
python3 -B .agents/harness/validation/test_sync.py
python3 -B .agents/harness/validation/test_loop.py
python3 -B .agents/harness/validation/test_writing.py
```

The GitHub Actions workflow defines the same checks for Windows, macOS, and Linux. It has not run remotely yet. [VALIDATION.md](VALIDATION.md) records checks performed for this package. The older harness validation report is historical evidence from September 29, not proof of current cross-platform behavior. Original staging snapshots and historical backups are omitted from this portable package; their old references describe the original installation.

After validation, run `python3 scripts/archive.py` to produce a release ZIP and SHA-256 checksum under `dist/`. The archiver includes only explicit source files and release documentation; it never sweeps the checkout for caches, credentials, or test artifacts. It verifies the ZIP contents against the original bytes.
