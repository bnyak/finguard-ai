
import time

import httpx
from langchain_core.messages import (
    AIMessage,
    HumanMessage,
    SystemMessage,
    ToolMessage,
)

from finguard.generation.ollama import MODEL_NAME, OLLAMA_URL


def call_qwen(messages, tools):
    """Call Ollama and convert its response to an AIMessage."""

    ollama_messages = []

    for message in messages:
        if isinstance(message, SystemMessage):
            ollama_messages.append({
                "role": "system",
                "content": message.content,
            })

        elif isinstance(message, HumanMessage):
            ollama_messages.append({
                "role": "user",
                "content": message.content,
            })

        elif isinstance(message, AIMessage):
            payload = {
                "role": "assistant",
                "content": message.content,
            }

            if message.tool_calls:
                payload["tool_calls"] = [
                    {
                        "type": "function",
                        "function": {
                            "name": call["name"],
                            "arguments": call["args"],
                        },
                    }
                    for call in message.tool_calls
                ]

            ollama_messages.append(payload)

        elif isinstance(message, ToolMessage):
            ollama_messages.append({
                "role": "tool",
                "tool_name": message.name,
                "content": str(message.content),
            })

    tool_schemas = [
        {
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.args_schema.model_json_schema(),
            },
        }
        for tool in tools
    ]

    start_time = time.perf_counter()
    print("\nCalling Qwen...", flush=True)
    response = httpx.post(
        OLLAMA_URL,
        json={
            "model": MODEL_NAME,
            "stream": False,
            "messages": ollama_messages,
            "tools": tool_schemas,
        },
        timeout=httpx.Timeout(
            connect=10.0,
            read=900.0,
            write=30.0,
            pool=10.0,
        ),
    )
    print(
        f"Qwen responded in {time.perf_counter() - start_time:.2f} seconds",
        flush=True,
    )

    response.raise_for_status()
    data = response.json()["message"]

    tool_calls = []

    for index, call in enumerate(data.get("tool_calls") or []):
        function = call["function"]

        tool_calls.append({
            "name": function["name"],
            "args": function["arguments"],
            "id": call.get("id") or f"call_{index}",
            "type": "tool_call",
        })

    return AIMessage(
        content=data.get("content") or "",
        tool_calls=tool_calls,
    )
