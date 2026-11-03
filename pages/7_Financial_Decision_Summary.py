"""Consolidated decision workspace: underwriting, affordability, readiness and runway."""
from dataclasses import replace
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from model import housing,cashflow
from affordability_summary import affordability_limits,time_to_down_payment
from purchase_timeline import dynamic_purchase_readiness
from scenario_header import active_scenario_header

fmt=lambda n: f"${n:,.0f}" if n is not None else "Not feasible in scan"
x=st.session_state["scenario"]
try:
    h=housing(x)
except ValueError as exc:
    st.error(f"Scenario requires adjustment: {exc}")
    st.stop()
active_scenario_header()
st.title("🧭 Financial Decision Summary")
st.caption("Your decision workspace · lender-style screening, purchasing power, savings readiness and five-year post-purchase cash flow.")
rent=st.session_state.get("applied_rent",{})
rent_monthly=sum(float(rent.get(k,0)) for k in ("base","utilities","internet","other"))

st.subheader("01 · Can I qualify for the selected mortgage?")
a,b,c,d=st.columns(4)
a.metric("Mortgage principal",fmt(h["mortgage_principal"]))
b.metric("Stress-test rate",f'{h["qualifying_rate"]:.2%}')
c.metric("GDS / 39% guide",f'{h["gds"]:.1%}')
d.metric("TDS / 44% guide",f'{h["tds"]:.1%}')
e,f,g,hcol=st.columns(4)
e.metric("LTV",f'{h["ltv"]:.1%}')
f.metric("LTI · salary multiple",f'{h["lti"]:.2f}×')
g.metric("Cash above reserve",fmt(h["cash_after_purchase"]-x.reserve_floor))
hcol.metric("Post-purchase monthly surplus",fmt(h["monthly_surplus"]))
if h["affordable"]:
    st.success("All modeled baseline screening, capital and monthly cash-flow checks pass.")
else:
    st.warning("One or more baseline checks fail. See the individual qualification conditions below.")
with st.expander("What qualifies? · Debt service, salary multiple and caveats"):
    for name,passed in h["conditions"].items():
        st.write(("✅ " if passed else "⚠️ ")+name.replace("_"," ").title())
    st.markdown("**GDS** includes stress-tested mortgage, property tax, heating and half of condo fees. **TDS** adds recurring debt payments. **LTV** is mortgage / property value; **LTI** is mortgage / annual gross income.")
    st.caption("39% GDS / 44% TDS are CMHC-style reference thresholds, not universal approvals. OSFI's 4.5× LTI is a portfolio measure, not an individual loan cap. No standard 5×, 10× or 20× salary rule applies.")

st.subheader("02 · Lifestyle-Preserving Affordability")
st.caption("A home is not truly affordable if it forces you to give up the monthly savings, discretionary spending or financial flexibility you want to keep.")
lifestyle_mode=st.radio("Lifestyle protection",["Maintain current monthly savings while renting","Set my own minimum monthly surplus","Basic non-negative cash flow"],horizontal=True,key="lifestyle_mode")
rent_baseline=x.net_monthly_income+x.other_monthly_income-x.living_monthly-x.other_debt_monthly-rent_monthly
if lifestyle_mode=="Maintain current monthly savings while renting":
    minimum_surplus=max(0.0,rent_baseline)
    st.info(
        f"Current estimated monthly surplus while renting: {fmt(rent_baseline)} / month. "
        f"Required post-purchase surplus: {fmt(minimum_surplus)} / month."
    )
elif lifestyle_mode=="Set my own minimum monthly surplus":
    minimum_surplus=float(st.number_input("Minimum post-purchase monthly surplus (CAD)",min_value=0.0,max_value=100000.0,value=1500.0,step=100.0,key="lifestyle_surplus_target"))
else:
    minimum_surplus=0.0
current_lifestyle_gap=h["monthly_surplus"]-minimum_surplus
a,b,c=st.columns(3)
a.metric("Required monthly surplus",fmt(minimum_surplus))
b.metric("Projected after-purchase surplus",fmt(h["monthly_surplus"]))
c.metric("Lifestyle buffer vs target",fmt(current_lifestyle_gap))
if current_lifestyle_gap>=0:
    st.success("The selected home preserves the chosen monthly surplus target under baseline assumptions.")
else:
    st.warning(f"The selected home falls short of your lifestyle target by {fmt(-current_lifestyle_gap)} per month.")
st.caption("Renting baseline = take-home income + other income − living expenses − debt payments − all-in rent. Do not include rent in living expenses, or it will be double-counted. A positive surplus target preserves savings capacity, not necessarily every aspect of quality of life.")

st.subheader("03 · What home price can I afford?")
st.caption("Three different constraints: available down-payment capital, income-based qualification and sustainable monthly lifestyle. These are illustrative screening ceilings, not lender offers.")
@st.cache_data(show_spinner=False)
def limits_cached(scenario, protected_surplus):
    return affordability_limits(scenario,minimum_surplus=protected_surplus)
with st.spinner("Scanning candidate home prices..."):
    limits=limits_cached(x,minimum_surplus)
a,b,c,d=st.columns(4)
a.metric("Capital ceiling",fmt(limits["capital"]))
b.metric("Income ceiling",fmt(limits["income"]))
c.metric("Lifestyle-preserving ceiling",fmt(limits["lifestyle"]))
d.metric("Combined ceiling",fmt(limits["combined"]))
st.caption(f"Current lifestyle protection target: {fmt(minimum_surplus)} / month. The combined ceiling must meet this target in addition to capital and mortgage qualification.")
st.caption("The price scan covers $1,000–$2,500,000 in $1,000 increments. 'Not feasible in scan' may mean the price is outside the scan or no candidate passes; it is not a zero-dollar valuation.")
with st.expander("How is the price ceiling determined?"):
    st.write("For each candidate price, retain the selected down-payment percentage and housing-cost assumptions. Recalculate closing costs, mortgage qualification, cash reserve and monthly surplus above your selected lifestyle target. The combined ceiling is the highest scanned price meeting all checks.")
    st.caption("Costs such as property taxes, maintenance and condo fees do not automatically scale with purchase price in this version. Review these inputs when comparing substantially different homes.")

st.subheader("04 · How long until I can buy?")
st.caption("Savings-to-down-payment is separate from full purchase readiness. Rent must not already be included in the Living Expenses input.")
a,b,c=st.columns(3)
years=a.slider("Planning horizon (years)",1,30,15,key="summary_savings_horizon")
savings_growth=b.slider("Annual savings growth (%)",-10,15,0,key="summary_savings_growth")/100
c.metric("Current all-in monthly rent",fmt(rent_monthly))
savings=time_to_down_payment(x,years,monthly_rent=rent_monthly,annual_savings_growth=savings_growth)
a,b,c=st.columns(3)
a.metric("Down payment + closing",fmt(savings["cash_target"]))
b.metric("Available above reserve",fmt(savings["available"]))
c.metric("Time to cash target",f'{savings["years_to_target"]:.1f} years' if savings["years_to_target"] is not None else f"Not within {years} years")
st.caption(f'Current monthly savings estimate while renting: {fmt(savings["monthly_savings"])}. Cash-target calculation holds home price fixed and does not guarantee lender qualification.')

st.markdown("#### When could I buy? · Dynamic purchase readiness")
a,b,c=st.columns(3)
home_growth=a.slider("Annual home-price growth (%)",-5.0,12.0,2.5,.5,key="timeline_growth")/100
income_growth=b.slider("Annual income growth (%)",-5.0,12.0,2.0,.5,key="timeline_income_growth")/100
rent_growth=c.slider("Annual rent growth (%)",-5.0,12.0,2.5,.5,key="timeline_rent_growth")/100
d,e=st.columns(2)
living_growth=d.slider("Annual living-cost growth (%)",-5.0,12.0,2.0,.5,key="timeline_living_growth")/100
asset_return=e.slider("Annual liquid-asset return (%)",-20.0,20.0,0.0,.5,key="timeline_asset_return")/100
timeline=pd.DataFrame(dynamic_purchase_readiness(x,15,home_growth,income_growth,rent_growth,living_growth,rent_monthly,asset_return))
fig=go.Figure()
fig.add_trace(go.Scatter(x=timeline["year"],y=timeline["assets"],name="Projected liquid assets",mode="lines+markers"))
fig.add_trace(go.Scatter(x=timeline["year"],y=timeline["capital_needed"],name="Down payment + closing + reserve",mode="lines",line=dict(dash="dash")))
fig.update_layout(height=360,xaxis_title="Years from now",yaxis_title="CAD",hovermode="x unified")
st.plotly_chart(fig,use_container_width=True)
ready=timeline.loc[timeline["purchase_ready"],"year"]
if len(ready):
    st.success(f"Earliest modeled purchase-ready year: year {int(ready.iloc[0])}. Capital, income qualification and cash-flow checks pass in this deterministic scenario.")
else:
    st.warning("No year within 15 years passes all modeled capital, qualification and cash-flow conditions.")
st.caption("The dynamic timeline compounds home prices, income, rent, living costs and asset returns. It is a scenario projection, not a promise of mortgage approval.")

st.subheader("05 · What happens to cash after purchase?")
st.caption("60-month post-closing cash runway using the current scenario's mortgage, ownership expenses, income and modeled renewal/shock assumptions.")
projection=pd.DataFrame(cashflow(replace(x,horizon_months=60)))
a,b,c=st.columns(3)
a.metric("Cash at month 60",fmt(float(projection["cash_balance"].iloc[-1])))
b.metric("Lowest cash in 5 years",fmt(float(projection["cash_balance"].min())))
c.metric("Months below reserve",str(int((projection["cash_balance"]<x.reserve_floor).sum())))
fig=go.Figure()
fig.add_trace(go.Scatter(x=projection["month"],y=projection["cash_balance"],name="Projected cash",mode="lines"))
fig.add_hline(y=x.reserve_floor,line_dash="dash",annotation_text="Minimum reserve")
fig.update_layout(height=350,xaxis_title="Months after purchase",yaxis_title="CAD",hovermode="x unified")
st.plotly_chart(fig,use_container_width=True)
with st.expander("View 60-month cash-flow ledger"):
    st.dataframe(projection[["month","income","mortgage","regular_expenses","special_assessment","net_cashflow","cash_balance"]],hide_index=True,use_container_width=True)
st.caption("This baseline projection does not inherit interactive shocks selected on the Risk & Stress page. Use that page for scenario-specific downside analysis.")

st.subheader("06 · Decision takeaway")
from decision_takeaway import evaluate_decision
result=evaluate_decision(h, minimum_surplus, limits, savings, years)
if result["status"]=="success":
    st.success(result["headline"])
else:
    st.warning(result["headline"])
for message in result["details"]:
    st.write("• " + message)
st.markdown("**Purchase-readiness snapshot**")
a,b,c=st.columns(3)
a.metric("Lifestyle-protected price ceiling",fmt(limits["combined"]))
b.metric("Available before purchase (above reserve)",fmt(savings["available"]))
c.metric("Time to selected property's cash target",result["time_label"])
st.caption("The price ceiling is based on a fixed candidate-price scan. The savings timeline addresses capital accumulation only; mortgage qualification and the desired lifestyle surplus must also be satisfied. No result constitutes a lending decision.")
with st.expander("Decision pathways · How to interpret the possible outcomes"):
    st.markdown("""
    - **Ready within the model:** Capital, lender-style screening, cash flow and the selected lifestyle savings target all pass. Review downside scenarios and rent-vs-buy opportunity cost.
    - **Qualified, but lifestyle constrained:** Bank-style checks and capital pass, but ownership reduces monthly savings below the protected target. Consider a lower-priced property, higher income or a deliberately revised target.
    - **Capital constrained:** Insufficient cash for down payment, closing costs and reserve. Evaluate the savings timeline or a lower purchase price.
    - **Income / debt-service constrained:** GDS/TDS qualification fails. Explore lower borrowing, debt reduction or higher qualifying income; savings alone do not resolve this.
    - **Cash-flow constrained:** Monthly surplus is negative even without lifestyle protection. Reconsider affordability before purchasing.
    - **Multiple constraints:** More than one condition fails. Address all binding constraints; satisfying one is not sufficient.
    """)
st.caption("Educational financial planning only. Mortgage approval, credit history, lender-specific qualifying costs, property appraisal, taxes and future market conditions require independent verification.")
