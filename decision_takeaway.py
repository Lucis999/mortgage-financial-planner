"""Pure, testable conditional interpretation of a modeled purchase decision."""
def evaluate_decision(h, minimum_surplus, limits, savings, years):
    conditions=h["conditions"]
    failed=[k for k,ok in conditions.items() if not ok]
    lifestyle_gap=h["monthly_surplus"]-minimum_surplus
    details=[]
    if not conditions.get("purchase_cash",False):
        details.append("Capital constraint: down payment, closing costs or minimum reserve is insufficient.")
    if not conditions.get("mortgage_qualification",False):
        details.append("Mortgage qualification constraint: modeled income/debt-service screening fails.")
    if not conditions.get("monthly_cashflow",False):
        details.append("Cash-flow constraint: modeled monthly household surplus is negative.")
    if lifestyle_gap<0:
        details.append(f"Lifestyle constraint: projected post-purchase surplus is ${-lifestyle_gap:,.0f} per month below your selected savings target.")
    if not details:
        headline="Selected property meets all modeled baseline and lifestyle-preservation conditions."
        status="success"
        details.append("Passing these checks is not mortgage approval; review downside scenarios, property comparability and rent-versus-buy net worth.")
    elif len(details)>1:
        headline="Multiple purchase-readiness constraints need attention."
        status="warning"
    elif lifestyle_gap<0:
        headline="The property may pass baseline screening but does not preserve the selected lifestyle target."
        status="warning"
    else:
        headline="The selected property does not meet all modeled baseline conditions."
        status="warning"
    time=savings["years_to_target"]
    time_label=(f"{time:.1f} years" if time is not None else f"Beyond {years} years")
    return {"status":status,"headline":headline,"details":details,"time_label":time_label,"failed":failed,"lifestyle_gap":lifestyle_gap,"combined_ceiling":limits["combined"]}
