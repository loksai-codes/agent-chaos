"""Fixed in-memory ground truth used by every simulated tool."""

from __future__ import annotations

EXCHANGE_USD = {"USD": 1.0, "EUR": 0.92, "GBP": 0.79, "INR": 83.1, "JPY": 150.0}
PRICES_USD = {
    "laptop": 1200.0, "phone": 800.0, "tablet": 500.0, "headphones": 150.0,
    "monitor": 350.0, "keyboard": 80.0, "camera": 950.0, "coffee": 4.5,
}
DISTANCES_KM = {
    ("New York", "Boston"): 306.0, ("Boston", "New York"): 306.0,
    ("San Francisco", "Los Angeles"): 617.0, ("Los Angeles", "San Francisco"): 617.0,
    ("London", "Manchester"): 336.0, ("Manchester", "London"): 336.0,
    ("Delhi", "Mumbai"): 1420.0, ("Mumbai", "Delhi"): 1420.0,
    ("Paris", "Lyon"): 465.0, ("Lyon", "Paris"): 465.0,
    ("Tokyo", "Osaka"): 515.0, ("Osaka", "Tokyo"): 515.0,
}
FUEL_USD_PER_LITER = {"USA": 1.05, "UK": 1.82, "India": 1.12, "Japan": 1.16, "France": 1.95}


def exchange_rate(base: str, quote: str) -> float:
    """Return units of quote currency per unit of base currency."""
    return EXCHANGE_USD[quote] / EXCHANGE_USD[base]


def distance_km(origin: str, destination: str) -> float:
    if origin == destination:
        return 0.0
    return DISTANCES_KM[(origin, destination)]


def ground_truth(task_id: str) -> float:
    """Compute task answers without consulting faultable tools."""
    if task_id == "laptops_eur":
        return 3 * PRICES_USD["laptop"] * exchange_rate("USD", "EUR")
    if task_id == "phone_gbp":
        return 2 * PRICES_USD["phone"] * exchange_rate("USD", "GBP")
    if task_id == "trip_ny_boston":
        return distance_km("New York", "Boston") * 0.08 * FUEL_USD_PER_LITER["USA"]
    if task_id == "trip_sf_la":
        return distance_km("San Francisco", "Los Angeles") * 0.07 * FUEL_USD_PER_LITER["USA"]
    if task_id == "camera_inr":
        return PRICES_USD["camera"] * exchange_rate("USD", "INR")
    if task_id == "monitor_jpy":
        return PRICES_USD["monitor"] * exchange_rate("USD", "JPY")
    if task_id == "coffee_trip":
        return PRICES_USD["coffee"] * 5 + distance_km("London", "Manchester") * 0.06 * FUEL_USD_PER_LITER["UK"]
    if task_id == "tablet_eur_tax":
        return PRICES_USD["tablet"] * exchange_rate("USD", "EUR") * 1.2
    raise KeyError(f"Unknown task: {task_id}")
