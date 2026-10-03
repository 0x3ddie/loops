---
name: work-debugging
description: Diagnose unclear bugs, regressions, or repeated failures using reproduction, focused experiments, and regression checks.
---

# Debugging

Use this workflow when the cause is uncertain. An obvious, well-understood fix does not need a ceremony.

## Establish the failure

Identify expected behavior, actual behavior, the relevant environment, and the smallest reproducible case. Read the full useful error and the code at the failing boundary. Check recent changes and existing tests. Record uncertainty when a production-only or intermittent issue cannot be reproduced locally.

## Investigate

- Form a specific hypothesis and choose the smallest observation that could disprove it.
- Follow data across the failing boundary. Compare a working example with the failing one. Use focused logging or a minimal test when existing evidence is insufficient.
- Change one relevant variable at a time. Keep diagnostic changes separate from the proposed fix, and remove temporary diagnostics when finished.
- If attempts repeatedly fail, reassess the hypothesis, reproduction, and architectural assumptions. Do not accumulate speculative patches or keep running the same failed command.
- Do not suppress an error or relax a test just to produce a passing result. A temporary workaround must identify the remaining defect and be justified by the task.

## Fix and verify

Apply the smallest change that addresses the demonstrated cause. Add a behavioral regression test when it is useful and feasible; first establish that it fails for the original reason. Verify the repaired case, the nearest relevant edge case, and required project checks after the final edit.

Report the cause and evidence, the behavioral change, and the checks actually run. If evidence supports only a hypothesis or workaround, say so.

This is an original local workflow. The broader [Superpowers collection](https://github.com/obra/superpowers) is a useful optional source for more prescriptive debugging and development processes; it is not a dependency of this skill.
