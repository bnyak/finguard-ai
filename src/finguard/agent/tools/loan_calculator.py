
from langchain_core.tools import tool


@tool
def calculate_loan_payment(
    principal: float,
    annual_rate: float,
    years: int,
) -> dict:
    """Calculate the monthly principal-and-interest payment
    for a fixed-rate, fully amortizing mortgage.

    Args:
        principal: Loan amount in dollars.
        annual_rate: Annual interest rate as a percentage, e.g. 6.5.
        years: Loan term in years.
    """
    if principal <= 0:
        raise ValueError("Principal must be positive.")

    if annual_rate < 0:
        raise ValueError("Annual interest rate cannot be negative.")

    if years <= 0:
        raise ValueError("Loan term must be positive.")

    monthly_rate = annual_rate / 100 / 12
    number_of_payments = years * 12

    if monthly_rate == 0:
        monthly_payment = principal / number_of_payments
    else:
        monthly_payment = (
            principal
            * monthly_rate
            * (1 + monthly_rate) ** number_of_payments
            / ((1 + monthly_rate) ** number_of_payments - 1)
        )

    total_payment = monthly_payment * number_of_payments
    total_interest = total_payment - principal

    return {
        "principal": round(principal, 2),
        "annual_rate_percent": annual_rate,
        "years": years,
        "monthly_payment": round(monthly_payment, 2),
        "total_interest": round(total_interest, 2),
        "total_payment": round(total_payment, 2),
    }
