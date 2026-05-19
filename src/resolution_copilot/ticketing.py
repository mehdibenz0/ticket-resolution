from __future__ import annotations
from datetime import datetime, timezone
from pathlib import Path
import json
from resolution_copilot.config import settings
from resolution_copilot.schemas import ClientIssue, TicketPayload


def build_ticket_payload(issue: ClientIssue, evidence: list[str], missing_information: list[str]) -> TicketPayload:
    priority = 'high' if any(word in issue.message.lower() for word in ['blocked', 'cannot', 'urgent']) else 'medium'
    return TicketPayload(
        title=f"Investigate: {issue.subject}",
        category='client_operations_escalation',
        priority=priority,
        problem_statement=issue.message,
        client_company=issue.client_company,
        requester_role=issue.requester_role,
        evidence_collected=evidence,
        reproduction_notes=[
            f"Reported via {issue.channel}.",
            f"Subject: {issue.subject}",
        ],
        missing_information=missing_information,
        proposed_owner='Operations / Product Support',
    )


def persist_ticket(ticket: TicketPayload) -> Path:
    settings.generated_ticket_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    safe = ''.join(ch.lower() if ch.isalnum() else '-' for ch in ticket.title)[:60].strip('-')
    path = settings.generated_ticket_dir / f'{timestamp}-{safe}.json'
    path.write_text(ticket.model_dump_json(indent=2), encoding='utf-8')
    return path
