from io import BytesIO
from openpyxl import load_workbook
from model import Inputs
from report import make_report
from rent_vs_buy import Comparison
from asset_model import AssetProfile
import pytest

@pytest.mark.parametrize("path", ["income","asset"])
def test_report_financing_pathways(path):
    x=Inputs()
    profile=AssetProfile(300000,550000,1,0.35,1.0,60000,0.25)
    data=make_report(x,asset_profile=profile,comparison=Comparison(monthly_rent=2700,years=5),financing=path)
    wb=load_workbook(BytesIO(data),read_only=True)
    assert len(wb.sheetnames)>=2
    assert len(data)>2000
