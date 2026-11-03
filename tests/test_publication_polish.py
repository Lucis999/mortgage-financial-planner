from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def test_capital_donut_unit_is_not_monthly():
    source=(ROOT/'pages/1_Financial_Overview.py').read_text(encoding='utf-8')
    assert 'unit="one-time capital"' in source
    assert 'def _donut(labels,values,total,colors,unit=' in source

def test_lifestyle_alert_no_markdown_artifacts():
    source=(ROOT/'pages/7_Financial_Decision_Summary.py').read_text(encoding='utf-8')
    assert 'Required post-purchase surplus: **' not in source

def test_screenshot_gallery_files_exist():
    images=list((ROOT/'docs/screenshots').glob('*.png'))
    assert len(images)>=20

def test_portfolio_case_study_exists():
    assert (ROOT/'docs/PORTFOLIO_CASE_STUDY.md').is_file()
