from dataclasses import replace
from model import Inputs,housing
from affordability_summary import affordability_limits,time_to_down_payment

def test_qualification_metrics():
 x=Inputs()
 h=housing(x)
 assert abs(h["lti"]-h["mortgage_principal"]/x.gross_annual_income)<1e-9
 assert abs(h["ltv"]-h["mortgage_principal"]/x.price)<1e-9
 assert h["qualifying_mortgage"]>=h["monthly_mortgage"]
 assert abs(h["qualifying_housing"]-(h["qualifying_mortgage"]+x.property_tax_monthly+x.heating_monthly+0.5*x.strata_monthly))<1e-8

def test_debt_changes_tds_not_gds():
 x=Inputs()
 h=housing(x)
 d=housing(replace(x,other_debt_monthly=x.other_debt_monthly+500))
 assert h["gds"]==d["gds"]
 assert d["tds"]>h["tds"]

def test_separate_price_limits():
 result=affordability_limits(Inputs(),ceiling=800000,step=10000)
 assert set(result)=={"capital","income","lifestyle","combined"}
 if result["combined"] is not None:
  assert all(result[k] is not None and result["combined"]<=result[k] for k in ("capital","income","lifestyle"))

def test_savings_horizon():
 x=Inputs(liquid_cash=0,net_monthly_income=7000,other_debt_monthly=0)
 a=time_to_down_payment(x,years=20,monthly_rent=1000)
 b=time_to_down_payment(x,years=20,monthly_rent=3000)
 assert a["years_to_target"] is not None
 assert b["years_to_target"] is None or b["years_to_target"]>=a["years_to_target"]
