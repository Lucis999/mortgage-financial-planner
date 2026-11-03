## v2.4.2 — Decision Takeaway formatting and publication updates
- Replaced currency-containing Markdown summary with native KPI cards and plain text, avoiding accidental math parsing.
- Added explicit, independently testable decision branches for qualification, capital, negative cash flow, lifestyle savings and combined constraints.
- Updated verified Purchase Capital Allocation and Lifestyle Preservation screenshots and related README/case study captions.
- Included the final Decision Takeaway screenshot and scenario-consistency caveat.
- Made test source reads explicitly UTF-8 for Windows portability.
- Added GitHub Actions tests on Ubuntu and Windows with Python 3.10 and 3.12.
- Corrected README mathematical delimiters for GitHub rendering.

## v2.4.1 — Screenshot-ready UI fixes

- Render the lifestyle information banner as plain text, preventing Markdown currency formatting from appearing literally.
- Label the purchase-capital doughnut as one-time capital rather than a monthly amount.
- Mark the two outdated screenshots for replacement in GitHub and portfolio documentation.

# Changelog

All notable project changes, consolidated from the original version-specific release notes. Earlier entries document historical states; the current architecture is described in the README.


---

# v2.4.0 — Lifestyle-Preserving Affordability
- Added three lifestyle-preservation modes in the consolidated Financial Decision Summary: match current rent-era monthly savings, set a custom monthly surplus target, or allow nonnegative cash flow.
- Lifestyle and combined home-price ceilings now respect the selected post-purchase surplus target.
- Added explicit lifestyle gap and eligibility messaging.
- Typography and responsive metric styling normalized; removed redundant CSS rules.
- Added targeted regression tests.
- Important: baseline savings assumes rent is excluded from living expenses. It does not measure subjective quality of life.


---

# v2.3.0 · Dedicated Financial Decision Summary Workspace

- New Workspace page: Financial Decision Summary, placed after the analytical pages.
- Relocated Financial Overview decision summary, Mortgage & Affordability price ceiling, Rent vs Buy purchase-readiness, and duplicated five-year cash-flow projection to a single destination.
- Consolidated mortgage qualification, GDS/TDS, LTV/LTI, stress test, reserve buffer, four home-price ceilings, down-payment savings horizon, dynamic readiness, and 60-month post-purchase cash runway.
- Clarified that the new summary uses baseline cash-flow assumptions rather than Risk & Stress page interactive shocks.
- Preserved underlying calculation engines and dedicated analytical pages.


---

# v2.2.0 — Mortgage qualification & purchase decision summary

- GDS/TDS, stress-tested payment, LTV, and LTI metrics with source-linked interpretation.
- Separate strata, insurance, heating, property tax and maintenance inputs to preserve lender-style ratio categories.
- Capital, income qualification, monthly lifestyle, and combined price ceilings.
- Salary multiple explanation and savings-to-down-payment timeline.
- Notes: this is a screening calculator; bank policies, property appraisal, insurance, credit and employment verification are outside scope.


---

# v2.1.1 · Financial Decision Summary fix

- Replaced conditional Streamlit rendering expression with explicit if/else statements.
- Prevents Streamlit DeltaGenerator objects from appearing as huge debug/API documentation in the financial summary.
- Updated version footer.
- No changes to financial calculations.


---

# v2.1.0 Beta — Reliability and Decision Clarity

- Scenario setup fields hydrate from the last applied scenario; persistent applied-version readout across analysis pages.
- Explicit actual net monthly income option alongside the approximate percentage method.
- Dynamic 15-year purchase-readiness projection: yearly income, rent, living expenses, home prices; monthly asset accumulation.
- Combined risk-stress summary and clear simplified-model caveat.
- Financial Overview decision summary for mortgage, reserve, rental cash-outflow and constraints.
- Consistent small applied-scenario header and iconography.

Known limitations: Streamlit browser rendering not validated in this environment; no verified tax engine; no stochastic Monte Carlo; joint asset stress uses simplified cash proxy. Year labels anchor to 2026 and are for the initial release period.


---

# v2.0.1 — Dedicated Scenario Workspace

- Moved all scenario form inputs from app-wide header to a standalone sidebar page, **Set Up Your Scenario**.
- Kept the three-column form and the Calculate & Update All Pages submit action.
- All other pages now show only their respective analytics, not the shared input form.
- Initializes a default scenario when the application first opens; submitted settings persist across page navigation.
- Set Up Your Scenario is the initial landing page.


---

# v2.0.0 Alpha

- Three-column scenario: purchase, combined finances, comparable rental with interior/exterior areas.
- Fixed risk page unreachable content caused by st.stop() in the 60-month ledger expander.
- Restored 60-month cash runway; added property-value, income and liquid-asset downside metrics and chart.
- Liquidity: reserve/cash/investment graph, annual transfer aggregation, and informative zero-transfer state.
- Added GDS/TDS/LTV financial glossary.
- Added capital-readiness timeline with explicit rent expense in savings; separate from net-worth decision.
- Advanced debt and net-income assumptions to avoid silently assuming zero debt and 75% take-home as facts.

Limitations: capital readiness is not a lender approval; user must check comparable housing quality, tax treatment and investment assumptions.


---

# v1.1.0 — Three-Column Cost Input Simplification
- Moved one-time closing costs and first-time buyer eligibility to Property & Mortgage.
- Reordered Income & Assets to gross income, liquid assets, minimum cash reserve, living expenses.
- Combined recurring monthly expenses into three inputs: strata & insurance; heating/hydro/electricity; property tax & maintenance.
- Updated Financial Overview ownership cost allocation chart to use the same grouped categories.
- Retained comparable renting inputs and all existing calculation pages.
- Combined input totals are stored in existing model fields to preserve calculation compatibility; category breakdowns are no longer separately tracked.


---

# v1.0.9 · Three-column scenario & shared resilience
- Replaced three scenario tabs with one three-column form.
- Simplified income inputs to gross monthly income, liquid assets, living costs and reserve.
- **Important model assumption:** net monthly income = 75% of gross; other debt payments = 0. This is not an actual tax computation.
- Split heating and hydro UI; both sum into existing monthly heating/utility model field.
- Kept BC property transfer tax calculated automatically; Other closing costs are one-time.
- Bedrooms accept 0.5 increments, with den = 0.5 convention.
- Reusable seven-level resilience spectrum in Overview and Asset & Liquidity.


---

# v1.0.8 · Comparable rent and scenario controls
- Explicit Calculate & Update All Pages form commits shared inputs.
- Shared rental base, gross yield, utilities and internet.
- Rent vs Buy and Overview show rent-implied property value against purchase price.
- Added conditional net-worth winner with caveats, mortgage comfort status, and clearer investment transfer labels.
- Asset trajectory annual return expanded to -100%–100%, including total investment loss.
- Invested share explanation notes current model limitation: allocation slider sets the initial post-closing cash/investment split.


---

# v1.0.6 — Export Repair & Comfort Spectrum
- Fixed Excel export: maps the visible Income-based / Asset-based selections to the calculation engine's income / asset identifiers.
- Added export tests covering both financing modes and validating the resulting Excel workbook.
- Added a seven-level, emoji-based Financial Comfort spectrum in Financial Overview, based on surplus, housing-to-net-income ratio and cash reserve.
- Preserved existing finance models and six-page navigation.
- Comfort scale is illustrative and is not a lender or wellbeing assessment.


---

# Mortgage Financial Planner v1.0.5 — UI & Brand Refresh
- Rebranded product-facing labels and titles, removing the former employer's name.
- Increased top content padding to avoid clipping by Streamlit's top toolbar.
- Unified navy, teal, off-white styling and sidebar navigation across pages.
- Added housing, budget comfort and liquidity visual indicators on Financial Overview.
- Improved scenario input presentation and updated overview links.
- All financial calculations are retained; visual indicators are heuristic, not lender advice.
- BC references remain where they describe the applicable geographic tax or policy model.


---

# v1.0.4 — Scenario UX and Diagnostic Fixes

- Shared inputs moved to the top of every page, editable in three tabs.
- Sidebar navigation reordered: Overview → Mortgage → Asset & Liquidity → Rent vs Buy → Risk → Advanced.
- Fixed Rent vs Buy financing pathway mismatch (UI labels vs simulation enum).
- Mortgage qualification checks now explain the precise numeric thresholds and failed constraints.
- Added reserve-risk status, cash-exhaustion month and three liquidity KPIs.
- Added a 60-month cash-flow ledger and chart to Asset & Liquidity.
- Financial models unchanged. Illustrative planning only; not lending advice.


---

# v1.0.3 — Six-page navigation and scenario integration

- Replaced two-page navigation with six real Streamlit pages.
- Consolidated core financial scenario inputs into one persistent app-entrypoint widget panel.
- Reused the original mortgage, asset trajectory, liquidity diagnostics, sensitivity, rent-versus-buy and report calculations without altering the underlying financial engines.
- Financial Overview is now a concise summary; no duplicated calculation widgets.
- Detailed tools are organized by purpose; Excel export and methodology are on the Advanced page.

## Notes
- Advanced module-specific parameters remain local to their own analytical pages.
- Shared property/income/expense inputs remain synchronized; users edit them in the sidebar.
- Existing financial policy assumptions are illustrative and have not been updated or independently verified.


---

# v1.0.2 Dashboard Consolidation

- Replaced ownership cost bar chart with a donut chart and central total.
- Combined Rent vs Buy net worth and optional static liquidity reserve references in one chart.
- Added explicit liquidity methodology and side-by-side reserve metrics.
- Moved affordability calculation explanation into its own expandable panel.
- Kept two functional navigation pages (dashboard and advanced analytics) to avoid decorative links.
- Existing advanced analytics, liquidity diagnostics, investment transfers, and Excel export retained unchanged.

## Proposed next navigation (not implemented)
- Overview; Mortgage & Affordability; Rent vs Buy; Asset & Liquidity; Risk & Stress Testing; Advanced Analytics & Export.
- Implement only after consolidating scenario inputs into shared session state; otherwise different pages can disagree.

## Limitations
- Dashboard and legacy advanced inputs are not yet synchronized.
- Static reserve references are not a year-by-year liquidity forecast.
- Browser visual QA still required.


---

# v1.0.1 — Dashboard UX & liquidity update

- Replaced decorative sidebar labels with real Streamlit navigation. Both dashboard and Full Analytics are reachable in either direction.
- Added optional methodology expanders within the dashboard.
- Separated investment collateral eligibility (0–100%) from market change stress (-100% to +100%).
- Added two dashed, horizontal liquidity stress reserve lines to Rent vs Buy, separate from projected net worth to avoid double-counting.
- **Important:** Rent reserve = initial liquid assets − 12 × initial monthly rent; buy reserve = post-closing liquid assets − 60 × initial monthly mortgage. These are static earmarking scenarios, not simulated future cash balances. Mortgage payments alone omit strata, taxes and maintenance. Negative results indicate liquidity shortfall.
- Existing Full Analytics uses its own input widgets; scenario parameters are not automatically synchronized across the two pages.
- Financial assumptions and BC policy approximations remain illustrative and require independent verification.

## v2.4.0 — Portfolio documentation and screenshot package (2026-11-03)
- Prepared formal GitHub README, independent portfolio case study, model and visualization guide, and 20-image screenshot gallery.
- Corrected one-time capital donut label and lifestyle information-banner formatting.
- Added documentation and UI-source regression checks; no financial model equations changed.
