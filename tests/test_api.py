from fastapi.testclient import TestClient
from resolution_copilot.app import app

client = TestClient(app)


def test_health():
    response = client.get('/health')
    assert response.status_code == 200
    assert response.json()['status'] == 'ok'


def test_analyze_case_api():
    payload = {
        'client_company': 'Alpine Robotics SA',
        'requester_role': 'HR Ops',
        'channel': 'email',
        'subject': 'Gift assignment rejected',
        'message': 'A newly added employee cannot receive a reward gift after being added yesterday.',
        'metadata': {'employee_identifier_present': True, 'account_identifier_present': True}
    }
    response = client.post('/analyze-case', json=payload)
    assert response.status_code == 200
    assert 'decision' in response.json()
