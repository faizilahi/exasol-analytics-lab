-- The query that settled the Tuesday argument between stores and region.

CREATE OR REPLACE VIEW tuesday_sales AS
SELECT
  f.sale_date,
  f.store_id,
  s.region_id,
  f.sku_id,
  f.revenue,
  f.list_cogs,
  f.landed_cogs
FROM fact_sales f
JOIN dim_store s USING (store_id)
WHERE f.sale_date = '2024-09-10'
  AND s.region_id = 'R-ATL-04';

CREATE OR REPLACE VIEW tuesday_shrink AS
SELECT store_id, SUM(shrink_amt) AS shrink_amt
FROM fact_shrink_adj
WHERE post_date = '2024-09-10'
GROUP BY store_id;

CREATE OR REPLACE VIEW tuesday_by_store AS
SELECT
  t.store_id,
  ROUND(SUM(t.revenue), 2) AS revenue,
  ROUND(SUM(t.list_cogs), 2) AS list_cogs,
  ROUND(SUM(t.landed_cogs), 2) AS landed_cogs,
  ROUND(COALESCE(MAX(sh.shrink_amt), 0), 2) AS shrink_amt,
  ROUND(SUM(t.revenue) - SUM(t.list_cogs), 2) AS store_ops_margin_dollars,
  ROUND(
    (SUM(t.revenue) - SUM(t.list_cogs)) / NULLIF(SUM(t.revenue), 0),
    4
  ) AS store_ops_margin_pct,
  ROUND(
    SUM(t.revenue) - SUM(t.landed_cogs) - COALESCE(MAX(sh.shrink_amt), 0),
    2
  ) AS region_margin_dollars,
  ROUND(
    (SUM(t.revenue) - SUM(t.landed_cogs) - COALESCE(MAX(sh.shrink_amt), 0))
      / NULLIF(SUM(t.revenue), 0),
    4
  ) AS region_margin_pct
FROM tuesday_sales t
LEFT JOIN tuesday_shrink sh USING (store_id)
GROUP BY t.store_id;

CREATE OR REPLACE VIEW tuesday_settlement AS
SELECT
  '2024-09-10' AS sale_date,
  'R-ATL-04' AS region_id,
  ROUND(SUM(revenue), 2) AS revenue,
  ROUND(SUM(list_cogs), 2) AS list_cogs,
  ROUND(SUM(landed_cogs), 2) AS landed_cogs,
  ROUND(SUM(shrink_amt), 2) AS shrink_amt,
  ROUND(SUM(store_ops_margin_dollars), 2) AS store_ops_margin_dollars,
  ROUND(SUM(store_ops_margin_dollars) / NULLIF(SUM(revenue), 0), 4) AS store_ops_margin_pct,
  ROUND(SUM(region_margin_dollars), 2) AS region_margin_dollars,
  ROUND(SUM(region_margin_dollars) / NULLIF(SUM(revenue), 0), 4) AS region_margin_pct
FROM tuesday_by_store;

CREATE OR REPLACE VIEW store_vs_region AS
SELECT
  store_id,
  revenue,
  store_ops_margin_pct,
  region_margin_pct,
  ROUND(store_ops_margin_pct - region_margin_pct, 4) AS margin_pct_gap
FROM tuesday_by_store
ORDER BY store_id;
