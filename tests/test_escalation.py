from resolution_copilot.schemas import ClientIssue
from resolution_copilot.retrieval import CaseRetriever
from resolution_copilot.llm import mock_assess


def test_novel_case_escalates():
    issue = ClientIssue(
        client_company='Romandie Mobility SA',
        requester_role='Finance Lead',
        channel='email',
        subject='Card balance mismatch after a reversed food purchase',
        message='A restaurant payment was reversed by the merchant, but the benefit balance did not change after 48 hours.'
    )
    retrieved = CaseRetriever().search(f'{issue.subject} {issue.message}', top_k=3)
    response = mock_assess(issue, retrieved)
    assert response.decision == 'ESCALATE_NEW_CASE'
    assert response.ticket_payload is not None
