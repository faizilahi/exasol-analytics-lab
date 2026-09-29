"""Synthetic Mid-Atlantic grocery POS + shrink — planted Tuesday totals."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
DATA.mkdir(parents=True, exist_ok=True)
RNG = np.random.default_rng(20240910)

# Worked Tuesday targets (must match README)
TUE = "2024-09-10"
TARGET_REV = 184220.40
TARGET_LIST_COGS = 134148.29  # => store-ops margin 50072.11 / 27.18%
TARGET_LANDED_COGS = 134977.90  # => +829.61 vs list
TARGET_SHRINK = 4812.50


def main() -> None:
    stores = pd.DataFrame(
        [
            {"store_id": "S-110", "region_id": "R-ATL-04", "banner": "Harbor Fresh", "sq_ft": 42000},
            {"store_id": "S-214", "region_id": "R-ATL-04", "banner": "Harbor Fresh", "sq_ft": 31000},
            {"store_id": "S-307", "region_id": "R-ATL-04", "banner": "Harbor Express", "sq_ft": 18000},
        ]
    )
    categories = ["Grocery", "Dairy", "Meat", "Produce", "HBA", "Frozen"]
    skus = pd.DataFrame(
        [
            {
                "sku_id": f"K-{i:03d}",
                "category": categories[i % 6],
                "dept_cd": categories[i % 6][:4].upper(),
                "list_cost": round(2.0 + (i % 17) * 0.75, 2),
                "landed_cost": round((2.0 + (i % 17) * 0.75) * 1.11, 2),
                "list_price": round((2.0 + (i % 17) * 0.75) / 0.72, 2),
            }
            for i in range(1, 61)
        ]
    )

    # Build proportional Tuesday lines, then scale to exact targets
    store_w = {"S-110": 0.42, "S-214": 0.35, "S-307": 0.23}
    tue_rows = []
    for store_id, w in store_w.items():
        n = int(140 * w / 0.23)  # ~ roughly proportional ticket counts
        for t in range(n):
            sku = skus.iloc[int(RNG.integers(0, len(skus)))]
            qty = int(RNG.integers(1, 6))
            tue_rows.append(
                {
                    "sale_date": TUE,
                    "store_id": store_id,
                    "sku_id": sku.sku_id,
                    "ticket_id": f"T-0910-{store_id}-{t:03d}",
                    "qty": qty,
                    "revenue": round(qty * float(sku.list_price), 2),
                    "list_cogs": round(qty * float(sku.list_cost), 2),
                    "landed_cogs": round(qty * float(sku.landed_cost), 2),
                }
            )
    tue = pd.DataFrame(tue_rows)
    tue = _scale_money(tue, TARGET_REV, TARGET_LIST_COGS, TARGET_LANDED_COGS)

    # Other weekdays — noisy, not calibrated
    other = []
    for d in pd.date_range("2024-09-09", "2024-09-15", freq="D"):
        ds = d.strftime("%Y-%m-%d")
        if ds == TUE:
            continue
        for store_id in store_w:
            for t in range(80):
                sku = skus.iloc[int(RNG.integers(0, len(skus)))]
                qty = int(RNG.integers(1, 5))
                other.append(
                    {
                        "sale_date": ds,
                        "store_id": store_id,
                        "sku_id": sku.sku_id,
                        "ticket_id": f"T-{d.strftime('%m%d')}-{store_id}-{t:03d}",
                        "qty": qty,
                        "revenue": round(qty * float(sku.list_price), 2),
                        "list_cogs": round(qty * float(sku.list_cost), 2),
                        "landed_cogs": round(qty * float(sku.landed_cost), 2),
                    }
                )
    sales = pd.concat([tue, pd.DataFrame(other)], ignore_index=True)

    shrink = pd.DataFrame(
        [
            {"post_date": TUE, "store_id": "S-110", "reason_cd": "THEFT", "shrink_amt": 2100.00},
            {"post_date": TUE, "store_id": "S-214", "reason_cd": "SPOIL", "shrink_amt": 1587.50},
            {"post_date": TUE, "store_id": "S-307", "reason_cd": "COUNT", "shrink_amt": 1125.00},
            {"post_date": "2024-09-11", "store_id": "S-110", "reason_cd": "SPOIL", "shrink_amt": 340.00},
        ]
    )
    assert round(float(shrink.loc[shrink["post_date"] == TUE, "shrink_amt"].sum()), 2) == TARGET_SHRINK

    stores.to_csv(DATA / "dim_store.csv", index=False)
    skus.to_csv(DATA / "dim_sku.csv", index=False)
    sales.to_csv(DATA / "fact_sales.csv", index=False)
    shrink.to_csv(DATA / "fact_shrink_adj.csv", index=False)

    meta = {
        "tuesday_revenue": round(float(tue["revenue"].sum()), 2),
        "tuesday_list_cogs": round(float(tue["list_cogs"].sum()), 2),
        "tuesday_landed_cogs": round(float(tue["landed_cogs"].sum()), 2),
        "tuesday_shrink": TARGET_SHRINK,
        "store_ops_margin_pct": round(
            (TARGET_REV - TARGET_LIST_COGS) / TARGET_REV, 4
        ),
        "region_margin_pct": round(
            (TARGET_REV - TARGET_LANDED_COGS - TARGET_SHRINK) / TARGET_REV, 4
        ),
    }
    (DATA / "generator_meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    print("Wrote synthetic retail facts:", meta)


def _scale_money(
    df: pd.DataFrame, rev: float, list_cogs: float, landed_cogs: float
) -> pd.DataFrame:
    out = df.copy()
    for col, target in (
        ("revenue", rev),
        ("list_cogs", list_cogs),
        ("landed_cogs", landed_cogs),
    ):
        cur = float(out[col].sum())
        if cur == 0:
            raise ValueError(col)
        out[col] = (out[col] * (target / cur)).round(2)
        # fix penny drift on last row
        drift = round(target - float(out[col].sum()), 2)
        out.iloc[-1, out.columns.get_loc(col)] = round(
            float(out.iloc[-1][col]) + drift, 2
        )
    return out


if __name__ == "__main__":
    main()
