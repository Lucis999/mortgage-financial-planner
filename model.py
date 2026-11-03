"""Transparent BC housing planning estimates. CAD, monthly cash flows."""
from dataclasses import dataclass, asdict, replace
from math import isfinite

@dataclass(frozen=True)
class Inputs:
    price: float = 700000
    down_pct: float = 0.20
    annual_rate: float = 0.045
    amort_years: int = 25
    gross_annual_income: float = 120000
    net_monthly_income: float = 7200
    other_monthly_income: float = 0
    liquid_cash: float = 220000
    other_debt_monthly: float = 300
    living_monthly: float = 2200
    strata_monthly: float = 420
    property_tax_monthly: float = 250
    condo_insurance_monthly: float = 95
    maintenance_monthly: float = 100
    heating_monthly: float = 70
    closing_other: float = 2500
    first_time_eligible: bool = False
    reserve_floor: float = 30000
    renewal_year: int = 5
    renewal_rate: float = 0.065
    unemployment_start: int = 7
    unemployment_months: int = 6
    replacement_income_monthly: float = 0
    assessment_month: int = 9
    assessment_amount: float = 10000
    horizon_months: int = 120
    max_gds: float = 0.39
    max_tds: float = 0.44
    stress_floor: float = 0.0525
    price_step: int = 1000

def validate(x: Inputs):
    for k,v in asdict(x).items():
        if isinstance(v,(float,int)) and (not isfinite(v) or (v<0 and k not in ())):
            raise ValueError(f'{k} must be nonnegative and finite')
    if not 0.05 <= x.down_pct <= 1: raise ValueError('Down payment percentage must be 5%–100%')
    if x.price<=0 or x.amort_years<=0 or x.horizon_months<1: raise ValueError('Invalid housing timeline')
    if x.max_gds>1 or x.max_tds>1: raise ValueError('Debt ratios must be <= 1')
    if x.renewal_year < 1 or x.price_step <= 0: raise ValueError('Renewal year and price step must be positive')

def min_down(price):
    if price<=500000: return price*.05
    if price<1500000: return 25000+(price-500000)*.10
    return price*.20

def ptt(price):
    # BC residential standard PTT including additional 2% above $3m.
    return min(price,200000)*.01 + max(0,min(price,2000000)-200000)*.02 + max(0,price-2000000)*.03 + max(0,price-3000000)*.02

def fthb_relief(price,eligible):
    # Simplified: full exemption <=500k, max $8k <=835k, phaseout to 860k.
    if not eligible: return 0
    if price<=500000: return ptt(price)
    if price<=835000: return min(ptt(price),8000)
    if price<860000: return min(ptt(price),8000)*(860000-price)/25000
    return 0

def insured_premium(price,down):
    if down>=price*.20-1e-7: return 0
    if price>=1500000: raise ValueError('Insured purchase price must be below $1.5m in this demo')
    ltv=(price-down)/price
    if ltv>.95+1e-8: raise ValueError('Down payment below minimum insured LTV')
    rate=.04 if ltv>.90 else .031 if ltv>.85 else .028
    return (price-down)*rate

def payment(balance,rate,months):
    if months<=0: return 0
    m=(1+rate/2)**(1/6)-1
    return balance/months if m==0 else balance*m/(1-(1+m)**(-months))

def balance_after(principal,rate,months_paid,total_months):
    m=(1+rate/2)**(1/6)-1
    p=payment(principal,rate,total_months)
    if m==0: return max(0,principal-p*months_paid)
    return max(0,principal*(1+m)**months_paid-p*((1+m)**months_paid-1)/m)

def housing(x:Inputs):
    validate(x)
    down=x.price*x.down_pct
    if down+1e-7<min_down(x.price): raise ValueError('Down payment below Canadian minimum')
    if x.amort_years>25 and down<x.price*.20: raise ValueError('Demo supports insured mortgages with 25-year amortization only')
    premium=insured_premium(x.price,down)
    principal=x.price-down+premium
    mortgage=payment(principal,x.annual_rate,x.amort_years*12)
    transfer=ptt(x.price)-fthb_relief(x.price,x.first_time_eligible)
    closing=transfer+x.closing_other
    cash_after=x.liquid_cash-down-closing
    recurring=x.strata_monthly+x.property_tax_monthly+x.condo_insurance_monthly+x.maintenance_monthly+x.heating_monthly
    monthly_housing=mortgage+recurring
    # Approximate qualifying stress rate: higher of contract + 2% and floor.
    qualify_rate=max(x.annual_rate+.02,x.stress_floor)
    qualify_mortgage=payment(principal,qualify_rate,x.amort_years*12)
    # Insurance + maintenance excluded from GDS/TDS, as typical lender qualification categories differ.
    qualify_housing=qualify_mortgage+x.property_tax_monthly+x.heating_monthly+x.strata_monthly*.5
    gross_monthly=x.gross_annual_income/12
    gds=qualify_housing/gross_monthly if gross_monthly else float('inf')
    tds=(qualify_housing+x.other_debt_monthly)/gross_monthly if gross_monthly else float('inf')
    monthly_surplus=x.net_monthly_income+x.other_monthly_income-monthly_housing-x.living_monthly-x.other_debt_monthly
    conditions={'mortgage_qualification':gds<=x.max_gds and tds<=x.max_tds,
                'purchase_cash':cash_after>=x.reserve_floor,
                'monthly_cashflow':monthly_surplus>=0}
    return dict(down=down,insurance_premium=premium,mortgage_principal=principal,monthly_mortgage=mortgage,
        ptt_before_relief=ptt(x.price),fthb_relief=fthb_relief(x.price,x.first_time_eligible),ptt_due=transfer,
        closing_costs=closing,cash_after_purchase=cash_after,monthly_housing=monthly_housing,
        monthly_surplus=monthly_surplus,gds=gds,tds=tds,qualifying_rate=qualify_rate,qualifying_mortgage=qualify_mortgage,qualifying_housing=qualify_housing,ltv=principal/x.price,lti=principal/x.gross_annual_income if x.gross_annual_income else float("inf"),
        conditions=conditions,affordable=all(conditions.values()))

def max_affordable(x:Inputs,limit=2500000):
    # Search full price grid: eligibility/insurance threshold can make feasibility nonmonotone.
    best=None
    for price in range(int(x.price_step),int(limit)+1,int(x.price_step)):
        try:
            y=housing(replace(x,price=float(price)))
            if y['affordable']: best=price
        except ValueError: pass
    return best

def renewal(x:Inputs):
    h=housing(x); n=x.amort_years*12; elapsed=min(n,x.renewal_year*12)
    balance=balance_after(h['mortgage_principal'],x.annual_rate,elapsed,n)
    new=payment(balance,x.renewal_rate,n-elapsed) if n>elapsed else 0
    return dict(balance_at_renewal=balance,current_payment=h['monthly_mortgage'],renewal_payment=new,
                monthly_increase=new-h['monthly_mortgage'],renewal_month=elapsed)

def cashflow(x:Inputs):
    h=housing(x); ren=renewal(x); cash=h['cash_after_purchase']; rows=[]
    for month in range(1,x.horizon_months+1):
        jobless=x.unemployment_start<=month<x.unemployment_start+x.unemployment_months if x.unemployment_months else False
        income=(x.replacement_income_monthly if jobless else x.net_monthly_income)+x.other_monthly_income
        mort=ren['renewal_payment'] if month>ren['renewal_month'] else h['monthly_mortgage']
        if month>x.amort_years*12: mort=0
        emergency=x.assessment_amount if month==x.assessment_month else 0
        out=mort+(h['monthly_housing']-h['monthly_mortgage'])+x.living_monthly+x.other_debt_monthly+emergency
        net=income-out; cash+=net
        rows.append(dict(month=month,income=income,mortgage=mort,regular_expenses=out-emergency-mort,
                         special_assessment=emergency,net_cashflow=net,cash_balance=cash,
                         below_reserve=cash<x.reserve_floor,unemployed=jobless))
    return rows

def heatmap(x:Inputs,price_factors=(.85,.925,1,1.075,1.15),rate_shifts=(-.02,-.01,0,.01,.02)):
    rows=[]
    for pf in price_factors:
        for shift in rate_shifts:
            try:
                scenario=replace(x,price=round(x.price*pf),annual_rate=max(0,x.annual_rate+shift))
                result=housing(scenario)
                rows.append(dict(price=scenario.price,rate=scenario.annual_rate,monthly_surplus=result['monthly_surplus'],affordable=result['affordable']))
            except ValueError:
                rows.append(dict(price=round(x.price*pf),rate=max(0,x.annual_rate+shift),monthly_surplus=None,affordable=False))
    return rows

def down_comparison(x:Inputs):
    rows=[]
    for pct in (.10,.20,.30,.40):
        try:
            result=housing(replace(x,down_pct=pct))
            rows.append(dict(down_pct=pct,**result))
        except ValueError: rows.append(dict(down_pct=pct,error='Not eligible under demo rules'))
    return rows
