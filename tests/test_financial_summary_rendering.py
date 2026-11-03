from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def test_summary_is_dedicated_page_not_embedded():
    overview=(ROOT/"pages/1_Financial_Overview.py").read_text(encoding='utf-8')
    mortgage=(ROOT/"pages/2_Mortgage_Affordability.py").read_text(encoding='utf-8')
    summary=(ROOT/"pages/7_Financial_Decision_Summary.py").read_text(encoding='utf-8')
    assert "### 🧭 Financial Decision Summary" not in overview
    assert "### 🧭 Purchase Decision Summary" not in mortgage
    assert 'st.title("🧭 Financial Decision Summary")' in summary
    assert "if h[\"affordable\"]:" not in summary or "st.success(" in summary
