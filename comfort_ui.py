"""Reusable illustrative financial resilience visualization."""
STATES=[("🥵","Critical","Cash shortfall or reserve failure"),("😫","Very strained","Very limited monthly flexibility"),("😟","Strained","Tight recurring budget"),("😐","Manageable","Moderate financial pressure"),("🙂","Stable","Reasonable cash buffer"),("😊","Comfortable","Strong monthly surplus"),("😎","Very comfortable","Large financial buffer")]
def comfort_level(surplus,liquidity,housing_share):
    if surplus<0 or liquidity<0:return 0
    if housing_share>.65 or surplus<250:return 1
    if housing_share>.55 or surplus<500:return 2
    if housing_share>.45 or surplus<1000:return 3
    if housing_share>.35 or surplus<1500:return 4
    if housing_share>.25 or surplus<2500:return 5
    return 6
def render_comfort(level,title="Financial resilience · Seven-level spectrum",details=None):
    import streamlit as st
    level=max(0,min(6,int(level)))
    with st.container(border=True):
        st.markdown(f"#### {title}")
        st.markdown(f"### {STATES[level][0]} {STATES[level][1]}")
        st.caption(STATES[level][2])
        st.progress((level+1)/7)
        cols=st.columns(7)
        for i,(emoji,label,description) in enumerate(STATES):
            with cols[i]:
                st.markdown(f"<div style='font-size:1.6rem;text-align:center;opacity:{1 if i==level else .4}'>{emoji}</div>",unsafe_allow_html=True)
                st.caption(("● " if i==level else "")+label)
        if details:st.caption(details)
        st.caption("Planning heuristic, not lender underwriting, a wellbeing assessment, or a forecast.")
