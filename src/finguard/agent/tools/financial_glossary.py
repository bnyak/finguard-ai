
from langchain_core.tools import tool

FINANCIAL_GLOSSARY = {
    "apr": (
        "Annual Percentage Rate (APR) represents the annualized "
        "cost of borrowing, including interest and certain loan fees."
    ),
    "interest rate": (
        "The interest rate is the percentage charged for borrowing "
        "the principal amount, excluding additional loan fees."
    ),
    "mortgage points": (
        "Mortgage discount points are upfront fees paid to a lender "
        "to obtain a lower mortgage interest rate. One point typically "
        "costs 1% of the loan amount."
    ),
    "escrow": (
        "An escrow account holds funds collected by a mortgage servicer "
        "to pay expenses such as property taxes and homeowners insurance."
    ),
    "lender credits": (
        "Lender credits reduce upfront closing costs, generally in "
        "exchange for accepting a higher interest rate."
    ),
}


@tool
def lookup_financial_definition(term: str) -> str:
    """Look up the definition of a financial or mortgage term.

    Use this tool for general financial terminology questions,
    such as APR, escrow, mortgage points, and lender credits.
    """
    normalized_term = term.strip().lower()

    definition = FINANCIAL_GLOSSARY.get(normalized_term)

    if definition is None:
        return f"No glossary definition found for '{term}'."

    return f"{term.strip()}: {definition}"
