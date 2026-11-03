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
from rental_assumptions import implied_rental_property_value, all_in_rent
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
st.title("Rent vs Buy")
st.caption("Shared property, income and expense inputs · British Columbia · CAD")
acash=st.session_state.get("asset_cash",300000)
invest=st.session_state.get("asset_invest",550000)
asset_down=st.session_state.get("asset_down",35)/100
eligible=st.session_state.get("asset_eligible",100)/100
ratio=st.session_state.get("asset_ratio",1.0)
reserve_target=st.session_state.get("asset_reserve",60000)
drawdown=st.session_state.get("asset_drawdown",25)/100
ap=AssetProfile(acash,invest,eligible,asset_down,ratio,reserve_target,drawdown)
st.subheader('Rent vs. Buy · Cash flow and net worth')
st.caption('Same starting wealth and income; two financial paths. Owner-occupied housing comparison, not rental-property investment underwriting.')
finance=st.radio('Mortgage pathway for buying', ['Income-based','Asset-based'],horizontal=True,key='rent_finance')
a,b,c=st.columns(3)
rent_settings=st.session_state.get("applied_rent",{"base":1800,"yield":.055,"utilities":0,"internet":0,"other":0})
rent=all_in_rent(rent_settings["base"],rent_settings["utilities"],rent_settings["internet"],rent_settings["other"])
a.metric("Comparable monthly rent (shared)",fmt(rent))
years=b.slider('Comparison horizon (years)',1,30,15,key='rent_years')
invest_return=c.slider('Annual investment return (%)',-20.0,20.0,5.0,.5,key='rent_return')/100
d,e,f=st.columns(3)
appreciation=d.slider('Property appreciation (%)',-10.0,12.0,2.5,.5,key='rent_appreciation')/100
rent_growth=e.slider('Annual rent growth (%)',-5.0,12.0,2.5,.5,key='rent_growth')/100
sale=f.slider('Selling costs (%)',0.0,10.0,4.0,.5,key='rent_selling')/100
with st.expander('Advanced · investment allocation & downside scenarios'):
    invest_fraction=st.slider('Initial invested fraction of liquid assets (%)',0,100,65,5,key='rent_fraction')/100
    if st.session_state.get('rent_shock_year',1)>years:
        st.session_state['rent_shock_year']=years
    shock_year=st.slider('Shock year',1,years,min(3,years),key='rent_shock_year')
    price_shock=st.slider('One-time home-price decline (%)',0,50,0,5,key='rent_price_shock')/100
    invest_shock=st.slider('One-time investment decline (%)',0,60,0,5,key='rent_invest_shock')/100
    ren_rate=st.slider('Renewal rate (%)',0.0,12.0,6.5,.25,key='rent_renewal_rate')/100
st.markdown("#### 🏠 Property-value comparability")
rental_value=implied_rental_property_value(rent_settings["base"],rent_settings["yield"])
if rent_settings.get("buy_beds") != rent_settings.get("rent_beds") or abs(rent_settings.get("buy_area",0)-rent_settings.get("rent_area",0))>100:
    st.warning(f"⚖️ Different housing quality: buy {rent_settings.get('buy_beds','?')} bed / {rent_settings.get('buy_area','?')} sq ft versus rent {rent_settings.get('rent_beds','?')} bed / {rent_settings.get('rent_area','?')} sq ft. A lower rent may reflect a smaller home; do not interpret the result as like-for-like.")
else:
    st.caption("Bedroom count and floor area are broadly aligned; neighborhood, condition and amenities still require verification.")
cva,cvb,cvc=st.columns(3)
cva.metric("Rental home · implied value",fmt(rental_value))
cvb.metric("Purchase home · asking price",fmt(x.price))
cvc.metric("Value difference",fmt(x.price-rental_value))
st.caption("Rental implied value = 12 × base monthly rent ÷ assumed gross yield. This does not establish equivalent living quality. Verify size, bedrooms, location, condition and amenities before interpreting the model.")
ex1,ex2=st.columns(2)
ex1.metric("Buy exterior space (sq ft)",f'{rent_settings.get("buy_exterior",0):,.0f}')
ex2.metric("Rent exterior space (sq ft)",f'{rent_settings.get("rent_exterior",0):,.0f}')
if abs(rent_settings.get("buy_exterior",0)-rent_settings.get("rent_exterior",0))>100:
    st.caption("Outdoor living space differs materially; treat the Rent vs Buy comparison as a lifestyle trade-off, not a strict matched-home comparison.")

cp=Comparison(monthly_rent=rent,renter_insurance=0,years=years,investment_return=invest_return,
    appreciation=appreciation,rent_growth=rent_growth,selling_cost_fraction=sale,
    investment_fraction=invest_fraction,
    shock_year=shock_year,
    price_shock=price_shock,
    investment_shock=invest_shock,
    renewal_rate=ren_rate)
bx=replace(x,down_pct=asset_down,liquid_cash=acash+invest) if finance=='Asset-based' else x
eligible_to_buy=True
if finance=='Asset-based':
    try:eligible_to_buy=asset_financing(x,ap)['asset_based_feasible']
    except ValueError:eligible_to_buy=False
try:
    if not eligible_to_buy:st.warning('Asset-based application-time eligibility is not met. The comparison is hypothetical, not financeable under these inputs.')
    rows=simulate(bx,cp,"asset" if finance=="Asset-based" else "income");df=pd.DataFrame(rows);last=rows[-1]
    st.markdown("#### ⚖️ Scenario decision · Modeled net worth")
    diff_final=float(last['net_worth_difference'])
    margin=max(1000,0.01*max(abs(float(last['buy_net_worth'])),abs(float(last['rent_net_worth']))))
    if abs(diff_final)<=margin:
        st.info("😐 Close result · Buying and renting produce similar modeled terminal net worth. Review liquidity, housing quality and sensitivity assumptions.")
    elif diff_final>0:
        st.success(f"🏡 Buying leads by {fmt(diff_final)} in modeled year-{years} net worth. This reflects home equity and assumed appreciation; compare upfront cash needs and downside risk.")
    else:
        st.info(f"🔑 Renting leads by {fmt(-diff_final)} in modeled year-{years} net worth. Retained investable capital and housing costs contribute; review rent growth and investment-return risk.")
    st.caption("Conditional scenario conclusion, not a recommendation or probability forecast. Renter insurance is set to zero separately here; include it in shared Other renter costs if not already included in the quoted rent.")
    metric_row([('Buy net worth' ,fmt(last['buy_net_worth'])),('Rent net worth',fmt(last['rent_net_worth'])),
                ('Buy − Rent',fmt(last['net_worth_difference'])),('Sustained crossover',str(break_even_year(rows) or 'None')+' years' if break_even_year(rows) else 'None')])
    st.markdown('#### Decision intelligence')
    diagnostic_cards(rent_buy_diagnostics(rows,cp))
    audit_panel(audit_rent_vs_buy(bx,cp,rows))
    st.markdown('#### Compare saved scenarios')
    if st.button('Save current scenario',key='save_rent_snapshot'):
        saved=st.session_state.setdefault('rent_snapshots',{})
        label=f'Scenario {len(saved)+1}'
        saved[label]={k:float(last[k]) for k in ('buy_net_worth','rent_net_worth','net_worth_difference')}
        st.success(f'{label} saved for this browser session.')
    if st.session_state.get('rent_snapshots'):
        st.dataframe(pd.DataFrame(compare_snapshots(st.session_state['rent_snapshots'])),hide_index=True,use_container_width=True)
        if st.button('Clear saved scenarios',key='clear_rent_snapshots'):
            st.session_state.pop('rent_snapshots',None)
            st.rerun()
    st.caption('Snapshots are stored in session memory only and disappear when the session ends.')
    st.markdown('#### 1. Cumulative housing cash spending')
    fig=go.Figure()
    for key,label in [('buy_cumulative_housing_cashflow','Buy'),('rent_cumulative_housing_cashflow','Rent')]:
        fig.add_trace(go.Scatter(x=df.year,y=df[key],name=label,mode='lines'))
    fig.update_layout(xaxis_title='Years',yaxis_title='Cumulative housing cash flow (CAD)',height=370)
    st.plotly_chart(fig,use_container_width=True)
    buy_spend=-float(last['buy_cumulative_housing_cashflow']);rent_spend=-float(last['rent_cumulative_housing_cashflow'])
    insight('Cumulative housing cash spending',
        f'Over {years} years, modeled housing-related cash outflows total {fmt(buy_spend)} for buying versus {fmt(rent_spend)} for renting.',
        f'The difference is {fmt(abs(buy_spend-rent_spend))} in cumulative cash outflows. The buy path includes down payment and closing costs; the rent path does not.',
        'A down payment and mortgage principal repayments also create home equity. This chart alone cannot determine which path creates more wealth.')
    explain('Cumulative housing cash flow',r'CF_{Buy}=-Down-Closing-\sum_{t=1}^{T}(Mortgage_t+OwnerCosts_t)',
        'Rent uses the negative sum of rent and renter insurance. Buy includes upfront purchase cash and ongoing housing costs. This is housing cash spending, not total household cash balance.',
        'Loan principal is a cash outflow but also increases home equity; net worth captures that separately.')
    st.markdown('#### 2. Projected net worth')
    fig=go.Figure()
    for key,label in [('buy_net_worth','Buy'),('rent_net_worth','Rent')]:
        fig.add_trace(go.Scatter(x=df.year,y=df[key],name=label,mode='lines'))
    fig.update_layout(xaxis_title='Years',yaxis_title='Estimated net worth (CAD)',height=390)
    st.plotly_chart(fig,use_container_width=True)
    diff=float(last['net_worth_difference']); pct=abs(diff)/max(1,abs(float(last['rent_net_worth'])))*100
    insight('Projected net worth',
        f'At year {years}, buying produces {fmt(last["buy_net_worth"])} in modeled net worth and renting {fmt(last["rent_net_worth"])}. '
        + ('Buying is ahead' if diff>0 else 'Renting is ahead' if diff<0 else 'The paths are tied')
        + f' by {fmt(abs(diff))} ({pct:.1f}% of rent-path net worth).',
        'The projection combines housing equity, financial assets and cash after accounting for mortgage balance and estimated selling costs.',
        'The outcome depends on assumed appreciation, investment returns, rental inflation and renewal rates; it is not a forecast.')
    explain('Net worth and home equity',r'NW_{Buy}=V(1-s)-B+Cash+Investments',
        'V is market home value, s is estimated selling-cost fraction and B is remaining mortgage principal. Rent net worth is cash plus investments. Interest reduces cash flow and is not subtracted twice.',
        'Excludes personal income taxes, investment capital gains tax, transaction-specific taxes and appreciation uncertainty.')
    st.markdown('#### Asset composition over time')
    fig=go.Figure()
    for key,label,color in [('home_equity','Home equity','#357d8d'),('buy_investments','Buy investments','#6582b6'),('rent_investments','Rent investments','#d7a450')]:
        fig.add_trace(go.Scatter(x=df.year,y=df[key],name=label,line=dict(color=color)))
    st.plotly_chart(chart_style(fig,'Home equity & investment assets'),use_container_width=True)
    insight('Asset composition',
        f'By year {years}, home equity is {fmt(last["home_equity"])}, buy-path investments are {fmt(last["buy_investments"])}, '
        f'and rent-path investments are {fmt(last["rent_investments"])}.',
        'Home equity is property value less outstanding mortgage principal; investment balances reflect each path’s available capital and monthly savings.',
        'These series are components, not totals. Home equity is less liquid than cash or publicly traded investments.')
    explain('Asset composition',r'Equity_t=Value_t-Balance_t',
        'Home equity reflects property value minus remaining principal. Investments include initial assets and net monthly savings invested after preserving a cash buffer. Both choices start with the same total liquid assets.')
    difference=last['net_worth_difference']
    leader='buying' if difference>0 else 'renting' if difference<0 else 'neither option'
    st.markdown('**Scenario interpretation**')
    st.write(f"At year {cp.years}, the modeled terminal net-worth difference (buy minus rent) is {fmt(difference)}. "
             f"Under these assumptions, {leader} has the higher modeled net worth. "
             f"This is not a recommendation: liquidity, housing stability, transaction costs and market uncertainty also matter.")
    st.markdown('#### 3. Break-even heatmap · Buy net worth − Rent net worth')
    if st.checkbox('Calculate 25-scenario break-even heatmap',value=False,key='rent_grid_on'):
        with st.spinner('Simulating 25 scenarios...'):grid=pd.DataFrame(break_even_grid(bx,cp))
        pivot=grid.pivot(index='investment_return',columns='appreciation',values='difference')
        fig=px.imshow(pivot.values,x=[f'{v:.0%}' for v in pivot.columns],y=[f'{v:.0%}' for v in pivot.index],
            labels={'x':'Annual home appreciation','y':'Annual investment return','color':'Buy − Rent (CAD)'},
            color_continuous_scale='RdYlGn',color_continuous_midpoint=0,aspect='auto')
        st.plotly_chart(fig,use_container_width=True)
        positives=int((grid['difference']>0).sum()); negatives=int((grid['difference']<0).sum())
        st.write(f'Across 25 tested return/appreciation combinations, buying has higher terminal net worth in {positives} scenarios and renting in {negatives}; the remainder are tied.')
        insight('Break-even sensitivity',
            f'Buying leads in {positives} of {len(grid)} combinations; renting leads in {negatives}.',
            'Each cell changes annual property appreciation and investment returns while keeping the other selected assumptions fixed. The zero boundary is the modeled break-even region.',
            'The tested scenarios are not equally likely and their count is not a probability of buying or renting outperforming.')
    explain('Break-even sensitivity',r'\Delta NW(g,r)=NW_{Buy}(g,r)-NW_{Rent}(g,r)',
        'Re-run both paths at each home appreciation and investment return pair. Positive cells favor buying on modeled terminal net worth; negative cells favor renting.',
        'A crossover is not a guarantee and can reverse under different assumptions.')
    st.markdown('#### 4. Downside and liquidity diagnostics')
    metric_row([('Buy cash at horizon',fmt(last['buy_cash'])),('Rent cash at horizon',fmt(last['rent_cash'])),
                ('Home equity',fmt(last['home_equity'])),('Mortgage outstanding',fmt(last['mortgage_balance']))])
    min_buy_cash=float(df['buy_cash'].min());min_rent_cash=float(df['rent_cash'].min())
    insight('Downside and liquidity',
        f'The lowest modeled cash balance is {fmt(min_buy_cash)} for buying and {fmt(min_rent_cash)} for renting. '
        f'At the horizon, the mortgage balance is {fmt(last["mortgage_balance"])}.',
        'Adjust the shock year, property-price decline, investment decline and renewal rate above to test how much financial flexibility remains.',
        'Cash balances near zero can hide investment liquidation; negative balances can signal an unfunded deficit.')
    explain('Downside stress and liquidity',r'V_{shock}=V(1-d_h),\quad I_{shock}=I(1-d_i)',
        'Apply one-time shocks in the selected year, continue monthly compounding, and use investments to cover negative cash balances.',
        'Negative cash after investments are exhausted signals an unfunded cash shortfall, not a feasible borrowing plan.')
except ValueError as err:st.warning(f'Cannot run comparison: {err}')

