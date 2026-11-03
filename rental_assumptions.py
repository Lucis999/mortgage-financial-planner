"""Illustrative rent estimate; user-entered examples, not market observations."""
from dataclasses import dataclass

RENT_PRESETS = {
    "1 bedroom · example": (2100.0, 0.0),
    "2 bedrooms · example": (3000.0, 0.0),
    "Townhouse · example": (3200.0, 0.0),
    "Custom annual yield": (None, None),
}

def annual_rent_yield(monthly_rent: float, property_price: float) -> float:
    if property_price <= 0 or monthly_rent < 0:
        raise ValueError("Property price must be positive and rent nonnegative")
    return 12 * monthly_rent / property_price

def monthly_rent_from_yield(property_price: float, annual_yield: float) -> float:
    if property_price <= 0 or annual_yield < 0:
        raise ValueError("Property price must be positive and annual yield nonnegative")
    return property_price * annual_yield / 12

def all_in_rent(base_rent: float, utilities: float, internet: float, other: float) -> float:
    if min(base_rent, utilities, internet, other) < 0:
        raise ValueError("Rent cost components must be nonnegative")
    return base_rent + utilities + internet + other


def implied_rental_property_value(monthly_base_rent: float, annual_gross_yield: float) -> float:
    if monthly_base_rent < 0 or annual_gross_yield <= 0:
        raise ValueError("Base rent must be nonnegative and gross yield must be positive")
    return 12 * monthly_base_rent / annual_gross_yield

def property_price_gap(purchase_price: float, rental_implied_price: float) -> float:
    return purchase_price-rental_implied_price
