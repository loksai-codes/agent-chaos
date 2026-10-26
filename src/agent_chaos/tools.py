"""Typed registry of deterministic simulated tools."""

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from pydantic import BaseModel, ConfigDict

from . import world


class InputModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class ExchangeInput(InputModel):
    base: str
    quote: str


class RateOutput(BaseModel):
    rate: float


class PriceInput(InputModel):
    item: str


class PriceOutput(BaseModel):
    item: str
    price_usd: float


class DistanceInput(InputModel):
    origin: str
    destination: str


class DistanceOutput(BaseModel):
    km: float


class FuelInput(InputModel):
    country: str


class FuelOutput(BaseModel):
    usd_per_liter: float


class CalculatorInput(InputModel):
    expression: str


class CalculatorOutput(BaseModel):
    result: float


@dataclass(frozen=True)
class Tool:
    name: str
    description: str
    input_model: type[BaseModel]
    output_model: type[BaseModel]
    fn: Callable[..., dict[str, Any]]
    read_only: bool = True
    invariant: Callable[[dict[str, Any]], bool] | None = None


class ToolRegistry:
    def __init__(self, tools: list[Tool] | None = None) -> None:
        self._tools = {tool.name: tool for tool in (tools or default_tools())}

    def get(self, name: str) -> Tool:
        try:
            return self._tools[name]
        except KeyError as exc:
            raise KeyError(f"Unknown tool: {name}") from exc

    def all(self) -> list[Tool]:
        return list(self._tools.values())


def _bounded(key: str, maximum: float) -> Callable[[dict[str, Any]], bool]:
    return lambda value: 0 <= value[key] <= maximum


def _calculate(expression: str) -> dict[str, float]:
    # The calculator accepts arithmetic only; no names, calls, or attribute access.
    import ast
    import operator

    ops = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
           ast.Div: operator.truediv, ast.Pow: operator.pow, ast.USub: operator.neg,
           ast.UAdd: operator.pos}

    def visit(node: ast.AST) -> float:
        if isinstance(node, ast.Constant) and type(node.value) in (int, float):
            return float(node.value)
        if isinstance(node, ast.BinOp) and type(node.op) in ops:
            return ops[type(node.op)](visit(node.left), visit(node.right))
        if isinstance(node, ast.UnaryOp) and type(node.op) in ops:
            return ops[type(node.op)](visit(node.operand))
        raise ValueError("Unsupported calculator expression")

    return {"result": visit(ast.parse(expression, mode="eval").body)}


def default_tools() -> list[Tool]:
    return [
        Tool("get_exchange_rate", "Get a currency conversion rate.", ExchangeInput, RateOutput,
             lambda base, quote: {"rate": world.exchange_rate(base, quote)}, invariant=_bounded("rate", 10000)),
        Tool("get_price", "Get an item's USD price.", PriceInput, PriceOutput,
             lambda item: {"item": item, "price_usd": world.PRICES_USD[item]}, invariant=_bounded("price_usd", 1_000_000)),
        Tool("get_distance_km", "Get distance between two cities.", DistanceInput, DistanceOutput,
             lambda origin, destination: {"km": world.distance_km(origin, destination)}, invariant=_bounded("km", 50_000)),
        Tool("get_fuel_price", "Get fuel price in USD per liter.", FuelInput, FuelOutput,
             lambda country: {"usd_per_liter": world.FUEL_USD_PER_LITER[country]}, invariant=_bounded("usd_per_liter", 100)),
        Tool("calculator", "Evaluate a basic arithmetic expression.", CalculatorInput, CalculatorOutput,
             _calculate, invariant=lambda value: abs(value["result"]) < 1e15),
    ]
