# Operating design

The system has a local experiment loop and a field validation loop. Each run tackles one measurable bottleneck. Its contract and event history survive a new chat or a different assistant. Work happens through the assistant's existing tools; a small local helper checks the evidence and records state.

The state sequence is baseline, candidate, review, release, field observation, regression protection, and complete. A recorded release intent marks a pending action before an external deployment; interruption requires reconciling provider state. Failed or inconclusive candidates return to experimentation within the original budget. A field regression requires rollback before another candidate. An inconclusive field result keeps the observation phase open until its allowance is exhausted. Offline runs skip release and field observation and finish as local results.

## Decisions and evidence

Choose the bottleneck from a trace, measured user flow, or reproducible report. Specify which user outcome should improve, the metric and unit, a meaningful improvement, and what must not worsen. Freeze those choices for a run. If the objective, evaluator, workload, or scoring rule changes, start a new versioned run with a new baseline.

Protect evaluator code, fixtures, and relevant regression tests by recording their file hashes. Keep the eventual regression threshold in a separate file so tightening it does not alter the scoring code. The helper detects changes in listed files; it is not a sandbox and cannot identify evaluator dependencies omitted from the contract. Review that file inventory.

For local screening, use repeated observations from comparable trials. The helper accepts a gain only when the entire candidate range beats the entire baseline range by the declared minimum. It rejects failed quality checks regardless of speed. Overlapping ranges are inconclusive. This deliberately conservative rule is a screening rule, not a confidence interval or a general statistical test. For noisy field experiments requiring formal inference, have a reviewed statistical analysis establish the observations and decision criteria; do not keep peeking until a result becomes favorable.

A review concerns the exact measured revision. Fixing a review finding invalidates the candidate evidence for the new revision. A release receipt must identify that reviewed revision and the actual flag. Field measurements must identify both candidate and control, match the predeclared context, and include artifacts that document the observation window and cohort selection. A date or a revision typed by an agent is not independently verified just because it is stored in JSON.

Before recording external evidence, read it from the benchmark runner, CI, Git provider, deployment service, or telemetry system. The helper snapshots submitted reports and hashes their referenced local artifacts. It rejects missing or altered evidence, mismatched revisions, and skipped phases. It cannot prove that a submitted report is truthful; source verification remains part of the skill and review.

## Project adapters

The project supplies the benchmark and correctness commands, a stable workload, exact revision identifiers, and any PR, flag, deployment, telemetry, and rollback tools. Use the native tools already present. Build an adapter only when the project needs one repeatedly; no generic cloud platform is required.

A local run can complete without a deployment. A flagged run cannot be called complete before field acceptance and regression protection. Defining a release contract does not grant permission to deploy. Inspect the task's existing authorization immediately before an external action; do not ask again when the action is already authorized.

Where the project has no traffic or telemetry, report the local result and the missing validation. Do not fabricate a field observation to close the record. Disable a failed experiment before revising it. Verify data compatibility separately if turning off a flag does not undo a migration or side effect.

## State and ownership

Store each run under `.agent-work/loops/<run-id>/` in the relevant project. `state.json` contains the frozen contract, protected-file hashes, current phase, and ordered evidence events. The helper uses a lock and replaces the state file atomically. One writer owns a run; separate experiments use separate records and isolated code changes.

The graph is deliberately small. Deterministic measurement and transition checks do not need a model. More agents are useful only for separable work or independent review. They are not a prerequisite for this system. A waiting state records why work cannot advance; it does not install a scheduler. Future recurring execution requires an explicitly authorized automation.

Budget candidate attempts and observation attempts independently. The deadline prevents fresh candidate work and fresh rollouts after it expires. Observation, rollback, and recording a completed result remain possible after expiry so a live experiment can be resolved safely. Record a halt explicitly. A halted live rollout remains pending rollback until recovery evidence arrives.

## Regression protection

After a repeatable accepted gain, tighten the performance limit with headroom rather than adopting the single best observation. The helper proposes the worst accepted local observation plus the contract's margin for lower-is-better metrics, or minus that margin for higher-is-better metrics. It never loosens the previous limit. Verify that the new limit leaves a real improvement and run the regression check against the accepted revision.

Keep the same correctness and quality checks. Track a harder exploratory workload separately from the suite that protects established behavior. A rejected idea stays in the event history with its evidence and reason, so the next session can choose a different hypothesis.

For an accepted flagged rollout, record who will expand the rollout, retire the temporary flag, and monitor the retained gain under the project's release policy. Completing one experiment does not silently authorize those later actions or continual work on another bottleneck.

## Writing acceptance

Writing is part of the result. The update must preserve all material facts, units, uncertainty, and failures; answer the user's current question first; and include enough evidence to act. Plain prose is the default. Formatting must serve a real comparison, sequence, code example, or requested document format.

Before delivering a substantive update, remove repeated background, stock transitions, decorative labels, promotional claims, and unsupported certainty. Check saved prose with the Humanizer writing checker, then review meaning and completeness yourself. A lint pass alone does not satisfy writing acceptance. Do not expose an intermediate critique unless requested.
