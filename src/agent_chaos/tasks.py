"""Small arithmetic tasks that exercise multiple tools."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, Protocol

from . import world


class CallContext(Protocol):
    def call(self, tool_name: str, **args: Any) -> Any: ...


@dataclass(frozen=True)
class Task:
    id: str
    prompt: str
    solve: Callable[[CallContext], float]
    answer: float
    tolerance: float = 0.01


def _laptops(ctx: CallContext) -> float:
    price = ctx.call("get_price", item="laptop")["price_usd"]
    rate = ctx.call("get_exchange_rate", base="USD", quote="EUR")["rate"]
    return price * 3 * rate


def _phone(ctx: CallContext) -> float:
    price = ctx.call("get_price", item="phone")["price_usd"]
    rate = ctx.call("get_exchange_rate", base="USD", quote="GBP")["rate"]
    return price * 2 * rate


def _trip(origin: str, destination: str, country: str, consumption: float) -> Callable[[CallContext], float]:
    def solve(ctx: CallContext) -> float:
        km = ctx.call("get_distance_km", origin=origin, destination=destination)["km"]
        fuel = ctx.call("get_fuel_price", country=country)["usd_per_liter"]
        return km * consumption * fuel
    return solve


def _camera(ctx: CallContext) -> float:
    return ctx.call("get_price", item="camera")["price_usd"] * ctx.call("get_exchange_rate", base="USD", quote="INR")["rate"]


def _monitor(ctx: CallContext) -> float:
    return ctx.call("get_price", item="monitor")["price_usd"] * ctx.call("get_exchange_rate", base="USD", quote="JPY")["rate"]


def _coffee_trip(ctx: CallContext) -> float:
    coffees = ctx.call("get_price", item="coffee")["price_usd"]
    km = ctx.call("get_distance_km", origin="London", destination="Manchester")["km"]
    fuel = ctx.call("get_fuel_price", country="UK")["usd_per_liter"]
    return coffees * 5 + km * 0.06 * fuel


def _tablet_tax(ctx: CallContext) -> float:
    price = ctx.call("get_price", item="tablet")["price_usd"]
    rate = ctx.call("get_exchange_rate", base="USD", quote="EUR")["rate"]
    return price * rate * 1.2


TASKS = [
    Task("laptops_eur", "How much do 3 laptops cost in EUR?", _laptops, world.ground_truth("laptops_eur")),
    Task("phone_gbp", "How much do 2 phones cost in GBP?", _phone, world.ground_truth("phone_gbp")),
    Task("trip_ny_boston", "Fuel cost for New York to Boston at 8 L/100 km, USD.", _trip("New York", "Boston", "USA", .08), world.ground_truth("trip_ny_boston")),
    Task("trip_sf_la", "Fuel cost for San Francisco to Los Angeles at 7 L/100 km, USD.", _trip("San Francisco", "Los Angeles", "USA", .07), world.ground_truth("trip_sf_la")),
    Task("camera_inr", "What does a camera cost in INR?", _camera, world.ground_truth("camera_inr")),
    Task("monitor_jpy", "What does a monitor cost in JPY?", _monitor, world.ground_truth("monitor_jpy")),
    Task("coffee_trip", "Five coffees plus fuel for London to Manchester at 6 L/100 km.", _coffee_trip, world.ground_truth("coffee_trip")),
    Task("tablet_eur_tax", "A tablet in EUR with 20% tax: total?", _tablet_tax, world.ground_truth("tablet_eur_tax")),
]


def get_task(task_id: str) -> Task:
    return next(task for task in TASKS if task.id == task_id)
