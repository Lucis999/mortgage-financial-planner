from asset_trajectory import ProjectionSettings,project_assets
from asset_model import AssetProfile
from model import Inputs

def test_total_loss_return_supported():
    x=Inputs()
    a=AssetProfile(300000,550000,1,.35,1,60000,.25)
    rows=project_assets(x,a,ProjectionSettings(years=1,shock_year=1,investment_return=-1,invested_share=.5))
    assert len(rows)==12
    assert all(row["investments"]>=-1e-6 for row in rows)

def test_invested_share_changes_initial_investment_gain():
    x=Inputs()
    a=AssetProfile(300000,550000,1,.35,1,60000,.25)
    settings=dict(years=1,shock_year=1,investment_return=.05,investment_drawdown=0)
    low=project_assets(x,a,ProjectionSettings(**settings,invested_share=.1))[0]
    high=project_assets(x,a,ProjectionSettings(**settings,invested_share=.9))[0]
    assert high["investment_gain"]>low["investment_gain"]
