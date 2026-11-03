import pytest
from rental_assumptions import annual_rent_yield,monthly_rent_from_yield,all_in_rent

def test_700k_3000_per_month():
    assert annual_rent_yield(3000,700000)==pytest.approx(36000/700000)
def test_annual_yield_roundtrip():
    assert monthly_rent_from_yield(700000,36000/700000)==pytest.approx(3000)
def test_rent_included_services_not_double_counted():
    assert all_in_rent(3000,0,0,0)==3000
def test_rent_separate_services():
    assert all_in_rent(2800,120,80,0)==3000
def test_invalid_yield():
    with pytest.raises(ValueError):annual_rent_yield(3000,0)
