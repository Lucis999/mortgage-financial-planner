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
st.title("Asset & Liquidity")
st.caption("Shared property, income and expense inputs · British Columbia · CAD")
st.subheader('Asset-supported financing & liquidity planning')
st.caption('Illustrative lender-specific 35% minimum down and application-time 1:1 eligible-asset test. No continuing asset-balance covenant is modeled.')
a,b,c=st.columns(3)
acash=a.number_input('Cash / deposits',0,10000000,300000,10000,key='asset_cash')
invest=b.number_input('Market investments',0,10000000,550000,10000,key='asset_invest')
asset_down=c.slider('Asset-based down payment (%)',35,80,35,5,key='asset_down')/100
d,e,f=st.columns(3)
eligible=d.slider('Recognized investment fraction (%)',0,100,100,5,key='asset_eligible')/100
ratio=e.slider('Eligible assets : loan ratio',0.25,2.0,1.0,.25,key='asset_ratio')
reserve_target=f.number_input('Target post-closing reserve',0,10000000,60000,5000,key='asset_reserve')
drawdown=st.slider('Investment drawdown stress (%)',0,60,25,5,key='asset_drawdown')/100
ap=AssetProfile(acash,invest,eligible,asset_down,ratio,reserve_target,drawdown)
try:
    ah=asset_financing(x,ap)
    metric_row([('Required mortgage',fmt(ah['required_loan'])),('Asset-supported limit',fmt(ah['asset_supported_loan_limit'])),
                ('Financing gap',fmt(ah['financing_gap'])),('Assets after closing',fmt(ah['remaining_assets']))])
    from comfort_ui import comfort_level,render_comfort
    asset_buffer=ah['remaining_assets']-ap.reserve_target
    asset_gap=ah['financing_gap']
    asset_level=comfort_level(h['monthly_surplus'],asset_buffer,h['monthly_housing']/max(1,x.net_monthly_income))
    if asset_gap>0:asset_level=0
    render_comfort(asset_level,"Asset & liquidity resilience · Seven-level spectrum",
        f"Financing gap {fmt(asset_gap)} · Assets above reserve {fmt(asset_buffer)} · Monthly surplus {fmt(h['monthly_surplus'])}. A financing gap forces the critical category.")
    if ah['asset_based_feasible']:
        st.success('Illustrative asset financing and reserve tests pass.')
    else:
        st.warning('Financing or liquidity condition is not met under the selected assumptions.')
    explain('Application-time asset-based eligibility',r'L_{eligible}=q\max(0,C+\alpha I-D-ClosingCosts)',
        'C is cash, I is investments, α is the lender-recognized fraction, and q is the illustrative loan-to-eligible-assets ratio. Required mortgage must not exceed this limit.',
        'This is a configurable representation of a specific product, not a universal Canadian high-net-worth mortgage rule.')
    metric_row([('Recognized assets after closing',fmt(ah['eligible_assets_after_closing'])),
                ('Target reserve',fmt(ap.reserve_target)),('Stressed assets (conservative)',fmt(ah['stressed_remaining_assets']))])
    explain('Asset drawdown and reserve',r'A_{stress}=A_{after}-I\times Drawdown',
        'Subtract a selected fraction of the original investment portfolio from remaining assets as a conservative stress proxy.',
        'This is not a post-approval bank covenant; actual portfolio composition and liquidation order matter.')
    st.markdown('#### Liquidity & capital allocation')
    down_cash=ah['down']+ah['closing_costs']
    allocation=pd.DataFrame({'Category':['Down payment & closing','Post-closing assets'],
        'CAD':[down_cash,max(0,ah['remaining_assets'])]})
    left,right=st.columns([1,1.3])
    with left:
        fig=px.pie(allocation,names='Category',values='CAD',hole=.58,
                   color_discrete_sequence=['#e7a64d','#347d93'])
        fig.update_layout(height=340,margin=dict(l=5,r=5,t=30,b=5),showlegend=True,
                          legend=dict(orientation='h',y=-.05))
        st.plotly_chart(fig,use_container_width=True)
    with right:
        fig=go.Figure()
        fig.add_trace(go.Bar(name='Required mortgage',x=['Financing'],y=[ah['required_loan']],marker_color='#3c7098'))
        fig.add_trace(go.Bar(name='Asset-supported limit',x=['Financing'],y=[ah['asset_supported_loan_limit']],marker_color='#2f9e84'))
        fig.add_trace(go.Bar(name='Post-closing assets',x=['Liquidity'],y=[max(0,ah['remaining_assets'])],marker_color='#e0a452'))
        fig.add_trace(go.Bar(name='Reserve target',x=['Liquidity'],y=[ap.reserve_target],marker_color='#c16c71'))
        fig.update_layout(barmode='group')
        st.plotly_chart(chart_style(fig,'Financing capacity & liquidity'),use_container_width=True)
    coverage=ah['asset_supported_loan_limit']-ah['required_loan']
    insight('Financing and capital allocation',
        f'The illustrative asset-supported limit is {fmt(ah["asset_supported_loan_limit"])} against a required mortgage of {fmt(ah["required_loan"])}. '
        + (f'The modeled funding gap is {fmt(ah["financing_gap"])}.' if ah['financing_gap']>0 else f'The indicative financing headroom is {fmt(max(0,coverage))}.'),
        f'After the down payment and closing costs, {fmt(ah["remaining_assets"])} remains, compared with a reserve target of {fmt(ap.reserve_target)}.',
        'The 1:1 asset test applies only at application in this illustrative product; bank underwriting can differ.')
    explain('Asset allocation and financing capacity',r'A_{remaining}=Cash+Investments-Down-Closing',
        'The allocation chart separates capital spent at closing from assets retained. The bars compare the required mortgage with the assumed application-time 1:1 financing limit, and remaining assets with the selected reserve target.')
    st.markdown('#### Monthly cash flow & financial asset trajectory')
    st.caption('After approval, the bank does not impose a continuing asset-balance test in this scenario. The following projection is a personal financial risk illustration, not a lender requirement.')
    a1,a2,a3=st.columns(3)
    proj_years=a1.slider('Projection years',1,30,15,key='asset_projection_years')
    proj_return=a2.slider('Annual investment return (%)',-100.0,100.0,5.0,1.0,key='asset_projection_return')/100
    proj_invest=a3.slider('Invested share after closing (%)',0,100,65,5,key='asset_projection_fraction')/100
    st.caption("Invested share after closing: the intended fraction of remaining liquid assets held in market investments rather than cash. The actual trajectory model may rebalance toward the cash reserve target; this control sets the initial post-closing allocation; subsequent transfers can change the mix to maintain your cash reserve.")
    if proj_return<=-.5 or proj_return>=.5:
        st.warning("Extreme return scenario: a constant annual return of this magnitude is a stress assumption, not a realistic central forecast.")
    asset_x=replace(x,down_pct=asset_down,liquid_cash=acash+invest)
    projection=ProjectionSettings(years=proj_years,investment_return=proj_return,
        investment_drawdown=ap.investment_drawdown,shock_year=min(3,proj_years),
        renewal_rate=x.renewal_rate,cash_target=reserve_target,invested_share=proj_invest)
    if ah['remaining_assets']>=0:
        proj=pd.DataFrame(project_assets(x,ap,projection))
        c1,c2=st.columns(2)
        with c1:
            fig=go.Figure()
            fig.add_trace(go.Scatter(x=proj.year,y=proj.net_cashflow,name='Monthly surplus',line=dict(color='#397a95')))
            fig.add_hline(y=0,line_dash='dash',line_color='#c16c71')
            st.plotly_chart(chart_style(fig,'Monthly household cash flow'),use_container_width=True)
        with c2:
            fig=go.Figure()
            for k,label,color in [('cash','Cash reserve','#2d8c82'),('investments','Investments','#5974b8')]:
                fig.add_trace(go.Scatter(x=proj.year,y=proj[k],name=label,line=dict(color=color)))
            fig.add_hline(y=reserve_target,line_dash='dot',line_color='#c16c71',annotation_text='Cash target')
            st.plotly_chart(chart_style(fig,'Financial assets over time'),use_container_width=True)
        start_surplus=float(proj['net_cashflow'].iloc[0]);end_surplus=float(proj['net_cashflow'].iloc[-1])
        start_assets=float(proj['total_financial_assets'].iloc[0]);end_assets=float(proj['total_financial_assets'].iloc[-1])
        min_assets=float(proj['total_financial_assets'].min())
        insight('Monthly cash flow',
            f'Modeled monthly surplus changes from {fmt(start_surplus)} to {fmt(end_surplus)} over {proj_years} years.',
            'The dashed zero line marks months when regular expenses exceed household income. Renewal can change the monthly payment.',
            'Positive monthly cash flow does not guarantee sufficient cash reserves during a market decline.')
        insight('Financial assets over time',
            f'Cash plus investments change from {fmt(start_assets)} after the first modeled month to {fmt(end_assets)}; the minimum is {fmt(min_assets)}.',
            'Cash and market investments are tracked separately. Investments may be liquidated to cover deficits, while excess cash above the target is invested.',
            'Investment returns are assumptions, not forecasts.')
        st.markdown('#### Financial decision insights')
        diagnostic_cards(asset_diagnostics(proj.to_dict('records'),reserve_target))
        audit_panel(audit_asset_trajectory(x,ap,projection,proj.to_dict('records')))
        st.markdown('#### Liquidity risk diagnostics')
        below=int((proj['cash']<reserve_target-1e-6).sum())
        forced=int((proj['liquidation']>1e-6).sum())
        unfunded=int((proj['unfunded_cash']>1e-6).sum())
        metric_row([('Minimum cash',fmt(float(proj['cash'].min()))),
            ('Months below target',f'{below} / {len(proj)}'),
            ('Months selling investments',str(forced)),
            ('Unfunded months',str(unfunded))])
        st.markdown("**💧 Reserve safety · Cash and investments**")
        reserve_fig=go.Figure()
        reserve_fig.add_trace(go.Scatter(x=proj.year,y=proj.cash,name="Cash balance",line=dict(color="#278c84",width=3)))
        reserve_fig.add_trace(go.Scatter(x=proj.year,y=proj.investments,name="Investments",line=dict(color="#657bb9",width=2)))
        reserve_fig.add_hline(y=reserve_target,line_dash="dash",line_color="#bd7a63",annotation_text="Minimum reserve")
        st.plotly_chart(chart_style(reserve_fig,"Liquidity sustainability · balances vs reserve"),use_container_width=True)
        st.markdown("**🔁 Investment transfers · contributions and withdrawals**")
        yearly=proj.assign(period=((proj.month-1)//12+1)).groupby("period",as_index=False)[["liquidation","contribution"]].sum()
        total_transfers=float(yearly[["liquidation","contribution"]].sum().sum())
        if total_transfers<=1e-6:
            st.info("No investment transfers required under these assumptions. Monthly cash stays within the modeled rebalancing rules.")
        else:
            transfer_fig=go.Figure()
            transfer_fig.add_trace(go.Bar(x=yearly.period,y=yearly.liquidation,name="Withdrawals",marker_color="#b86b66"))
            transfer_fig.add_trace(go.Bar(x=yearly.period,y=yearly.contribution,name="Contributions",marker_color="#2d8c82"))
            transfer_fig.update_layout(barmode="group",xaxis_title="Projection year",xaxis=dict(dtick=1),yaxis=dict(rangemode="tozero"))
            st.plotly_chart(chart_style(transfer_fig,"Annual investment transfers · CAD per year"),use_container_width=True)
            st.caption("Annual totals are aggregated from the monthly ledger. Hover to inspect values; returns and market gains are not counted as contributions.")
        if unfunded:
            st.error(f'Liquidity warning: {unfunded} months have an unfunded cash shortfall even after available investments are used.')
        elif below:
            st.warning(f'Reserve caution: cash is below the selected {fmt(reserve_target)} target in {below} modeled months; {forced} months require investment sales.')
        else:
            st.success('Modeled cash stays at or above the reserve target; no unfunded shortfall is detected.')
        insight('Liquidity and investment transfers',
            f'The projection requires investment withdrawals in {forced} months, and records {below} months below the cash target.',
            f'Total simulated investment withdrawals are {fmt(float(proj["liquidation"].sum()))}; total new contributions are {fmt(float(proj["contribution"].sum()))}.',
            'This is a personal reserve test after mortgage approval, not an ongoing lender asset covenant.')
        explain('Cash/investment ledger and reserve test',
            r'Cash_t=Cash_{t-1}+Income_t-Expenses_t+Sales_t-Contributions_t',
            'At closing, down payment and closing costs are funded from deposits first, then investments. Each month investment returns and any market shock affect investments; cash covers expenses. Investments are sold only when cash becomes negative (not merely when cash is below the target); surplus cash above the target is invested. Loan principal and interest are calculated separately.',
            'No taxes on realized gains, transaction costs, or asset lockups. Cash below target is a caution; negative cash after exhausting investments is an unfunded deficit.')
    else:
        st.warning('Closing cash exceeds available assets; an asset projection cannot be generated.')
    st.caption('Important: the Income-Based calculator uses the sidebar total liquid assets; this asset module uses its own cash and investment inputs.')
except ValueError as err:st.warning(f'Adjust asset inputs: {err}')

