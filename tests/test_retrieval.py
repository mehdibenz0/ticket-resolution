from resolution_copilot.retrieval import CaseRetriever


def test_retrieval_finds_gift_case():
    retriever = CaseRetriever()
    results = retriever.search('new employee cannot receive a reward gift', top_k=1)
    assert results[0]['case_id'] == 'CASE-GIFT-001'
    assert results[0]['score'] > 0
