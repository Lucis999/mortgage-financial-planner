"""v1.4: deterministic, explainable insights and risk diagnostics."""
from dataclasses import dataclass
from statistics import mean

@dataclass(frozen=True)
class Diagnostic:
    title: str
    status: str
    observation: str
    significance: str
    next_step: str


def asset_diagnostics(rows, target):
    if not rows:return []
    below=sum(r['cash']<target-0.01 for r in rows)
    unfunded=sum(r['unfunded_cash']>0.01 for r in rows)
    sales=sum(r['liquidation']>0.01 for r in rows)
    mincash=min(r['cash'] for r in rows)
    if unfunded:
        status='Unfunded shortfall'
        meaning=f'{unfunded} month(s) remain underfunded after investment liquidation.'
    elif below:
        status='Below reserve target'
        meaning=f'Cash falls below the selected reserve in {below} of {len(rows)} months.'
    else:
        status='Reserve maintained'
        meaning='Cash stays at or above the selected reserve throughout the projection.'
    return [Diagnostic('Liquidity resilience',status,
        f'Minimum cash ${mincash:,.0f}; investment sales in {sales} month(s).',meaning,
        'Test a lower income, higher renewal rate, or larger market decline.'),
        Diagnostic('Investment reliance','Investment sales' if sales else 'No forced sales',
        f'Total investment sales ${sum(r["liquidation"] for r in rows):,.0f}.',
        'Investment liquidation can reduce future compounding and may create tax or transaction costs not modeled.',
        'Compare different cash reserve targets and investment returns.')]


def rent_buy_diagnostics(rows,c):
    if not rows:return []
    last=rows[-1];diff=last['net_worth_difference'];base=max(abs(last['buy_net_worth']),abs(last['rent_net_worth']),1)
    close=abs(diff)/base<.03
    leader='Buying' if diff>0 else 'Renting' if diff<0 else 'Neither pathway'
    buy_unfunded=sum(r['buy_cash']<-.01 for r in rows)
    rent_unfunded=sum(r['rent_cash']<-.01 for r in rows)
    return [Diagnostic('Long-term wealth comparison','Close outcome' if close else f'{leader} leads',
        f'At year {c.years}, Buy − Rent = ${diff:,.0f} ({abs(diff)/base:.1%} of the larger modeled net worth).',
        'A small terminal difference is sensitive to assumptions; neither outcome is guaranteed.' if close else 'The comparison measures modeled net worth, not quality of life or housing stability.',
        'Change property appreciation, investment return and selling costs to test robustness.'),
        Diagnostic('Liquidity stress','Unfunded months' if buy_unfunded or rent_unfunded else 'No negative cash',
        f'Buy: {buy_unfunded} negative-cash months; Rent: {rent_unfunded} negative-cash months.',
        'Negative cash after available investments are exhausted indicates an infeasible financing path.',
        'Review emergency reserves and cash flow under adverse scenarios.')]


def compare_snapshots(snapshots):
    """Snapshots: label -> {net_worth_difference, buy_net_worth, rent_net_worth}."""
    return [{'Scenario':label,'Buy net worth':d['buy_net_worth'],
             'Rent net worth':d['rent_net_worth'],'Buy − Rent':d['net_worth_difference']}
            for label,d in snapshots.items()]
