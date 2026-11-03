from dataclasses import replace
import pytest
from model import Inputs, payment, balance_after, housing, renewal, cashflow, ptt, min_down
from asset_model import AssetProfile, asset_financing
from asset_trajectory import ProjectionSettings, project_assets
from integrity import audit_asset_trajectory, audit_rent_vs_buy
from rent_vs_buy import Comparison, simulate


def test_zero_interest_payment_and_balance():
    assert payment(120000, 0, 120) == 1000
    assert balance_after(120000, 0, 60, 120) == 60000


def test_amortization_ends_at_zero():
    x=Inputs(amort_years=15, renewal_year=15, horizon_months=190, unemployment_months=0, assessment_amount=0)
    assert renewal(x)['renewal_payment']==0
    assert cashflow(x)[-1]['mortgage']==0


def test_payment_identity():
    x=Inputs()
    h=housing(x)
    assert h['mortgage_principal']==pytest.approx(x.price*(1-x.down_pct)+h['insurance_premium'])
    assert h['monthly_housing']==pytest.approx(h['monthly_mortgage']+x.strata_monthly+x.property_tax_monthly+x.condo_insurance_monthly+x.maintenance_monthly+x.heating_monthly)


def test_tax_brackets_arithmetic_only():
    assert ptt(200000)==2000
    assert ptt(700000)==12000
    assert min_down(700000)==45000


def test_asset_reconciliation():
    x=Inputs(liquid_cash=850000)
    a=AssetProfile()
    s=ProjectionSettings(years=2, shock_year=1)
    rows=project_assets(x,a,s)
    assert all(c.passed for c in audit_asset_trajectory(x,a,s,rows))


def test_rent_buy_reconciliation():
    x=Inputs(liquid_cash=850000)
    c=Comparison(years=2,shock_year=1)
    rows=simulate(x,c)
    assert all(check.passed for check in audit_rent_vs_buy(x,c,rows))


def test_bad_down_payment_rejected():
    with pytest.raises(ValueError): housing(Inputs(down_pct=.05,price=700000))


def test_invalid_financing_rejected():
    with pytest.raises(ValueError): simulate(Inputs(liquid_cash=850000),Comparison(years=1),financing='unknown')
