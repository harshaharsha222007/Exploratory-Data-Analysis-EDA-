"""
Exploratory Data Analysis (EDA) - Customer Orders Dataset
Run:  python eda_analysis.py
Needs: pandas, numpy, matplotlib, openpyxl (for .xlsx)
Charts are saved to ./eda_output/
"""
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ---------------- CONFIG: edit to match your file ----------------
FILE = "dataset.xlsx"        # path to your Excel file
SHEET = 0                    # sheet name or index
COL_ORDER = "OrderID"
COL_DATE = "Date"
COL_PRODUCT = "Product"
COL_QTY = "Quantity"
COL_UNIT = "UnitPrice"
COL_TOTAL = "TotalPrice"
COL_COUPON = "CouponCode"
COL_CART = "ItemsInCart"     # set to None if the column does not exist
# -----------------------------------------------------------------

OUT = "eda_output"
os.makedirs(OUT, exist_ok=True)
plt.rcParams.update({"figure.dpi": 120, "axes.spines.top": False, "axes.spines.right": False})
TEAL, AMBER, INK = "#2EC4B6", "#F5A524", "#0F1B2D"


def section(title):
    print("\n" + "=" * 60 + f"\n{title}\n" + "=" * 60)


# 1. LOAD & INSPECT ---------------------------------------------------------
df = pd.read_excel(FILE, sheet_name=SHEET)
section("1. STRUCTURE")
print("Shape:", df.shape)
print(df.dtypes)
print(df.head())

# 2. DATA QUALITY -----------------------------------------------------------
section("2. DATA QUALITY")
missing = df.isna().sum()
print("Missing values per column:\n", missing[missing > 0])
print("Duplicate rows:", df.duplicated().sum())
if COL_DATE in df:
    df[COL_DATE] = pd.to_datetime(df[COL_DATE], errors="coerce")

# 3. DESCRIPTIVE STATISTICS (count, mean, median, ...) ----------------------
section("3. DESCRIPTIVE STATISTICS")
num_cols = [c for c in [COL_QTY, COL_UNIT, COL_TOTAL, COL_CART] if c and c in df]
stats = df[num_cols].agg(["count", "mean", "median", "std", "min", "max"]).T
stats["skew"] = df[num_cols].skew()
print(stats.round(2))
stats.round(2).to_csv(f"{OUT}/descriptive_stats.csv")

# 4. DISTRIBUTIONS ----------------------------------------------------------
section("4. DISTRIBUTIONS")
fig, axes = plt.subplots(1, len(num_cols), figsize=(4 * len(num_cols), 3.5))
for ax, c in zip(np.atleast_1d(axes), num_cols):
    ax.hist(df[c].dropna(), bins=30, color=TEAL, edgecolor="white")
    ax.axvline(df[c].mean(), color=AMBER, lw=2, label="mean")
    ax.axvline(df[c].median(), color=INK, lw=2, ls="--", label="median")
    ax.set_title(c)
    ax.legend(fontsize=8)
plt.tight_layout()
plt.savefig(f"{OUT}/distributions.png")
plt.close()
for c in num_cols:
    tag = "right-skewed" if df[c].skew() > 0.5 else "left-skewed" if df[c].skew() < -0.5 else "roughly symmetric"
    print(f"{c}: skew={df[c].skew():.2f} ({tag})")

# 5. OUTLIERS (IQR method) --------------------------------------------------
section("5. OUTLIERS (IQR)")
q1, q3 = df[COL_TOTAL].quantile([0.25, 0.75])
iqr = q3 - q1
lo, hi = q1 - 1.5 * iqr, q3 + 1.5 * iqr
out = df[(df[COL_TOTAL] < lo) | (df[COL_TOTAL] > hi)].sort_values(COL_TOTAL, ascending=False)
print(f"Q1={q1:.2f}  Q3={q3:.2f}  IQR={iqr:.2f}  fences=({lo:.2f}, {hi:.2f})")
print(f"Outliers found: {len(out)}")
print(out.head(10))
out.to_csv(f"{OUT}/outliers.csv", index=False)

fig, ax = plt.subplots(figsize=(7, 2.8))
ax.boxplot(df[COL_TOTAL].dropna(), vert=False, patch_artist=True,
           boxprops=dict(facecolor=TEAL), medianprops=dict(color=INK, lw=2),
           flierprops=dict(markerfacecolor=AMBER, markeredgecolor=AMBER))
ax.set_title(f"{COL_TOTAL} - box plot with IQR outliers")
plt.tight_layout()
plt.savefig(f"{OUT}/outliers_boxplot.png")
plt.close()

# 6. PRODUCT PERFORMANCE ----------------------------------------------------
section("6. PRODUCT PERFORMANCE")
prod = (df.groupby(COL_PRODUCT)
          .agg(orders=(COL_ORDER, "count"), revenue=(COL_TOTAL, "sum"), avg_order=(COL_TOTAL, "mean"))
          .sort_values("revenue", ascending=False))
print(prod.round(2))
prod.round(2).to_csv(f"{OUT}/product_performance.csv")

fig, axes = plt.subplots(1, 2, figsize=(10, 3.8))
prod["revenue"].sort_values().plot.barh(ax=axes[0], color=TEAL, title="Revenue by product")
prod["orders"].plot.bar(ax=axes[1], color=AMBER, title="Orders by product", rot=45)
plt.tight_layout()
plt.savefig(f"{OUT}/product_performance.png")
plt.close()

# 7. TRENDS OVER TIME -------------------------------------------------------
if COL_DATE in df:
    section("7. TRENDS")
    df["Year"] = df[COL_DATE].dt.year
    yearly = df.groupby("Year").agg(orders=(COL_ORDER, "count"),
                                    revenue=(COL_TOTAL, "sum"),
                                    avg_order=(COL_TOTAL, "mean"))
    print(yearly.round(2))
    print("Latest date in data:", df[COL_DATE].max().date(),
          "(a partial final year is not comparable with full years)")
    yearly.round(2).to_csv(f"{OUT}/yearly_trend.csv")

    fig, axes = plt.subplots(1, 2, figsize=(10, 3.6))
    yearly["orders"].plot(ax=axes[0], marker="o", color=TEAL, lw=3, title="Orders by year")
    yearly["avg_order"].plot.bar(ax=axes[1], color=AMBER, title="Average order value", rot=0)
    plt.tight_layout()
    plt.savefig(f"{OUT}/yearly_trend.png")
    plt.close()

    monthly = df.set_index(COL_DATE).resample("MS")[COL_TOTAL].agg(["count", "sum"])
    fig, ax = plt.subplots(figsize=(9, 3.5))
    monthly["count"].plot(ax=ax, color=TEAL, title="Monthly order volume")
    plt.tight_layout()
    plt.savefig(f"{OUT}/monthly_trend.png")
    plt.close()

# 8. RELATIONSHIPS (correlation) --------------------------------------------
section("8. CORRELATION WITH TOTAL PRICE")
corr = df[num_cols].corr(method="pearson")
print(corr.round(2))
corr.round(2).to_csv(f"{OUT}/correlation.csv")

fig, ax = plt.subplots(figsize=(5, 4.2))
im = ax.imshow(corr, cmap="YlGnBu", vmin=-1, vmax=1)
ax.set_xticks(range(len(corr)), corr.columns, rotation=45, ha="right")
ax.set_yticks(range(len(corr)), corr.columns)
for i in range(len(corr)):
    for j in range(len(corr)):
        ax.text(j, i, f"{corr.iloc[i, j]:.2f}", ha="center", va="center", fontsize=9)
plt.colorbar(im)
plt.tight_layout()
plt.savefig(f"{OUT}/correlation_heatmap.png")
plt.close()

fig, axes = plt.subplots(1, 2, figsize=(9, 3.6))
for ax, c in zip(axes, [COL_QTY, COL_UNIT]):
    ax.scatter(df[c], df[COL_TOTAL], s=10, alpha=0.4, color=TEAL)
    ax.set_xlabel(c)
    ax.set_ylabel(COL_TOTAL)
    ax.set_title(f"{c} vs {COL_TOTAL} (r = {df[c].corr(df[COL_TOTAL]):.2f})")
plt.tight_layout()
plt.savefig(f"{OUT}/scatter_relationships.png")
plt.close()

# 9. COUPON ANALYSIS --------------------------------------------------------
if COL_COUPON in df:
    section("9. COUPON USAGE")
    df["HasCoupon"] = df[COL_COUPON].notna()
    print(df["HasCoupon"].value_counts(normalize=True).round(3))
    print(df.groupby("HasCoupon")[COL_TOTAL].agg(["count", "mean", "median"]).round(2))

# 10. KEY OBSERVATIONS ------------------------------------------------------
section("10. KEY OBSERVATIONS")
print(f"- {len(df):,} orders analysed; mean {COL_TOTAL} {df[COL_TOTAL].mean():,.2f} vs median {df[COL_TOTAL].median():,.2f}")
print(f"- Top product by revenue: {prod.index[0]}; lowest: {prod.index[-1]}")
print(f"- {len(out)} outliers above the IQR upper fence ({hi:,.2f})")
print(f"- Corr with {COL_TOTAL}: " + ", ".join(f"{c}={corr.loc[c, COL_TOTAL]:.2f}" for c in num_cols if c != COL_TOTAL))
print(f"\nCharts and tables saved in ./{OUT}/")