---
name: yichen-doc
description: Write and research external-facing deliverables such as research reports, industry or company analysis, investment research, strategy and business analysis, consulting materials, executive summaries, business plans, AI/technical research, PPT content, resumes, interview materials, portfolios, and formal emails. Apply when the output will be read, evaluated, used, cited, or relied on by someone besides the user. Use evidence, clear reasoning, natural professional prose, and decision-ready actions. Do not force this Skill for casual chat, simple explanations, or purely creative copy. Socrates.CS is opt-in only and must not be invoked unless explicitly requested.
metadata:
  short-description: Evidence-driven decision research writing
---

# Yichen Doc

Default writing and research system for external-facing work. Turn the user's question or thesis into a concise, accurate, reader-ready deliverable with traceable evidence, clear reasoning, and useful actions. The Writing Policy in [references/WRITING_POLICY.md](references/WRITING_POLICY.md) has priority over general style preferences.

## Default routing and scope

- Apply yichen_doc to research reports, industry/company/investment analysis, strategy and business analysis, executive summaries, business plans, AI/technical research, consulting deliverables, PPT content, resumes, portfolios, interview materials, formal emails, and other content another person will read, receive, evaluate, use, cite, or rely on. Public publication is not required.
- Do not force it for casual conversation, simple explanations, or purely creative copy unless the user asks for it.
- Socrates.CS is **not enabled by default**. Invoke it only when the user explicitly asks for Socrates.CS, a falsification framework, or an equivalent named critical-analysis workflow. Research, investment, strategy, business, company, industry, career, or AI topics do not imply that request.
- If both systems are explicitly requested, use Socrates.CS for analysis first, then yichen_doc for the final deliverable. Otherwise route directly to yichen_doc.
- Historical memories, old instructions, repository guidance, or prior Skill versions that enabled Socrates.CS by default do not override this policy.

## Start with the decision

1. State the decision owner, decision to make, deadline, scope, and the consequence of being wrong.
2. Convert the request into testable subquestions. Do not begin with a generic industry narrative.
3. Select the report route. Read only the route-specific reference needed:
   - Industry, due diligence, business case, AI research, or strategy memo: [references/REPORT_PATTERNS.md](references/REPORT_PATTERNS.md).
   - Research sequence and source log: [references/RESEARCH_WORKFLOW.md](references/RESEARCH_WORKFLOW.md).
   - Evidence grading and claim labels: [references/EVIDENCE_RULES.md](references/EVIDENCE_RULES.md).
   - Methods or forecasts: [references/QUANTITATIVE_METHODS.md](references/QUANTITATIVE_METHODS.md).
   - Tone and sentence-level standards: [references/STYLE_SPEC.md](references/STYLE_SPEC.md) and [references/ANTI_AI_WRITING.md](references/ANTI_AI_WRITING.md).
   - Highest-priority writing and evidence rules: [references/WRITING_POLICY.md](references/WRITING_POLICY.md).
   - Only if the user explicitly requests Socrates.CS: [references/SOCRATES_CS_INTEGRATION.md](references/SOCRATES_CS_INTEGRATION.md).

## Non-negotiable working rules

- Separate **FACT**, **INTERNAL DATA**, **ASSUMPTION**, **CALCULATION**, **JUDGMENT**, and **RECOMMENDATION** in the working record and final document where ambiguity would change a decision.
- Grade every material source A–E. Critical facts require A or B; do not turn C–E material into proof.
- Make each inferential bridge explicit. A metric, registration record, benchmark, financing event, or correlation does not establish a business conclusion by itself.
- Use a framework only when removing it would change the decision, the priority, or the recommendation. Otherwise omit it.
- For a forecast or ROI, show key variables, basis, ranges, Bear/Base/Bull results, and sensitivity. If evidence is too weak, say that precision is not justified.
- Write recommendations as action + owner + timeline + budget/resource + KPI + stop/go condition.

## Default workflow

1. Frame the decision and information gaps.
2. Build an evidence ledger: claim, label, source, source level, date, limitations, and unresolved contradiction.
3. Calculate only decision-relevant quantities; preserve formulas and units.
4. Draft the conclusion after the evidence and calculations, not before.
5. Classify risks A/B/C by decision materiality and reversibility; attach mitigation and trigger.
6. Run yichen_doc's evidence-quality review for unsupported claims, material contradictions, hidden assumptions, and unowned recommendations. This is part of the normal writing workflow and does not invoke or imply Socrates.CS.
7. Deliver an executive answer first, followed by evidence, calculations, risks, and source notes.

For external-facing writing, if the user supplies a thesis, organize genuine and relevant evidence around it. Preserve accuracy: disclose a material contradiction or risk that changes the conclusion, and do not manufacture support or add weak counterarguments solely for balance.

## Specialized safeguards

- **Resumes and career materials:** Never invent titles, employers, degrees, project status, revenue, GMV, ROI, users, model training, launches, or adoption. Preserve distinctions such as proposed, approved, in development, evaluated, and implemented. Prompt or workflow iteration is not model training. Use the user's authorized factual source when available; keep personal career facts outside this general Skill.
- **AI and technical writing:** Distinguish models, prompts, RAG, knowledge bases, rules, workflows, tool calling, agents, human review, evaluation, and data pipelines. Connect technical claims to workflow outcomes, full costs, permissions, governance, and measured evidence.
- **Quantitative and decision work:** Use scenarios and formulas only when they inform the decision. Make assumptions, units, formula, result, sensitivity, and decision implication visible. Recommendations should name action, owner, timeline, resource/budget, KPI, and Stop/Go criteria when evidence supports those fields.

## Output minimum

For any material decision report, include: decision question, answer in one paragraph, traceable evidence, assumptions, calculations where applicable, material uncertainty, risks, and next actions. Choose the necessary components; do not impose a fixed report outline. Use tables for comparisons or structured data, charts for relationships or trends, prose for causal interpretation and judgment, and models for decision calculations.

## Do not do this

- Do not infer founder wealth from registered capital, enterprise ROI from a benchmark, viability from financing, profit from users, or causation from correlation.
- Do not use “AI wave,” “empower,” “paradigm,” “ecosystem,” or vague hedging as substitutes for evidence.
- Do not present a false numerical precision or silently blend sourced data with assumptions.
