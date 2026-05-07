"""
Dashboard Streamlit untuk Proyek Analisis Data: E-Commerce Public Dataset (Olist).

Cara menjalankan secara lokal:
    streamlit run dashboard.py

Dashboard ini memvisualisasikan jawaban dari kedua pertanyaan bisnis pada notebook,
yaitu (1) tren pesanan & revenue beserta kategori unggulan, dan (2) distribusi
geografis & segmentasi RFM pelanggan.
"""

import os
import pandas as pd
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns

# ---------------------------------------------------------------------------
# Konfigurasi halaman
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Olist E-Commerce Dashboard",
    page_icon="🛒",
    layout="wide",
)

sns.set_style("whitegrid")
plt.rcParams["font.size"] = 10


# ---------------------------------------------------------------------------
# Load data (di-cache agar cepat)
# ---------------------------------------------------------------------------
@st.cache_data
def load_data():
    """Memuat main_data.csv dari folder yang sama dengan dashboard.py."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(base_dir, "main_data.csv")
    df = pd.read_csv(csv_path)
    df["order_purchase_timestamp"] = pd.to_datetime(df["order_purchase_timestamp"])
    df["order_delivered_customer_date"] = pd.to_datetime(
        df["order_delivered_customer_date"], errors="coerce"
    )
    df["order_estimated_delivery_date"] = pd.to_datetime(
        df["order_estimated_delivery_date"], errors="coerce"
    )
    return df


df = load_data()

# ---------------------------------------------------------------------------
# Sidebar: Filter
# ---------------------------------------------------------------------------
st.sidebar.title("🔎 Filter Data")
st.sidebar.markdown("Gunakan filter di bawah untuk menyesuaikan tampilan dashboard.")

min_date = df["order_purchase_timestamp"].min().date()
max_date = df["order_purchase_timestamp"].max().date()

date_range = st.sidebar.date_input(
    "Rentang Tanggal Pemesanan",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
)
if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date, end_date = min_date, max_date

# Filter state
all_states = sorted(df["customer_state"].unique().tolist())
selected_states = st.sidebar.multiselect(
    "State Pelanggan (kosongkan = semua)",
    options=all_states,
    default=[],
)

# Apply filter
mask = (
    (df["order_purchase_timestamp"].dt.date >= start_date)
    & (df["order_purchase_timestamp"].dt.date <= end_date)
)
if selected_states:
    mask &= df["customer_state"].isin(selected_states)
filtered = df.loc[mask].copy()

st.sidebar.markdown("---")
st.sidebar.metric("Baris setelah filter", f"{len(filtered):,}")

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
st.title("🛒 Olist Brazilian E-Commerce — Analytics Dashboard")
st.markdown(
    "Dashboard ini merangkum hasil analisis data e-commerce Olist untuk periode "
    "**September 2016 – Oktober 2018**, mencakup tren penjualan, kategori unggulan, "
    "distribusi geografis, dan segmentasi pelanggan berbasis **RFM Analysis**."
)
st.markdown("---")

# ---------------------------------------------------------------------------
# KPIs
# ---------------------------------------------------------------------------
total_revenue = filtered["price"].sum()
total_orders = filtered["order_id"].nunique()
total_customers = filtered["customer_unique_id"].nunique()
avg_order_value = total_revenue / total_orders if total_orders else 0

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Revenue", f"R$ {total_revenue:,.0f}")
c2.metric("Total Pesanan", f"{total_orders:,}")
c3.metric("Pelanggan Unik", f"{total_customers:,}")
c4.metric("Avg. Order Value", f"R$ {avg_order_value:,.2f}")

st.markdown("---")

# ---------------------------------------------------------------------------
# Pertanyaan 1: Tren bulanan & kategori
# ---------------------------------------------------------------------------
st.header("Pertanyaan 1: Tren Pesanan, Revenue & Kategori Unggulan")

# Tren bulanan
filtered["year_month"] = filtered["order_purchase_timestamp"].dt.to_period("M").astype(str)
monthly = (
    filtered.groupby("year_month")
    .agg(total_orders=("order_id", "nunique"), total_revenue=("price", "sum"))
    .reset_index()
)
monthly["year_month"] = pd.to_datetime(monthly["year_month"])
monthly = monthly.sort_values("year_month")

st.subheader("📈 Tren Jumlah Pesanan & Revenue Bulanan")
fig, axes = plt.subplots(2, 1, figsize=(12, 7), sharex=True)
axes[0].plot(monthly["year_month"], monthly["total_orders"],
             marker="o", linewidth=2, color="#2E86AB")
axes[0].fill_between(monthly["year_month"], monthly["total_orders"],
                     alpha=0.15, color="#2E86AB")
axes[0].set_ylabel("Jumlah Pesanan")
axes[0].set_title("Jumlah Pesanan Bulanan", loc="left", fontweight="bold")
axes[0].grid(True, alpha=0.3)

axes[1].plot(monthly["year_month"], monthly["total_revenue"],
             marker="o", linewidth=2, color="#06A77D")
axes[1].fill_between(monthly["year_month"], monthly["total_revenue"],
                     alpha=0.15, color="#06A77D")
axes[1].set_ylabel("Revenue (R$)")
axes[1].set_xlabel("Bulan")
axes[1].set_title("Total Revenue Bulanan", loc="left", fontweight="bold")
axes[1].grid(True, alpha=0.3)
axes[1].yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{x/1000:.0f}K"))

plt.xticks(rotation=45)
plt.tight_layout()
st.pyplot(fig)
plt.close(fig)

with st.expander("📌 Insight Tren Bulanan"):
    st.markdown(
        "- Pertumbuhan signifikan terjadi sepanjang 2017 hingga awal 2018.\n"
        "- *Peak* penjualan jatuh pada **November 2017** karena momen Black Friday (24 Nov 2017).\n"
        "- Setelah lonjakan tersebut, jumlah pesanan stabil di kisaran 5.500–6.800/bulan."
    )

# Top kategori
st.subheader("🏷️ Top 10 Kategori Produk berdasarkan Revenue")
top_cat = (
    filtered.groupby("product_category")["price"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
)
fig, ax = plt.subplots(figsize=(10, 6))
colors = ["#C73E1D"] + ["#7BA7BC"] * 9
ax.barh(top_cat.index[::-1], top_cat.values[::-1], color=colors[::-1])
ax.set_xlabel("Total Revenue (R$)")
ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{x/1000:.0f}K"))
ax.set_title("Top 10 Kategori Produk", loc="left", fontweight="bold")
for i, v in enumerate(top_cat.values[::-1]):
    ax.text(v, i, f"  R$ {v/1000:,.0f}K", va="center", fontsize=9)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
plt.tight_layout()
st.pyplot(fig)
plt.close(fig)

with st.expander("📌 Insight Kategori"):
    st.markdown(
        "- Kategori `health_beauty`, `watches_gifts`, dan `bed_bath_table` adalah penyumbang revenue tertinggi.\n"
        "- Kategori produk gaya hidup dan perawatan diri menjadi pendorong utama bisnis."
    )

st.markdown("---")

# ---------------------------------------------------------------------------
# Pertanyaan 2: Distribusi geografis & RFM
# ---------------------------------------------------------------------------
st.header("Pertanyaan 2: Distribusi Geografis & Segmentasi RFM")

# Top state
st.subheader("🗺️ Top 10 State berdasarkan Revenue")
state_perf = (
    filtered.groupby("customer_state")
    .agg(
        total_customers=("customer_unique_id", "nunique"),
        total_revenue=("price", "sum"),
    )
    .sort_values("total_revenue", ascending=False)
    .head(10)
)

fig, ax = plt.subplots(figsize=(10, 5))
colors = ["#C73E1D"] + ["#7BA7BC"] * 9
ax.bar(state_perf.index, state_perf["total_revenue"], color=colors)
ax.set_ylabel("Total Revenue (R$)")
ax.set_xlabel("State")
ax.set_title("Top 10 State berdasarkan Revenue", loc="left", fontweight="bold")
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{x/1e6:.1f}M"))
for i, v in enumerate(state_perf["total_revenue"]):
    ax.text(i, v, f"R$ {v/1e6:.2f}M", ha="center", va="bottom", fontsize=9)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
plt.tight_layout()
st.pyplot(fig)
plt.close(fig)

with st.expander("📌 Insight Geografis"):
    st.markdown(
        "- **São Paulo (SP)** mendominasi dengan revenue ~3× lipat dibanding Rio de Janeiro.\n"
        "- Tiga state teratas (SP, RJ, MG) menyumbang lebih dari 62% revenue total — "
        "terdapat ketimpangan geografis yang sangat kuat ke wilayah Tenggara Brazil."
    )

# RFM Analysis
st.subheader("👥 Segmentasi Pelanggan berdasarkan RFM Analysis")

@st.cache_data
def compute_rfm(_df: pd.DataFrame) -> pd.DataFrame:
    if _df.empty:
        return pd.DataFrame()
    ref_date = _df["order_purchase_timestamp"].max() + pd.Timedelta(days=1)
    rfm = (
        _df.groupby("customer_unique_id")
        .agg(
            recency=("order_purchase_timestamp", lambda x: (ref_date - x.max()).days),
            frequency=("order_id", "nunique"),
            monetary=("price", "sum"),
        )
        .reset_index()
    )
    # R-score: small recency = high score
    try:
        rfm["R_score"] = pd.qcut(rfm["recency"], q=5, labels=[5, 4, 3, 2, 1]).astype(int)
    except ValueError:
        rfm["R_score"] = 3
    # F-score: discrete mapping
    def f_score(f):
        if f == 1: return 1
        if f == 2: return 3
        if f <= 4: return 4
        return 5
    rfm["F_score"] = rfm["frequency"].apply(f_score)
    # M-score
    try:
        rfm["M_score"] = pd.qcut(rfm["monetary"], q=5, labels=[1, 2, 3, 4, 5]).astype(int)
    except ValueError:
        rfm["M_score"] = 3
    rfm["RFM_score"] = rfm["R_score"] + rfm["F_score"] + rfm["M_score"]
    def seg(s):
        if s >= 12: return "Champions"
        if s >= 9: return "Loyal Customers"
        if s >= 6: return "Potential Loyalists"
        return "At Risk"
    rfm["segment"] = rfm["RFM_score"].apply(seg)
    return rfm


rfm = compute_rfm(filtered)

if rfm.empty:
    st.warning("Tidak ada data pelanggan pada filter yang dipilih.")
else:
    seg_order = ["Champions", "Loyal Customers", "Potential Loyalists", "At Risk"]
    seg_colors = {
        "Champions": "#06A77D",
        "Loyal Customers": "#2E86AB",
        "Potential Loyalists": "#F18F01",
        "At Risk": "#C73E1D",
    }
    counts = rfm["segment"].value_counts().reindex(seg_order, fill_value=0)

    col_a, col_b = st.columns([2, 1])

    with col_a:
        fig, ax = plt.subplots(figsize=(8, 5))
        bars = ax.bar(counts.index, counts.values,
                      color=[seg_colors[s] for s in counts.index])
        ax.set_ylabel("Jumlah Pelanggan")
        ax.set_title("Distribusi Segmen Pelanggan (RFM)",
                     loc="left", fontweight="bold")
        total = counts.sum()
        for bar, v in zip(bars, counts.values):
            pct = v / total * 100 if total else 0
            ax.text(bar.get_x() + bar.get_width() / 2, v,
                    f"{v:,}\n({pct:.1f}%)", ha="center", va="bottom", fontsize=9)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close(fig)

    with col_b:
        st.markdown("**Ringkasan per Segmen**")
        summary = (
            rfm.groupby("segment")
            .agg(
                pelanggan=("customer_unique_id", "count"),
                avg_recency_hari=("recency", "mean"),
                avg_monetary_brl=("monetary", "mean"),
            )
            .round(1)
            .reindex(seg_order)
        )
        st.dataframe(summary)

    with st.expander("📌 Insight RFM"):
        st.markdown(
            "- Mayoritas pelanggan berada di segmen **At Risk** — sebagian besar adalah *one-time buyer*.\n"
            "- Segmen **Champions** dan **Loyal Customers** kecil jumlahnya namun berkontribusi pada *avg monetary* tertinggi.\n"
            "- Strategi retensi sebaiknya difokuskan pada Champions dan Loyal Customers."
        )

    # Spending Tier (Manual Clustering / Binning)
    st.subheader("💎 Customer Spending Tier (Manual Clustering)")
    bins = [
        0,
        rfm["monetary"].quantile(0.25),
        rfm["monetary"].quantile(0.50),
        rfm["monetary"].quantile(0.75),
        rfm["monetary"].max() + 1,
    ]
    labels = ["Bronze (Q1)", "Silver (Q2)", "Gold (Q3)", "Platinum (Q4)"]
    rfm["spending_tier"] = pd.cut(
        rfm["monetary"], bins=bins, labels=labels, include_lowest=True
    )
    tier = (
        rfm.groupby("spending_tier")
        .agg(
            n_customers=("customer_unique_id", "count"),
            total_revenue=("monetary", "sum"),
        )
        .reset_index()
    )
    tier["pct_revenue"] = (
        tier["total_revenue"] / tier["total_revenue"].sum() * 100
    ).round(1)

    fig, ax = plt.subplots(figsize=(10, 4.5))
    tier_colors = ["#CD7F32", "#C0C0C0", "#FFD700", "#3D3D8E"]
    ax.bar(tier["spending_tier"].astype(str), tier["pct_revenue"], color=tier_colors)
    ax.set_ylabel("% Kontribusi Revenue")
    ax.set_title("Kontribusi Revenue per Spending Tier",
                 loc="left", fontweight="bold")
    for i, v in enumerate(tier["pct_revenue"]):
        ax.text(i, v, f"{v:.1f}%", ha="center", va="bottom", fontsize=10, fontweight="bold")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

    with st.expander("📌 Insight Spending Tier"):
        st.markdown(
            "- Tier **Platinum (top 25% pelanggan)** menyumbang lebih dari **60% revenue** — "
            "konsisten dengan **prinsip Pareto (80/20)** dalam ritel.\n"
            "- Program loyalitas dan retensi sebaiknya difokuskan pada Tier Gold dan Platinum."
        )

st.markdown("---")
st.caption(
    "© Proyek Analisis Data — E-Commerce Public Dataset (Olist) | "
    "Dibuat dengan Python, Pandas, Matplotlib, dan Streamlit."
)
