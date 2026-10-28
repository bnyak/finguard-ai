from unittest.mock import patch

from fastapi.testclient import TestClient
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

# Replace this import with your actual FastAPI app module.
from finguard.api.main import app

client = TestClient(app)


def test_agent_ask_endpoint():
    mock_result = {
        "messages": [
            HumanMessage(content="What is APR?"),
            ToolMessage(
                content="APR is the annual percentage rate.",
                name="lookup_financial_definition",
                tool_call_id="call_1",
            ),
            AIMessage(content="APR stands for annual percentage rate."),
        ]
    }

    with patch(
        "finguard.api.routes.agent_routes.agent_graph.invoke",
        return_value=mock_result,
    ):
        response = client.post(
            "/agent/ask",
            json={"question": "What is APR?", "max_steps": 5},
        )

    assert response.status_code == 200
    assert response.json() == {
        "answer": "APR stands for annual percentage rate.",
        "tools_used": ["lookup_financial_definition"],
    }


def test_agent_ask_rejects_empty_question():
    response = client.post(
        "/agent/ask",
        json={"question": ""},
    )

    assert response.status_code == 422