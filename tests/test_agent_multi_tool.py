
from unittest.mock import patch

from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

from finguard.agent.graph import agent_graph


def test_agent_uses_two_tools():
    # First Qwen response: request two tools.
    tool_request = AIMessage(
        content="",
        tool_calls=[
            {
                "name": "search_documents",
                "args": {
                    "query": "mortgage points",
                    "top_k": 3,
                    "document_id": 2,
                },
                "id": "call_search_1",
                "type": "tool_call",
            },
            {
                "name": "calculate_loan_payment",
                "args": {
                    "principal": 300000,
                    "annual_rate": 6.5,
                    "years": 30,
                },
                "id": "call_calc_1",
                "type": "tool_call",
            },
        ],
    )

    # Second Qwen response: final answer.
    final_response = AIMessage(
        content=(
            "Mortgage points are upfront charges that can reduce "
            "the interest rate. The monthly principal-and-interest "
            "payment is $1,896.20."
        )
    )

    with patch(
        "finguard.agent.graph.call_qwen",
        side_effect=[tool_request, final_response],
    ) as mock_qwen:
        result = agent_graph.invoke(
            {
                "messages": [
                    HumanMessage(
                        content=(
                            "Explain mortgage points from the CFPB "
                            "document and calculate the monthly payment "
                            "for $300,000 at 6.5% over 30 years."
                        )
                    )
                ],
                "remaining_steps": 4,
            },
            config={"recursion_limit": 10},
        )

    tool_messages = [
        message
        for message in result["messages"]
        if isinstance(message, ToolMessage)
    ]

    print("\nTool results:")
    for message in tool_messages:
        print(f"\nTool: {message.name}")
        print(message.content)

    assert len(tool_messages) == 2

    search_result = next(
        message
        for message in tool_messages
        if message.name == "search_documents"
    )

    calculator_result = next(
        message
        for message in tool_messages
        if message.name == "calculate_loan_payment"
    )

    assert "Document ID: 2" in search_result.content
    assert "Page:" in search_result.content
    assert "1896.2" in calculator_result.content

    assert mock_qwen.call_count == 2
    assert result["messages"][-1].content.strip()

    print("\nFinal answer:", result["messages"][-1].content)
