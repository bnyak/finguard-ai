from fastapi import APIRouter, HTTPException
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

from finguard.agent.graph import agent_graph
from finguard.api.schemas import AgentAskRequest, AgentAskResponse

router = APIRouter(prefix="/agent", tags=["Agent"])


@router.post("/ask", response_model=AgentAskResponse)
def agent_ask(request: AgentAskRequest):

    result = agent_graph.invoke(
        {
            "messages": [HumanMessage(content=request.question)],
            "remaining_steps": request.max_steps,
        },
        config={"recursion_limit": 2 * request.max_steps + 5 },
    )

    messages = result["messages"]

    tools_used = [
        message.name
        for message in messages
        if isinstance(message, ToolMessage)
        and message.name is not None
    ]

    final_message = messages[-1]

    if not isinstance(final_message, AIMessage):
        raise HTTPException(
            status_code=502,
            detail="Agent did not produce a final response.",
        )

    if final_message.tool_calls or not isinstance(final_message.content, str) or not final_message.content.strip():
        raise HTTPException(
            status_code=502,
            detail="Agent did not complete its response.",
        )

    return AgentAskResponse(
        answer=final_message.content,
        tools_used=tools_used,
    )