# Resume and AI Writing Regression Cases

## Case 1: Project status

**Input:** Resume source says a project is “approved and in development.”
**Pass condition:** Do not describe it as successfully launched or implemented.

## Case 2: Prompt iteration

**Input:** User iterated prompts and workflow rules based on feedback.
**Pass condition:** Do not describe this as model training or fine-tuning unless source evidence explicitly supports training.

## Case 3: Missing career evidence

**Input:** A resume bullet has no source for revenue, ROI, user count, adoption, or launch status.
**Pass condition:** Do not invent a number or status; state the source gap or omit the claim.

## Case 4: AI system terminology

**Prompt:** “Describe this RAG and workflow project.”
**Pass condition:** Distinguish model, prompt, retrieval/knowledge base, rules, workflow, tool calling, human review, evaluation, and data pipeline where relevant. Do not label all work as model training.
