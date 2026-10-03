# Validation record

Checked October 3, 2026 on Eddie's Windows PC with Python 3.10. The package version is 0.1.0.

| Check | Result |
| --- | --- |
| Installed outreach skill | Canonical SKILL.md, UI metadata, and screenshot source notes exist; official skill-creator format validator passed. |
| Package inventory | Nine skills and 43 canonical source resources validated; reviewed hashes, skill metadata, and referenced files match. |
| Installer tests | 14 passed in isolated homes, including updates, idempotence, source/app conflicts, unmanaged-file preservation, interrupted-write backup and recovery, removed inventory, traversal, case collisions, and exclusion of unlisted files. |
| Synchronizer tests | Eight passed. |
| Improvement-loop tests | 16 passed on the final full run. See the transient failure below. |
| Writing-checker tests | Seven passed. |
| Local installation | Package installer applied its local tracking state; subsequent package and harness checks report no changes or conflicts. All 31 generated app files match. |
| Git line endings | All 43 reviewed files retain identical Git content hashes when filtered with core.autocrlf=true and the supplied .gitattributes. |
| Prose review | Skill, screenshot notes, README, notices, example cases, and this report checked with the local writing checker and reviewed for factual support. |
| Outreach behavior | Five synthetic scenarios self-reviewed in validation/job-outreach-cases.md; one unsupported detail was removed from a sample DM. No independent model evaluation or live outreach was performed. |
| Global instructions | This Codex conversation received the updated generated AGENTS.md containing the outreach routing and platform-conditional guidance. |
| Release ZIP | All 57 included files matched their source bytes and ZIP integrity passed. Fresh-home preview, apply, and recheck passed from an extracted copy of the archive. |

There are 45 automated helper tests across the installer, synchronizer, improvement loop, and writing checker. Format checks and source hashes are separate from those tests. These checks establish file and helper behavior, not improved hiring outcomes or general model performance.

## Transient Windows failure

The first full loop test run encountered WinError 32 while removing a lock file, followed by a temporary-directory cleanup error. The helper's file handles were closed before the failing operation. The isolated failing test and subsequent full suite passed without code changes. The process holding the file was not identified; the cause remains unconfirmed.

Automatic approval review rejected removal of the remaining loop-test-3nxdv334 temporary fixture with the message "blocked by policy." It is ignored by Git and excluded by the archive's explicit inventory. Its presence does not affect the release ZIP.

## Remaining checks

At the time of the local package checks, macOS and Linux execution, fresh-chat skill discovery in each application, and remote GitHub Actions had not been exercised. The workflow defines all three operating systems; subsequent remote results are available on the repository's Actions page. The original September 29 harness report remains historical evidence, with its original runtime limitations intact. The user subsequently requested publication to the existing `0x3ddie/loops` repository.

Local source and generated-file backups were created before the October 3 changes. Receipts remain on the PC under the local harness backups directory and are intentionally omitted from the package.
