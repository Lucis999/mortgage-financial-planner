from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def test_lifestyle_banner_plain_text():
    text=(ROOT/'pages/7_Financial_Decision_Summary.py').read_text(encoding='utf-8')
    assert 'Current estimated monthly surplus while renting:' in text
    assert 'Required post-purchase surplus:' in text
    assert '**{fmt(minimum_surplus)}' not in text
def test_capital_donut_not_monthly():
    text=(ROOT/'pages/1_Financial_Overview.py').read_text(encoding='utf-8')
    assert 'unit="one-time capital"' in text
    assert 'unit="total capital"' not in text
def test_final_screenshot_is_documented():
    text=(ROOT/'docs/screenshots/README.md').read_text(encoding='utf-8')
    assert '](decision-takeaway.png)' in text
    assert (ROOT/'docs/screenshots/decision-takeaway.png').is_file()
    assert 'pending final screenshot' not in text
