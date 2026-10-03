# Running the record helper

Python 3.10 or later is sufficient. Use a verified Python executable: `python3` on macOS/Linux or `py -3` on Windows when the Python launcher is installed. Replace `LOOP_SCRIPT` with the absolute path to this skill's `scripts/loop.py`, and `PROJECT_PATH` with the actual project directory. Use a fresh run ID.

```sh
python3 LOOP_SCRIPT init --project PROJECT_PATH --run search-latency --contract contract.json
python3 LOOP_SCRIPT record --project PROJECT_PATH --run search-latency --kind baseline --evidence evidence/baseline.json
python3 LOOP_SCRIPT status --project PROJECT_PATH --run search-latency
```

On Windows, replace `python3` with `py -3`, or invoke the configured runtime's full path in PowerShell with `&`. These example paths must be replaced before running the commands.

All supplied file paths must be relative to the selected project. The contract example is deliberately rejected until its example fields are replaced. The helper never executes a command contained in a report. It writes only under the selected run directory. Source code, deployment, and Git operations use the agent's existing tools.

## Measurement report

Baseline and candidate reports use this shape. A candidate also needs `hypothesis`. Samples are repeated observations of the declared metric, with the same workload and environment. For p95 latency, each number is an independently measured p95 over a defined workload, not an arbitrary individual request latency. A report must contain all required checks as actual booleans, and at least one existing raw-output artifact.

```json
{
  "revision": "exact revision or immutable build ID",
  "context": "same context string as the contract",
  "metric": "search_p95",
  "unit": "ms",
  "samples": [280, 281, 279, 283, 282],
  "checks": {"correctness": true, "regressions": true, "cost_budget": true},
  "artifacts": ["evidence/baseline-run.log"]
}
```

Record a candidate with `--kind candidate`. Its revision must differ from the baseline. Each candidate consumes one attempt, including a rejected or inconclusive one. A recorded candidate does not change the baseline. Restore only the experiment's own changes before another attempt when necessary.

The helper returns `improved`, `regressed`, `inconclusive`, or `failed_checks`. A promising candidate advances to review. Others remain at candidate generation while the budget permits. An expired budget stops candidate generation.

## Review and release

Review reports contain `revision`, `passed` (boolean), `reviewer`, `notes`, and `artifacts`. The artifacts should include the actual diff review, required checks, and relevant user-flow evidence. A failed review returns to candidate generation. Record a separate self-review honestly when an independent reviewer was unavailable.

Before an external release, record `release_intent` with `revision`, `flag`, `authorization`, `notes` describing the actual target and recovery plan, and `artifacts` containing the verified preflight record. This writes a pending state before the side effect. Check the deadline again immediately before starting deployment. After an interruption, inspect provider state before retrying.

A subsequent `release` report contains `revision`, `flag`, `deployment_id`, `authorization`, and `artifacts`. `authorization` describes the user's existing authorization and its scope. It is a record, not a permission system. The receipt artifact must come from the actual deployment service or equivalent verifiable source. A late receipt may document an already started release after the deadline. A reviewed local run advances directly to regression protection.

## Field observation and rollback

A field report contains `control` and `candidate` measurement objects with the same fields as above. Both use the contract's `release.field_context`. The control revision matches the original baseline; the candidate revision matches the released candidate. If production's actual control differs, establish a new appropriate run instead of treating unlike versions as comparable. Include raw telemetry and cohort/window details in their artifacts.

Field reports increment a separate observation count. An improvement advances to regression protection. A regression or failed checks requires rollback. Inconclusive observations remain pending; exhausting the allowance requires rollback rather than an unsupported success claim.

Rollback reports contain `revision` (the experiment being disabled), `flag`, `recovered` (boolean), `notes`, and `artifacts`. False recovery remains pending. True recovery returns to candidate generation if budget remains, otherwise stops. Turning off a flag is insufficient when data or other side effects still need recovery. A halted pending release also needs recovery evidence, which may establish that deployment never happened and the original control remains active.

## Ratchet and finish

The status output gives a proposed regression threshold after evidence acceptance. Apply that threshold in the project's separate regression configuration and verify it. A `ratchet` report contains `revision`, `threshold`, `checks`, and `artifacts`. Its threshold must equal the proposed value and all required checks must pass. A margin that leaves no actual tightening must be revised in a new run contract, not silently changed after seeing the result.

`--kind halt` accepts a report with a nonempty `reason`; it records why work stopped. If a flagged release is live, the record remains pending rollback. Halt and rollback remain available when protected files or evidence were damaged, allowing recovery to be documented. Preserve the damaged evidence for investigation.

Read-only `status` rechecks protected files and all recorded artifact hashes, and marks altered evidence as an integrity issue. Never edit `state.json` to manufacture a transition. If a process was killed and left `.lock`, inspect the PID and ensure the process is no longer running before removing that exact lock file. Resume from the last committed state and verify external actions before retrying.
