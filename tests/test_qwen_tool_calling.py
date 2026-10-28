
import httpx

from finguard.generation.ollama import MODEL_NAME, OLLAMA_URL


def test_qwen_tool_calling():
    response = httpx.post(
        OLLAMA_URL,
        json={
            "model": MODEL_NAME,
            "stream": False,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are a financial assistant. "
                        "Use the available tools for calculations."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        "Calculate the monthly mortgage payment "
                        "for a $300,000 loan at 6.5% for 30 years."
                    ),
                },
            ],
            "tools": [
                {
                    "type": "function",
                    "function": {
                        "name": "calculate_loan_payment",
                        "description": (
                            "Calculate the monthly principal-and-interest "
                            "payment for a fixed-rate mortgage."
                        ),
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "principal": {
                                    "type": "number",
                                    "description": "Loan amount in dollars",
                                },
                                "annual_rate": {
                                    "type": "number",
                                    "description": "Annual rate as a percentage",
                                },
                                "years": {
                                    "type": "integer",
                                    "description": "Loan term in years",
                                },
                            },
                            "required": [
                                "principal",
                                "annual_rate",
                                "years",
                            ],
                        },
                    },
                }
            ],
        },
        timeout=300.0,
    )

    response.raise_for_status()
    data = response.json()

    tool_calls = data["message"].get("tool_calls", [])

    print("\nTool calls:", tool_calls)
    print("Model response:", data["message"].get("content"))

    assert len(tool_calls) > 0

    function = tool_calls[0]["function"]

    assert function["name"] == "calculate_loan_payment"

    arguments = function["arguments"]

    assert float(arguments["principal"]) == 300000
    assert float(arguments["annual_rate"]) == 6.5
    assert int(arguments["years"]) == 30
