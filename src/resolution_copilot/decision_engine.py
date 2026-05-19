from __future__ import annotations
from resolution_copilot.schemas import ClientIssue
from resolution_copilot.config import settings


def derive_deterministic_decision(issue: ClientIssue, retrieved_cases: list[dict]) -> dict:
    top_score = retrieved_cases[0]['score'] if retrieved_cases else 0.0
    text = f"{issue.subject} {issue.message}".lower()

    missing_identifiers = []
    if 'employee' in text and not issue.metadata.employee_identifier_present:
        missing_identifiers.append('employee identifier')
    if ('account' in text or 'client' in text) and not issue.metadata.account_identifier_present:
        missing_identifiers.append('client account identifier')

    obviously_missing_context = any(phrase in text for phrase in [
        'does not work', 'it fails', 'please help', 'something is wrong'
    ]) and len(issue.message.split()) < 18

    if obviously_missing_context:
        return {
            'decision': 'REQUEST_MORE_INFORMATION',
            'confidence': 0.58,
            'issue_category': 'insufficient_context',
            'escalation_reason': None,
        }

    novel_payment_patterns = any(phrase in text for phrase in [
        'reversed', 'refund', 'credited back', 'chargeback', 'balance mismatch'
    ])

    if top_score >= settings.similarity_threshold and not novel_payment_patterns:
        confidence = min(0.97, max(0.76, top_score + 0.12))
        return {
            'decision': 'RESOLVE_FROM_KNOWLEDGE',
            'confidence': round(confidence, 2),
            'issue_category': retrieved_cases[0]['category'],
            'escalation_reason': None,
        }

    return {
        'decision': 'ESCALATE_NEW_CASE',
        'confidence': round(max(0.62, 1 - top_score), 2),
        'issue_category': 'novel_or_uncertain_case',
        'escalation_reason': 'No sufficiently similar precedent was found in the internal knowledge base.',
    }
