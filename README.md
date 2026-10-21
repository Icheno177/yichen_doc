# yichen_doc

**Evidence-driven writing and research for decisions and external readers.** `yichen_doc` is the default writing system for research reports, industry and company analysis, investment work, strategy and business analysis, executive summaries, business plans, AI/technical research, consulting deliverables, PPT content, resumes, interview materials, portfolios, formal emails, and other content another person may read or rely on.

It turns a question or stated thesis into an accurate, reader-ready document. The Skill separates evidence from assumptions, makes calculations traceable, writes in direct natural language, and ends with a decision or useful next step. It is instruction-first and requires no provider, proprietary data, or external service.

## When it applies

Use yichen_doc when preparing a substantive deliverable for someone besides the user. Publication is not required. Codex may select it implicitly for matching work; casual chat, simple explanations, and purely creative copy do not need it unless requested.

Examples of explicit invocation:

```text
使用 yichen_doc 写一份企业 AI Agent 行业报告。
$yichen-doc Assess whether Company A should fund a 90-day AI support-agent pilot.
```

After yichen_doc is configured by repository-level [AGENTS.md](AGENTS.md), the first request may also be phrased without naming the Skill:

```text
写一份企业 AI Agent 行业报告。
```

## Writing philosophy

The shortest useful decision chain is:

> Research Question → Facts & Evidence → Structured Decomposition → Quantitative Analysis / Business Model → Judgment → Decision Recommendation → Execution

Use only the stages and sections the question needs. If the user supplies a thesis, organize genuine, relevant support around it. Preserve material contradictions and risks; do not distort evidence or add weak objections for the appearance of balance.

## Evidence first

Distinguish FACT, INTERNAL DATA, ASSUMPTION, CALCULATION, JUDGMENT, and RECOMMENDATION. Prefer direct and official records, regulatory and government sources, company filings, audited or investor materials, and high-quality research. Record source, date, period, unit, denominator, and limitations when they affect the claim. State “公开资料未披露”, “N/A”, “Missing Data”, or “当前材料无法支持该结论” when support is absent. Never infer business outcomes from a proxy such as registered capital, financing, users, benchmarks, or correlation alone.

## Direct, natural writing

Avoid templated contrast formulas, AI identity disclaimers, empty narration, unsupported hedging, and marketing language. State the subject, action, evidence, and implication plainly. Prefer numbers over adjectives, outcomes over process descriptions, and informative headings over generic labels. Full rules and examples are in [references/WRITING_POLICY.md](references/WRITING_POLICY.md) and [references/ANTI_AI_WRITING.md](references/ANTI_AI_WRITING.md).

## Quantitative and decision orientation

Use a model only when it can change the decision. For forecasts, use Bear/Base/Bull cases where useful and show assumptions, formulas, outputs, sensitivity, and decision implications. Include full operating cost, review effort, error remediation, integration, and governance in AI business cases. Recommendations identify Action, Owner, Timeline, Budget/Resource, KPI, and Stop/Go criteria when evidence supports them.

## Resume and AI safeguards

Resumes must not invent titles, employers, degrees, project status, revenue, GMV, ROI, user counts, model training, launches, or adoption. Preserve distinctions such as proposed, approved, in development, evaluated, and implemented. Prompt/workflow iteration is not model training. Personal career facts belong in a separate authorized source, not this general Skill.

AI writing distinguishes models, prompts, RAG, knowledge bases, rules, workflows, tool calling, agents, human review, evaluation, and data pipelines. Technical capability is connected to measured workflow value, cost, permissions, and governance.

## Socrates.CS is opt-in only

Socrates.CS is an optional falsification and critical-analysis system. It is **not enabled by default** and is invoked only when the user explicitly requests Socrates.CS, a falsification framework, or equivalent named workflow. Research, strategy, investment, business, company, industry, career, and AI topics do not imply a request.

Default:

```text
User request → yichen_doc
```

When the user explicitly requests both:

```text
User request → Socrates.CS analysis/falsification → yichen_doc → final output
```

Example:

```text
使用 Socrates.CS 分析这个商业判断，然后用 yichen_doc 输出正式报告。
```

Prior memories, old prompts, repository guidance, or historical Skill versions do not override this opt-in rule. See [references/SOCRATES_CS_INTEGRATION.md](references/SOCRATES_CS_INTEGRATION.md).

## Architecture

| Layer | Purpose |
| --- | --- |
| [SKILL.md](SKILL.md) | Trigger, routing, workflow, and safeguards |
| [references/](references/) | Writing policy, evidence, methods, reporting, and optional Socrates guidance |
| [examples/](examples/) | Anonymized research and business-writing specimens |
| [tests/](tests/) | Behavior-focused acceptance and regression cases |
| [AGENTS.md](AGENTS.md) | Repository-level default writing instructions |
| [agents/openai.yaml](agents/openai.yaml) | Codex UI metadata and implicit-invocation setting |

The Codex Skill name is `yichen-doc`; the repository folder intentionally remains `yichen_doc`.

## Examples and tests

Examples use Company A/B and hypothetical inputs:

- [Industry research](examples/industry_research.md)
- [Due diligence](examples/due_diligence.md)
- [Business case](examples/business_case.md)
- [AI research](examples/ai_research.md)

Acceptance cases are in [tests/](tests/). They test evidence discipline, routing, Socrates opt-in behavior, anti-AI writing, thesis handling, resume safeguards, and technical terminology.

## Installation and use in Codex

### Personal Skill on Windows

From the directory containing this repository:

```powershell
New-Item -ItemType Directory -Force "$env:USERPROFILE\.agents\skills"
Copy-Item -Recurse -Force .\yichen_doc "$env:USERPROFILE\.agents\skills\yichen_doc"
```

Restart Codex if the Skill does not appear immediately. User-scoped Skills are discovered under `$HOME/.agents/skills`; repository-scoped Skills belong in `.agents/skills`.

### Repository-scoped installation

Copy the directory into a target repository as:

```text
<repo>/.agents/skills/yichen_doc/
```

The included `AGENTS.md` demonstrates how to make yichen_doc the repository's default for substantive external-facing writing. Do not copy it into a repository unless that default is wanted there.

## Limits

The Skill improves research and writing discipline; it cannot create missing evidence, replace professional advice, or guarantee an outcome. Source access, primary-data availability, and authorized internal information determine what can be concluded.

## License

MIT. See [LICENSE](LICENSE).
