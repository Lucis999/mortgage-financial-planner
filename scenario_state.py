"""Keep the setup form consistent with the last applied immutable scenario."""
from dataclasses import asdict


def form_defaults(scenario, rental, net_mode="estimated"):
    x=scenario; r=rental
    gross=x.gross_annual_income/12
    return {
        "field_price":int(x.price),"field_rate":round(x.annual_rate*100,2),
        "field_down":int(round(x.down_pct*100)),"field_amort":x.amort_years,
        "field_closing":int(x.closing_other),"field_fthb":x.first_time_eligible,
        "buy_bedrooms":float(r.get("buy_beds",2)),"buy_area":int(r.get("buy_area",850)),
        "buy_exterior":int(r.get("buy_exterior",100)),"field_cash":int(x.liquid_cash),
        "field_gross_monthly":int(gross),"field_reserve":int(x.reserve_floor),
        "field_living":int(x.living_monthly),



        "field_net_share":int(round(100*x.net_monthly_income/gross)) if gross else 75,
        "field_net_mode":net_mode,"field_net_actual":int(x.net_monthly_income),
        "field_debt":int(x.other_debt_monthly),
        "field_strata":int(x.strata_monthly),
        "field_insurance":int(x.condo_insurance_monthly),
        "field_tax":int(x.property_tax_monthly),
        "field_maintenance":int(x.maintenance_monthly),
        "field_heating":int(x.heating_monthly),
        "shared_base_rent":float(r.get("base",1800)),
        "shared_gross_yield":round(r.get("yield",.055)*100,1),
        "rent_bedrooms":float(r.get("rent_beds",1)),"rent_area":int(r.get("rent_area",650)),
        "rent_exterior":int(r.get("rent_exterior",0)),
        "shared_rent_utilities":float(r.get("utilities",0)),
        "shared_rent_internet":float(r.get("internet",0)),
        "shared_rent_other":float(r.get("other",0)),
    }

def scenario_signature(scenario, rental):
    return (tuple(sorted(asdict(scenario).items())),tuple(sorted(rental.items())))
