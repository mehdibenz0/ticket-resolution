from __future__ import annotations
from fastapi import FastAPI
from resolution_copilot.schemas import ClientIssue, CopilotResponse, HealthResponse
from resolution_copilot.config import settings
from resolution_copilot.retrieval import CaseRetriever
from resolution_copilot.llm import assess_issue
from resolution_copilot.ticketing import persist_ticket
from resolution_copilot.notifications import notify_escalation
from resolution_copilot.metrics import log_run

app = FastAPI(
    title='B2B Resolution Copilot',
    version='1.0.0',
    description='AI copilot for retrieving similar B2B operations cases and preparing safe next actions.'
)
retriever = CaseRetriever()


@app.get('/health', response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status='ok', llm_mode=settings.llm_mode)


@app.post('/analyze-case', response_model=CopilotResponse)
def analyze_case(issue: ClientIssue) -> CopilotResponse:
    query = f"{issue.subject} {issue.message}"
    retrieved = retriever.search(query, top_k=3)
    response = assess_issue(issue, retrieved)
    if response.ticket_payload:
        persist_ticket(response.ticket_payload)
        notify_escalation(response)
    log_run(issue, response)
    return response
