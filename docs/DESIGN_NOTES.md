# Dashboard Redesign v1.0 — Change Notes

- Replaced the sidebar-first parameter form with a main-content three-tab scenario editor.
- Reduced the sidebar to workspace orientation and a link to Full Analytics.
- Kept existing KPI cards, affordability chart, capital allocation, renewal/liquidity, rent-vs-buy and asset-supported financing.
- Preserved calculation modules without modifying numerical logic.
- Existing Full Analytics remains separate and inputs do not automatically synchronize between pages.

## Quality gates
- 8 regression tests passed.
- Python compilation passed.
- Browser QA pending; Streamlit unavailable in packaging environment.
- Policy and underwriting assumptions require separate review before production use.
