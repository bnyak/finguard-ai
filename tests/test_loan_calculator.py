
import pytest

from finguard.agent.tools.loan_calculator import (
    calculate_loan_payment,
)


def test_standard_mortgage():
    result = calculate_loan_payment.invoke({
        "principal": 300000,
        "annual_rate": 6.5,
        "years": 30,
    })

    assert result["monthly_payment"] == pytest.approx(
        1896.20, abs=0.01
    )
    assert result["total_interest"] > 0


def test_zero_interest():
    result = calculate_loan_payment.invoke({
        "principal": 120000,
        "annual_rate": 0,
        "years": 10,
    })

    assert result["monthly_payment"] == 1000
    assert result["total_interest"] == 0


@pytest.mark.parametrize(
    "principal, annual_rate, years",
    [
        (0, 6.5, 30),
        (-100000, 6.5, 30),
        (300000, -1, 30),
        (300000, 6.5, 0),
    ],
)
def test_invalid_loan_inputs(principal, annual_rate, years):
    with pytest.raises(ValueError):
        calculate_loan_payment.invoke({
            "principal": principal,
            "annual_rate": annual_rate,
            "years": years,
        })
