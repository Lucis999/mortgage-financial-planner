import pytest
from model import Inputs
from purchase_timeline import dynamic_purchase_readiness
from scenario_state import form_defaults,scenario_signature

def test_defaults_roundtrip():
    x=Inputs(price=850000,down_pct=.3,net_monthly_income=9000,liquid_cash=430000)
    r={'base':2200,'yield':.06,'buy_beds':2.5,'rent_beds':1.5}
    z=form_defaults(x,r,'Actual monthly take-home')
    assert z['field_price']==850000
    assert z['field_net_actual']==9000
    assert z['field_net_mode']=='Actual monthly take-home'
    assert z['buy_bedrooms']==2.5
    assert z['shared_gross_yield']==6

def test_signature_detects_changes():
    x=Inputs();r={'base':1800}
    assert scenario_signature(x,r)!=scenario_signature(x,{'base':2000})

def test_dynamic_projection_changes_with_rent_growth():
    x=Inputs(liquid_cash=350000)
    low=dynamic_purchase_readiness(x,years=5,monthly_rent_cost=1800,annual_rent_growth=0)
    high=dynamic_purchase_readiness(x,years=5,monthly_rent_cost=1800,annual_rent_growth=.1)
    assert high[-1]['assets']<low[-1]['assets']

def test_dynamic_projection_income_growth_increases_assets():
    x=Inputs(liquid_cash=350000)
    flat=dynamic_purchase_readiness(x,years=5,annual_income_growth=0,monthly_rent_cost=1800)
    grow=dynamic_purchase_readiness(x,years=5,annual_income_growth=.05,monthly_rent_cost=1800)
    assert grow[-1]['assets']>flat[-1]['assets']

def test_negative_asset_return_reduces_assets():
    x=Inputs(liquid_cash=350000)
    flat=dynamic_purchase_readiness(x,years=3,annual_asset_return=0)
    loss=dynamic_purchase_readiness(x,years=3,annual_asset_return=-.2)
    assert loss[-1]['assets']<flat[-1]['assets']

def test_invalid_projection_growth():
    with pytest.raises(ValueError):
        dynamic_purchase_readiness(Inputs(),annual_asset_return=-1)
