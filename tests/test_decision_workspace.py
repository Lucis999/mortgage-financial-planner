from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def test_workspace_navigation():
    nav=(ROOT/"app.py").read_text(encoding='utf-8')
    assert 'pages/7_Financial_Decision_Summary.py' in nav
    assert nav.index('pages/5_Risk_Stress.py') < nav.index('pages/7_Financial_Decision_Summary.py')
def test_sections_consolidated():
    summary=(ROOT/"pages/7_Financial_Decision_Summary.py").read_text(encoding='utf-8')
    for label in ("Can I qualify", "What home price", "Lifestyle-Preserving Affordability", "How long until I can buy", "What happens to cash", "Decision takeaway"):
        assert label in summary
    assert "When could I buy?" not in (ROOT/"pages/3_Rent_vs_Buy.py").read_text(encoding='utf-8')
    assert "Five-year monthly cash-flow projection" not in (ROOT/"pages/5_Risk_Stress.py").read_text(encoding='utf-8')
    assert "Five-year monthly cash-flow projection" not in (ROOT/"pages/4_Asset_Liquidity.py").read_text(encoding='utf-8')
