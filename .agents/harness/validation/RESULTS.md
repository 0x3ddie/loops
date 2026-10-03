# Validation results

Checked September 29, 2026, after adding the improvement loop, revised writing contract, and automatic project kickoff.

| Check | Result |
| --- | --- |
| Codex bundled skill-creator `quick_validate.py` | All eight installed skills passed |
| Codex UI metadata | All eight parsed; description lengths and explicit skill references passed |
| Manifest resources | All 25 canonical skill resources exist and match their current reviewed hashes |
| Snapshot history | Initial-install hashes and upstream commits retained; locally changed files use separate current hashes |
| Application synchronization | All 28 generated destination files match; no drift or conflicts |
| Global instruction size | CORE.md is 7,939 bytes |
| Synchronizer tests | Eight tests passed in an isolated temporary home |
| Loop record tests | Sixteen tests passed using synthetic evidence in isolated temporary projects |
| Writing checker tests | Seven tests passed, including preservation and technical-content exclusions |
| Design document prose check | LOOP-DESIGN.md passed plain mode; content also reviewed for source attribution and limitations |
| Codex global loading | The current chat received the updated AGENTS.md after synchronization, including loop routing and writing rules |
| Claude Code runtime loading | Not exercised; files installed at documented personal locations |
| Cursor runtime loading | Not exercised; local always-apply rule and shared skills installed at documented locations |
| Behavioral smoke scenarios | Documented in SMOKE-PROMPTS.md; not executed as separate agent sessions |

The eight tests cover read-only inspection, initial installation and empty-file backup, idempotent reapplication, backup during updates, independent-edit preservation, preservation of unmanaged nonempty files, rejection of source traversal, exclusion of unlisted resources, and preservation of files removed from the inventory. Some tests cover more than one property.

The loop tests exercise local and flagged completion, phase order, revision identity, metric/context/sample validation, failed correctness checks, candidate and observation budgets, deadlines, protected-file and artifact integrity, lock contention, state preservation after rejected input, threshold tightening, and recovery after an interrupted rollout. They simulate receipts and telemetry; no production deployment or actual performance gain is represented by these fixtures.

The writing tests check selected canned phrases and formatting, exact repeated paragraphs, meaningful lists, document mode, code/quotation/frontmatter exclusions, and a command-line check that leaves its input unchanged. They do not grade factual truth or prove that an assistant will always follow the prose contract.

The first Humanizer format check hit the Windows Python launcher's legacy text decoding default. Re-running the official validator in UTF-8 mode passed without changing the skill's text. Use `py -3.10 -X utf8` for that validator; normal synchronization already reads UTF-8 explicitly. PyYAML 6.0.3 was installed only under this harness's `.tools` directory for validation.

Initial deployment backup: `../backups/20260929T165336950805Z/`. The receipt distinguishes new files from previous files. The prior Codex global AGENTS.md was empty and its exact empty contents were saved.

This revision's canonical-source backup is `../backups/sources-20260929T193427926800Z/`. Its generated-destination backup is `../backups/20260929T195357897988Z/`. Existing plugin caches, application settings, and the roboarm repository were not edited.

All 31 automated tests passed. Validation establishes helper behavior, file integrity, format, and synchronization. Cross-assistant task performance has not been measured. Run the fixed smoke scenarios and actual project experiments before attributing improvements to these instructions.

The automatic-startup revision changed instructions, metadata, and the project template; helper code was unchanged, so the 31 helper tests were not repeated. The changed project-setup skill passed the official format validator. All eight metadata files and 25 current resource hashes were checked, the README passed the document-mode writing check, and all 28 generated destinations match. The source diff was inspected for new-project, unclear-goal, resumed-project, and small-edit routing. Corresponding runtime cases were added to SMOKE-PROMPTS.md but have not run in separate assistant sessions. This Codex chat received the updated startup instructions after synchronization.

Startup source backup: `../backups/sources-startup-20260929T201811417162Z/`. Startup destination backup: `../backups/20260929T201900568690Z/`.
