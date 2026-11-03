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
st.title("Mortgage & Affordability")
st.markdown("#### 🏠 Mortgage comfort · Qualification and monthly cash flow")
comfort=h["monthly_surplus"]
status="😊 Comfortable" if comfort>=1500 and h["affordable"] else "🙂 Manageable" if comfort>=500 and h["affordable"] else "😟 Tight" if comfort>=0 and h["affordable"] else "🥵 Constraints not met"
st.info(f"{status} · Modeled monthly surplus {fmt(comfort)}. GDS {h['gds']:.1%}, TDS {h['tds']:.1%}. These are illustrative screening indicators, not approval decisions.")

st.caption("Shared property, income and expense inputs · British Columbia · CAD")
st.subheader('Income-based mortgage planning')
metric_row([('Monthly mortgage',fmt(h['monthly_mortgage'])),('Total housing cost',fmt(h['monthly_housing'])),
            ('Cash after closing',fmt(h['cash_after_purchase'])),('Monthly surplus',fmt(h['monthly_surplus']))])
explain('Mortgage payment',r'M=\frac{Lr_m}{1-(1+r_m)^{-n}}',
    'L is financed principal (including any default insurance premium), n is amortization months, and r_m is the effective monthly rate converted from a Canadian semi-annual-compounding nominal annual rate.')
explain('Monthly surplus',r'S=I_{net}+I_{other}-M-C_{owner}-E_{living}-D',
    'Subtract monthly mortgage, strata, taxes, condo insurance, heating, maintenance, living expenses and other debt payments from take-home income.')
st.markdown('#### Qualification & closing costs')
metric_row([('GDS',f"{h['gds']:.1%}"),('TDS',f"{h['tds']:.1%}"),('BC transfer tax',fmt(h['ptt_due'])),('Closing cash',fmt(h['down']+h['closing_costs']))])
explain('GDS / TDS and qualification',r'GDS=\frac{M_{stress}+T+H+0.5F}{I_{gross}/12}\quad TDS=GDS+\frac{D}{I_{gross}/12}',
    'The qualifying payment uses the higher of contract rate + 2 percentage points or the model stress floor. The model compares ratios with 39% / 44% planning thresholds.',
    'Lenders may use different thresholds, asset tests and qualifying expenses.')
explain('Purchase cash & property transfer tax',r'C_{closing}=D+PTT(P)-Relief(P)+C_{other}',
    'The model applies simplified BC property transfer tax tiers and optional first-time buyer relief. Mortgage default insurance is financed when applicable.',
    'Tax eligibility and policy thresholds must be verified against official BC rules.')
if h['affordable']:st.success('All three illustrative income, cash reserve and monthly budget checks pass.')
else:st.info('One or more planning checks do not pass. This is not a lender decision.')
st.markdown("**Qualification checks · What passes and why**")
check_details=[
 ("Mortgage qualification",h["conditions"]["mortgage_qualification"],
  f"GDS {h['gds']:.1%} vs limit {x.max_gds:.0%}; TDS {h['tds']:.1%} vs limit {x.max_tds:.0%}.",
  "Reduce debt, increase qualifying income, increase down payment, or consider a less expensive property."),
 ("Purchase cash & reserve",h["conditions"]["purchase_cash"],
  f"Post-closing cash {fmt(h['cash_after_purchase'])} vs minimum reserve {fmt(x.reserve_floor)}. "
  f"Down payment {fmt(h['down'])}; closing costs {fmt(h['closing_costs'])}.",
  "Increase liquid funds, reduce purchase costs, or adjust the down payment while respecting lending requirements."),
 ("Monthly cash flow",h["conditions"]["monthly_cashflow"],
  f"Monthly surplus {fmt(h['monthly_surplus'])} vs minimum $0. "
  f"Net income plus other income {fmt(x.net_monthly_income+x.other_monthly_income)}; "
  f"housing {fmt(h['monthly_housing'])}; living {fmt(x.living_monthly)}; debt {fmt(x.other_debt_monthly)}.",
  "Reduce recurring expenses, increase income, or select a lower-cost home.")
]
for title,passed,detail,action in check_details:
    with st.expander(("✅ " if passed else "❌ ")+title,expanded=not passed):
        st.write(detail)
        if not passed:st.caption("Potential improvement: "+action)
st.caption("These are planning checks, not lender underwriting decisions.")
if st.button('Calculate maximum modeled property price',key='max_button'):
    with st.spinner('Checking candidate prices...'):
        st.session_state.max_result=max_affordable(x)
        st.session_state.max_key=x
maximum=st.session_state.get('max_result') if st.session_state.get('max_key')==x else None
if maximum is not None:st.metric('Maximum modeled property price',fmt(maximum))
explain('Maximum property price',r'P^*=\max\{P: GDS\leq g,\ TDS\leq t,\ Cash\geq Reserve,\ Surplus\geq0\}',
    'Searches a $1,000 property-price grid and checks all three constraints at each price.',
    'This is a planning estimate, not a mortgage approval.')

st.markdown("#### 🏦 Canadian bank qualification · Five core measures")
st.caption("CMHC 39% GDS / 44% TDS planning benchmarks. OSFI 4.5× LTI is a portfolio-monitoring threshold, **not** an individual approval cap.")
a,b,c,d,e=st.columns(5)
a.metric("GDS",f"{h['gds']:.1%}",delta=f"{(x.max_gds-h['gds'])*100:+.1f} pp room",delta_color="normal")
b.metric("TDS",f"{h['tds']:.1%}",delta=f"{(x.max_tds-h['tds'])*100:+.1f} pp room",delta_color="normal")
c.metric("LTV",f"{h['ltv']:.1%}")
d.metric("LTI",f"{h['lti']:.2f}×")
e.metric("Stress-test rate",f"{h['qualifying_rate']:.2%}")
st.caption(f"Contract payment {fmt(h['monthly_mortgage'])}/mo · Qualifying payment {fmt(h['qualifying_mortgage'])}/mo · Qualifying housing cost {fmt(h['qualifying_housing'])}/mo")
with st.expander("Bank ratios · Definitions, formulas and interpretation"):
    st.markdown("""
- **GDS** = (stress-tested mortgage + property tax + heating + 50% condo fees) / gross monthly income. CMHC benchmark **39%**.
- **TDS** = (GDS housing-cost numerator + other monthly debt payments) / gross monthly income. CMHC benchmark **44%**.
- **LTV** = mortgage principal including any financed default-insurance premium / purchase price. It measures leverage; this model's figure can differ from the lender's base-loan LTV.
- **LTI** = mortgage principal / gross annual income. OSFI's **4.5×** threshold is a portfolio-level concentration measure for uninsured mortgages, **not a fixed personal borrowing limit**.
- **Stress test** = max(contract interest rate + 2 percentage points, 5.25%). Used for qualifying payments rather than actual contract payments.
- **Debt-to-income (DTI)** is ambiguous across jurisdictions: monthly debt-service DTI overlaps TDS; balance-to-income DTI is a different measure. We use explicit TDS and LTI to avoid duplication.
""")
    st.caption("Sources: [CMHC debt service](https://www.cmhc-schl.gc.ca/professionals/project-funding-and-mortgage-financing/mortgage-loan-insurance/calculating-gds-tds) · [OSFI stress test](https://www.osfi-bsif.gc.ca/en/supervision/financial-institutions/banks/minimum-qualifying-rate-uninsured-mortgages) · [OSFI LTI](https://www.osfi-bsif.gc.ca/en/supervision/financial-institutions/banks/loan-income-limits-uninsured-mortgage-portfolios). Screening only.")

st.markdown("#### 📚 Financial terminology · What the ratios mean")
with st.container(border=True):
    st.markdown("**GDS — Gross Debt Service Ratio**: qualifying housing costs as a percentage of gross monthly income. Lower GDS generally leaves more gross income for non-housing expenses.")
    st.markdown("**TDS — Total Debt Service Ratio**: qualifying housing costs plus recurring debt payments as a percentage of gross monthly income. It helps screen overall debt burden.")
    st.markdown("**LTV — Loan-to-Value Ratio**: mortgage principal divided by purchase price. Higher LTV generally means less initial equity.")
    st.markdown("**Cash to Close**: down payment plus estimated one-time closing costs. **Monthly Surplus**: take-home income less modeled recurring costs and debt payments.")
    st.caption("The qualification ratios use a stress-tested mortgage payment; they differ from actual monthly cash flow. Thresholds and eligible expenses vary by lender.")
