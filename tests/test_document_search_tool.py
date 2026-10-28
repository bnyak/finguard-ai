
from finguard.agent.tools.document_search import search_documents


def test_document_search_tool():
    result = search_documents.invoke({
        "query": "What are mortgage points?",
        "top_k": 3,
    })

    print("\nRetrieved passages:\n", result)

    assert isinstance(result, str)
    assert "Document ID: 2" in result
    assert "Page:" in result
    assert "Content:" in result
    assert "mortgage" in result.lower()


def test_document_search_with_document_filter():
    result = search_documents.invoke({
        "query": "What are mortgage points?",
        "top_k": 3,
        "document_id": 2,
    })

    print("\nFiltered passages:\n", result)

    assert "Document ID: 2" in result
    assert "Document ID: 1" not in result
    assert "Content:" in result
