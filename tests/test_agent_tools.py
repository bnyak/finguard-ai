from finguard.agent.tools.document_search import search_documents


def test_search_documents_tool():
    result = search_documents.invoke({
        "query": "What are mortgage points?",
        "top_k": 3,
    })

    assert "Points are a percentage of a loan" in result
    assert "Document ID:" in result
    assert "Page:" in result
    assert result.count("Document ID:") == 3