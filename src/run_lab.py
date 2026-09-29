"""Exasol-pattern analytics on DuckDB stand-in."""
from pathlib import Path
import duckdb, pandas as pd
ROOT = Path(__file__).resolve().parents[1]
DATA, OUT = ROOT/"data", ROOT/"output"; OUT.mkdir(parents=True, exist_ok=True)
con = duckdb.connect()
con.execute(f"CREATE TABLE dim_store AS SELECT * FROM read_csv_auto('{(DATA/'dim_store.csv').as_posix()}')")
con.execute(f"CREATE TABLE dim_sku AS SELECT * FROM read_csv_auto('{(DATA/'dim_sku.csv').as_posix()}')")
con.execute(f"CREATE TABLE fact_sales AS SELECT * FROM read_csv_auto('{(DATA/'fact_sales.csv').as_posix()}')")
# Teaching note: prefer distributing fact on store_id for regional packs
sql = """
SELECT s.region, k.category,
       ROUND(SUM(f.revenue),2) AS revenue,
       ROUND(SUM(f.revenue-f.cogs),2) AS margin,
       ROUND(SUM(f.revenue-f.cogs)/NULLIF(SUM(f.revenue),0),4) AS margin_pct
FROM fact_sales f
JOIN dim_store s USING(store_id)
JOIN dim_sku k USING(sku_id)
GROUP BY 1,2
ORDER BY revenue DESC
"""
df = con.execute(sql).df()
df.to_csv(OUT/"summary.csv", index=False)
pd.DataFrame([{"metric":"fact_rows","value":len(pd.read_csv(DATA/"fact_sales.csv"))}]).to_csv(OUT/"control_totals.csv", index=False)
print(df.head())
print("Wrote", OUT/"summary.csv")

