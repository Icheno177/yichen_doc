# Quantitative Methods

Use a method only when it changes a live decision. State input sources, units, period, formulas, assumptions, and limitations.

## Market sizing

- **TAM:** total demand under the stated market definition.
- **SAM:** portion serviceable given geography, product, regulation, and channel.
- **SOM:** realistically obtainable portion under capacity, conversion, competition, and time constraints.

Use top-down sizing to set a ceiling and bottom-up sizing to test operating feasibility. Reconcile definitions before comparing figures.

## Operating and investment economics

- **GMV:** transaction value; do not call it revenue.
- **Revenue:** price × recognized volume, net of the relevant take rate/returns.
- **Unit economics:** contribution per unit = revenue per unit − variable cost per unit.
- **ROI:** (incremental benefit − incremental cost) / incremental cost.
- **TCO:** acquisition + implementation + integration + training + operating + risk/control + decommissioning costs.
- **Payback:** time until cumulative incremental cash benefit recovers the investment.
- **DCF:** discount projected free cash flow only when duration, risk, and cash-flow evidence warrant it.

For AI/agent economics include model/inference cost, orchestration, integration, review, error remediation, latency/SLA, monitoring, and avoided labor or revenue impact. “Tokens are cheap” is not an ROI model.

## Causal and experimental methods

Use DID, regression, event study, or controlled experiments only when the decision depends on causal attribution and the data/method assumptions are credible. State treatment, comparison group, timing, confounders, and threats to validity. A correlation is not proof of impact.

## Forecasts, uncertainty, and scenarios

Always provide Bear/Base/Bull when forecasting affects a decision:

| Variable | Basis | Bear | Base | Bull | Sensitivity |
| --- | --- | --- | --- | --- | --- |

Show the output of each case and identify which variable can reverse the recommendation. If the evidence cannot establish a reasonable range, do not produce false precision; recommend data collection or a bounded experiment.

## Risk scoring and cost-benefit

Score only to prioritize action, not to simulate precision. Define scale, likelihood, impact, reversibility, owner, mitigation, and trigger. A useful risk register changes resource allocation or a stop/go decision.
