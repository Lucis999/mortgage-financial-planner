"""Transparent monthly cash/investment ledger for an asset-financed purchase.
Application-time financing is handled separately in asset_model.py.
"""
from dataclasses import dataclass, replace
from model import Inputs, housing, payment
from asset_model import AssetProfile, asset_financing

@dataclass(frozen=True)
class ProjectionSettings:
    years: int = 15
    investment_return: float = .05
    investment_drawdown: float = .25
    shock_year: int = 3
    renewal_year: int = 5
    renewal_rate: float = .065
    cash_target: float = 60000
    invested_share: float | None = None


def project_assets(x: Inputs, a: AssetProfile, s: ProjectionSettings):
    if not 1 <= s.years <= 30 or not 1 <= s.shock_year <= s.years:
        raise ValueError('Invalid projection horizon or shock year')
    if s.investment_return < -1 or not 0 <= s.investment_drawdown <= 1 or s.cash_target < 0 or (s.invested_share is not None and not 0<=s.invested_share<=1):
        raise ValueError('Invalid investment or reserve settings')
    result=asset_financing(x,a)
    if result['remaining_assets'] < 0:
        raise ValueError('Closing costs exceed available assets')
    spend=result['down']+result['closing_costs']
    # Explicit liquidation order: cash first, investments second.
    cash=max(0,a.cash-spend)
    investments=a.investments-max(0,spend-a.cash)
    if investments < -1e-8:
        raise ValueError('Not enough funds to close')
    investments=max(0,investments)
    if s.invested_share is not None:
        total=cash+investments
        investments=total*s.invested_share
        cash=total-investments
    principal=result['mortgage_principal']
    balance=principal
    months_left=x.amort_years*12
    current_rate=x.annual_rate
    monthly_payment=result['monthly_mortgage']
    monthly_return=(1+s.investment_return)**(1/12)-1
    recurring=result['monthly_housing']-result['monthly_mortgage']
    rows=[]
    for month in range(1,s.years*12+1):
        if month==s.renewal_year*12+1 and months_left>0:
            current_rate=s.renewal_rate
            monthly_payment=payment(balance,current_rate,months_left)
        investment_gain=investments*monthly_return
        investments+=investment_gain
        shock_loss=0.
        if month==(s.shock_year-1)*12+1:
            shock_loss=investments*s.investment_drawdown
            investments-=shock_loss
        m=(1+current_rate/2)**(1/6)-1
        interest=balance*m
        principal_paid=min(balance,max(0,monthly_payment-interest)) if months_left>0 else 0
        paid=interest+principal_paid if months_left>0 else 0
        balance=max(0,balance-principal_paid)
        months_left=max(0,months_left-1)
        income=x.net_monthly_income+x.other_monthly_income
        spending=x.living_monthly+x.other_debt_monthly+recurring+paid
        net=income-spending
        cash+=net
        liquidation=0.
        if cash<0 and investments>0:
            liquidation=min(-cash,investments)
            investments-=liquidation
            cash+=liquidation
        contribution=0.
        if cash>s.cash_target:
            contribution=cash-s.cash_target
            investments+=contribution
            cash=s.cash_target
        rows.append(dict(month=month,year=month/12,cash=cash,investments=investments,
            total_financial_assets=cash+investments,net_cashflow=net,
            mortgage_balance=balance,investment_gain=investment_gain,shock_loss=shock_loss,
            liquidation=liquidation,contribution=contribution,
            reserve_shortfall=max(0,s.cash_target-cash),unfunded_cash=max(0,-cash),
            mortgage_payment=paid,mortgage_interest=interest,mortgage_principal_paid=principal_paid))
    return rows
