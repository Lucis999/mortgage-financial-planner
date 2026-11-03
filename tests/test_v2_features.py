from dataclasses import replace
import pytest
from model import Inputs
from stress_extensions import downside_summary
from purchase_timeline import capital_readiness

def test_downside_decline_reduces_equity():
    x=Inputs(down_pct=.3,liquid_cash=350000,other_debt_monthly=0)
    s=downside_summary(x,.2,.25,.3)
    assert s['stressed_equity']<s['baseline_equity']
    assert s['reduced_income_surplus']<0 or s['reduced_income_surplus']<s['baseline_equity']
    assert s['stressed_cash']<=s['baseline_cash']

def test_no_decline_is_baseline():
    s=downside_summary(Inputs(down_pct=.3,liquid_cash=350000),0,0,0)
    assert s['stressed_equity']==pytest.approx(s['baseline_equity'])
    assert s['stressed_cash']==pytest.approx(s['baseline_cash'])

def test_purchase_timeline_has_16_years():
    rows=capital_readiness(Inputs(down_pct=.3,liquid_cash=350000),15)
    assert len(rows)==16
    assert rows[0]['year']==0 and rows[-1]['year']==15

def test_price_growth_increases_capital_need():
    x=Inputs(down_pct=.3,liquid_cash=350000)
    r=capital_readiness(x,5,.05)
    assert r[5]['capital_needed']>r[0]['capital_needed']

def test_invalid_stress():
    with pytest.raises(ValueError):downside_summary(Inputs(),1.1,0,0)

def test_rent_reduces_savings_not_mortgage_qualification():
    x=Inputs(down_pct=.3,liquid_cash=350000)
    base=capital_readiness(x,2,monthly_rent_cost=0)
    renting=capital_readiness(x,2,monthly_rent_cost=1800)
    assert renting[1]["assets"]==pytest.approx(base[1]["assets"]-21600)
    assert renting[0]["monthly_qualifies"]==base[0]["monthly_qualifies"]
