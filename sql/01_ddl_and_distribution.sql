-- Exasol-flavored teaching DDL (executed on DuckDB stand-in).
-- Region Tuesday packs: DISTRIBUTE BY store_id so region filters stay node-local.
-- Category Monday packs would instead DISTRIBUTE BY sku_id.

-- CREATE TABLE fact_sales (
--   sale_date DATE,
--   store_id VARCHAR(16),
--   sku_id VARCHAR(32),
--   ticket_id VARCHAR(32),
--   qty INTEGER,
--   revenue DECIMAL(18,2),
--   list_cogs DECIMAL(18,2),
--   landed_cogs DECIMAL(18,2)
-- ) DISTRIBUTE BY HASH(store_id) -- region path
-- ;

CREATE OR REPLACE VIEW v_fact_sales_distributed AS
SELECT
  sale_date,
  store_id,
  sku_id,
  ticket_id,
  qty,
  revenue,
  list_cogs,
  landed_cogs,
  -- surrogate of hash distribution bucket for teaching diagnostics
  MOD(ABS(HASH(store_id)), 3) AS store_dist_bucket,
  MOD(ABS(HASH(sku_id)), 8) AS sku_dist_bucket
FROM fact_sales;
