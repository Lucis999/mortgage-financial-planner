from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def test_setup_only_on_dedicated_page():
    app=(ROOT/'app.py').read_text(encoding='utf-8')
    setup=(ROOT/'pages/0_Setup_Scenario.py').read_text(encoding='utf-8')
    assert 'st.form("scenario_form"' not in app
    assert 'st.form("scenario_form"' in setup
    assert 'default=True' in app.split('0_Setup_Scenario.py')[1].split('),')[0]
    assert 'scenario_version' in setup
    assert 'applied_rent' in setup
def test_other_pages_do_not_render_shared_form():
    for page in (ROOT/'pages').glob('*.py'):
        if page.name!='0_Setup_Scenario.py':
            assert 'st.form("scenario_form"' not in page.read_text(encoding='utf-8')
