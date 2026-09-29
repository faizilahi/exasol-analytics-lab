"""
Settlement engine for the Tuesday gross-margin argument.

Rebuilds store-ops (list cost, no shrink) vs region pack (landed + shrink)
using Exasol-style set SQL on DuckDB.
"""
from __future__ import annotations

from pathlib import Path

import duckdb
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUT = ROOT / "output"
SQL = ROOT / "sql"
OUT.mkdir(parents=True, exist_ok=True)


def connect() -> duckdb.DuckDBPyConnection:
    con = duckdb.connect()
    for name in ("dim_store", "dim_sku", "fact_sales", "fact_shrink_adj"):
        path = (DATA / f"{name}.csv").as_posix()
        con.execute(f"CREATE OR REPLACE TABLE {name} AS SELECT * FROM read_csv_auto('{path}')")
    return con


def run_settlement(con: duckdb.DuckDBPyConnection) -> dict:
    ddl = (SQL / "01_ddl_and_distribution.sql").read_text(encoding="utf-8")
    settle = (SQL / "02_tuesday_settlement.sql").read_text(encoding="utf-8")
    # DDL file is comments + CREATE VIEW; execute statements split by semicolon carefully
    for stmt in _statements(ddl + "\n" + settle):
        con.execute(stmt)

    settlement = con.execute("SELECT * FROM tuesday_settlement").df()
    comparison = con.execute("SELECT * FROM store_vs_region").df()
    by_store = con.execute("SELECT * FROM tuesday_by_store").df()

    settlement.to_csv(OUT / "tuesday_settlement.csv", index=False)
    comparison.to_csv(OUT / "store_vs_region.csv", index=False)
    by_store.to_csv(OUT / "tuesday_by_store.csv", index=False)

    row = settlement.iloc[0].to_dict()
    return row


def _statements(sql_text: str) -> list[str]:
    lines = []
    for line in sql_text.splitlines():
        if line.strip().startswith("--"):
            continue
        lines.append(line)
    blob = "\n".join(lines)
    return [s.strip() for s in blob.split(";") if s.strip()]


def explain_delta(row: dict) -> pd.DataFrame:
    """Break the store-ops vs region gap into shrink and cost-basis pieces."""
    store_margin_dollars = float(row["store_ops_margin_dollars"])
    region_margin_dollars = float(row["region_margin_dollars"])
    shrink = float(row["shrink_amt"])
    cost_basis = store_margin_dollars - region_margin_dollars - shrink
    return pd.DataFrame(
        [
            {"component": "store_ops_margin_dollars", "amount": round(store_margin_dollars, 2)},
            {"component": "less_shrink_journal", "amount": round(-shrink, 2)},
            {"component": "less_landed_vs_list_cost", "amount": round(-cost_basis, 2)},
            {"component": "region_margin_dollars", "amount": round(region_margin_dollars, 2)},
            {
                "component": "check_sum_to_region",
                "amount": round(store_margin_dollars - shrink - cost_basis, 2),
            },
        ]
    )


def distribution_note(con: duckdb.DuckDBPyConnection) -> pd.DataFrame:
    """Synthetic EXPLAIN-style note: row counts by distribution key cardinality."""
    return con.execute(
        """
        SELECT
          'hash(store_id)' AS distribution_key,
          COUNT(DISTINCT store_id) AS distinct_keys,
          COUNT(*) AS fact_rows,
          ROUND(COUNT(*) * 1.0 / COUNT(DISTINCT store_id), 1) AS rows_per_key
        FROM fact_sales
        WHERE sale_date = '2024-09-10'
        UNION ALL
        SELECT
          'hash(sku_id)',
          COUNT(DISTINCT sku_id),
          COUNT(*),
          ROUND(COUNT(*) * 1.0 / COUNT(DISTINCT sku_id), 1)
        FROM fact_sales
        WHERE sale_date = '2024-09-10'
        """
    ).df()


def main() -> None:
    con = connect()
    row = run_settlement(con)
    bridge = explain_delta(row)
    bridge.to_csv(OUT / "margin_bridge.csv", index=False)
    dist = distribution_note(con)
    dist.to_csv(OUT / "distribution_note.csv", index=False)

    print("Tuesday settlement")
    print(pd.DataFrame([row]).to_string(index=False))
    print("\nMargin bridge")
    print(bridge.to_string(index=False))
    print("\nDistribution note")
    print(dist.to_string(index=False))


if __name__ == "__main__":
    main()
