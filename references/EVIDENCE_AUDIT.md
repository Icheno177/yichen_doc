# Evidence-to-Claim Audit

Supply explicit `claims` and `sources` arrays in the private audit manifest. Claims should record ID, text/location, evidence label, source IDs, criticality, definition, unit, reporting period and limitation. Sources should record title, publisher, date, period, URL or file locator, A–E grade, definition and limitations.

The engine checks labels, unknown/missing source IDs and absent grades. Optional URL checking records reachability only. A reachable URL does not prove its contents support the claim; compare the source and claim scope manually.

Check period, currency, denominator, definition and units; keep company-reported figures attributed; avoid overstating proxies, registrations, benchmarks, user counts and correlations; distinguish FACT, INTERNAL_DATA, ASSUMPTION, CALCULATION, JUDGMENT and RECOMMENDATION; record contradictions and missing evidence rather than filling gaps.

Without a claim ledger, evidence audit is `NOT_RUN`; the engine does not infer a complete claim graph from prose.
