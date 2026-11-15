import os

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import seaborn as sns
import streamlit as st

# ------------------------------------------------------------------ Konfigurasi
st.set_page_config(page_title="E-Commerce Dashboard", page_icon="🛒", layout="wide")

HIGHLIGHT = "#2a78d6"
ACCENT = "#eb6834"
MUTED = "#c9c8c3"
TEXT = "#0b0b0b"
TEXT_2 = "#52514e"

sns.set_theme(style="white")
plt.rcParams.update({
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.edgecolor": TEXT_2, "axes.labelcolor": TEXT_2,
    "xtick.color": TEXT_2, "ytick.color": TEXT_2,
    "axes.titleweight": "bold", "axes.titlesize": 13, "axes.titlecolor": TEXT,
})

DATA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "main_data.csv")


# ------------------------------------------------------------------ Helper functions
@st.cache_data
def load_data(path):
    df = pd.read_csv(path, parse_dates=["order_purchase_timestamp", "order_delivered_customer_date",
                                        "order_estimated_delivery_date"])
    return df


def create_monthly_df(df):
    monthly = (df.set_index("order_purchase_timestamp")
                 .resample("MS")
                 .agg(order_count=("order_id", "nunique"), revenue=("price", "sum"))
                 .reset_index())
    monthly["revenue_mom_pct"] = monthly["revenue"].pct_change() * 100
    monthly["order_mom_pct"] = monthly["order_count"].pct_change() * 100
    return monthly


def create_category_df(df):
    cat = (df.groupby("product_category")
             .agg(revenue=("price", "sum"), order_count=("order_id", "nunique"))
             .sort_values("revenue", ascending=False)
             .reset_index())
    cat["share_pct"] = cat["revenue"] / cat["revenue"].sum() * 100
    return cat


def create_order_level_df(df):
    return df.drop_duplicates("order_id")


def create_state_df(order_df):
    state = (order_df.groupby("customer_state")
                     .agg(order_count=("order_id", "count"), late_count=("is_late", "sum"),
                          late_pct=("is_late", "mean"), avg_review=("review_score", "mean"))
                     .sort_values("late_pct", ascending=False)
                     .reset_index())
    state["late_pct"] = state["late_pct"] * 100
    return state


def assign_segment(r, f, m):
    if f >= 2 and r >= 4:
        return "Champions"
    if f >= 2:
        return "Loyal (pembeli ulang)"
    if r >= 4 and m >= 4:
        return "Pelanggan baru bernilai tinggi"
    if r >= 4:
        return "Pelanggan baru"
    if r == 3:
        return "Perlu perhatian"
    if m >= 4:
        return "Berisiko hilang (bernilai tinggi)"
    return "Hibernasi"


def quintile_score(series, labels):
    """Skor kuintil sama seperti di notebook; jika data terlalu sedikit/banyak nilai kembar,
    gunakan ranking agar batas kuintil tetap unik."""
    try:
        return pd.qcut(series, 5, labels=labels).astype(int)
    except ValueError:
        return pd.qcut(series.rank(method="first"), 5, labels=labels).astype(int)


def short_brl(value, _=None):
    if value >= 1e6:
        return f"{value / 1e6:.1f} jt"
    if value >= 1e4:
        return f"{value / 1e3:.0f} rb"
    if value >= 1e3:
        return f"{value / 1e3:.1f} rb"
    return f"{value:.0f}"


def create_rfm_df(df):
    reference_date = df["order_purchase_timestamp"].max() + pd.Timedelta(days=1)
    rfm = df.groupby("customer_unique_id").agg(
        last_purchase=("order_purchase_timestamp", "max"),
        frequency=("order_id", "nunique"),
        monetary=("price", "sum"),
    ).reset_index()
    rfm["recency"] = (reference_date - rfm["last_purchase"]).dt.days
    rfm["R_score"] = quintile_score(rfm["recency"], [5, 4, 3, 2, 1])
    rfm["M_score"] = quintile_score(rfm["monetary"], [1, 2, 3, 4, 5])
    rfm["F_score"] = np.select([rfm["frequency"] >= 3, rfm["frequency"] == 2], [3, 2], default=1)
    rfm["segment"] = [assign_segment(r, f, m) for r, f, m in zip(rfm["R_score"], rfm["F_score"], rfm["M_score"])]
    return rfm


def fmt_brl(value):
    if value >= 1e6:
        return f"R$ {value / 1e6:,.2f} jt"
    if value >= 1e3:
        return f"R$ {value / 1e3:,.1f} rb"
    return f"R$ {value:,.0f}"


# ------------------------------------------------------------------ Load data
all_df = load_data(DATA_PATH)
min_date = all_df["order_purchase_timestamp"].min().date()
max_date = all_df["order_purchase_timestamp"].max().date()

# ------------------------------------------------------------------ Sidebar (filter)
with st.sidebar:
    st.title("🛒 Olist E-Commerce")
    st.caption("Pesanan berstatus *delivered*, Januari 2017 – Agustus 2018")

    date_range = st.date_input("Rentang tanggal pembelian", value=[min_date, max_date],
                               min_value=min_date, max_value=max_date)
    if isinstance(date_range, (list, tuple)) and len(date_range) == 2:
        start_date, end_date = date_range
    else:
        start_date, end_date = min_date, max_date

    states = sorted(all_df["customer_state"].dropna().unique())
    selected_states = st.multiselect("State pelanggan", options=states, default=[],
                                     placeholder="Semua state")

mask = ((all_df["order_purchase_timestamp"].dt.date >= start_date) &
        (all_df["order_purchase_timestamp"].dt.date <= end_date))
if selected_states:
    mask &= all_df["customer_state"].isin(selected_states)
main_df = all_df[mask]

st.title("E-Commerce Public Dataset Dashboard")
st.caption(f"Periode: {start_date:%d %b %Y} – {end_date:%d %b %Y} · "
           f"State: {', '.join(selected_states) if selected_states else 'semua'}")

if main_df.empty:
    st.warning("Tidak ada data untuk filter yang dipilih. Silakan ubah rentang tanggal atau state.")
    st.stop()

order_df = create_order_level_df(main_df)
monthly_df = create_monthly_df(main_df)
category_df = create_category_df(main_df)
state_df = create_state_df(order_df)

# ------------------------------------------------------------------ KPI
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total pesanan", f"{order_df['order_id'].nunique():,}")
col2.metric("Total revenue", fmt_brl(main_df["price"].sum()))
col3.metric("Rata-rata review score", f"{order_df['review_score'].mean():.2f} / 5")
col4.metric("Pesanan terlambat", f"{order_df['is_late'].mean():.1%}")

st.divider()

# ------------------------------------------------------------------ Pertanyaan 1: Tren bulanan
st.subheader("1. Tren Pesanan dan Revenue Bulanan")
if len(monthly_df) >= 2:
    peak = monthly_df.loc[monthly_df["revenue"].idxmax()]
    m1, m2, m3 = st.columns(3)
    m1.metric("Bulan puncak revenue", f"{peak['order_purchase_timestamp']:%B %Y}")
    m2.metric("Revenue bulan puncak", fmt_brl(peak["revenue"]),
              delta=None if pd.isna(peak["revenue_mom_pct"]) else f"{peak['revenue_mom_pct']:.1f}% MoM")
    m3.metric("Pesanan bulan puncak", f"{int(peak['order_count']):,}",
              delta=None if pd.isna(peak["order_mom_pct"]) else f"{peak['order_mom_pct']:.1f}% MoM")

fig, axes = plt.subplots(1, 2, figsize=(16, 5))
peak_idx = monthly_df["revenue"].idxmax()
for ax, col, title, scale, ylabel in [
    (axes[0], "revenue", "Revenue per bulan", 1e6, "Revenue (juta BRL)"),
    (axes[1], "order_count", "Jumlah pesanan per bulan", 1, "Jumlah pesanan"),
]:
    ax.plot(monthly_df["order_purchase_timestamp"], monthly_df[col] / scale, color=HIGHLIGHT,
            linewidth=2, marker="o", markersize=5)
    ax.scatter(monthly_df.loc[peak_idx, "order_purchase_timestamp"], monthly_df.loc[peak_idx, col] / scale,
               s=120, color=ACCENT, zorder=3, label="Bulan puncak revenue")
    ax.set_ylim(0, monthly_df[col].max() / scale * 1.15)
    ax.set_title(title, loc="left")
    ax.set_ylabel(ylabel)
    ax.grid(axis="y", color="#e8e7e3", linewidth=0.8)
    ax.tick_params(axis="x", rotation=45)
    ax.legend(frameon=False, loc="lower right")
axes[1].yaxis.set_major_formatter(mtick.StrMethodFormatter("{x:,.0f}"))
plt.tight_layout()
st.pyplot(fig)
plt.close(fig)

# ------------------------------------------------------------------ Pertanyaan 2: Kategori
st.subheader("2. Revenue per Kategori Produk")
max_n = min(15, len(category_df))
if max_n > 1:
    top_n = st.slider("Jumlah kategori yang ditampilkan", min_value=1, max_value=max_n, value=min(10, max_n))
else:
    top_n = max_n
top_share = category_df.head(top_n)["share_pct"].sum()
c1, c2 = st.columns(2)
c1.metric(f"Kontribusi {top_n} kategori teratas", f"{top_share:.1f}%")
c2.metric("Jumlah kategori terjual", f"{len(category_df)}")

fig, axes = plt.subplots(1, 2, figsize=(16, max(4, top_n * 0.5)))
top = category_df.head(top_n).iloc[::-1]
bottom = category_df.tail(top_n).iloc[::-1]
n_hl = min(3, top_n)
axes[0].barh(top["product_category"], top["revenue"], color=[MUTED] * (top_n - n_hl) + [HIGHLIGHT] * n_hl)
axes[0].set_title(f"{top_n} kategori dengan revenue tertinggi", loc="left")
axes[1].barh(bottom["product_category"], bottom["revenue"], color=[ACCENT] * n_hl + [MUTED] * (top_n - n_hl))
axes[1].set_title(f"{top_n} kategori dengan revenue terendah", loc="left")
for ax, data in [(axes[0], top), (axes[1], bottom)]:
    for i, v in enumerate(data["revenue"]):
        ax.text(v, i, f"  {fmt_brl(v)}", va="center", fontsize=9, color=TEXT)
    ax.set_xlim(0, data["revenue"].max() * 1.3)
    ax.set_xlabel("Revenue (BRL)")
    ax.xaxis.set_major_formatter(mtick.FuncFormatter(short_brl))
    ax.grid(axis="x", color="#e8e7e3", linewidth=0.8)
plt.tight_layout()
st.pyplot(fig)
plt.close(fig)
st.caption("Catatan: skala sumbu x kedua grafik berbeda. Revenue = total harga barang tanpa ongkos kirim.")

# ------------------------------------------------------------------ Pertanyaan 3: Keterlambatan
st.subheader("3. Keterlambatan Pengiriman dan Review Score")
late_review = (order_df.groupby("is_late")["review_score"].mean()
                       .rename(index={False: "Tepat waktu", True: "Terlambat"}))
k1, k2, k3 = st.columns(3)
k1.metric("Review pesanan tepat waktu", f"{late_review.get('Tepat waktu', np.nan):.2f}")
k2.metric("Review pesanan terlambat", f"{late_review.get('Terlambat', np.nan):.2f}")
if {"Tepat waktu", "Terlambat"}.issubset(late_review.index):
    k3.metric("Selisih", f"{late_review['Tepat waktu'] - late_review['Terlambat']:.2f} poin")

fig, axes = plt.subplots(1, 2, figsize=(16, 5.5), gridspec_kw={"width_ratios": [1, 1.6]})
bar_colors = [HIGHLIGHT if i == "Tepat waktu" else ACCENT for i in late_review.index]
bars = axes[0].bar(late_review.index, late_review.values, color=bar_colors, width=0.55)
for b, v in zip(bars, late_review.values):
    axes[0].text(b.get_x() + b.get_width() / 2, v + 0.08, f"{v:.2f}", ha="center", fontsize=12,
                 fontweight="bold", color=TEXT)
axes[0].set_ylim(0, 5)
axes[0].set_ylabel("Rata-rata review score (1-5)")
axes[0].set_title("Rata-rata review score", loc="left")

top_state = state_df.head(10).iloc[::-1]
n_state = len(top_state)
national = order_df["is_late"].mean() * 100
axes[1].barh(top_state["customer_state"], top_state["late_pct"],
             color=[MUTED] * max(0, n_state - 3) + [ACCENT] * min(3, n_state))
axes[1].axvline(national, color=TEXT_2, linestyle="--", linewidth=1.2,
                label=f"Rata-rata filter: {national:.1f}%")
for i, (v, n) in enumerate(zip(top_state["late_pct"], top_state["order_count"])):
    axes[1].text(v, i, f"  {v:.1f}% (n={n:,})", va="center", fontsize=9, color=TEXT)
axes[1].set_xlim(0, max(top_state["late_pct"].max(), national) * 1.35 + 0.1)
axes[1].xaxis.set_major_formatter(mtick.PercentFormatter(decimals=0))
axes[1].set_xlabel("Persentase pesanan terlambat")
axes[1].set_title("State dengan persentase keterlambatan tertinggi", loc="left")
axes[1].legend(frameon=False, loc="lower right")
axes[1].grid(axis="x", color="#e8e7e3", linewidth=0.8)
plt.tight_layout()
st.pyplot(fig)
plt.close(fig)

with st.expander("Lihat tabel keterlambatan per state"):
    st.dataframe(state_df.rename(columns={
        "customer_state": "State", "order_count": "Pesanan", "late_count": "Terlambat",
        "late_pct": "% Terlambat", "avg_review": "Rata-rata review"}).round(2),
        hide_index=True)

# ------------------------------------------------------------------ Analisis lanjutan: RFM
st.subheader("4. Segmentasi Pelanggan (RFM Analysis)")
if main_df["customer_unique_id"].nunique() < 5:
    st.info("Jumlah pelanggan terlalu sedikit untuk analisis RFM. Perluas filter.")
else:
    rfm_df = create_rfm_df(main_df)
    r1, r2, r3 = st.columns(3)
    r1.metric("Rata-rata recency", f"{rfm_df['recency'].mean():.0f} hari")
    r2.metric("Rata-rata frequency", f"{rfm_df['frequency'].mean():.2f} pesanan")
    r3.metric("Rata-rata monetary", fmt_brl(rfm_df["monetary"].mean()))

    seg = (rfm_df.groupby("segment")
                 .agg(customers=("customer_unique_id", "count"), avg_monetary=("monetary", "mean"))
                 .sort_values("customers"))
    seg["pct"] = seg["customers"] / seg["customers"].sum() * 100
    colors = [ACCENT if s.startswith("Berisiko") else HIGHLIGHT if s in ("Champions", "Loyal (pembeli ulang)")
              else MUTED for s in seg.index]

    fig, axes = plt.subplots(1, 2, figsize=(16, 5), sharey=True)
    axes[0].barh(seg.index, seg["customers"], color=colors)
    for i, (v, p) in enumerate(zip(seg["customers"], seg["pct"])):
        axes[0].text(v, i, f"  {v:,} ({p:.1f}%)", va="center", fontsize=9, color=TEXT)
    axes[0].set_xlim(0, seg["customers"].max() * 1.3)
    axes[0].set_xlabel("Jumlah pelanggan")
    axes[0].set_title("Jumlah pelanggan per segmen", loc="left")
    axes[1].barh(seg.index, seg["avg_monetary"], color=colors)
    for i, v in enumerate(seg["avg_monetary"]):
        axes[1].text(v, i, f"  {v:,.0f} BRL", va="center", fontsize=9, color=TEXT)
    axes[1].set_xlim(0, seg["avg_monetary"].max() * 1.3)
    axes[1].set_xlabel("Rata-rata monetary (BRL)")
    axes[1].set_title("Rata-rata nilai belanja per segmen", loc="left")
    for ax in axes:
        ax.grid(axis="x", color="#e8e7e3", linewidth=0.8)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)
    st.caption("Biru = pembeli ulang (Champions & Loyal), oranye = pelanggan bernilai tinggi yang berisiko hilang. "
               "Skor R dan M memakai kuintil (1-5); skor F: 1 = 1 pesanan, 2 = 2 pesanan, 3 = ≥3 pesanan.")

st.divider()
st.caption("Proyek Analisis Data · Rizky Ramdhani · Sumber data: Olist Brazilian E-Commerce Public Dataset")
