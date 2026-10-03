---
name: work-improvement-loop
description: Run measurable improvement experiments from a protected baseline through review, controlled rollout, field evidence, and regression protection.
---

# Improvement loop

Use for a measurable optimization or an explicitly requested experiment workflow. A typo, ordinary bug fix, or unmeasured design exploration does not need a loop. This skill follows documented Anthropic practices; it is our implementation, not a copy of an internal Anthropic system.

Read [the operating design](references/design.md) when starting or changing a loop. Read [the evidence format](references/evidence.md) when initializing a record or importing measurements. The executor is the current agent with its available tools. `scripts/loop.py` records evidence and checks transitions; it does not call models, execute benchmark commands, open PRs, deploy, or schedule future turns.

## Start

Inspect the actual project, instructions, working-tree state, and existing observations. Choose one bottleneck tied to a user outcome. Write a run contract from `assets/contract.example.json`, replacing example facts with verified project facts. Decide the metric, meaningful gain, workload, required regression checks, protected evaluator files, candidate limit, deadline, release mode, and rollback method before measuring candidates.

Use an isolated checkout when needed to protect existing work. A thread is a coordination surface; the experiment's durable record lives in the project. Create a separate chat, delegate, or schedule work only when the user has authorized that workflow.

## Execute

1. Initialize the record to protect evaluator files, then run the unchanged baseline and required checks. Save raw outputs with the revision and environment and record the baseline with the helper.
2. State one testable hypothesis. Make a focused change within the agreed scope. Run the same workload and checks, preserve the outputs, and record the candidate. The helper screens repeated observations conservatively; a candidate can improve, regress, or remain inconclusive.
3. Review a promising candidate against the actual diff, evidence, compatibility, and user flow. Use an independent reviewer when available and authorized; otherwise make a separate review pass and record that limitation. An unresolved finding sends the candidate back for work. Any code change requires a new candidate measurement and review.
4. If shipment is in scope, prepare a reviewable PR with the hypothesis, baseline, result, and rollout/rollback details. Follow existing authorization for merge and deployment. Record release intent before a flagged deployment, then verify the released revision and flag and record the receipt. An interruption leaves release status unresolved until the actual provider state is checked. A passing local test never substitutes for a receipt.
5. Observe candidate and control under the defined field workload. Keep the deployed candidate fixed during observation. Preserve sample counts, observation window, cohort assignment, raw telemetry, and quality/cost checks. Inconclusive evidence remains inconclusive. A regression or exhausted observation allowance requires disabling the experiment and verifying recovery.
6. After accepted evidence, protect the gain with a regression threshold that retains noise headroom and the original quality checks. Record the test evidence and threshold. Close the run with a concise result; select the next bottleneck only within the authorized objective and budget.

## Resume and stop

Read the durable run state before acting. Verify the actual checkout and release state; recover interrupted external actions by inspecting receipts before retrying. Do not redeploy simply because a chat forgot the result. Save hypotheses, discarded attempts, artifact locations, and the next action in the record.

Stop candidate generation at the deadline or candidate limit. A blocked decision records the missing evidence. Never weaken the evaluator to claim a win, silently reset the baseline, or re-run identical failed work indefinitely. If an experiment is live, stopping includes its documented rollback or handoff; tool failure leaves recovery visibly pending.

## Writing

Report the result, supporting measurement, and the next material decision in plain prose. Keep the event history in the run record. Do not announce phase names, recite the checklist, print internal JSON, or call a local result a shipped improvement. Follow the local Humanizer output contract. Preserve uncertainty and important failures even when the update must be short.
