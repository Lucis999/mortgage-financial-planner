# Financial Model & Visualization Guide

This guide documents the **implemented planning model** and the purpose of each dashboard component. Currency is CAD. All screenshots and numeric examples are hypothetical.

## A. Input taxonomy and data flow

**Shared scenario** (`pages/0_Setup_Scenario.py`, `scenario_state.py`): property price, down-payment %, mortgage rate, amortization, closing costs, buyer eligibility; liquid assets and minimum reserve; gross and estimated net income; other income, living costs, monthly debt; strata, condo insurance, heating, property tax and maintenance; comparable rent, rental yield, utilities, internet, other renter costs; bedrooms and floor areas.

**Page-level controls** supplement the shared inputs: owner internet; asset recognition and drawdown, investment allocation/returns; rent-vs-buy horizon, home appreciation, rent growth, selling costs; renewal and income-disruption scenarios; savings and price-growth assumptions; lifestyle preservation mode.

**Data flow:** Scenario input → applied Streamlit session state → model functions → analytical pages → final decision summary → optional Excel export. Page-specific stress controls do not necessarily propagate to the Summary.

## B. Mortgage qualification

Mortgage principal = purchase price − down payment + financed default-insurance premium, where modeled. Canadian mortgage payment uses a monthly rate derived from nominal annual interest compounded semiannually:

`r_month = (1 + nominal_rate / 2)^(1/6) − 1`

`payment = principal × r_month / [1 − (1 + r_month)^(-months)]`

Qualifying rate = `max(contract_rate + 0.02, 0.0525)`.

Qualifying housing cost = qualifying mortgage payment + property tax + heating + 50% strata fees. GDS divides this cost by gross monthly income; TDS adds recurring monthly debt payments before dividing. The interface uses 39% and 44% as screening benchmarks. Condo insurance and maintenance affect household cash flow but are not included in this simplified GDS/TDS numerator.

LTV = modeled mortgage principal / property price; LTI = modeled mortgage principal / gross annual income. LTI is descriptive, **not** a fixed loan-approval multiplier. The model's LTV may include financed insurance premium, unlike a lender's base-loan LTV.

## C. Purchase capital and cash flow

Cash to close = down payment + modeled closing costs (including simplified BC property transfer tax). Remaining liquid assets = liquid assets − cash to close. Reserve buffer = remaining liquid assets − selected minimum reserve.

Ownership monthly outflow = contractual mortgage payment + strata + property tax + condo insurance + maintenance + heating. Household surplus = estimated net monthly income + other income − ownership outflow − living expenses − debt payments.

**Interpretation:** A positive surplus is a necessary baseline cash-flow check, but it does not establish credit approval or preservation of prior savings.

## D. Reverse affordability and lifestyle preservation

The price scan evaluates candidate properties at CAD 1,000 increments up to CAD 2.5 million. The reported **capital ceiling** is the highest scanned price that retains the minimum reserve. The **income ceiling** is the highest passing modeled GDS/TDS screening. The **lifestyle ceiling** is the highest price whose post-purchase surplus meets the target. The **combined ceiling** is the highest price passing all three constraints.

Lifestyle modes:

1. **Maintain current monthly savings while renting:** target = `max(0, estimated net income + other income − living expenses − debts − all-in rent)`.
2. **Custom monthly surplus:** target is user-entered nonnegative CAD per month.
3. **Basic nonnegative cash flow:** target = CAD 0.

**Key assumption:** The selected recurring ownership costs are held fixed across the price scan. The tool does not guarantee that homes at different prices have comparable property taxes, maintenance, strata fees or living quality. Rental costs must not already be included in `living expenses` or the baseline will double-count rent.

## E. Down-payment and purchase timing

Cash target = selected down payment + modeled closing costs. Available cash = max(0, liquid assets − reserve floor). Estimated rent-era monthly savings = net income + other income − living expenses − debts − all-in rent. The savings model accumulates monthly savings over the selected horizon and optionally grows the savings amount annually.

A separate dynamic readiness scenario changes property price, income, rent, living expenses and liquid assets using annual growth assumptions and checks capital, income and cash-flow readiness. Both calculations are deterministic and should not be read as predictions.

## F. Rent versus buy

The comparison models two pathways: buy a property and build home equity while investing remaining funds, or rent and retain investable capital. Inputs include property appreciation, investment returns, rent growth, selling costs, horizon and financing pathway. Outputs include home equity, investment balances, terminal net worth, crossover signals and a 5×5 return/appreciation heatmap.

The heatmap cell value is `buy terminal net worth − rent terminal net worth`; green/positive favors the modeled buying pathway and red/negative favors renting under the selected assumptions. The count of favorable cells is **not a probability**. The two properties may not be comparable in bedrooms, area or neighborhood.

## G. Asset-supported financing and liquidity

The illustrative asset-supported model estimates a lending limit using eligible investments and a selected recognition/loan ratio. It is not an actual lender product. Asset trajectories track cash, investments, reserve target, monthly transfers and annual contributions/withdrawals. Investment return and asset shocks are user-specified, not inferred from market data.

Read the cash line against the reserve floor; an investment balance above zero does not necessarily imply immediately available liquidity. The contribution/withdrawal chart shows transfers, not market returns.

## H. Risk and stress testing

Renewal scenarios recompute payment using remaining principal and remaining amortization. Emergency cash scenarios include job-loss income replacement and one-time special assessments. Additional stress inputs apply property-price declines, take-home income reductions and liquid-asset drawdowns. Sensitivity heatmaps test changes in purchase price and mortgage rate.

**Distinction:** Nonnegative cash flow under a stress scenario does not prove qualification or purchase-capital sufficiency. The combined downside is a joint deterministic shock, not a probability distribution.

## I. Chart interpretation index

| Chart | Question answered | Variables / reading rule | Caution |
|---|---|---|---|
| Own/rent donuts | What drives housing outflow? | Mortgage, fees, utilities, tax, rent | Cash flow, not economic cost |
| Monthly outflow bars | Which option requires more cash each month? | All-in ownership vs rental cash | Mortgage principal builds equity |
| Purchase capital donut/bars | Where does available capital go? | Down payment, closing costs, remaining assets | One-time amounts, not monthly |
| GDS/TDS/LTV/LTI KPIs | What do screening indicators imply? | Stress rate, gross income, debts, principal | Not a lender decision |
| Asset allocation bars | How does financing compare with eligible assets? | Mortgage, asset limit, reserves | Hypothetical lender pathway |
| Cash/investment trajectories | How do financial assets evolve? | Returns, transfers, reserve floor | Return assumptions not forecasts |
| Investment transfer bars | When is cash invested or withdrawn? | Annual contributions and withdrawals | Transfers exclude market gains |
| Rent/buy net-worth cards | Which path has higher modeled net worth? | Appreciation, rent growth, returns, selling costs | Sensitive to assumptions |
| Rent/buy break-even heatmap | When does buying outperform renting? | 5 home-appreciation × 5 investment-return combinations | Not scenario probabilities |
| Emergency cash runway | Does cash fall below reserves? | Renewal, unemployment, assessment | Selected shock assumptions only |
| Price/rate sensitivity | How does monthly surplus respond? | Property price × mortgage rate | Cash flow does not equal qualification |
| Lifestyle preservation | Does buying preserve the desired savings? | Current rent-era savings vs ownership surplus | Not a complete wellbeing metric |
| Price ceilings | Which constraint binds first? | Capital, GDS/TDS, surplus target | Costs fixed across scanned prices |

## J. Model limitations and validation

This tool does not implement a personal income-tax calculator, credit scoring, lender-specific underwriting, property appraisal, market-price data, or probability-weighted investment outcomes. BC transfer-tax and mortgage-insurance assumptions are simplified. All real financial decisions require independent checks of current rules and individual circumstances.

Model tests use Pytest and syntax compilation. Real-browser navigation, interactive charts, Excel download, and current government/lender rule checks should be verified separately before a public release is described as production-ready.
