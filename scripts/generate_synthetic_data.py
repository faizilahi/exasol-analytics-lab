import numpy as np, pandas as pd
from pathlib import Path
RNG = np.random.default_rng(42)
ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"; DATA.mkdir(parents=True, exist_ok=True)
stores = pd.DataFrame({"store_id":[f"S{i:03d}" for i in range(1,21)],
  "region": RNG.choice(["North","South","East","West"],20),
  "format": RNG.choice(["Flagship","Express","Outlet"],20)})
skus = pd.DataFrame({"sku_id":[f"K{i:04d}" for i in range(1,51)],
  "category": RNG.choice(["Grocery","Apparel","Electronics","Home"],50),
  "unit_cost": RNG.uniform(2,80,50).round(2)})
rows=[]
for d in pd.date_range("2024-01-01","2024-06-30",freq="D"):
  n=int(RNG.integers(80,140))
  for _ in range(n):
    s=stores.sample(1,random_state=int(RNG.integers(0,1e9))).iloc[0]
    k=skus.sample(1,random_state=int(RNG.integers(0,1e9))).iloc[0]
    qty=int(RNG.integers(1,6)); price=round(float(k.unit_cost)*(1+RNG.uniform(0.15,0.55)),2)
    rows.append({"sale_date":d.date(),"store_id":s.store_id,"sku_id":k.sku_id,"qty":qty,
      "revenue":round(qty*price,2),"cogs":round(qty*float(k.unit_cost),2)})
stores.to_csv(DATA/"dim_store.csv",index=False); skus.to_csv(DATA/"dim_sku.csv",index=False)
pd.DataFrame(rows).to_csv(DATA/"fact_sales.csv",index=False)
print("Wrote Exasol lab synthetic data", DATA)

