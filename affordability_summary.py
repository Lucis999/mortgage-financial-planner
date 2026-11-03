"""Separate mortgage underwriting, capital, and lifestyle price ceilings."""
from dataclasses import replace
from math import ceil
from model import Inputs, housing

def affordability_limits(x: Inputs, ceiling=2500000, step=1000, minimum_surplus=0):
    if minimum_surplus < 0: raise ValueError("Minimum monthly surplus must be nonnegative")
    best={"capital":None,"income":None,"lifestyle":None,"combined":None}
    for price in range(step,ceiling+1,step):
        try:
            h=housing(replace(x,price=float(price)))
        except ValueError:
            continue
        checks={"capital":h["conditions"]["purchase_cash"],
                "income":h["conditions"]["mortgage_qualification"],
                "lifestyle":h["monthly_surplus"]>=minimum_surplus,
                "combined":h["conditions"]["purchase_cash"] and h["conditions"]["mortgage_qualification"] and h["monthly_surplus"]>=minimum_surplus}
        for k,ok in checks.items():
            if ok:best[k]=price
    return best

def time_to_down_payment(x: Inputs, years=15, monthly_rent=0, annual_savings_growth=0):
    if not 1<=years<=30 or annual_savings_growth<=-1 or monthly_rent<0:
        raise ValueError("Invalid savings assumptions")
    h=housing(x)
    target=h["down"]+h["closing_costs"]
    available=max(0,x.liquid_cash-x.reserve_floor)
    savings=x.net_monthly_income+x.other_monthly_income-x.living_monthly-x.other_debt_monthly-monthly_rent
    reached=0.0 if available>=target else None
    cash=available
    if reached is None:
        for m in range(1,years*12+1):
            cash+=savings*(1+annual_savings_growth)**((m-1)//12)
            if cash>=target:
                reached=m/12
                break
    return {"cash_target":target,"available":available,"monthly_savings":savings,"years_to_target":reached}
