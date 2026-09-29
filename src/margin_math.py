"""Margin diagnostics helpers used by run_settlement and tests."""
from __future__ import annotations


def margin_pct(revenue: float, margin_dollars: float) -> float:
    if revenue == 0:
        return 0.0
    return round(margin_dollars / revenue, 4)


def bridge_components(
    store_ops_margin: float, region_margin: float, shrink: float
) -> dict[str, float]:
    cost_basis = round(store_ops_margin - region_margin - shrink, 2)
    return {
        "shrink": round(shrink, 2),
        "landed_vs_list": cost_basis,
        "explained": round(shrink + cost_basis, 2),
        "observed_gap": round(store_ops_margin - region_margin, 2),
    }


def assert_bridge_closes(store_ops: float, region: float, shrink: float, tol: float = 0.02) -> bool:
    parts = bridge_components(store_ops, region, shrink)
    return abs(parts["explained"] - parts["observed_gap"]) <= tol
