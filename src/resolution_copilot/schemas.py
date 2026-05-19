from __future__ import annotations
from typing import Any, Literal
from pydantic import BaseModel, Field


class IssueMetadata(BaseModel):
    employee_created_recently: bool | None = None
    gift_amount_chf: float | None = None
    employee_identifier_present: bool | None = None
    account_identifier_present: bool | None = None
    attachment_present: bool | None = None
    additional: dict[str, Any] = Field(default_factory=dict)


class ClientIssue(BaseModel):
    client_company: str = Field(..., min_length=2)
    requester_role: str = Field(..., min_length=2)
    channel: Literal['email', 'form', 'chat', 'internal'] = 'form'
    subject: str = Field(..., min_length=4)
    message: str = Field(..., min_length=10)
    metadata: IssueMetadata = Field(default_factory=IssueMetadata)


class RetrievedCase(BaseModel):
    case_id: str
    title: str
    category: str
    score: float
    resolution_summary: str
    why_relevant: str


class TicketPayload(BaseModel):
    title: str
    category: str
    priority: Literal['low', 'medium', 'high']
    problem_statement: str
    client_company: str
    requester_role: str
    evidence_collected: list[str]
    reproduction_notes: list[str]
    missing_information: list[str]
    proposed_owner: str


class CopilotResponse(BaseModel):
    decision: Literal['RESOLVE_FROM_KNOWLEDGE', 'REQUEST_MORE_INFORMATION', 'ESCALATE_NEW_CASE']
    confidence: float = Field(..., ge=0.0, le=1.0)
    issue_category: str
    operator_summary: str
    recommended_steps: list[str]
    clarifying_questions: list[str]
    draft_client_reply: str
    similar_cases: list[RetrievedCase]
    evidence: list[str]
    escalation_reason: str | None = None
    ticket_payload: TicketPayload | None = None


class HealthResponse(BaseModel):
    status: str
    llm_mode: str
