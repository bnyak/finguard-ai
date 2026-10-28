
from finguard.agent.tools.financial_glossary import (
    lookup_financial_definition,
)


def test_lookup_apr():
    result = lookup_financial_definition.invoke({"term": "APR"})
    assert "Annual Percentage Rate" in result


def test_lookup_case_insensitive():
    result = lookup_financial_definition.invoke({"term": "  ESCROW  "})
    assert "property taxes" in result


def test_lookup_unknown_term():
    result = lookup_financial_definition.invoke({"term": "unknown financial term"})
    assert "No glossary definition found" in result
