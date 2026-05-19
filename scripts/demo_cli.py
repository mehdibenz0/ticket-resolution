from __future__ import annotations
import argparse
import json
from pathlib import Path
import requests

SCENARIO_FILES = {
    'known': 'known_gift_distribution_issue.json',
    'missing': 'missing_context_issue.json',
    'novel': 'novel_refund_issue.json',
}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--scenario', choices=SCENARIO_FILES, default='known')
    parser.add_argument('--url', default='http://localhost:8000/analyze-case')
    args = parser.parse_args()

    path = Path('data/sample_requests') / SCENARIO_FILES[args.scenario]
    payload = json.loads(path.read_text(encoding='utf-8'))
    response = requests.post(args.url, json=payload, timeout=30)
    response.raise_for_status()
    print(json.dumps(response.json(), indent=2))


if __name__ == '__main__':
    main()
