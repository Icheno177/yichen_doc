# Example: Benchmark Result to Workflow Decision

## Claim under review

A vendor reports a +20 point improvement on an agent benchmark. Should Company A deploy the agent to all service workflows?

## Answer

No. The benchmark is capability evidence, not business-value evidence. It does not establish performance on Company A's tool permissions, data quality, latency target, error tolerance, integration workload, or human-review cost.

## Validation design

| Measure | Baseline | Pilot measure | Stop/go threshold |
| --- | --- | --- | --- |
| Task completion | manual workflow | blinded audit | ≥ baseline quality |
| Critical error | current process | incident review | ≤ agreed tolerance |
| End-to-end latency | current SLA | production-like run | within SLA |
| Cost per completed task | labor + systems | full agent TCO | lower than base case |
| Human review | current QA | sampled review | no hidden transfer of work |

## Decision

Run one bounded workflow with reversible permissions. Scale only after the pilot produces workflow-level evidence across quality, cost, latency, integration, and human oversight.
