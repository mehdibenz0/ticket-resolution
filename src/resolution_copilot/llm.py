from __future__ import annotations
import json
from resolution_copilot.config import settings
from resolution_copilot.schemas import ClientIssue, CopilotResponse, RetrievedCase
from resolution_copilot.decision_engine import derive_deterministic_decision
from resolution_copilot.ticketing import build_ticket_payload


def _recommended_steps_for(category: str) -> list[str]:
    library = {
        'gift_distribution': [
            'Verify that the employee exists in the latest synchronized roster.',
            'Check that the employee is eligible for reward distribution under the client account.',
            'Retry the assignment after the account or eligibility refresh.',
            'If the error persists, escalate with employee ID, client account ID, and timestamp.',
        ],
        'platform_access': [
            'Confirm that the user invitation was sent to the expected email address.',
            'Check whether the activation link expired or was already consumed.',
            'Resend the activation flow if policy permits.',
            'Escalate with account reference if access remains blocked.',
        ],
        'card_payment_scope': [
            'Confirm the merchant category and transaction type.',
            'Check whether the transaction falls within the allowed benefit usage scope.',
            'Explain any spending restriction clearly to the client-facing team.',
            'Escalate only if the merchant classification appears inconsistent.',
        ],
        'insufficient_context': [
            'Ask for the affected user or account reference.',
            'Ask for the exact action attempted and error text.',
            'Ask for timestamp and screenshots if available.',
        ],
        'novel_or_uncertain_case': [
            'Preserve the customer message and relevant metadata.',
            'Create a structured escalation ticket for investigation.',
            'Avoid overconfident customer messaging until root cause is validated.',
        ],
    }
    return library.get(category, library['novel_or_uncertain_case'])


def _clarifying_questions(issue: ClientIssue, decision: str) -> list[str]:
    if decision != 'REQUEST_MORE_INFORMATION':
        return []
    return [
        'Which employee or account is affected?',
        'What exact action was attempted immediately before the issue?',
        'What exact error message or screenshot is available?',
    ]


def _draft_reply(decision: str, issue: ClientIssue) -> str:
    if decision == 'RESOLVE_FROM_KNOWLEDGE':
        return (
            'Thanks for flagging this. We found that this appears to match a known operational pattern. '
            'We recommend following the validation steps below first, and we can escalate immediately if the issue remains unresolved.'
        )
    if decision == 'REQUEST_MORE_INFORMATION':
        return (
            'Thanks for reaching out. To investigate this properly, could you please share the affected user or account reference, '
            'the exact action attempted, and any visible error message or screenshot?'
        )
    return (
        'Thanks for reporting this. We have prepared an internal investigation because the issue does not clearly match an existing documented case. '
        'We will review it with the relevant team and follow up with the next step.'
    )


def mock_assess(issue: ClientIssue, retrieved_cases: list[dict]) -> CopilotResponse:
    decision = derive_deterministic_decision(issue, retrieved_cases)
    similar_cases = [RetrievedCase(**item) for item in retrieved_cases]
    evidence = [
        f"Top retrieved case score: {retrieved_cases[0]['score']}" if retrieved_cases else 'No retrieved case passed ranking.',
        f"Issue channel: {issue.channel}",
        f"Client company: {issue.client_company}",
    ]
    clarifying_questions = _clarifying_questions(issue, decision['decision'])
    ticket_payload = None
    if decision['decision'] == 'ESCALATE_NEW_CASE':
        ticket_payload = build_ticket_payload(issue, evidence, missing_information=[])
    return CopilotResponse(
        decision=decision['decision'],
        confidence=decision['confidence'],
        issue_category=decision['issue_category'],
        operator_summary=(
            'This issue appears to match a documented precedent and can likely be handled from the knowledge base.'
            if decision['decision'] == 'RESOLVE_FROM_KNOWLEDGE'
            else 'The information provided is not yet sufficient for a confident operational recommendation.'
            if decision['decision'] == 'REQUEST_MORE_INFORMATION'
            else 'The issue appears novel or too weakly matched to prior cases, so a structured escalation should be created.'
        ),
        recommended_steps=_recommended_steps_for(decision['issue_category']),
        clarifying_questions=clarifying_questions,
        draft_client_reply=_draft_reply(decision['decision'], issue),
        similar_cases=similar_cases,
        evidence=evidence,
        escalation_reason=decision['escalation_reason'],
        ticket_payload=ticket_payload,
    )


def anthropic_assess(issue: ClientIssue, retrieved_cases: list[dict]) -> CopilotResponse:
    if not settings.anthropic_api_key:
        raise RuntimeError('ANTHROPIC_API_KEY is required when LLM_MODE=anthropic')
    from anthropic import Anthropic
    client = Anthropic(api_key=settings.anthropic_api_key)
    schema = CopilotResponse.model_json_schema()
    prompt = {
        'task': 'Assess a B2B client operations issue using only the provided evidence. If no evidence strongly supports resolution, escalate or request more information.',
        'issue': issue.model_dump(),
        'retrieved_cases': retrieved_cases,
        'rules': [
            'Do not invent internal facts.',
            'Use RESOLVE_FROM_KNOWLEDGE only when the retrieved cases materially support it.',
            'Use REQUEST_MORE_INFORMATION when the user message is too vague for a safe recommendation.',
            'Use ESCALATE_NEW_CASE when the issue appears novel or low-confidence.',
            'If escalating, include a complete ticket_payload.',
        ],
    }
    message = client.messages.create(
        model=settings.anthropic_model,
        max_tokens=1800,
        temperature=0,
        system='You are a careful operations copilot for a B2B benefits platform. Return only JSON matching the required schema.',
        messages=[{'role': 'user', 'content': json.dumps(prompt)}],
        output_config={'format': {'type': 'json_schema', 'schema': schema}},
    )
    text = ''.join(block.text for block in message.content if getattr(block, 'type', '') == 'text')
    return CopilotResponse.model_validate_json(text)


def assess_issue(issue: ClientIssue, retrieved_cases: list[dict]) -> CopilotResponse:
    if settings.llm_mode.lower() == 'anthropic':
        return anthropic_assess(issue, retrieved_cases)
    return mock_assess(issue, retrieved_cases)
