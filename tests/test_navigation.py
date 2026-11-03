from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def test_six_page_navigation():
    app=(ROOT/'app.py').read_text(encoding='utf-8')
    for name in ['1_Financial_Overview','2_Mortgage_Affordability','3_Rent_vs_Buy','4_Asset_Liquidity','5_Risk_Stress','6_Advanced_Export']:
        assert name in app
        assert (ROOT/'pages'/f'{name}.py').is_file()
def test_shared_scenario():
    assert 'st.session_state["scenario"]=new_scenario' in (ROOT/'pages/0_Setup_Scenario.py').read_text(encoding='utf-8')
    assert 'st.form_submit_button' in (ROOT/'pages/0_Setup_Scenario.py').read_text(encoding='utf-8')
    assert 'st.form("scenario_form"' not in (ROOT/'app.py').read_text(encoding='utf-8')
    assert '0_Setup_Scenario.py' in (ROOT/'app.py').read_text(encoding='utf-8')
    for p in (ROOT/'pages').glob('*.py'):
        assert 'st.session_state["scenario"]' in p.read_text(encoding='utf-8')
def test_analytics_preserved():
    assert 'Liquidity risk diagnostics' in (ROOT/'pages/4_Asset_Liquidity.py').read_text(encoding='utf-8')
    assert 'Investment transfers' in (ROOT/'pages/4_Asset_Liquidity.py').read_text(encoding='utf-8')
    assert 'heatmap(x)' in (ROOT/'pages/5_Risk_Stress.py').read_text(encoding='utf-8')
    assert 'make_report(' in (ROOT/'pages/6_Advanced_Export.py').read_text(encoding='utf-8')
