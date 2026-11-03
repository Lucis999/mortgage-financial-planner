"""Small, consistent applied-scenario readout on analysis pages."""
import streamlit as st

def active_scenario_header():
    x=st.session_state["scenario"]
    st.caption(f"🟢 Active scenario #{st.session_state.get('scenario_version',1)} · 🏠 Purchase ${x.price:,.0f} · 💰 Down {x.down_pct:.0%} · 📉 Rate {x.annual_rate:.2%} · 👤 Gross income ${x.gross_annual_income/12:,.0f}/mo · Edit in Set Up Your Scenario")
