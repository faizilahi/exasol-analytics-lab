# Exasol Analytics Lab (Columnar MPP Patterns)

**Author:** [Faiz Elahi](https://github.com/faizilahi) (`faizilahi`) · **Type:** EDUCATIONAL LAB · **Synthetic data only**

---

## Educational disclaimer

This is an **educational portfolio lab**. Datasets are **synthetic**. It does **not** claim employment at a customer, hospital, bank, SAP shop, or Oracle estate. No real PHI/PII. No live cloud spend. No API keys required.

---

## Problem statement

Teams need interactive SQL on large fact tables with MPP-minded set-based joins, hash distribution teaching notes, and low-latency aggregates for merchandising and risk packs.

**Domain focus:** Retail / finance analytics

---

## Why this tool (Exasol-style columnar MPP SQL (DuckDB stand-in))

| Spreadsheet rollups | Exasol-style SQL on a columnar engine |
|---|---|
| Opaque joins | Explicit star-schema SQL |
| No distribution thinking | Documented partition/distribution notes |

---

## Architecture

```mermaid
flowchart LR
  GEN[generate_synthetic_data.py]
  DATA[data/*.csv]
  RUN[run_lab.py]
  OUT[output/*.csv]
  CHART[generate_charts.py]
  IMG[docs/images/*.png]
  GEN --> DATA --> RUN --> OUT
  OUT --> CHART --> IMG
```

See [`docs/architecture.md`](docs/architecture.md).

---

## Dataset dictionary

| File | Grain | Notes |
|------|-------|-------|
| `dim_store.csv` | Store | Region, format |
| `dim_sku.csv` | SKU | Category, unit cost |
| `fact_sales.csv` | Sale line | Store/day/SKU revenue |
| `output/summary.csv` | Region×category | Margin and revenue |

---

## Prerequisites

- Python 3.10+
- Packages in `requirements.txt`

---

## How to run

```powershell
cd "exasol-analytics-lab-"
python -m venv .venv
.\\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python scripts/generate_synthetic_data.py
python src/run_lab.py
python scripts/generate_charts.py
```

Inspect `output/summary.csv` and `docs/images/primary_metric.png`.

---

## Local vs cloud (honest)

**DuckDB** stands in for Exasol locally. No Exasol cluster, license, or cloud SaaS is used. SQL dialect is ANSI-leaning with teaching comments for Exasol habits (distribution keys, LUTs).

---

## Results interpretation

Open `output/` CSVs and the PNGs under `docs/images/`. Numbers are synthetic teaching fixtures — use them to explain grain, filters, and control totals, not as real business KPIs.

---

## Limitations

- Stand-in engines (DuckDB/SQLite/pandas) replace paid MPP/warehouses where noted.
- Simplified schemas vs production SAP/Oracle/Hive estates.
- Charts are matplotlib teaching visuals, not vendor BI embeds.

---

## Exercises

1. Add a distribution-key note choosing `store_id` vs `sku_id`.
2. Rewrite the margin query with a ROLLUP teaching CTE.
3. Plant a bad join and catch it with a control total.

---

## License / attribution

Educational portfolio content by Faiz Elahi. Synthetic data for teaching only.

