
from langchain_core.messages import HumanMessage, ToolMessage

from finguard.agent.graph import agent_graph


def test_agent_searches_cfpb_document():
    result = agent_graph.invoke(
        {
            "messages": [
                HumanMessage(
                    content=(
                        "According to the uploaded CFPB document, "
                        "what are mortgage points? "
                        "Use the search_documents tool. "
                        "Include the document ID and page number "
                        "from the retrieved evidence."
                    )
                )
            ],
            "remaining_steps": 4,
        },
        config={"recursion_limit": 10},
    )

    for message in result["messages"]:
        print("\nMessage type:", message.type)
        print("Content:", message.content)

        if getattr(message, "tool_calls", None):
            print("Tool calls:", message.tool_calls)

    tool_messages = [
        message
        for message in result["messages"]
        if isinstance(message, ToolMessage)
    ]

    assert tool_messages, "The agent did not execute any tools."

    search_results = [
        message
        for message in tool_messages
        if message.name == "search_documents"
    ]

    assert search_results, "The document search tool was not executed."

    retrieved_text = "\n".join(
        str(message.content)
        for message in search_results
    )

    assert "Document ID:" in retrieved_text
    assert "Page:" in retrieved_text

    final_message = result["messages"][-1]

    assert final_message.type == "ai"
    assert final_message.content.strip(), "The agent returned an empty answer."

    print("\nFINAL ANSWER:\n", final_message.content)
