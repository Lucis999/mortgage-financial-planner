"""Dedicated scenario configuration workspace."""
import streamlit as st
from model import Inputs
from scenario_state import form_defaults, scenario_signature

st.title("⚙️ Set Up Your Scenario")
if "scenario" in st.session_state:
    if st.session_state.get("_form_loaded_version") != st.session_state.get("scenario_version"):
        defaults=form_defaults(st.session_state["scenario"],st.session_state.get("applied_rent",{}),st.session_state.get("net_income_mode","Estimated percentage"))
        for key,value in defaults.items(): st.session_state[key]=value
        st.session_state["_form_loaded_version"]=st.session_state.get("scenario_version")
st.caption(f"Active scenario #{st.session_state.get('scenario_version',1)} · Change inputs and press Calculate to apply them.")
st.caption("Configure the shared assumptions here, then calculate once to update every analysis page.")
with st.form("scenario_form",clear_on_submit=False):
  st.markdown("### Set up your scenario")
  st.caption("One-time purchase costs are separate from recurring monthly housing costs.")
  col_property,col_finance,col_rental=st.columns(3,gap="medium")
  with col_property:
    with st.container(border=True):
      st.markdown("#### 🏠 Property & Mortgage")
      price=st.number_input("Purchase price (CAD)",100000,2500000,700000,10000,key="field_price")
      rate=st.number_input("Mortgage rate (%)",0.0,12.0,4.5,.25,key="field_rate")/100
      down=st.slider("Down payment (%)",5,80,30,5,key="field_down")/100
      amort=st.selectbox("Amortization (years)",[15,20,25,30],index=2,key="field_amort")
      closing=st.number_input("One-time closing costs (CAD)",0,100000,2500,500,key="field_closing")
      fthb=st.checkbox("First-time buyer eligibility confirmed",False,key="field_fthb")
      st.markdown("**📐 Buying housing size**")
      buy_beds=st.number_input("Buy bedrooms (den = 0.5)",0.0,10.0,2.0,.5,key="buy_bedrooms")
      buy_area=st.number_input("Buy interior area (sq ft)",0,20000,850,25,key="buy_area")
      buy_exterior=st.number_input("Buy exterior area · balcony / yard (sq ft)",0,50000,100,25,key="buy_exterior")
      st.caption("Closing costs are one-time. Exterior space is tracked separately from interior area.")
  with col_finance:
    with st.container(border=True):
      st.markdown("#### 💰 Assets, Income & Monthly Cash Flow")
      assets=st.number_input("Total liquid assets (CAD)",0,10000000,350000,10000,key="field_cash")
      gross_monthly=st.number_input("Gross monthly income (CAD)",0,500000,10000,250,key="field_gross_monthly")
      reserve=st.number_input("Minimum cash reserve",0,10000000,30000,5000,key="field_reserve")
      living=st.number_input("Living expenses / month",0,1000000,2200,100,key="field_living")
      st.caption("Condo fees and insurance are entered separately under Bank qualification below.")
      st.caption("Heating and energy are entered separately under Bank qualification below.")
      st.caption("Property tax and maintenance are entered separately under Bank qualification below.")
      with st.expander("🏦 Bank qualification · Detailed housing costs"):
        st.caption("Split costs for accurate GDS/TDS: 50% of strata and all heating/property tax count toward qualification. Insurance and maintenance affect actual cash flow only.")
        strata_detail=st.number_input("Strata / condo fees per month",0,100000,420,10,key="field_strata")
        insurance_detail=st.number_input("Condo insurance per month",0,100000,95,10,key="field_insurance")
        tax_detail=st.number_input("Property tax per month",0,100000,250,10,key="field_tax")
        maintenance_detail=st.number_input("Maintenance per month",0,100000,100,10,key="field_maintenance")
        heating_detail=st.number_input("Heating / energy per month",0,100000,70,10,key="field_heating")
        st.caption("The three grouped figures above remain for visual reference. The five detailed fields drive the applied scenario.")
      with st.expander("⚙️ Advanced income & debt assumptions"):
        net_mode=st.radio("Take-home income method",["Estimated percentage","Actual monthly take-home"],horizontal=True,key="field_net_mode")
        net_income_fraction=st.slider("Estimated take-home share of gross (%)",30,100,75,1,key="field_net_share")/100
        net_actual=st.number_input("Actual monthly take-home income (CAD)",0,500000,7500,100,key="field_net_actual")
        debt=st.number_input("Other monthly debt payments (CAD)",0,100000,0,50,key="field_debt")
        st.caption("Take-home percentage is an assumption, not a tax calculation. Debt is included in TDS and monthly cash flow.")
  with col_rental:
    with st.container(border=True):
      st.markdown("#### 🔑 Rental Scenario")
      base_rent=st.number_input("Comparable base rent / month (CAD)",0.0,30000.0,1800.0,50.0,key="shared_base_rent")
      gross_yield=st.number_input("Assumed gross rental yield (%)",0.1,20.0,5.5,0.1,key="shared_gross_yield")
      rent_beds=st.number_input("Rent bedrooms (den = 0.5)",0.0,10.0,1.0,.5,key="rent_bedrooms")
      rent_area=st.number_input("Rent interior area (sq ft)",0,20000,650,25,key="rent_area")
      rent_exterior=st.number_input("Rent exterior area · balcony / yard (sq ft)",0,50000,0,25,key="rent_exterior")
      rent_utilities=st.number_input("Extra utilities / month (if not included)",0.0,3000.0,0.0,10.0,key="shared_rent_utilities")
      rent_internet=st.number_input("Extra internet / month (if not included)",0.0,1000.0,0.0,10.0,key="shared_rent_internet")
      rent_other=st.number_input("Other renter costs / month",0.0,3000.0,0.0,10.0,key="shared_rent_other")
      st.caption("Rent and purchase should be comparable in bedrooms, size, neighborhood and condition. Den = 0.5 is a display convention.")
  submitted=st.form_submit_button("🧮 Calculate & Update All Pages",type="primary",use_container_width=True)
if submitted or "scenario" not in st.session_state:
    new_scenario=Inputs(price=price,down_pct=down,annual_rate=rate,amort_years=amort,gross_annual_income=gross_monthly*12,net_monthly_income=(net_actual if net_mode=="Actual monthly take-home" else gross_monthly*net_income_fraction),other_monthly_income=0,liquid_cash=assets,other_debt_monthly=debt,living_monthly=living,reserve_floor=reserve,strata_monthly=strata_detail,property_tax_monthly=tax_detail,condo_insurance_monthly=insurance_detail,maintenance_monthly=maintenance_detail,heating_monthly=heating_detail,closing_other=closing,first_time_eligible=fthb)
    st.session_state["scenario"]=new_scenario
    st.session_state["applied_rent"]={"base":base_rent,"yield":gross_yield/100,"utilities":rent_utilities,"internet":rent_internet,"other":rent_other,"buy_beds":buy_beds,"rent_beds":rent_beds,"buy_area":buy_area,"rent_area":rent_area,"buy_exterior":buy_exterior,"rent_exterior":rent_exterior}
    st.session_state["net_income_mode"]=net_mode
    st.session_state["scenario_version"]=st.session_state.get("scenario_version",0)+1
    st.session_state["_form_loaded_version"]=st.session_state["scenario_version"]
    st.success("Scenario applied to all pages.")
else:
    st.caption("Inputs are staged until you press **Calculate & Update All Pages**. Current results use the last applied scenario.")

st.info("Return to Financial Overview or another analysis page using the sidebar. All pages use the most recently applied scenario.")
