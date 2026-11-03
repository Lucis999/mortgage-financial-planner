from pathlib import Path
from dataclasses import replace
from model import Inputs, housing, cashflow
from affordability_summary import affordability_limits, time_to_down_payment

ROOT=Path(__file__).resolve().parents[1]

def test_documentation_matches_current_navigation():
    readme=(ROOT/'README.md').read_text(encoding='utf-8')
    nav=(ROOT/'app.py').read_text(encoding='utf-8')
    for title in ('Set Up Your Scenario','Financial Overview','Mortgage & Affordability',
                  'Asset & Liquidity','Rent vs Buy','Risk & Stress Testing',
                  'Financial Decision Summary','Advanced Analytics & Export'):
        assert title in readme and title in nav
    assert (ROOT/'CHANGELOG.md').exists()
    assert len(list(ROOT.glob('CHANGELOG_v*.md')))==0
    assert 'v1.0.3' not in readme.splitlines()[0]

def test_financial_baseline_consistency():
    x=Inputs()
    h=housing(x)
    assert h['mortgage_principal']>0
    assert h['qualifying_mortgage']>=h['monthly_mortgage']
    assert h['gds']<=h['tds']
    assert abs(h['cash_after_purchase']-(x.liquid_cash-h['down']-h['closing_costs']))<1e-8
    assert abs(h['monthly_surplus']-(x.net_monthly_income+x.other_monthly_income-h['monthly_housing']-x.living_monthly-x.other_debt_monthly))<1e-8

def test_lifestyle_protection_never_expands_ceiling():
    x=Inputs()
    base=affordability_limits(x,ceiling=850000,step=5000,minimum_surplus=0)
    protected=affordability_limits(x,ceiling=850000,step=5000,minimum_surplus=1500)
    for k in ('lifestyle','combined'):
        if protected[k] is not None:
            assert base[k] is not None and protected[k]<=base[k]

def test_savings_progress_and_cashflow_horizon():
    x=Inputs()
    low=time_to_down_payment(x,years=15,monthly_rent=1500)
    high=time_to_down_payment(x,years=15,monthly_rent=2500)
    assert low['monthly_savings']>high['monthly_savings']
    rows=cashflow(replace(x,horizon_months=60))
    assert len(rows)==60
    assert rows[-1]['month']==60
    assert all('cash_balance' in r for r in rows)
