
from langchain_core.messages import HumanMessage

from finguard.agent.graph import agent_graph


def test_agent_calculates_mortgage():
    result = agent_graph.invoke({
        "messages": [
            HumanMessage(
                content=(
                    "Calculate the monthly principal-and-interest "
                    "payment for a $300,000 mortgage at 6.5% "
                    "over 30 years."
                )
            )
        ],
        "remaining_steps": 4,
    })

    for message in result["messages"]:
        print(
            "\nMessage:",
            message.type,
            "\nContent:",
            message.content,
        )

    tool_messages = [
        message
        for message in result["messages"]
        if message.type == "tool"
    ]

    assert len(tool_messages) >= 1
    assert any(
        "1896.2" in str(message.content)
        for message in tool_messages
    )
