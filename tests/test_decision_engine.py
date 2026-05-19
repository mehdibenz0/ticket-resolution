from resolution_copilot.schemas import ClientIssue
from resolution_copilot.retrieval import CaseRetriever
from resolution_copilot.llm import mock_assess


def test_known_case_resolves_from_knowledge():
    issue = ClientIssue(
        client_company='Alpine Robotics SA',
        requester_role='HR Ops',
        channel='email',
        subject='Gift budget cannot be assigned to one employee',
        message='A newly added employee cannot receive the CHF 100 reward and distribution is rejected.',
        metadata={'employee_identifier_present': True, 'account_identifier_present': True}
    )
    retrieved = CaseRetriever().search(f'{issue.subject} {issue.message}', top_k=3)
    response = mock_assess(issue, retrieved)
    assert response.decision == 'RESOLVE_FROM_KNOWLEDGE'
    assert response.ticket_payload is None


def test_vague_case_requests_more_information():
    issue = ClientIssue(
        client_company='Helvetia Labs AG',
        requester_role='People Ops',
        channel='form',
        subject='Portal issue',
        message='Something does not work. Please help.'
    )
    retrieved = CaseRetriever().search(f'{issue.subject} {issue.message}', top_k=3)
    response = mock_assess(issue, retrieved)
    assert response.decision == 'REQUEST_MORE_INFORMATION'
    assert response.clarifying_questions
