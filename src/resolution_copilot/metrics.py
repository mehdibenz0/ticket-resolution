from __future__ import annotations
from datetime import datetime, timezone
import json
from resolution_copilot.config import settings
from resolution_copilot.schemas import ClientIssue, CopilotResponse


def log_run(issue: ClientIssue, response: CopilotResponse) -> None:
    settings.run_log_path.parent.mkdir(parents=True, exist_ok=True)
    row = {
        'timestamp_utc': datetime.now(timezone.utc).isoformat(),
        'client_company': issue.client_company,
        'channel': issue.channel,
        'decision': response.decision,
        'confidence': response.confidence,
        'issue_category': response.issue_category,
        'similar_case_count': len(response.similar_cases),
    }
    with settings.run_log_path.open('a', encoding='utf-8') as handle:
        handle.write(json.dumps(row) + '\n')
