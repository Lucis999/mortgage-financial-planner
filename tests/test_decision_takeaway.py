from decision_takeaway import evaluate_decision

def case(conditions, surplus=1000, target=1000):
    h={"conditions":conditions,"monthly_surplus":surplus}
    return evaluate_decision(h,target,{"combined":300000},{"years_to_target":2.5},15)

def test_all_pass():
    r=case({"purchase_cash":True,"mortgage_qualification":True,"monthly_cashflow":True})
    assert r["status"]=="success" and r["time_label"]=="2.5 years"

def test_lifestyle_only():
    r=case({"purchase_cash":True,"mortgage_qualification":True,"monthly_cashflow":True},1000,1500)
    assert r["status"]=="warning" and "Lifestyle constraint" in r["details"][0]

def test_multiple_constraints():
    r=case({"purchase_cash":False,"mortgage_qualification":False,"monthly_cashflow":True},1000,2000)
    assert len(r["details"])==3 and "Multiple" in r["headline"]

def test_cashflow_failure():
    r=case({"purchase_cash":True,"mortgage_qualification":True,"monthly_cashflow":False},-50,0)
    assert any("Cash-flow constraint" in m for m in r["details"])

def test_time_not_reached():
    r=evaluate_decision({"conditions":{"purchase_cash":False,"mortgage_qualification":True,"monthly_cashflow":True},"monthly_surplus":100},0,{"combined":None},{"years_to_target":None},15)
    assert r["time_label"]=="Beyond 15 years"
