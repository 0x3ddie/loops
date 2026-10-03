# Design sources

Checked September 29, 2026. This system implements selected published practices. It does not reproduce Anthropic's private development process or claim the same shipping performance.

[Building effective agents](https://www.anthropic.com/engineering/building-effective-agents), December 19, 2024, describes simple composable workflows, explicit checks between steps, and evaluator feedback. We use a small state machine and add complexity only where a project needs it. That page now points readers to Managed Agents for current infrastructure guidance.

[Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents), November 26, 2025, describes initialization, incremental work, persistent progress records, and end-to-end verification. We use a frozen run contract, one hypothesis at a time, resumable state, and recorded evidence. Its sample app and shell tooling are not copied into unrelated projects.

[Demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents), January 9, 2026, distinguishes capability and regression evaluation, recommends repeated trials and appropriate graders, and combines offline evaluation with field monitoring and human feedback. We keep experimental improvements separate from regression protection and distinguish local acceptance from field acceptance.

[Scaling Managed Agents](https://www.anthropic.com/engineering/managed-agents), April 8, 2026, separates durable session records from the agent harness and execution environment. Our much smaller local design separates the run record from the current chat and uses existing tools for execution. We do not install a cloud service or reproduce its isolation architecture.

[Claude Code's quality postmortem](https://www.anthropic.com/engineering/april-23-postmortem), April 23, 2026, documents shortcomings in evaluation coverage and a verbosity instruction that reduced measured intelligence. It calls for broader per-model evaluation, soak periods, and gradual rollout. Our writing rules therefore remove filler and decorative formatting without a universal token cap. Harness or prompt changes must retain task quality and be checked across the models actually in use.

Our specific state names, file format, attempt limits, range-separation screen, rollback rules, threshold calculation, and writing linter are local design choices. They are not attributed to Anthropic. The range screen is conservative and is not a statistical significance claim.
