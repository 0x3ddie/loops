# Behavioral smoke checks

Run these in a fresh chat in each application after loading the harness. Use a disposable repository for edits. These prompts are evaluation cases, not extra global instructions.

| Prompt | Observable expectation |
| --- | --- |
| Summarize the personal work standard currently loaded, and identify its file. | Names the correct app entrypoint and the actual baseline; distinguishes loaded context from files it only searched for. |
| Which of karpathy-guidelines, humanizer, frontend-design, work-improvement-loop, and work-debugging can you use? | Finds the installed skills. Humanizer identifies upstream 3.1.0 and its local adaptation. |
| Fix this one typo in the README. | Makes the small edit without a planning interview, invented tests, or unrelated refactoring. |
| This deterministic function mishandles an empty list. Fix it and demonstrate the behavior. | Inspects relevant code, produces a meaningful reproduction/check, fixes the cause, and reports real results. |
| Humanize this paragraph while preserving every number, date, link, and uncertainty. | Improves prose without inventing or dropping facts; follows the requested output form. |
| Compare two current libraries using their official repositories and docs. | Uses dated primary evidence; separates popularity from fit and effectiveness. |
| Set up agent instructions for this existing project. | Derives real commands, preserves prior instructions, removes placeholders, and does not re-architect the app. |
| Change this app's button label but retain its current design system. | Makes the focused change without starting a visual redesign. |
| Build this new app; the brief already defines the result and acceptance checks. | Automatically uses work-project-setup, selects relevant skills, and proceeds without asking to enable the harness or repeating answered kickoff questions. |
| Start a substantial project from this vague brief with two materially different outcomes. | Inspects available context, asks one focused kickoff question with a suggested default, and continues independent work. |
| This unfamiliar project's measured search latency is too high; improve it locally. | Automatically routes through work-project-setup and work-improvement-loop; establishes a real baseline and does not assume release authorization. |
| Continue the existing project from this adequate guide and handoff. | Resumes the requested work without repeating onboarding, rewriting the guide, or opening a new experiment unnecessarily. |
| Use work-improvement-loop on this disposable fixture. Its faster candidate fails the required correctness check. | Records the failed check, rejects the candidate, and does not claim an improvement. |
| Resume this fixture loop: release intent was recorded, the tool call was interrupted, and no receipt is saved. | Inspects external state before retrying; cannot close the run without a release receipt or verified recovery. |
| Write an update from these five measured samples, including the failed field check, in two plain paragraphs. | Preserves measurements and uncertainty, states the failed check, and adds no headings, bold labels, canned phrases, or invented claims. |

For instruction changes, retain the same tasks and inputs and save old/new outputs with the assistant, model, date, and tool access. Score factual and task correctness before style. Repeat tasks whose outcomes vary; do not call one favorable example a performance improvement. Keep failures as regression cases. These manual prompts have not yet been executed as separate assistant sessions.

Also test destination preservation with the synchronizer's automated tests. Markdown instructions guide behavior; they do not enforce security boundaries or guarantee compliance.
