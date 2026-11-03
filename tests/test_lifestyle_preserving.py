from dataclasses import replace
from model import Inputs,housing
from affordability_summary import affordability_limits
from pathlib import Path

def test_protected_ceiling_not_higher_than_basic():
    x=Inputs()
    basic=affordability_limits(x,ceiling=900000,step=10000)
    protected=affordability_limits(x,ceiling=900000,step=10000,minimum_surplus=2000)
    for k in ("lifestyle","combined"):
        if protected[k] is not None:
            assert basic[k] is not None
            assert protected[k]<=basic[k]

def test_protected_ceiling_passes_all_conditions():
    x=Inputs()
    limits=affordability_limits(x,ceiling=900000,step=10000,minimum_surplus=1000)
    if limits["combined"] is not None:
        h=housing(replace(x,price=limits["combined"]))
        assert h["conditions"]["purchase_cash"]
        assert h["conditions"]["mortgage_qualification"]
        assert h["monthly_surplus"]>=1000

def test_negative_target_rejected():
    try:affordability_limits(Inputs(),minimum_surplus=-1)
    except ValueError:pass
    else:assert False

def test_summary_ui_controls_and_headings():
    p=(Path(__file__).resolve().parents[1]/"pages/7_Financial_Decision_Summary.py").read_text(encoding='utf-8')
    assert "Maintain current monthly savings while renting" in p
    assert "Set my own minimum monthly surplus" in p
    assert "limits_cached(x,minimum_surplus)" in p
    assert "06 · Decision takeaway" in p
