"""Mortgage Financial Planner — dedicated setup workspace and shared scenario."""
import streamlit as st
from model import Inputs
st.set_page_config(page_title="Mortgage Financial Planner",page_icon="🏡",layout="wide",initial_sidebar_state="expanded")
st.markdown("""<style>
/* Consistent, proposal-inspired navy / teal editorial design */
:root {--mf-navy:#142c43;--mf-teal:#177888;--mf-cream:#f4f8fa;}
[data-testid="stAppViewContainer"]{background:linear-gradient(180deg,#f4f8fb 0%,#fff 55%)!important}
[data-testid="stSidebar"]{background:#142c43!important}
[data-testid="stSidebar"] *{color:#f0f6fa!important}
[data-testid="stSidebar"] [data-testid="stSidebarNavLink"]{border-radius:10px}
[data-testid="stSidebar"] [data-testid="stSidebarNavLink"]:hover{background:#24506a!important}
[data-testid="stSidebar"] [aria-current="page"]{background:#216477!important}
.block-container{max-width:1400px!important;padding-top:4.5rem!important;padding-bottom:5rem!important}
h1,h2,h3{color:#142c43!important;letter-spacing:-.035em}
h1{font-size:2.15rem!important;line-height:1.18!important}
h2{font-size:1.55rem!important;line-height:1.28!important;margin-top:1.4rem!important}
h3{font-size:1.18rem!important;line-height:1.35!important}
[data-testid="stMetricLabel"] p{font-size:.85rem!important;line-height:1.4!important;overflow-wrap:anywhere}
[data-testid="stMetricValue"]{font-variant-numeric:tabular-nums}
[data-testid="stMetricValue"] div{font-size:clamp(1.25rem,2vw,1.85rem)!important}
[data-testid="stMetric"]{min-width:0;padding:.65rem .75rem!important}
[data-testid="column"]{min-width:0}
[data-testid="stCaptionContainer"]{line-height:1.5!important}
@media(max-width:1000px){
 .block-container{padding-left:1.2rem!important;padding-right:1.2rem!important}
 h1{font-size:1.85rem!important}
 [data-testid="stMetricValue"] div{font-size:1.4rem!important}
}
[data-testid="stMetric"]{background:white!important;border:1px solid #dce8ef!important;border-left:3px solid #17808c!important;border-radius:14px!important;box-shadow:0 5px 20px rgba(18,45,70,.05)!important}
[data-testid="stMetricLabel"]{color:#627b8e!important}
[data-testid="stMetricValue"]{color:#15324b!important}
[data-testid="stExpander"]{border:1px solid #dbe5eb!important;border-radius:13px!important;background:rgba(255,255,255,.78)}
[data-testid="stTabs"] button{font-weight:600}
[data-testid="stTabs"] button[aria-selected="true"]{color:#167887!important}
[data-testid="stAlert"]{border-radius:13px}
.mf-brand{display:flex;align-items:center;gap:15px;padding:17px 20px;background:linear-gradient(110deg,#142d45,#18788a);color:white;border-radius:17px;box-shadow:0 12px 28px rgba(16,57,76,.15);margin:4px 0 14px}
.mf-brand strong{display:block;font-size:1.35rem;letter-spacing:-.02em}
.mf-brand small{display:block;color:#c5e4e8;font-size:.68rem;letter-spacing:.15em;margin-top:3px}
.mf-brand-icon{width:43px;height:43px;border-radius:12px;background:#ffffff22;display:grid;place-items:center;font-size:1.8rem}
.mf-eyebrow{font-size:.7rem;color:#187888;font-weight:700;letter-spacing:.14em}
.mf-section{border-top:1px solid #e1e9ee;padding-top:12px}

</style>""", unsafe_allow_html=True)
st.markdown("""<div class="mf-brand"><span class="mf-brand-icon">⌂</span><span><strong>Mortgage Financial Planner</strong><small>FINANCIAL DECISION STUDIO · V2.4 BETA · CAD</small></span></div>""",unsafe_allow_html=True)
st.caption("Explore mortgage affordability, long-term wealth and financial resilience with one shared scenario.")
# Initialize a usable default scenario without rendering the editor on analysis pages.
# The dedicated setup workspace owns all scenario form widgets and applies changes.
if "scenario" not in st.session_state:
    st.session_state["scenario"] = Inputs(
        price=700000,down_pct=.30,annual_rate=.045,amort_years=25,
        gross_annual_income=120000,net_monthly_income=7500,
        other_monthly_income=0,liquid_cash=350000,other_debt_monthly=0,
        living_monthly=2200,reserve_floor=30000,strata_monthly=515,
        property_tax_monthly=350,condo_insurance_monthly=0,
        maintenance_monthly=0,heating_monthly=70,closing_other=2500,
        first_time_eligible=False)
    st.session_state["applied_rent"] = {
        "base":1800.0,"yield":.055,"utilities":0.0,"internet":0.0,
        "other":0.0,"buy_beds":2.0,"rent_beds":1.0,
        "buy_area":850,"rent_area":650,"buy_exterior":100,"rent_exterior":0}
    st.session_state["scenario_version"] = 1
nav=st.navigation({"WORKSPACE":[
    st.Page("pages/0_Setup_Scenario.py",title="Set Up Your Scenario",icon="⚙️",default=True),
    st.Page("pages/1_Financial_Overview.py",title="Financial Overview",icon="🏠"),
    st.Page("pages/2_Mortgage_Affordability.py",title="Mortgage & Affordability",icon="🧮"),
    st.Page("pages/4_Asset_Liquidity.py",title="Asset & Liquidity",icon="💼"),
    st.Page("pages/3_Rent_vs_Buy.py",title="Rent vs Buy",icon="⚖️"),
    st.Page("pages/5_Risk_Stress.py",title="Risk & Stress Testing",icon="🛡️"),
    st.Page("pages/7_Financial_Decision_Summary.py",title="Financial Decision Summary",icon="🧭")],
    "TOOLS & EXPORT":[st.Page("pages/6_Advanced_Export.py",title="Advanced Analytics & Export",icon="📊")]})
nav.run()
