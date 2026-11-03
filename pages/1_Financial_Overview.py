"""Mortgage Financial Planner — standalone financial dashboard.

Financial logic is imported from the tested foundation; this file only presents
scenario calculations. Advanced legacy tools remain available in the sidebar.
"""
from dataclasses import replace
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from scenario_header import active_scenario_header
from model import Inputs, housing, renewal, cashflow, heatmap
from rent_vs_buy import Comparison, simulate, break_even_year
from asset_model import AssetProfile, asset_financing
from rental_assumptions import RENT_PRESETS, annual_rent_yield, monthly_rent_from_yield, all_in_rent, implied_rental_property_value


st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&display=swap');
html,body,[class*=css], [data-testid="stApp"] {font-family:'DM Sans',sans-serif;}
[data-testid="stAppViewContainer"] {background:linear-gradient(180deg,#f3f7fb 0%,#fbfcfe 52%);}
[data-testid="stSidebar"] {background:#12273e;}
[data-testid="stSidebar"] * {color:#edf5fb!important;}
[data-testid="stSidebar"] [data-baseweb="input"] input {color:#142b41!important;}
[data-testid="stSidebar"] [data-baseweb="select"] * {color:#142b41!important;}
.block-container {max-width:1480px;padding-top:4.5rem;padding-bottom:4rem;}
h1,h2,h3 {letter-spacing:-.035em;color:#152c43;}
[data-testid="stMetric"] {background:#fff;border:1px solid #e3eaf1;padding:17px 18px;border-radius:15px;box-shadow:0 7px 22px rgba(17,45,73,.04);}
[data-testid="stMetricLabel"] {color:#5a7188;font-size:.84rem;}
[data-testid="stMetricValue"] {color:#142c44;font-size:clamp(1.25rem,2vw,1.95rem);}
[data-testid="stAlert"] {border-radius:13px;}
div[data-testid="stVerticalBlockBorderWrapper"] > div {border-radius:16px!important;}
[data-testid="stPageLink"] {border-radius:12px;}
.hero {background:linear-gradient(115deg,#122e48,#176c7c);padding:28px 30px;border-radius:20px;color:white;margin-bottom:16px;box-shadow:0 16px 40px rgba(14,50,72,.13)}
.hero h1 {color:white;margin:0 0 8px;font-size:2.15rem;}
.hero p {color:#d4e7ed;margin:0;}
.eyebrow {font-size:.72rem;letter-spacing:.16em;font-weight:700;color:#a3d9df;margin-bottom:9px;}
.section-label {font-size:1.05rem;font-weight:700;color:#19354e;margin:12px 0;}
.note {color:#64778a;font-size:.84rem;}
[data-testid="stTabs"] button {font-weight:600;}
[data-testid="stAppViewContainer"] .stButton button {border-radius:10px;}
</style>""",unsafe_allow_html=True)

def money(v):return f"${v:,.0f}"
def chart_layout(fig,title, ytitle="CAD"):
    fig.update_layout(title=dict(text=title,font=dict(size=16,color="#17334a")),font=dict(family="DM Sans"),height=355,margin=dict(l=12,r=12,t=55,b=18),paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",hovermode="x unified",legend=dict(orientation="h",y=1.13,x=0),xaxis=dict(showgrid=False),yaxis=dict(title=ytitle,gridcolor="#e5edf3",tickprefix="$",tickformat=",.0f"))
    return fig

active_scenario_header()
st.markdown('''<div class="hero"><div class="eyebrow">MORTGAGE · FINANCIAL PLANNER</div><h1>Plan your purchase with confidence.</h1><p>Understand affordability, compare buying with renting, and test your financial resilience.</p></div>''', unsafe_allow_html=True)
st.caption("Illustrative financial scenarios · CAD · Not lender approval or current policy verification")

st.markdown("### Financial Overview")
st.caption("Edit your assumptions in the dedicated Set Up Your Scenario workspace. All analysis pages use the last applied scenario.")
x=st.session_state["scenario"]
with st.expander("ⓘ How this is calculated · mortgage, cash flow & qualification"):
    st.markdown("**Mortgage:** financed principal and Canadian semi-annual compounding. **Closing cash:** down payment + modeled closing costs. **Surplus:** net income + other income − housing costs − living expenses − debt. **GDS/TDS:** illustrative stress-tested screening ratios, not lender approval.")
st.markdown("### Your financial snapshot")

try:
    h=housing(x)
except ValueError as e:
    st.error(f"Scenario cannot be calculated: {e}. Adjust your inputs above.")
    st.stop()

st.caption('Results use the last scenario applied in the workspace.')
a,b,c,d=st.columns(4)
a.metric("Monthly mortgage",money(h['monthly_mortgage']))
b.metric("Total monthly housing",money(h['monthly_housing']))
c.metric("Cash after closing",money(h['cash_after_purchase']))
d.metric("Monthly household surplus",money(h['monthly_surplus']))

# Rent assumption is deliberately editable: examples are not verified market data.
st.markdown("### Housing cost comparison · Own vs Rent")
st.caption("Illustrative rental scenarios, not a property appraisal. Compare a similar-sized home and use the same treatment of utilities and services on both sides.")
rent_settings=st.session_state.get("applied_rent",{"base":1800,"yield":.055,"utilities":0,"internet":0,"other":0})
base_rent=rent_settings["base"]
annual_yield=rent_settings["yield"]
rental_value=implied_rental_property_value(base_rent,annual_yield)
if rent_settings.get("buy_beds") != rent_settings.get("rent_beds") or abs(rent_settings.get("buy_area",0)-rent_settings.get("rent_area",0))>100:
    st.warning(f"⚖️ Different housing quality: buy {rent_settings.get('buy_beds','?')} bed / {rent_settings.get('buy_area','?')} sq ft versus rent {rent_settings.get('rent_beds','?')} bed / {rent_settings.get('rent_area','?')} sq ft. A lower rent may reflect a smaller home; do not interpret the result as like-for-like.")
else:
    st.caption("Bedroom count and floor area are broadly aligned; neighborhood, condition and amenities still require verification.")
rent_total=all_in_rent(base_rent,rent_settings["utilities"],rent_settings["internet"],rent_settings["other"])
c1,c2,c3=st.columns(3)
c1.metric("Comparable rental home · implied value",money(rental_value))
c2.metric("Home to buy · purchase price",money(x.price))
c3.metric("Purchase − rental implied value",money(x.price-rental_value))
st.caption(f"Rent {money(base_rent)}/month ÷ {annual_yield:.1%} gross annual yield × 12. The two homes are NOT automatically equivalent: verify beds, usable area, neighborhood, age and amenities. Change rent and yield in the shared scenario form above.")
rent_labels=["Base rent","Utilities","Internet","Other"]
rent_values=[base_rent,rent_settings["utilities"],rent_settings["internet"],rent_settings["other"]]
cost_labels=["Mortgage","Strata & insurance","Heating / hydro / electricity","Property tax & maintenance"]
cost_values=[h["monthly_mortgage"],x.strata_monthly+x.condo_insurance_monthly,x.heating_monthly,x.property_tax_monthly+x.maintenance_monthly]
owner_total=h["monthly_housing"]
# Owner-side internet is outside the current financial engine; offer a like-for-like add-on.
owner_internet=st.number_input("Owner internet / month (comparison only; not included in mortgage qualification)",0.0,1000.0,float(rent_settings["internet"]),10.0,key="overview_owner_internet")
owner_comparable=owner_total+owner_internet
c1,c2,c3=st.columns(3)
c1.metric("Own · monthly housing & internet",money(owner_comparable))
c2.metric("Rent · all-in monthly",money(rent_total))
c3.metric("Monthly own − rent",money(owner_comparable-rent_total),delta=money(rent_total-owner_comparable),delta_color="normal")
st.caption("Monthly cash-outflow comparison only: mortgage principal builds equity; this is not a net-worth or opportunity-cost comparison. Rent vs Buy provides the long-term analysis.")

st.markdown("#### Monthly ownership vs rental cost allocation")
left,right=st.columns(2,gap="large")
def _donut(labels,values,total,colors,unit="per month"):
    fig=go.Figure(go.Pie(labels=labels,values=values,hole=.68,
        marker=dict(colors=colors),textinfo="percent",sort=False,
        hovertemplate="%{label}: $%{value:,.0f}<extra></extra>"))
    fig.update_layout(height=315,margin=dict(l=8,r=8,t=12,b=40),
        legend=dict(orientation="h",y=-.12),paper_bgcolor="rgba(0,0,0,0)",
        annotations=[dict(text=money(total)+(f"<br>{unit}" if unit else ""),x=.5,y=.5,showarrow=False,font=dict(size=17,color="#17334a"))])
    return fig
with left:
    with st.container(border=True):
        st.markdown("**🏡 Ownership allocation**")
        st.plotly_chart(_donut(cost_labels+["Internet"],cost_values+[owner_internet],owner_comparable,
            ["#176c7c","#4b9ca6","#9bcbd1","#d6e8ea","#d2c8a4"]),use_container_width=True)
with right:
    with st.container(border=True):
        st.markdown("**🔑 Rental allocation**")
        st.plotly_chart(_donut(rent_labels,rent_values,rent_total,
            ["#e0a25b","#9bcbd1","#4b9ca6","#b8dbe0"]),use_container_width=True)

with st.container(border=True):
    fig=go.Figure()
    fig.add_trace(go.Bar(name="Own",y=["Monthly housing cost"],x=[owner_comparable],orientation="h",marker_color="#176c7c",
        text=[money(owner_comparable)],textposition="auto"))
    fig.add_trace(go.Bar(name="Rent",y=["Monthly housing cost"],x=[rent_total],orientation="h",marker_color="#e0a25b",
        text=[money(rent_total)],textposition="auto"))
    fig.update_layout(title="Monthly cash outflow · Direct comparison",height=245,
        barmode="group",margin=dict(l=12,r=12,t=48,b=25),xaxis_title="CAD per month",
        legend=dict(orientation="h",y=1.17),paper_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig,use_container_width=True)

st.markdown("### Affordability & financing")
with st.container(border=True):
    q1,q2,q3=st.columns(3)
    q1.metric("GDS (stressed)",f"{h['gds']:.1%}")
    q2.metric("TDS (stressed)",f"{h['tds']:.1%}")
    q3.metric("Cash needed to close",money(h["down"]+h["closing_costs"]))
    if h["affordable"]:
        st.success("All modeled income, cash-reserve and monthly-surplus checks pass.")
    else:
        failed=[k.replace("_"," ") for k,v in h["conditions"].items() if not v]
        st.warning("Planning checks needing attention: "+", ".join(failed)+".")
    with st.expander("ⓘ How this is calculated · qualification and closing costs"):
        st.markdown("GDS/TDS use modeled qualifying costs and gross income. Cash to close includes down payment and modeled closing costs. Planning checks are not a lender decision.")

st.markdown("### Purchase capital allocation")
with st.container(border=True):
    left,right=st.columns([1,1.2],gap="large")
    closing_cash=h["down"]+h["closing_costs"]
    remaining=max(0,h["cash_after_purchase"])
    capital_labels=["Down payment","Closing costs","Remaining liquid assets"]
    capital_values=[h["down"],h["closing_costs"],remaining]
    with left:
        st.plotly_chart(_donut(capital_labels,capital_values,sum(capital_values),
            ["#176c7c","#e5a65b","#b7dce0"],unit="one-time capital"),use_container_width=True)
    with right:
        st.metric("Post-closing liquid assets",money(h["cash_after_purchase"]))
        st.metric("Minimum cash reserve",money(x.reserve_floor))
        st.metric("Above / below reserve",money(h["cash_after_purchase"]-x.reserve_floor))
        st.caption("Closing cost estimates include simplified British Columbia property transfer tax assumptions.")
    bar=go.Figure(go.Bar(x=capital_labels,y=capital_values,
        marker_color=["#176c7c","#e5a65b","#b7dce0"],
        text=[money(v) for v in capital_values],textposition="outside"))
    bar.update_layout(title="Purchase capital · Dollar allocation",height=300,
        margin=dict(l=15,r=15,t=48,b=22),yaxis_title="CAD",
        paper_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(bar,use_container_width=True)
from comfort_ui import comfort_level,render_comfort
surplus=h["monthly_surplus"]
liquidity=h["cash_after_purchase"]-x.reserve_floor
ratio=h["monthly_housing"]/max(1,x.net_monthly_income+x.other_monthly_income)
render_comfort(comfort_level(surplus,liquidity,ratio),"Financial resilience · What each expression means")
c1,c2,c3=st.columns(3)
c1.metric("Monthly surplus",money(surplus))
c2.metric("Housing / estimated net income",f"{ratio:.1%}")
c3.metric("Cash above reserve",money(liquidity))
with st.expander("How is the financial resilience level assigned?"):
    st.write("The most restrictive of monthly surplus, housing-to-estimated-net-income ratio, and cash reserve determines the level. The seven emojis represent increasing financial flexibility, not work fatigue.")
st.markdown("### Continue your financial journey")
a,b,c,d=st.columns(4)
a.page_link("pages/2_Mortgage_Affordability.py",label="Mortgage & Affordability",icon="🧮")
b.page_link("pages/4_Asset_Liquidity.py",label="Asset & Liquidity",icon="💼")
c.page_link("pages/3_Rent_vs_Buy.py",label="Rent vs Buy",icon="⚖️")
d.page_link("pages/5_Risk_Stress.py",label="Risk & Stress",icon="🛡️")
st.caption("Mortgage Financial Planner · v2.1.1 · Educational scenarios, not lender approval")

