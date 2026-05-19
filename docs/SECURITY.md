# Security and Privacy Notes

## What this demo does right
- Uses synthetic data only.
- Stores all secrets in environment variables.
- Separates evidence retrieval from generated conclusions.
- Avoids auto-resolving low-confidence or novel issues.
- Persists generated escalation tickets for auditability.

## Production considerations
- Authentication and authorization for all API endpoints.
- PII minimization before sending context to an LLM.
- Redaction layer for employee identifiers where possible.
- Approval gate before sending customer-facing messages automatically.
- Event logs for escalations, overrides, and resolutions.
- Rate limiting and abuse controls on public webhooks.
