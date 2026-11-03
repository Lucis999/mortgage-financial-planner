import pytest
from rental_assumptions import implied_rental_property_value,property_price_gap

def test_rent_1800_yield_55():
    assert implied_rental_property_value(1800,.055)==pytest.approx(392727.272727)

def test_price_gap():
    assert property_price_gap(700000,implied_rental_property_value(1800,.055))==pytest.approx(307272.727273)

def test_yield_must_be_positive():
    with pytest.raises(ValueError):implied_rental_property_value(1800,0)
