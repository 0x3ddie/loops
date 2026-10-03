# Agent-kit project

This repository packages Eddie's personal working standard, nine selected skills, and the measured improvement-loop helper. Canonical release inputs are under `.agents/harness` and `.agents/skills`. `scripts/install.py` installs an explicit inventory into a chosen home directory; it defaults to preview only.

Use Python 3.10 or later. Installation has no third-party dependencies. Metadata validation uses the pinned PyYAML package in `requirements-dev.txt`.

From this repository root, run `python3 scripts/validate.py`, `python3 scripts/test_install.py`, and each of `test_sync.py`, `test_loop.py`, and `test_writing.py` under `.agents/harness/validation`. Use `py -3 -X utf8` on Windows, or the active environment's Python executable. Installer tests use temporary homes inside `work/`; never test mutations against a real home.

Preserve independent edits. Check both source files and generated destinations before applying anything, create backups and a receipt before changing files, and keep removed inventory for manual reconciliation. Do not add force-overwrite or automatic deletion behavior. Preserve licenses and source attribution. Update `canonical_current_sha256` only after reviewing actual skill changes; leave initial-install and upstream hashes intact.

The repository must not include credentials, application state, personal application records, screenshots, caches, backups, or experiment runs. Keep the package's skills separate from bundled plugin caches. The measured loop records evidence; it does not run recurring jobs.

When changing installation behavior, run preservation tests and inspect a fresh-home installation. Source validation and synthetic tests do not establish model quality, in-app discovery, or macOS compatibility. Record those checks separately in `VALIDATION.md`.
