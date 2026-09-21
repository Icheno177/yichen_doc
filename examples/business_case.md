# Example: AI Support-Triage Business Case

## Decision

Fund a 90-day pilot for Company A's support triage workflow, capped at ¥480k.

## Inputs

| Item | Label | Value | Basis |
| --- | --- | --- | --- |
| Monthly tickets | INTERNAL DATA | 24,000 | 2026Q2 service log |
| Manual handling time | INTERNAL DATA | 6 minutes/ticket | sampled time study |
| Automation eligible share | ASSUMPTION | 30%–45% | quality review needed |
| Loaded labor cost | ASSUMPTION | ¥1.20/minute | finance estimate |
| Pilot cost | FACT | ¥480k | vendor quote |

## Calculation

Base annual gross labor capacity released:

24,000 × 12 × 40% × 6 minutes × ¥1.20 = ¥829,440.

This is capacity value, not booked savings. Realized savings require headcount avoidance, redeployment, or revenue conversion.

| Scenario | Eligible share | Quality pass | Annual capacity value | Decision |
| --- | --- | --- | --- | --- |
| Bear | 30% | 75% | ¥466,560 | Do not scale |
| Base | 40% | 85% | ¥705,024 | Extend with controls |
| Bull | 45% | 90% | ¥839,808 | Prepare scale case |

## Recommendation

**Action:** Pilot with human review for all customer-impacting responses. **Owner:** Support Operations. **By:** 90 days. **Budget:** ¥480k. **KPI:** ≥85% audited routing accuracy and ≥25% handling-time reduction. **Stop/go:** Stop if critical-routing error exceeds 1% for two consecutive weeks.
