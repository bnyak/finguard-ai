
from typing import Annotated, TypedDict

from langchain_core.messages import (
    AnyMessage,
    SystemMessage,
    ToolMessage,
)
from langgraph.graph import (
    END,
    START,
    StateGraph,
    add_messages,
)
from langgraph.prebuilt import ToolNode

from finguard.agent.ollama_adapter import call_qwen
from finguard.agent.tools.document_search import search_documents
from finguard.agent.tools.financial_glossary import (
    lookup_financial_definition,
)
from finguard.agent.tools.loan_calculator import (
    calculate_loan_payment,
)

TOOLS = [
    search_documents,
    lookup_financial_definition,
    calculate_loan_payment,
]

SYSTEM_PROMPT = """
You are FinGuard AI, a financial document intelligence assistant.

Use search_documents for questions about uploaded PDFs.
Use lookup_financial_definition for general financial terminology.
Use calculate_loan_payment for mortgage calculations.

Never invent document citations or calculation results.
Use tools whenever information or calculations require them.
Clearly state that mortgage payments exclude taxes and insurance.
"""


class AgentState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
    remaining_steps: int


def agent_node(state: AgentState):
    if state["remaining_steps"] <= 0:
        return {
            "messages": [],
            "remaining_steps": 0,
        }

    response = call_qwen(
        messages=[
            SystemMessage(content=SYSTEM_PROMPT),
            *state["messages"],
        ],
        tools=TOOLS,
    )

    return {
        "messages": [response],
        "remaining_steps": state["remaining_steps"] - 1,
    }



def is_invalid_tool_selection(state: AgentState) -> bool:
    messages = state["messages"]
    last_message = messages[-1]

    # Only validate requests that clearly concern uploaded documents.
    user_messages = [
        message.content
        for message in messages
        if message.type == "human"
        and isinstance(message.content, str)
    ]

    if not user_messages:
        return False

    question = user_messages[-1].lower()

    document_question = any(
        phrase in question
        for phrase in (
            "according to the uploaded",
            "according to the document",
            "according to the policy",
        )
    )

    # A question may legitimately request both document
    # information and a calculation.
    calculation_requested = any(
        phrase in question
        for phrase in (
            "calculate",
            "monthly payment",
            "loan payment",
        )
    )

    if not document_question or calculation_requested:
        return False

    return any(
        tool_call["name"] == "calculate_loan_payment"
        for tool_call in last_message.tool_calls
    )



def route_agent(state: AgentState):
    last_message = state["messages"][-1]

    if (
        last_message.tool_calls
        and state["remaining_steps"] > 0
    ):
        if is_invalid_tool_selection(state):
            return "invalid_tool"

        return "tools"

    return END


def reject_invalid_tool(state: AgentState):
    last_message = state["messages"][-1]

    return {
        "messages": [
            ToolMessage(
                content=(
                    "Tool execution rejected: "
                    "the requested tool does not match "
                    "the document-only question."
                ),
                tool_call_id=tool_call["id"],
                name=tool_call["name"],
            )
            for tool_call in last_message.tool_calls
        ]
    }



builder = StateGraph(AgentState)

builder.add_node("agent", agent_node)
builder.add_node("tools", ToolNode(TOOLS))
builder.add_node("invalid_tool", reject_invalid_tool)

builder.add_edge(START, "agent")

builder.add_conditional_edges(
    "agent",
    route_agent,
    {
        "tools": "tools",
        "invalid_tool": "invalid_tool",
        END: END,
    },
)

builder.add_edge("tools", "agent")
builder.add_edge("invalid_tool", END)

agent_graph = builder.compile()