
from langchain_core.messages import HumanMessage, ToolMessage

from finguard.agent.graph import agent_graph


def test_real_qwen_uses_multiple_tools():
    result = agent_graph.invoke(
        {
            "messages": [
                HumanMessage(
                    content=(
                        "According to the uploaded CFPB document, "
                        "explain mortgage points. Also calculate "
                        "the monthly principal-and-interest payment "
                        "for a $300,000 mortgage at 6.5% for 30 years."
                    )
                )
            ],
            "remaining_steps": 5,
        },
        config={"recursion_limit": 15},
    )

    for message in result["messages"]:
        print("\nMessage:", message.type)
        print("Content:", message.content)

        if getattr(message, "tool_calls", None):
            print("Tool calls:", message.tool_calls)

    tool_messages = [
        message
        for message in result["messages"]
        if isinstance(message, ToolMessage)
    ]

    tool_names = {message.name for message in tool_messages}

    assert "search_documents" in tool_names
    assert "calculate_loan_payment" in tool_names

    final_answer = result["messages"][-1].content

    assert final_answer.strip()
    assert "1,896" in final_answer or "1896" in final_answer

    print("\nFINAL ANSWER:\n", final_answer)
