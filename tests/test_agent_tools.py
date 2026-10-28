from finguard.agent.tools.document_search import search_documents


def test_search_documents_tool():
    result = search_documents.invoke({
        "query": "What are mortgage points?",
        "top_k": 3,
    })

    assert "mortgage points" in result
    assert "top_k=3" in result