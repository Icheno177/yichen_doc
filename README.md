# yichen_doc

**Evidence-driven Decision Research Writing** for strategy, industry research, due diligence, business cases, AI research, and executive decision memos.

\`yichen_doc\` turns a vague research request into a decision-ready document: it separates facts from assumptions, grades evidence, exposes calculations, tests inference bridges, and ends with an owned recommendation. It is an instruction-first Codex Skill; no proprietary data, model provider, or external service is required.

## Core philosophy

Good decision writing is not a longer narrative. It is an auditable chain:

> decision question → evidence → assumptions → calculations → judgment → action

Numbers outrank adjectives. Temporal facts outrank slogans. A framework is useful only if it changes the decision. When evidence cannot support precision, the correct output is an explicit uncertainty—not a precise-looking number.

## What it supports

| Document type | Typical decision |
| --- | --- |
| Industry research | Which market, segment, or timing deserves attention? |
| Due diligence | Is the opportunity credible, material, and reversible enough to pursue? |
| Business case | Should we fund, build, buy, or defer? |
| AI research | Does an AI capability create workflow-level value under real operating constraints? |
| Strategy memo | What should a named owner do next, under what stop/go rule? |

## Architecture

| Layer | Purpose |
| --- | --- |
| [SKILL.md](SKILL.md) | Compact trigger, routing, workflow, and hard guards |
| [references/](references/) | Detailed evidence, method, style, reporting, and optional Socrates.CS guidance |
| [examples/](examples/) | Anonymized decision-writing specimens |
| [tests/](tests/) | Behavior-focused acceptance cases |
| [agents/openai.yaml](agents/openai.yaml) | Optional Codex UI metadata; implicit invocation remains enabled |

The required Codex Skill metadata is in \`SKILL.md\`: \`name\` and a discriminating \`description\`. The Skill itself is named **\`yichen-doc\`** (hyphenated for Codex naming conventions); the repository directory intentionally remains **\`yichen_doc\`**.

## Installation

### Codex CLI / desktop: personal Skill on Windows

From the directory containing this repository:

\`\`\`powershell
New-Item -ItemType Directory -Force "$env:USERPROFILE\\.agents\\skills"
Copy-Item -Recurse -Force .\\yichen_doc "$env:USERPROFILE\\.agents\\skills\\yichen_doc"
\`\`\`

Restart Codex if the Skill does not appear immediately. Current Codex documentation describes user-scoped discovery at \`$HOME/.agents/skills\`; repository-scoped Skills belong in \`.agents/skills\`.

### Repository-scoped installation

Copy this directory into the target repository as:

\`\`\`text
<repo>/.agents/skills/yichen_doc/
\`\`\`

### Invocation

In Codex CLI or an IDE integration, invoke it explicitly:

\`\`\`text
$yichen-doc Assess whether Company A should fund a 90-day AI support-agent pilot.
\`\`\`

It may also be selected automatically for matching research-writing tasks. The Skill has no mandatory tool or MCP dependency.

## Socrates.CS: optional falsification interface

Socrates.CS is **not** a dependency. \`yichen_doc\` owns the research, document, and decision workflow. If Socrates.CS exists in the environment, use it after drafting to challenge causal links, hidden assumptions, missing counterevidence, and overconfident recommendations. If it does not exist, run the same falsification questions manually. See [references/SOCRATES_CS_INTEGRATION.md](references/SOCRATES_CS_INTEGRATION.md).

## Evidence and calculation discipline

- Critical claims use Level A or B evidence; Level C supports context or trends; Level D is labeled as a company claim; Level E is only a lead or sentiment signal.
- Every material statement is distinguishable as FACT, INTERNAL DATA, ASSUMPTION, CALCULATION, JUDGMENT, or RECOMMENDATION.
- Forecasts and ROI use Bear/Base/Bull cases, variable ranges, formula visibility, and sensitivity—not one-point certainty.
- Recommendations identify an action, owner, timeline, resource/budget, KPI, and stop/go condition.

## Examples and acceptance cases

The examples use Company A/B and hypothetical values only:

- [Industry research](examples/industry_research.md)
- [Due diligence](examples/due_diligence.md)
- [Business case](examples/business_case.md)
- [AI research](examples/ai_research.md)

Behavioral tests are in [tests/](tests/); they evaluate decision quality and anti-overclaim behavior rather than exact wording.

## Limitations

This Skill improves structure and research discipline; it does not create evidence that has not been collected, replace legal/accounting/investment advice, or guarantee a decision outcome. Source access, primary-data availability, and authorized internal data still determine what can be concluded.

## License

MIT. See [LICENSE](LICENSE).
