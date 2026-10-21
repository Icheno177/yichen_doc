# Report Routing Acceptance Cases

## Case 1: Agent benchmark

**Prompt:** “An agent benchmark improved by 20 points. Deploy agents to all workflows.”
**Pass condition:** Route to AI research. Test workflow cost, errors, human review, latency, integration, permissions, and risk tolerance. Do not convert a benchmark directly into enterprise ROI.

## Case 2: Market entry

**Prompt:** “Should we enter this sector?”
**Pass condition:** Route to industry research. Define the segment and entry decision, then use market boundary, demand/supply/economics, competition, scenarios, and entry conditions. Frameworks are optional.

## Case 3: Acquisition

**Prompt:** “Should we acquire Company B?”
**Pass condition:** Route to due diligence. Surface disqualifiers, verification gaps, concentration, legal/technical/commercial risks, and conditions precedent before a recommendation.

## Case 4: Investment research does not imply Socrates.CS

**Prompt:** “分析这家公司是否值得投资。”
**Pass condition:** yichen_doc applies. Socrates.CS does not apply unless the user explicitly asks for it.

## Case 5: Explicit Socrates.CS request

**Prompt:** “使用 Socrates.CS 分析这家公司是否值得投资。”
**Pass condition:** Socrates.CS analysis/falsification runs first, followed by yichen_doc for the final deliverable.

## Case 6: Industry report does not imply Socrates.CS

**Prompt:** “帮我写一份行业研究报告。”
**Pass condition:** yichen_doc applies. No automatic Socrates.CS invocation.

## Case 7: Casual/simple requests

**Prompt:** “用一句话解释什么是市盈率。”
**Pass condition:** Do not force yichen_doc for a simple explanation.
