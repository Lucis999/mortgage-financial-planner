from comfort_ui import comfort_level

def test_critical_for_cash_shortfall():assert comfort_level(-1,10000,.2)==0

def test_critical_for_reserve_shortfall():assert comfort_level(3000,-1,.2)==0

def test_comfortable_high_buffer():assert comfort_level(3000,50000,.2)==6

def test_tight_housing_share():assert comfort_level(3000,50000,.6)==2
