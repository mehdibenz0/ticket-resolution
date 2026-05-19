# Architecture Notes

## Core design

The application separates five concerns:

1. **Intake** — API / UI / n8n webhook.
2. **Retrieval** — search similar historical cases before asking the LLM to reason.
3. **Assessment** — Claude or mocked structured reasoning.
4. **Actioning** — reply drafting, clarifying questions, or ticket creation.
5. **Observability** — auditable run log and measurable decision outcomes.

## Why retrieval comes before generation

A support copilot that answers directly from model priors is unsafe. This project first retrieves the closest internal precedents and then requires the assessment layer to use that evidence conservatively.

## Why three decisions instead of two

Most business workflows are not merely “resolve vs escalate.” A meaningful third state is:

- `REQUEST_MORE_INFORMATION`

This prevents noisy escalations caused by low-quality incoming requests and demonstrates process thinking rather than blind automation.

## Production upgrades

Potential next steps:
- replace local TF-IDF retrieval with vector + BM25 hybrid search;
- add reranking;
- connect to Jira / Zendesk / CRM;
- use role-based access controls;
- add approval workflow before customer-facing reply dispatch;
- turn the knowledge base into a live feedback loop from resolved cases.
