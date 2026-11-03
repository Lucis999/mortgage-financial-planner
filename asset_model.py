"""Illustrative application-time asset-supported financing; NOT lender approval."""
from dataclasses import dataclass
from dataclasses import replace
from model import Inputs, housing

@dataclass(frozen=True)
class AssetProfile:
    cash: float = 300000
    investments: float = 550000
    eligible_investment_fraction: float = 1.0
    down_pct: float = .35
    asset_to_loan_ratio: float = 1.0
    reserve_target: float = 60000
    investment_drawdown: float = .25


def asset_financing(x: Inputs, a: AssetProfile):
    if min(a.cash,a.investments,a.eligible_investment_fraction,a.asset_to_loan_ratio,a.reserve_target,a.investment_drawdown)<0:
        raise ValueError('Asset inputs must be non-negative')
    if not 0 <= a.eligible_investment_fraction <= 1 or not 0 <= a.investment_drawdown <= 1:
        raise ValueError('Fractions must be between zero and one')
    if not .35 <= a.down_pct <= 1:
        raise ValueError('The illustrative asset-based option requires at least 35% down')
    y=replace(x,down_pct=a.down_pct,liquid_cash=a.cash+a.investments)
    h=housing(y)
    # Application-time recognition only. Down payment and closing cash are deducted
    # from eligible assets, with unrecognized investments spent first if needed.
    spend=h['down']+h['closing_costs']
    eligible_before=a.cash+a.investments*a.eligible_investment_fraction
    eligible_after=max(0,eligible_before-spend)
    loan_required=h['mortgage_principal']
    asset_supported=eligible_after*a.asset_to_loan_ratio
    # Cash cannot be assumed to remain intact if spent at closing.
    remaining_total=a.cash+a.investments-spend
    reserve_ok=remaining_total>=a.reserve_target
    finance_ok=loan_required<=asset_supported+1e-7
    stressed_assets=max(0,remaining_total-a.investments*a.investment_drawdown)
    return {**h,'required_loan':loan_required,'eligible_assets_before':eligible_before,
        'eligible_assets_after_closing':eligible_after,'asset_supported_loan_limit':asset_supported,
        'financing_gap':max(0,loan_required-asset_supported),'asset_eligible':finance_ok,
        'remaining_assets':remaining_total,'reserve_ok':reserve_ok,
        'stressed_remaining_assets':stressed_assets,
        'asset_based_feasible':finance_ok and reserve_ok and remaining_total>=0}
