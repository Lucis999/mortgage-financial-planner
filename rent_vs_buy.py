"""Monthly, equal-starting-wealth rent-versus-buy simulator.
Cash and invested assets are kept separate. Interest is paid through cash flow,
never subtracted again from home equity. Returns are deterministic scenarios.
"""
from dataclasses import dataclass, replace
from model import Inputs, housing, payment

@dataclass(frozen=True)
class Comparison:
    monthly_rent: float = 2700
    renter_insurance: float = 30
    rent_growth: float = .025
    appreciation: float = .025
    investment_return: float = .05
    years: int = 15
    selling_cost_fraction: float = .04
    cash_buffer: float = 30000
    investment_fraction: float = .65
    renewal_rate: float = .065
    renewal_year: int = 5
    price_shock: float = 0
    investment_shock: float = 0
    shock_year: int = 3


def simulate(x: Inputs, c: Comparison, financing='income'):
    if financing not in ('income', 'asset'):
        raise ValueError('Unknown financing pathway')
    # Asset eligibility is checked by the caller; the amortization and wealth
    # engine is shared. This does NOT constitute asset-based loan approval.
    if not 1<=c.years<=30 or not 0<=c.investment_fraction<=1:
        raise ValueError('Invalid horizon or investment fraction')
    if not -1<c.appreciation or not -1<c.investment_return or not -1<c.rent_growth:
        raise ValueError('Growth rates must be greater than -100%')
    if not 0<=c.selling_cost_fraction<1 or not 0<=c.price_shock<=1 or not 0<=c.investment_shock<=1:
        raise ValueError('Invalid shock or selling cost')
    if c.renewal_rate < 0 or c.renewal_year < 1 or c.shock_year < 1:
        raise ValueError('Renewal and shock settings must be nonnegative and valid')
    if c.monthly_rent<0 or c.renter_insurance<0 or c.cash_buffer<0:
        raise ValueError('Costs and cash buffer must be nonnegative')
    h=housing(x)
    if h['cash_after_purchase']<0: raise ValueError('Insufficient assets to fund the purchase')
    # Initial investment/cash allocation is identical for both alternatives,
    # before purchasing, so initial total wealth is equal.
    initial=x.liquid_cash
    rent_inv=initial*c.investment_fraction
    rent_cash=initial-rent_inv
    buy_total=h['cash_after_purchase']
    buy_inv=min(rent_inv,buy_total)
    buy_cash=buy_total-buy_inv
    principal=h['mortgage_principal']; balance=principal
    remaining=x.amort_years*12
    current_rate=x.annual_rate
    current_payment=h['monthly_mortgage']
    house_value=x.price
    rows=[]
    other_costs=h['monthly_housing']-h['monthly_mortgage']
    for month in range(1,c.years*12+1):
        if month==(c.renewal_year*12+1) and balance>0:
            current_rate=c.renewal_rate
            current_payment=payment(balance,current_rate,max(1,remaining))
        house_value*=(1+c.appreciation)**(1/12)
        rent=c.monthly_rent*(1+c.rent_growth)**((month-1)/12)
        monthly_invest=(1+c.investment_return)**(1/12)-1
        buy_gain=buy_inv*monthly_invest
        rent_gain=rent_inv*monthly_invest
        buy_inv+=buy_gain
        rent_inv+=rent_gain
        buy_shock_loss=rent_shock_loss=0.0
        if month==(c.shock_year-1)*12+1:
            house_value*=1-c.price_shock
            buy_shock_loss=buy_inv*c.investment_shock
            rent_shock_loss=rent_inv*c.investment_shock
            buy_inv-=buy_shock_loss
            rent_inv-=rent_shock_loss
        monthly_rate=(1+current_rate/2)**(1/6)-1
        interest=balance*monthly_rate
        principal_paid=min(balance,max(0,current_payment-interest)) if remaining>0 else 0
        actual_payment=interest+principal_paid if remaining>0 else 0
        balance=max(0,balance-principal_paid)
        remaining=max(0,remaining-1)
        monthly_income=x.net_monthly_income+x.other_monthly_income
        # Same non-housing living expenses in both alternatives.
        common=x.living_monthly+x.other_debt_monthly
        buy_net=monthly_income-common-other_costs-actual_payment
        rent_net=monthly_income-common-rent-c.renter_insurance
        buy_cash+=buy_net
        rent_cash+=rent_net
        # Cash deficits are funded from investments. Excess cash is invested
        # above the selected cash buffer. Negative net assets remain visible.
        buy_sale=rent_sale=buy_contribution=rent_contribution=0.0
        if buy_cash<0 and buy_inv>0:
            transfer=min(-buy_cash,buy_inv);buy_inv-=transfer;buy_cash+=transfer;buy_sale=transfer
        if rent_cash<0 and rent_inv>0:
            transfer=min(-rent_cash,rent_inv);rent_inv-=transfer;rent_cash+=transfer;rent_sale=transfer
        if buy_cash>c.cash_buffer:
            buy_contribution=buy_cash-c.cash_buffer;buy_inv+=buy_contribution;buy_cash=c.cash_buffer
        if rent_cash>c.cash_buffer:
            rent_contribution=rent_cash-c.cash_buffer;rent_inv+=rent_contribution;rent_cash=c.cash_buffer
        buy_nw=house_value*(1-c.selling_cost_fraction)-balance+buy_cash+buy_inv
        rent_nw=rent_cash+rent_inv
        rows.append({'month':month,'year':month/12,'buy_cash':buy_cash,'rent_cash':rent_cash,
          'buy_investments':buy_inv,'rent_investments':rent_inv,'property_value':house_value,
          'mortgage_balance':balance,'home_equity':house_value-balance,
          'buy_net_worth':buy_nw,'rent_net_worth':rent_nw,'net_worth_difference':buy_nw-rent_nw,
          'buy_monthly_net_cashflow':buy_net,'rent_monthly_net_cashflow':rent_net,
          'buy_housing_cost':other_costs+actual_payment,'rent_housing_cost':rent+c.renter_insurance,
          'buy_investment_gain':buy_gain,'rent_investment_gain':rent_gain,
          'buy_shock_loss':buy_shock_loss,'rent_shock_loss':rent_shock_loss,
          'buy_investment_sales':buy_sale,'rent_investment_sales':rent_sale,
          'buy_contributions':buy_contribution,'rent_contributions':rent_contribution,
          'mortgage_interest':interest,'mortgage_principal_paid':principal_paid,'mortgage_payment':actual_payment,
          'buy_cumulative_housing_cashflow':0,'rent_cumulative_housing_cashflow':0})
    buy_cum=-h['down']-h['closing_costs'];rent_cum=0
    for row in rows:
        buy_cum-=row['buy_housing_cost'];rent_cum-=row['rent_housing_cost']
        row['buy_cumulative_housing_cashflow']=buy_cum
        row['rent_cumulative_housing_cashflow']=rent_cum
    return rows


def break_even_year(rows):
    # First year after which buying stays ahead for the remaining horizon.
    yearly=[r for r in rows if r['month']%12==0]
    for i,r in enumerate(yearly):
        if r['net_worth_difference']>=0 and all(z['net_worth_difference']>=0 for z in yearly[i:]):
            return int(r['year'])
    return None


def break_even_grid(x,c,appreciations=(-.02,0,.02,.04,.06),returns=(0,.03,.05,.07,.10)):
    return [{'appreciation':g,'investment_return':r,
             'difference':simulate(x,replace(c,appreciation=g,investment_return=r))[-1]['net_worth_difference']}
            for r in returns for g in appreciations]
