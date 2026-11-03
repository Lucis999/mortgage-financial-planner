"""Transparent supplementary downside calculations for scenario testing."""
from model import Inputs, housing

def downside_summary(x: Inputs, home_decline: float, income_decline: float, liquid_drawdown: float):
    if any(not 0 <= z <= 1 for z in (home_decline,income_decline,liquid_drawdown)):
        raise ValueError("Stress percentages must be between zero and one")
    h=housing(x)
    loan=h["mortgage_principal"]
    stressed_value=x.price*(1-home_decline)
    baseline_cash=h["cash_after_purchase"]
    stressed_cash=baseline_cash-max(0,baseline_cash)*liquid_drawdown
    return {"baseline_equity":x.price-loan,"stressed_equity":stressed_value-loan,
            "stressed_ltv":loan/stressed_value if stressed_value else float("inf"),
            "baseline_cash":baseline_cash,"stressed_cash":stressed_cash,
            "reduced_income_surplus":h["monthly_surplus"]-x.net_monthly_income*income_decline}
