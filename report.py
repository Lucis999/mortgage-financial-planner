"""Portable Excel export using openpyxl; in-memory, no server-side storage."""
from io import BytesIO
from dataclasses import asdict
from openpyxl import Workbook
from openpyxl.styles import PatternFill, Font, Alignment
from openpyxl.utils import get_column_letter
from model import housing, renewal, cashflow, heatmap, down_comparison
from asset_model import asset_financing
from rent_vs_buy import simulate, break_even_grid

NOTES=[
 ('Purpose','Portfolio scenario analysis; not lending approval, investment or tax advice.'),
 ('Jurisdiction','Illustrative British Columbia owner-occupied condo; verify current policy and lender terms.'),
 ('Income qualification','GDS and TDS estimated from gross income and stressed mortgage payment; not lender approval.'),
 ('Asset qualification','Illustrative 35% minimum down and application-time eligible assets after closing at 1:1; lender-specific assumption.'),
 ('Asset collateral','No ongoing asset maintenance requirement modeled after mortgage approval.'),
 ('Home equity','Current property value minus outstanding principal. Interest is already included in cash flow.'),
 ('Net worth','Buy: estimated resale proceeds less mortgage balance plus cash and investments; Rent: cash and investments.'),
 ('Rent comparison','Same starting liquid wealth and monthly income; positive surplus invested above a cash buffer.'),
 ('Cash flow','Cumulative housing cash spending includes purchase cash for Buy and monthly housing outlays for both.'),
 ('Investment returns','Deterministic nominal scenario assumptions, not predictions; tax, fees and realized capital gains excluded.'),
 ('Housing costs','User estimates for property tax, strata, insurance, maintenance, heating; no automatic inflation for owner costs.'),
 ('Closing/selling costs','Closing tax and fees at purchase; estimated selling cost applied to home valuation at comparison dates.'),
 ('Rental expenses','Rental payments grow at assumed rate; renter insurance held constant.'),
 ('Stress shocks','One-time investment and home price shocks applied in selected year.'),
 ('Funding','Cash deficits draw down investments; negative cash after investment exhaustion flags unmet funding.'),
 ('BC PTT','Simplified tiers and first-time buyer relief; additional taxes, GST and rebates excluded.'),
 ('Mortgage insurance','Simplified default insurance premium; distinct from monthly condo insurance.'),
 ('Privacy','No account or database; Excel is created in memory.'),
 ('Source: BC PTT','https://www2.gov.bc.ca/gov/content/taxes/property-taxes/property-transfer-tax'),
 ('Source: Canada down payment','https://www.canada.ca/en/financial-consumer-agency/services/mortgages/down-payment.html')]

def make_report(x, maximum=None, asset_profile=None, comparison=None, financing='income'):
    wb=Workbook();wb.remove(wb.active)
    def sheet(name,headers,rows):
        ws=wb.create_sheet(name);ws.append(list(headers))
        for row in rows:
            ws.append([v if isinstance(v,(str,int,float,bool)) or v is None else str(v) for v in row])
        ws.freeze_panes='A2';ws.auto_filter.ref=ws.dimensions
        for cell in ws[1]:
            cell.fill=PatternFill('solid',fgColor='17324D');cell.font=Font(bold=True,color='FFFFFF')
        ws.row_dimensions[1].height=26
        for i,h in enumerate(headers,1): ws.column_dimensions[get_column_letter(i)].width=min(40,max(18,len(str(h))+3))
        return ws
    h=housing(x);rn=renewal(x)
    overview=[('Maximum affordable price',maximum),('Monthly mortgage',h['monthly_mortgage']),
      ('Monthly housing',h['monthly_housing']),('Monthly surplus',h['monthly_surplus']),
      ('Down payment',h['down']),('Closing cash',h['down']+h['closing_costs']),
      ('Cash after purchase',h['cash_after_purchase']),('Mortgage default insurance',h['insurance_premium']),
      ('BC property transfer tax',h['ptt_due']),('GDS',h['gds']),('TDS',h['tds']),
      ('Renewal payment',rn['renewal_payment']),('Renewal balance',rn['balance_at_renewal'])]
    sheet('Overview',['Metric','Value'],overview)
    sheet('Inputs',['Parameter','Value'],list(asdict(x).items()))
    for name,rows in [('CashFlow',cashflow(x)),('Sensitivity',heatmap(x)),('DownPayment',down_comparison(x))]:
        headers=list(dict.fromkeys(k for row in rows for k in row))
        sheet(name,headers,[[row.get(k) for k in headers] for row in rows])
    if asset_profile:
        data=asset_financing(x,asset_profile)
        sheet('AssetFinancing',['Metric','Value'],list(data.items()))
        sheet('AssetInputs',['Parameter','Value'],list(asdict(asset_profile).items()))
    if comparison:
        rows=simulate(x,comparison,financing)
        headers=list(rows[0]);sheet('RentVsBuy',headers,[[r[k] for k in headers] for r in rows])
        grid=break_even_grid(x,comparison)
        sheet('BreakEven',['Appreciation','Investment return','Buy minus Rent'],
              [[r['appreciation'],r['investment_return'],r['difference']] for r in grid])
        sheet('ComparisonInputs',['Parameter','Value'],list(asdict(comparison).items()))
    ws=sheet('Assumptions_Limits',['Topic','Explanation'],NOTES)
    ws.column_dimensions['A'].width=35;ws.column_dimensions['B'].width=105
    for row in ws.iter_rows(min_row=2):row[1].alignment=Alignment(wrap_text=True,vertical='top')
    output=BytesIO();wb.save(output);return output.getvalue()
