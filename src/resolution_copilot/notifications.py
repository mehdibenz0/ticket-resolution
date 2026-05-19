from __future__ import annotations
import requests
from resolution_copilot.config import settings
from resolution_copilot.schemas import CopilotResponse


def notify_escalation(response: CopilotResponse) -> None:
    if not settings.slack_webhook_url or not response.ticket_payload:
        return
    payload = {
        'text': (
            '🚨 New AI-generated escalation ticket\n'
            f"*Client:* {response.ticket_payload.client_company}\n"
            f"*Issue:* {response.ticket_payload.title}\n"
            f"*Reason:* {response.escalation_reason or 'Low confidence / novel case'}"
        )
    }
    requests.post(settings.slack_webhook_url, json=payload, timeout=5)
