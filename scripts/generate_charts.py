"""Generate matplotlib charts for Exasol Analytics Lab (Columnar MPP Patterns)."""
from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output"
IMG = ROOT / "docs" / "images"
IMG.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(OUT / "summary.csv")
fig, ax = plt.subplots(figsize=(8, 4.5))
ax.bar(df["region"].astype(str), df["revenue"], color="#2E86AB")
ax.set_title("Exasol-pattern regional revenue (synthetic)")
ax.set_ylabel("revenue")
plt.xticks(rotation=25, ha="right")
fig.tight_layout()
fig.savefig(IMG / "primary_metric.png", dpi=120)
plt.close()

fig2, ax2 = plt.subplots(figsize=(7, 4))
ax2.plot(range(len(df)), df["revenue"], marker="o", color="#A23B72")
ax2.set_title("Exasol-pattern regional revenue (synthetic) — trend view")
ax2.set_ylabel("revenue")
fig2.tight_layout()
fig2.savefig(IMG / "trend.png", dpi=120)
plt.close()
print(f"Wrote charts to {IMG}")

