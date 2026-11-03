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
st.title("Risk & Stress Testing")
st.caption("🟢 Resilient → 🟠 Reserve pressure → 🔴 Cash shortfall. Stress states are determined by modeled cash balances and reserve thresholds, not personal emotional wellbeing.")
st.caption("Shared property, income and expense inputs · British Columbia · CAD")
st.markdown('#### Renewal & emergency liquidity')

a,b,c=st.columns(3)
ry=a.slider('Renewal year',1,10,5,key='risk_ry')
rr=b.slider('Renewal rate (%)',0.0,12.0,6.5,.25,key='risk_rr')/100
unemployment=c.slider('Months without employment income',0,24,6,key='risk_unemployment')
d,e,f=st.columns(3)
start=d.slider('Income disruption starts (month)',1,36,7,key='risk_start')
assessment=e.number_input('Special assessment',0,1000000,10000,1000,key='risk_assessment')
amonth=f.slider('Assessment month',1,60,9,key='risk_amonth')
sx=replace(x,renewal_year=ry,renewal_rate=rr,unemployment_start=start,
           unemployment_months=unemployment,assessment_amount=assessment,assessment_month=amonth)
rn=renewal(sx);metric_row([('Renewal payment',fmt(rn['renewal_payment'])),('Payment change',fmt(rn['monthly_increase'])),('Renewal principal',fmt(rn['balance_at_renewal']))])
explain('Mortgage renewal',r'B_k=L(1+r_m)^k-M\frac{(1+r_m)^k-1}{r_m}',
    'Calculate remaining principal at renewal, then re-amortize over the remaining months using the scenario renewal rate.')
cf=pd.DataFrame(cashflow(sx));fig=go.Figure()
fig.add_trace(go.Scatter(x=cf.month,y=cf.cash_balance,name='Cash balance',mode='lines'))
fig.add_hline(y=sx.reserve_floor,line_dash='dash',annotation_text='Reserve floor')
fig.update_layout(title='Emergency liquidity trajectory',xaxis_title='Month',yaxis_title='CAD',height=360)
st.plotly_chart(fig,use_container_width=True)
min_cash=float(cf['cash_balance'].min()); end_cash=float(cf['cash_balance'].iloc[-1]); below=int(cf['below_reserve'].sum())
st.markdown("#### Financial resilience · Visual risk indicator")
first_negative=cf.loc[cf["cash_balance"]<0,"month"]
first_below=cf.loc[cf["cash_balance"]<sx.reserve_floor,"month"]
if len(first_negative):
    st.error(f"🔴 🥵 Cash exhausted · first negative balance in month {int(first_negative.iloc[0])}. The modeled scenario requires additional funding.")
elif len(first_below):
    st.warning(f"🟠 😰 Reserve under pressure · first month below your {fmt(sx.reserve_floor)} target: month {int(first_below.iloc[0])}.")
else:
    st.success(f"🟢 🙂 Reserve maintained · projected cash stays above {fmt(sx.reserve_floor)} across {len(cf)} months.")
a1,a2,a3=st.columns(3)
a1.metric("Lowest projected cash",fmt(min_cash))
a2.metric("Months below reserve",f"{below} / {len(cf)}")
a3.metric("Cash exhaustion",f"Month {int(first_negative.iloc[0])}" if len(first_negative) else "Not reached")
st.caption("Indicators reflect only the modeled income, costs and shocks; they do not measure personal wellbeing.")
insight('Emergency liquidity',
    f'The projected cash balance ends at {fmt(end_cash)} and reaches a low of {fmt(min_cash)}. '
    f'The balance falls below the selected reserve floor in {below} of {len(cf)} modeled months.',
    'The line shows how renewal, income disruption and a one-time special assessment affect available cash.',
    'A positive final balance does not rule out a temporary liquidity shortfall.')
explain('Liquidity runway and shocks',r'Cash_t=Cash_{t-1}+Income_t-Housing_t-Living_t-Debt_t-Assessment_t',
    'Income disruption replaces take-home income with the specified scenario amount (zero by default). A one-time special assessment is charged in its selected month.')
st.markdown('#### Property price × mortgage rate sensitivity')
hm=pd.DataFrame(heatmap(x));p=hm.pivot(index='price',columns='rate',values='monthly_surplus')
fig=px.imshow(p.values,x=[f'{r:.1%}' for r in p.columns],y=[fmt(v) for v in p.index],
              labels={'x':'Mortgage rate','y':'Property price','color':'Monthly surplus'},
              color_continuous_scale='RdYlGn',color_continuous_midpoint=0,aspect='auto')
st.plotly_chart(fig,use_container_width=True)
viable=hm[hm['monthly_surplus']>=0]
total=len(hm)
best=hm.loc[hm['monthly_surplus'].idxmax()]
worst=hm.loc[hm['monthly_surplus'].idxmin()]
st.markdown('**Scenario interpretation**')
st.write(f"{len(viable)} of {total} tested combinations ({len(viable)/total:.0%}) have non-negative monthly cash flow. "
         f"The modeled monthly surplus ranges from {fmt(worst['monthly_surplus'])} to {fmt(best['monthly_surplus'])}.")
at_price=hm.iloc[(hm['price']-x.price).abs().argsort()[:len(hm['rate'].unique())]]
if not at_price.empty:
    st.caption('The heatmap tests monthly cash flow, not bank mortgage qualification; GDS/TDS and closing liquidity must also be considered.')
baseline=float(h['monthly_surplus'])
viable_rate=hm.loc[(hm['price']-x.price).abs().idxmin(),'rate']
insight('Price and interest-rate sensitivity',
    f'At the selected inputs, estimated monthly surplus is {fmt(baseline)}. '
    f'Across the {total} price/rate combinations, {len(viable)} ({len(viable)/total:.0%}) show non-negative monthly cash flow.',
    f'The lowest modeled surplus is {fmt(worst["monthly_surplus"])} at {fmt(worst["price"])} and {worst["rate"]:.2%} interest; '
    f'the highest is {fmt(best["monthly_surplus"])} at {fmt(best["price"])} and {best["rate"]:.2%}.',
    'Non-negative monthly cash flow does not establish mortgage approval or sufficient closing liquidity.')
explain('Affordability sensitivity',r'S(P,i)=I_{net}-Mortgage(P,i)-OtherCosts',
    'Each cell recomputes housing cost and monthly surplus at the selected price and rate while holding other assumptions constant.')
st.markdown('#### Down payment scenarios')
dc=down_comparison(x)
st.dataframe(pd.DataFrame([{'Down %':f"{z['down_pct']:.0%}",'Monthly mortgage':z.get('monthly_mortgage'),
    'Cash after purchase':z.get('cash_after_purchase'),'Insurance premium':z.get('insurance_premium'),
    'Meets constraints':z.get('affordable',False)} for z in dc]),hide_index=True,use_container_width=True)
explain('Down payment comparison',r'Loan=P-D+InsurancePremium',
    'Recalculate principal, default insurance, payment and remaining cash at 10%, 20%, 30% and 40% down.')


# Additional downside diagnostics: simple, transparent static stress metrics.
st.markdown("#### 🛡️ Additional downside scenarios")
sc1,sc2,sc3=st.columns(3)
price_decline=sc1.slider("Property value decline (%)",0,50,20,5,key="risk_price_decline")/100
income_reduction=sc2.slider("Take-home income reduction (%)",0,100,25,5,key="risk_income_reduction")/100
investment_drawdown=sc3.slider("Liquid-asset market drawdown (%)",0,80,30,5,key="risk_investment_decline")/100
from stress_extensions import downside_summary
summary=downside_summary(x,price_decline,income_reduction,investment_drawdown)
metric_row([("🏠 Stressed home equity",fmt(summary["stressed_equity"])),
            ("📉 Stressed LTV",f'{summary["stressed_ltv"]:.1%}'),
            ("💸 Reduced-income surplus",fmt(summary["reduced_income_surplus"])),
            ("🪙 Stressed post-closing liquid assets",fmt(summary["stressed_cash"]))])
fig=go.Figure()
fig.add_trace(go.Bar(name="Baseline",x=["Home equity","Post-closing liquid assets"],y=[summary["baseline_equity"],summary["baseline_cash"]],marker_color="#318b8d"))
fig.add_trace(go.Bar(name="Stressed",x=["Home equity","Post-closing liquid assets"],y=[summary["stressed_equity"],summary["stressed_cash"]],marker_color="#ca7771"))
fig.update_layout(barmode="group",height=330,title="Asset downside · Baseline vs stressed",yaxis_title="CAD")
st.plotly_chart(fig,use_container_width=True)
st.caption("Illustrative independent stress adjustments; this is not a joint probability model. The market drawdown is applied to post-closing liquid assets as a conservative proxy.")
st.markdown("#### 🧩 Combined downside · Joint scenario")
st.caption("Apply the selected home-price, income and liquid-asset shocks together. This is a sensitivity test, not a probability estimate.")
combined_cash=summary['stressed_cash']
combined_surplus=summary['reduced_income_surplus']
combined_equity=summary['stressed_equity']
with st.container(border=True):
    q1,q2,q3=st.columns(3)
    q1.metric("🏠 Home equity after shock",fmt(combined_equity))
    q2.metric("💧 Liquid assets after shock",fmt(combined_cash))
    q3.metric("💸 Monthly surplus after income shock",fmt(combined_surplus))
    if combined_cash<x.reserve_floor or combined_surplus<0:
        st.warning("Combined stress exposes a reserve or cash-flow constraint. Review housing cost, emergency savings and investment concentration.")
    else:
        st.success("Modeled reserve and monthly cash flow remain nonnegative under the selected joint shocks.")
    st.caption("Liquid-asset shock is applied to a simplified post-closing balance, not a separately identified investment portfolio.")
