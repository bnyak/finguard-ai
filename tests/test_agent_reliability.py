
from langchain_core.messages import AIMessage, HumanMessage

from finguard.agent.graph import route_agent


def test_agent_rejects_wrong_tool_for_document_question():
    state = {
        "messages": [
            HumanMessage(
                content=(
                    "According to the uploaded fraud policy, "
                    "when is enhanced review required?"
                )
            ),
            AIMessage(
                content="",
                tool_calls=[
                    {
                        "name": "calculate_loan_payment",
                        "args": {
                            "principal": 300000,
                            "annual_interest_rate": 6.5,
                            "years": 30,
                        },
                        "id": "wrong_tool_1",
                    }
                ],
            ),
        ],
        "remaining_steps": 3,
    }

    result = route_agent(state)

    assert result == "invalid_tool"



from unittest.mock import patch

from finguard.agent.graph import agent_graph


def test_graph_does_not_execute_wrong_tool():
    wrong_tool_response = AIMessage(
        content="",
        tool_calls=[
            {
                "name": "calculate_loan_payment",
                "args": {
                    "principal": 300000,
                    "annual_interest_rate": 6.5,
                    "years": 30,
                },
                "id": "wrong_tool_2",
            }
        ],
    )

    with (
        patch(
            "finguard.agent.graph.call_qwen",
            return_value=wrong_tool_response,
        ),
        patch(
            "finguard.agent.graph.calculate_loan_payment"
        ) as mock_calculator,
    ):
        result = agent_graph.invoke(
            {
                "messages": [
                    HumanMessage(
                        content=(
                            "According to the uploaded fraud policy, "
                            "when is enhanced review required?"
                        )
                    )
                ],
                "remaining_steps": 3,
            }
        )

    assert mock_calculator.call_count == 0
    assert result["messages"][-1].content.startswith(
        "Tool execution rejected:"
    )


def test_agent_allows_calculator_for_mixed_document_question():
    state = {
        "messages": [
            HumanMessage(
                content=(
                    "According to the uploaded mortgage guide, "
                    "calculate the monthly payment for a loan."
                )
            ),
            AIMessage(
                content="",
                tool_calls=[
                    {
                        "name": "calculate_loan_payment",
                        "args": {
                            "principal": 300000,
                            "annual_interest_rate": 6.5,
                            "years": 30,
                        },
                        "id": "valid_tool_1",
                    }
                ],
            ),
        ],
        "remaining_steps": 3,
    }

    assert route_agent(state) == "tools"
