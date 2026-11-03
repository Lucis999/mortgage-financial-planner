from pathlib import Path
root=Path(__file__).resolve().parents[1]
def test_input_layout_and_grouped_costs():
 s=(root/'pages/0_Setup_Scenario.py').read_text(encoding='utf-8')
 assert s.index('One-time closing costs')<s.index('#### 💰 Assets, Income & Monthly Cash Flow')
 assert s.index('Minimum cash reserve')<s.index('Living expenses / month')
 for label in ['Strata / condo fees per month','Condo insurance per month','Property tax per month','Maintenance per month','Heating / energy per month']:
  assert label in s
 assert 'strata_monthly=strata_detail' in s
 assert 'property_tax_monthly=tax_detail' in s
 assert 'closing_other=closing' in s
 assert 'Rental Scenario' in s
def test_overview_grouped_legend():
 s=(root/'pages/1_Financial_Overview.py').read_text(encoding='utf-8')
 assert '"Strata & insurance"' in s
 assert '"Property tax & maintenance"' in s
