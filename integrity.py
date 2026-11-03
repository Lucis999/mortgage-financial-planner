"""v1.3: independent monthly ledger reconciliation; tolerances are CAD."""
from dataclasses import dataclass
from math import isfinite
from model import Inputs, housing
from asset_model import AssetProfile, asset_financing

@dataclass(frozen=True)
class Check:
    name: str
    max_error: float
    passed: bool
    detail: str


def _check(name, errors, detail, tolerance=.02):
    worst=max((abs(v) for v in errors),default=0.0)
    return Check(name,worst,isfinite(worst) and worst<=tolerance,detail)


def audit_rent_vs_buy(x:Inputs,c,rows):
    """Reconstruct each ledger from independent starting balances and flows."""
    h=housing(x)
    initial=x.liquid_cash
    rent_inv=initial*c.investment_fraction
    rent_cash=initial-rent_inv
    buy_inv=min(rent_inv,h['cash_after_purchase'])
    buy_cash=h['cash_after_purchase']-buy_inv
    mortgage=h['mortgage_principal']
    checks=[]
    for side in ('buy','rent'):
        cash=buy_cash if side=='buy' else rent_cash
        inv=buy_inv if side=='buy' else rent_inv
        cash_errors=[];inv_errors=[];nw_errors=[]
        for r in rows:
            cash+=r[f'{side}_monthly_net_cashflow']+r[f'{side}_investment_sales']-r[f'{side}_contributions']
            inv+=r[f'{side}_investment_gain']-r[f'{side}_shock_loss']-r[f'{side}_investment_sales']+r[f'{side}_contributions']
            cash_errors.append(cash-r[f'{side}_cash'])
            inv_errors.append(inv-r[f'{side}_investments'])
            nw=(r['property_value']*(1-c.selling_cost_fraction)-r['mortgage_balance'] if side=='buy' else 0)+cash+inv
            nw_errors.append(nw-r[f'{side}_net_worth'])
        checks.extend([_check(f'{side.title()} cash ledger',cash_errors,'Cash = previous cash + net operating flow + investment sales − contributions'),
                       _check(f'{side.title()} investment ledger',inv_errors,'Investments = previous balance + returns − shock loss − sales + contributions'),
                       _check(f'{side.title()} net worth',nw_errors,'Net worth reconstructed from property liquidation value, debt and financial assets')])
    debt=[];payments=[];equity=[];differences=[]
    for r in rows:
        mortgage-=r['mortgage_principal_paid']
        debt.append(mortgage-r['mortgage_balance'])
        payments.append(r['mortgage_payment']-r['mortgage_interest']-r['mortgage_principal_paid'])
        equity.append(r['home_equity']-(r['property_value']-r['mortgage_balance']))
        differences.append(r['net_worth_difference']-r['buy_net_worth']+r['rent_net_worth'])
    checks.extend([_check('Mortgage principal roll-forward',debt,'Original principal minus monthly principal repayments'),
                   _check('Payment split',payments,'Payment = interest + principal'),
                   _check('Home equity',equity,'Home value minus remaining principal'),
                   _check('Buy − Rent identity',differences,'Net worth difference equals buy minus rent')])
    return checks


def audit_asset_trajectory(x:Inputs,a:AssetProfile,s,rows):
    h=asset_financing(x,a)
    spend=h['down']+h['closing_costs']
    cash=max(0,a.cash-spend)
    inv=a.investments-max(0,spend-a.cash)
    principal=h['mortgage_principal']
    cash_err=[];inv_err=[];debt_err=[];payment_err=[]
    for r in rows:
        cash+=r['net_cashflow']+r['liquidation']-r['contribution']
        inv+=r['investment_gain']-r['shock_loss']-r['liquidation']+r['contribution']
        principal-=r['mortgage_principal_paid']
        cash_err.append(cash-r['cash'])
        inv_err.append(inv-r['investments'])
        debt_err.append(principal-r['mortgage_balance'])
        payment_err.append(r['mortgage_payment']-r['mortgage_interest']-r['mortgage_principal_paid'])
    return [_check('Asset cash ledger',cash_err,'Cash balance reconstructed monthly'),
            _check('Asset investment ledger',inv_err,'Investment balance reconstructed monthly'),
            _check('Asset mortgage roll-forward',debt_err,'Principal balance reconciles'),
            _check('Asset mortgage payment split',payment_err,'Interest and principal sum to payment')]
