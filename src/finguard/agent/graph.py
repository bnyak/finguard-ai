
from typing import Annotated, TypedDict

from langchain_core.messages import (
    AnyMessage,
    SystemMessage,
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


def route_agent(state: AgentState):
    last_message = state["messages"][-1]

    if (
        last_message.tool_calls
        and state["remaining_steps"] > 0
    ):
        return "tools"

    return END


builder = StateGraph(AgentState)

builder.add_node("agent", agent_node)
builder.add_node("tools", ToolNode(TOOLS))

builder.add_edge(START, "agent")

builder.add_conditional_edges(
    "agent",
    route_agent,
    {
        "tools": "tools",
        END: END,
    },
)

builder.add_edge("tools", "agent")

agent_graph = builder.compile()
