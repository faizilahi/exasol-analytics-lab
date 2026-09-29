# Gross Margin Tuesday: Stores vs Region (Exasol-style SQL)

[Faiz Elahi](https://www.linkedin.com/in/faizilahi) — [pendataco.com](https://pendataco.com) — [github.com/faizilahi](https://github.com/faizilahi)

Synthetic retail POS and shrink adjustments only. No vendor employment claim.

A Mid-Atlantic grocery region manager and three store GMs argued about a Tuesday gross-margin print. The region pack showed **24.1%**. Store ops insisted their registers were closer to **27%**. The gap was distribution of the sales fact (hash on `sku_id` for category packs) plus a late shrink journal that only the region cube absorbed. This lab rebuilds the argument in Exasol-flavored SQL on DuckDB, settles the number, and leaves the worked totals in `output/`.

## The Tuesday number

Week of 2024-09-09. Region `R-ATL-04`, stores `S-110`, `S-214`, `S-307`.

| Source | Gross margin % | Revenue | Margin $ |
|--------|----------------|---------|----------|
| Store-ops register rollup (local) | 27.18% | $184,220.40 | $50,072.11 |
| Region Tuesday pack (distributed fact + shrink) | 24.12% | $184,220.40 | $44,430.00 |
| Settled query (this lab) | **24.12%** | $184,220.40 | $44,430.00 |

Store rollups omitted the `shrink_adj` fact and used list cost instead of landed cost. Same tickets, different cost basis and missing journal.

## Distribution of the fact

Exasol teaching pattern: distribute the largest fact on the join key you filter most. Category Monday packs want `DISTRIBUTE BY sku_id`. Region Tuesday packs want `DISTRIBUTE BY store_id`. This lab’s DDL comment and `EXPLAIN`-style note live in `sql/01_ddl_and_distribution.sql`. The generator plants a deliberate skew so `store_id` distribution keeps region filters local while a `sku_id`-only layout would reshuffle every Tuesday pack.

## The query that settled it

`sql/02_tuesday_settlement.sql` joins `fact_sales` to landed-cost dim, left-joins `fact_shrink_adj` for the Tuesday post, and computes margin as `(revenue - landed_cogs - shrink_amt) / revenue`. Output lands in `output/tuesday_settlement.csv` and `output/store_vs_region.csv`.

```powershell
pip install -r requirements.txt
python scripts/generate_synthetic_data.py
python src/run_settlement.py
```

Worked result after a clean run: region margin **24.12%**, store-ops inflated print **27.18%**, delta explained entirely by shrink ($4,812.50) plus landed-vs-list cost ($829.61).
