"""Mortgage Financial Planner — three-path portfolio demo."""
from dataclasses import replace
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import streamlit as st
from scenario_header import active_scenario_header
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from model import Inputs,housing,renewal,cashflow,heatmap,down_comparison,max_affordable
from asset_model import AssetProfile,asset_financing
from asset_trajectory import ProjectionSettings,project_assets
from rent_vs_buy import Comparison,simulate,break_even_year,break_even_grid
from report import make_report
from integrity import audit_rent_vs_buy,audit_asset_trajectory
from intelligence import asset_diagnostics,rent_buy_diagnostics,compare_snapshots


st.markdown('''<style>.block-container{max-width:1370px;padding-top:4.5rem}h1,h2,h3{letter-spacing:-.025em}
[data-testid="stMetric"]{border:1px solid #dbe5ef;border-radius:12px;padding:13px;background:#f8fafc}
[data-testid="stSidebar"]{background:#142c43}
[data-testid="stMetricValue"]{font-size:clamp(1.1rem,1.9vw,1.7rem)!important;white-space:normal;overflow-wrap:anywhere}
[data-testid="stMetricLabel"]{font-size:.8rem}
[data-testid="stMetric"]{min-width:0;box-shadow:0 4px 14px rgba(30,55,75,.05);border-left:3px solid #318b8d} [data-testid="stMetric"]:hover{box-shadow:0 8px 22px rgba(30,55,75,.09)}
[data-testid="stTabs"] button{font-weight:600}
[data-testid="stExpander"]{border-radius:10px} [data-testid="stAlert"]{border-radius:12px} [data-testid="stTabs"] [role="tab"]{padding:.75rem 1.1rem} .block-container h4{margin-top:1.1rem}
</style>''',unsafe_allow_html=True)
fmt=lambda n: f'${n:,.0f}' if n is not None else '—'

def explain(title,formula,logic,limits='Illustrative planning model; not lender approval or a forecast.'):
    with st.expander('ⓘ How is this calculated? · '+title):
        st.markdown('**Core formula**');st.latex(formula)
        st.markdown('**Method:** '+logic)
        st.caption('Limitations: '+limits)

def insight(title, headline, details, caution=None):
    """Plain-language, scenario-dependent interpretation; no implied approval."""
    with st.container(border=True):
        st.markdown(f"**Chart takeaway · {title}**")
        st.write(headline)
        st.caption(details)
        if caution:
            st.caption('**Interpretation limit:** ' + caution)

def diagnostic_cards(items):
    for d in items:
        with st.container(border=True):
            st.markdown(f"**{d.title} · {d.status}**")
            st.write(d.observation)
            st.caption('Why it matters: ' + d.significance)
            st.caption('Explore next: ' + d.next_step)

def audit_panel(checks):
    ok=sum(c.passed for c in checks)
    with st.expander(f'Financial integrity · {ok}/{len(checks)} reconciliations passed'):
        if ok==len(checks):st.success('All monthly ledger identities reconcile within CAD $0.02.')
        else:st.error('A reconciliation discrepancy was detected. Treat projected results as provisional.')
        st.dataframe(pd.DataFrame([{'Check':c.name,'Status':'PASS' if c.passed else 'FAIL',
            'Maximum discrepancy (CAD)':round(c.max_error,6),'Basis':c.detail} for c in checks]),
            hide_index=True,use_container_width=True)
        st.caption('Identity checks verify internal consistency, not external lending rules, taxes or forecast accuracy.')

def metric_row(items):
    cols=st.columns(len(items))
    for col,(name,value) in zip(cols,items):
        with col:
            st.metric(name,value)

def chart_style(fig,title,yaxis='CAD'):
    fig.update_layout(title=dict(text=title,font=dict(size=18)),height=370,
        margin=dict(l=15,r=15,t=55,b=25),hovermode='x unified',
        legend=dict(orientation='h',y=1.08,x=0),
        plot_bgcolor='rgba(0,0,0,0)',paper_bgcolor='rgba(0,0,0,0)',
        yaxis=dict(title=yaxis,tickformat=',.0f',gridcolor='rgba(130,150,170,.17)'))
    return fig



from model import Inputs
x=st.session_state["scenario"]
try:
    h=housing(x)
except ValueError as err:
    st.error(f"Adjust shared scenario inputs: {err}")
    st.stop()

active_scenario_header()
st.title("Advanced Analytics & Export")
st.caption("Shared property, income and expense inputs · British Columbia · CAD")
ap=AssetProfile(st.session_state.get("asset_cash",300000),st.session_state.get("asset_invest",550000),st.session_state.get("asset_eligible",100)/100,st.session_state.get("asset_down",35)/100,st.session_state.get("asset_ratio",1.0),st.session_state.get("asset_reserve",60000),st.session_state.get("asset_drawdown",25)/100)
cp=Comparison(monthly_rent=st.session_state.get("rent_monthly",2700),years=st.session_state.get("rent_years",15))
finance_label=st.session_state.get("rent_finance","Income-based")
finance={"Income-based":"income","Asset-based":"asset","income":"income","asset":"asset"}.get(finance_label)
if finance is None:
    st.warning(f"Unknown saved financing selection {finance_label!r}; defaulting to income-based financing.")
    finance="income" 
st.divider()
with st.expander('Methodology, model limitations & privacy'):
    st.markdown('''**Educational financial decision-support demo. Not mortgage pre-approval or investment advice.**

- BC tax and mortgage insurance rules are simplified and may not reflect the latest policy, exceptions, or lender practices.
- Asset-based 35% down and 1:1 recognized assets is a **user-described product assumption**, not a universal lending rule.
- Income-based eligibility is evaluated using the model's GDS/TDS assumptions. Asset-based eligibility is tested at application only.
- Buy vs Rent compares similar owner-occupied housing and assumes the same starting wealth and income.
- Mortgage interest is included in monthly cash flow; only outstanding principal reduces home equity.
- Net worth values show estimated liquidation proceeds net of a selling-cost assumption, but exclude tax impacts.
- No login, database, tracking, or persistent storage. Avoid entering sensitive personal financial information.

Official references: [BC property transfer tax](https://www2.gov.bc.ca/gov/content/taxes/property-taxes/property-transfer-tax) · [Canadian down payment](https://www.canada.ca/en/financial-consumer-agency/services/mortgages/down-payment.html)''')
try:
    report_x=bx if 'bx' in locals() else x
    excel=make_report(report_x,maximum=st.session_state.get('max_result') if st.session_state.get('max_key')==x else None,
       asset_profile=ap,comparison=cp,financing=finance)
    st.download_button('⬇ Download complete Excel scenario report',excel,'mortgage_financial_planner_analysis.xlsx',
      mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',use_container_width=True)
except Exception as err:
    st.error(f'Excel report unavailable: {err}')
    st.caption('The export uses the current shared scenario and the selected Rent vs Buy financing pathway.')
st.caption('Mortgage Financial Planner · Portfolio demo · Python / Streamlit')
