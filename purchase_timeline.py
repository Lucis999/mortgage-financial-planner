"""Capital-only purchase readiness timeline. Not an underwriting approval."""
from dataclasses import replace
from model import Inputs, housing

def capital_readiness(x: Inputs, years=15, annual_home_growth=.025, annual_savings_growth=0.0, monthly_rent_cost=0.0):
    if not 1<=years<=30 or annual_home_growth<=-1 or annual_savings_growth<=-1:
        raise ValueError("Invalid projection assumptions")
    monthly_savings=x.net_monthly_income-x.living_monthly-x.other_debt_monthly-monthly_rent_cost
    assets=x.liquid_cash
    rows=[]
    for year in range(years+1):
        price=x.price*(1+annual_home_growth)**year
        projected=replace(x,price=price,liquid_cash=max(0,assets))
        try:
            h=housing(projected)
            capital_needed=h['down']+h['closing_costs']+x.reserve_floor
            monthly_qualifies=h['conditions']['mortgage_qualification'] and h['conditions']['monthly_cashflow']
        except ValueError:
            capital_needed=float('nan');monthly_qualifies=False
        rows.append(dict(year=year,assets=assets,capital_needed=capital_needed,
            capital_ready=assets>=capital_needed,monthly_qualifies=monthly_qualifies,
            purchase_ready=assets>=capital_needed and monthly_qualifies))
        assets+=12*monthly_savings*(1+annual_savings_growth)**year
    return rows


def dynamic_purchase_readiness(x: Inputs, years=15, annual_home_growth=.025,
        annual_income_growth=.02, annual_rent_growth=.025,
        annual_living_growth=.02, monthly_rent_cost=0.0,
        annual_asset_return=0.0):
    """Year-by-year rent, expenses, income, capital and qualification screening.

    Savings accrue monthly; year-end capital is evaluated after twelve months.
    Assumes no investment volatility, no taxes beyond supplied net income, and
    fixed nominal down-payment share. Never treats negative assets as cash.
    """
    if not 1<=years<=30 or min(annual_home_growth,annual_income_growth,
            annual_rent_growth,annual_living_growth,annual_asset_return)<=-1:
        raise ValueError("Invalid projection growth rate")
    assets=float(x.liquid_cash); rows=[]
    for year in range(years+1):
        price=x.price*(1+annual_home_growth)**year
        gross=x.gross_annual_income*(1+annual_income_growth)**year
        net=x.net_monthly_income*(1+annual_income_growth)**year
        living=x.living_monthly*(1+annual_living_growth)**year
        rent=monthly_rent_cost*(1+annual_rent_growth)**year
        projected=replace(x,price=price,liquid_cash=max(0,assets),
            gross_annual_income=gross,net_monthly_income=net,living_monthly=living)
        try:
            h=housing(projected)
            needed=h['down']+h['closing_costs']+x.reserve_floor
            qualified=h['conditions']['mortgage_qualification'] and h['conditions']['monthly_cashflow']
        except ValueError:
            needed=float('nan');qualified=False
        rows.append(dict(year=year,assets=assets,capital_needed=needed,
            monthly_rent=rent,net_income=net,living_cost=living,
            annual_savings=12*(net-living-x.other_debt_monthly-rent),
            capital_ready=assets>=needed,monthly_qualifies=qualified,
            purchase_ready=assets>=needed and qualified))
        if year<years:
            monthly_net=(net-living-x.other_debt_monthly-rent)
            monthly_return=(1+annual_asset_return)**(1/12)-1
            for _ in range(12): assets=assets*(1+monthly_return)+monthly_net
    return rows
