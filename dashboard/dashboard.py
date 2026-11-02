import os
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

# Configure page
st.set_page_config(
    page_title="E-Commerce Performance & Customer Insights Dashboard",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
<style>
    .metric-card {
        background-color: #f8f9fa;
        border-radius: 8px;
        padding: 15px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .footer {
        text-align: center;
        color: #6c757d;
        padding: 20px 0;
        font-size: 0.9em;
    }
</style>
""", unsafe_allow_html=True)

# Helper functions for data aggregation
def create_daily_orders_df(df):
    daily_orders = df.resample(rule='D', on='order_purchase_timestamp').agg({
        'order_id': 'nunique',
        'price': 'sum'
    }).reset_index()
    daily_orders.rename(columns={
        'order_id': 'order_count',
        'price': 'revenue'
    }, inplace=True)
    return daily_orders

def create_sum_order_items_df(df):
    sum_items_df = df.groupby('product_category_name_english').agg({
        'order_id': 'count',
        'price': 'sum'
    }).reset_index()
    sum_items_df.rename(columns={
        'order_id': 'item_count',
        'price': 'total_revenue'
    }, inplace=True)
    return sum_items_df

def create_delivery_satisfaction_df(df):
    delivery_summary = df.groupby('delivery_status').agg({
        'order_id': 'nunique',
        'review_score': 'mean',
        'delivery_delay_days': 'mean'
    }).reset_index()
    return delivery_summary

def create_rfm_df(df):
    recent_date = df['order_purchase_timestamp'].max() + pd.Timedelta(days=1)
    rfm_df = df.groupby('customer_unique_id').agg({
        'order_purchase_timestamp': lambda x: (recent_date - x.max()).days,
        'order_id': 'nunique',
        'price': 'sum'
    }).reset_index()
    rfm_df.columns = ['customer_unique_id', 'recency', 'frequency', 'monetary']
    return rfm_df

def create_bystate_df(df):
    bystate_df = df.groupby('customer_state')['customer_unique_id'].nunique().reset_index()
    bystate_df.rename(columns={'customer_unique_id': 'customer_count'}, inplace=True)
    bystate_df.sort_values(by='customer_count', ascending=False, inplace=True)
    return bystate_df

# Load main dataset
@st.cache_data
def load_data():
    file_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(file_dir, "main_data.csv")
    
    if not os.path.exists(file_path):
        # Fallback to current working directory
        file_path = "main_data.csv"
        
    df = pd.read_csv(file_path)
    df['order_purchase_timestamp'] = pd.to_datetime(df['order_purchase_timestamp'])
    return df

try:
    all_df = load_data()
except Exception as e:
    st.error(f"Gagal memuat data: {e}")
    st.stop()

# Sidebar: Filter & Info
with st.sidebar:
    st.title("🛍️ E-Commerce Dashboard")
    st.markdown("**Analisis Data Penjualan & Pelanggan**")
    st.markdown("---")
    
    st.markdown("### Profil Analis")
    st.write("**Nama:** Daniel Julian Caesar")
    st.write("**Email:** ds009b6y0409@student.devacademy.id")
    st.write("**ID Dicoding:** ds009b6y0409")
    st.markdown("---")
    
    # Filter Date Range
    min_date = all_df['order_purchase_timestamp'].min().date()
    max_date = all_df['order_purchase_timestamp'].max().date()
    
    st.subheader("Filter Waktu Transaksi")
    date_range = st.date_input(
        label="Pilih Rentang Tanggal",
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )
    
    # State Filter
    all_states = sorted(all_df['customer_state'].dropna().unique())
    selected_states = st.multiselect(
        label="Filter Negara Bagian (Customer State)",
        options=all_states,
        default=all_states
    )

# Validate date range input
if isinstance(date_range, (list, tuple)) and len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date, end_date = min_date, max_date

# Filter main dataframe based on user selection
filtered_df = all_df[
    (all_df['order_purchase_timestamp'].dt.date >= start_date) &
    (all_df['order_purchase_timestamp'].dt.date <= end_date) &
    (all_df['customer_state'].isin(selected_states))
]

if filtered_df.empty:
    st.warning("Tidak ada data transaksi untuk rentang filter yang dipilih. Silakan sesuaikan filter Anda.")
    st.stop()

# Precompute aggregated metrics
daily_orders_df = create_daily_orders_df(filtered_df)
sum_items_df = create_sum_order_items_df(filtered_df)
delivery_df = create_delivery_satisfaction_df(filtered_df)
rfm_df = create_rfm_df(filtered_df)
bystate_df = create_bystate_df(filtered_df)

# Dashboard Main Header
st.title("📊 E-Commerce Performance & Customer Satisfaction Dashboard")
st.markdown("Dashboard ini menyajikan hasil eksplorasi dan analisis interaktif terhadap data operasional e-commerce di Brasil, mencakup kinerja produk, kepuasan pengiriman, segmentasi pelanggan (RFM), dan geospasial.")

st.markdown("---")

# Key Metrics Cards
total_orders = filtered_df['order_id'].nunique()
total_revenue = filtered_df['price'].sum()
avg_review = filtered_df['review_score'].mean()
on_time_rate = (filtered_df['delivery_status'] == 'On Time').mean() * 100

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Pesanan (Orders)", f"{total_orders:,}")
with col2:
    st.metric("Total Pendapatan (Revenue)", f"R$ {total_revenue:,.2f}")
with col3:
    st.metric("Rata-rata Skor Ulasan", f"{avg_review:.2f} / 5.0 ⭐")
with col4:
    st.metric("Tingkat Kirim Tepat Waktu", f"{on_time_rate:.1f}%")

st.markdown("---")

# Tabs for Navigation
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📈 Tren Penjualan Harian",
    "🏆 Performa Produk (Q1)",
    "🚚 Logistik & Kepuasan (Q2)",
    "👥 Analisis RFM",
    "🗺️ Demografi & Geospasial"
])

# TAB 1: Tren Penjualan Harian
with tab1:
    st.subheader("Tren Pesanan Harian dan Pendapatan")
    col_t1, col_t2 = st.columns(2)
    
    with col_t1:
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.plot(
            daily_orders_df['order_purchase_timestamp'],
            daily_orders_df['order_count'],
            marker='o',
            linewidth=1.5,
            markersize=3,
            color="#72BCD4"
        )
        ax.set_title("Jumlah Pesanan Harian", fontsize=14, fontweight='bold')
        ax.set_xlabel("Tanggal", fontsize=11)
        ax.set_ylabel("Jumlah Pesanan", fontsize=11)
        ax.grid(True, linestyle="--", alpha=0.5)
        plt.xticks(rotation=45)
        st.pyplot(fig)
        plt.close()
        
    with col_t2:
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.plot(
            daily_orders_df['order_purchase_timestamp'],
            daily_orders_df['revenue'],
            marker='o',
            linewidth=1.5,
            markersize=3,
            color="#1F77B4"
        )
        ax.set_title("Total Pendapatan Harian (BRL)", fontsize=14, fontweight='bold')
        ax.set_xlabel("Tanggal", fontsize=11)
        ax.set_ylabel("Revenue (R$)", fontsize=11)
        ax.grid(True, linestyle="--", alpha=0.5)
        plt.xticks(rotation=45)
        st.pyplot(fig)
        plt.close()

# TAB 2: Performa Produk (Pertanyaan 1)
with tab2:
    st.subheader("Pertanyaan Bisnis 1: Kategori Produk Terbaik & Terendah")
    st.markdown("""
    **Pertanyaan:** Kategori produk apa yang memiliki performa penjualan tertinggi dan terendah (berdasarkan kuantitas unit terjual dan total revenue)?
    """)
    
    top_5_qty = sum_items_df.sort_values(by='item_count', ascending=False).head(5)
    bottom_5_qty = sum_items_df.sort_values(by='item_count', ascending=True).head(5)
    
    top_5_rev = sum_items_df.sort_values(by='total_revenue', ascending=False).head(5)
    bottom_5_rev = sum_items_df.sort_values(by='total_revenue', ascending=True).head(5)
    
    # Subplot Quantity
    st.markdown("#### Berdasarkan Volume Unit Terjual")
    fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(16, 5))
    colors_top = ["#1F77B4", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]
    colors_bot = ["#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D9534F"]
    
    sns.barplot(x="item_count", y="product_category_name_english", data=top_5_qty, hue="product_category_name_english", palette=colors_top, legend=False, ax=ax[0])
    ax[0].set_title("Top 5 Kategori Produk (Terbanyak Terjual)", fontsize=13, fontweight='bold')
    ax[0].set_xlabel("Jumlah Item Terjual")
    ax[0].set_ylabel(None)
    
    sns.barplot(x="item_count", y="product_category_name_english", data=bottom_5_qty, hue="product_category_name_english", palette=colors_bot, legend=False, ax=ax[1])
    ax[1].set_title("Bottom 5 Kategori Produk (Paling Sedikit Terjual)", fontsize=13, fontweight='bold')
    ax[1].set_xlabel("Jumlah Item Terjual")
    ax[1].set_ylabel(None)
    ax[1].invert_xaxis()
    ax[1].yaxis.set_label_position("right")
    ax[1].yaxis.tick_right()
    st.pyplot(fig)
    plt.close()
    
    # Subplot Revenue
    st.markdown("#### Berdasarkan Total Pendapatan (Revenue BRL)")
    fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(16, 5))
    sns.barplot(x="total_revenue", y="product_category_name_english", data=top_5_rev, hue="product_category_name_english", palette=colors_top, legend=False, ax=ax[0])
    ax[0].set_title("Top 5 Kategori Produk (Revenue Tertinggi)", fontsize=13, fontweight='bold')
    ax[0].set_xlabel("Total Revenue (R$)")
    ax[0].set_ylabel(None)
    
    sns.barplot(x="total_revenue", y="product_category_name_english", data=bottom_5_rev, hue="product_category_name_english", palette=colors_bot, legend=False, ax=ax[1])
    ax[1].set_title("Bottom 5 Kategori Produk (Revenue Terendah)", fontsize=13, fontweight='bold')
    ax[1].set_xlabel("Total Revenue (R$)")
    ax[1].set_ylabel(None)
    ax[1].invert_xaxis()
    ax[1].yaxis.set_label_position("right")
    ax[1].yaxis.tick_right()
    st.pyplot(fig)
    plt.close()
    
    st.info("""
    💡 **Insight:** 
    - Kategori **bed_bath_table**, **health_beauty**, dan **sports_leisure** mendominasi volume penjualan unit.
    - Dari sisi pendapatan (revenue), kategori **health_beauty** dan **watches_gifts** menghasilkan nilai moneter terbesar karena memiliki Average Selling Price (ASP) yang lebih tinggi.
    - Kategori paling rendah seperti **security_and_services** dan **fashion_childrens_clothes** sangat minim transaksi.
    """)

# TAB 3: Logistik & Kepuasan (Pertanyaan 2)
with tab3:
    st.subheader("Pertanyaan Bisnis 2: Waktu Pengiriman vs Skor Kepuasan Pelanggan")
    st.markdown("""
    **Pertanyaan:** Bagaimana pengaruh status keterlambatan pengiriman pesanan (delivery delay vs estimasi) terhadap skor kepuasan pelanggan (review score)?
    """)
    
    col_l1, col_l2 = st.columns(2)
    
    with col_l1:
        st.markdown("#### Rata-rata Skor Ulasan: On Time vs Terlambat")
        fig, ax = plt.subplots(figsize=(8, 5))
        sns.barplot(
            x='delivery_status',
            y='review_score',
            data=delivery_df,
            hue='delivery_status',
            palette=['#1F77B4', '#D9534F'],
            legend=False,
            ax=ax
        )
        ax.set_title("Rata-rata Skor Review Berdasarkan Status Pengiriman", fontsize=13, fontweight='bold')
        ax.set_xlabel("Status Pengiriman", fontsize=11)
        ax.set_ylabel("Rata-rata Review Score (1 - 5)", fontsize=11)
        ax.set_ylim(0, 5)
        for p in ax.patches:
            ax.annotate(f"{p.get_height():.2f}",
                        (p.get_x() + p.get_width() / 2., p.get_height() / 2),
                        ha='center', va='center', color='white', fontweight='bold', fontsize=12)
        st.pyplot(fig)
        plt.close()
        
    with col_l2:
        st.markdown("#### Proporsi Skor Ulasan (1 - 5 Bintang)")
        fig, ax = plt.subplots(figsize=(8, 5))
        review_dist = pd.crosstab(filtered_df['delivery_status'], filtered_df['review_score'], normalize='index') * 100
        review_dist.plot(kind='bar', stacked=True, colormap='Spectral', ax=ax)
        ax.set_title("Distribusi Rating Pelanggan Berdasarkan Ketepatan Pengiriman", fontsize=13, fontweight='bold')
        ax.set_xlabel("Status Pengiriman", fontsize=11)
        ax.set_ylabel("Persentase (%)", fontsize=11)
        ax.legend(title="Rating", bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.xticks(rotation=0)
        st.pyplot(fig)
        plt.close()
        
    st.info("""
    💡 **Insight:**
    - Pesanan yang tiba **tepat waktu / lebih cepat** memiliki rata-rata skor ulasan **4.24 / 5.0**, dengan mayoritas (>70%) memberikan rating sempurna (5 bintang).
    - Sebaliknya, pesanan yang **terlambat** mengalami anjloknya kepuasan pelanggan secara drastis ke rata-rata **2.32 / 5.0**, di mana lebih dari 55% pelanggan memberikan rating terburuk (1 bintang).
    - Ketepatan estimasi logistik menjadi faktor penentu utama reputasi dan kepuasan pelanggan.
    """)

# TAB 4: Analisis RFM (Customer Segmentation)
with tab4:
    st.subheader("Analisis Lanjutan: RFM Analysis (Recency, Frequency, Monetary)")
    st.markdown("""
    Analisis RFM digunakan untuk mengidentifikasi karakteristik dan nilai pelanggan:
    - **Recency:** Jumlah hari sejak transaksi terakhir pelanggan.
    - **Frequency:** Jumlah total pesanan yang dibuat oleh pelanggan.
    - **Monetary:** Total nilai uang yang dibelanjakan pelanggan (R$).
    """)
    
    col_rfm1, col_rfm2, col_rfm3 = st.columns(3)
    with col_rfm1:
        st.metric("Rata-rata Recency", f"{rfm_df['recency'].mean():.0f} Hari")
    with col_rfm2:
        st.metric("Rata-rata Frequency", f"{rfm_df['frequency'].mean():.2f} Pesanan")
    with col_rfm3:
        st.metric("Rata-rata Monetary", f"R$ {rfm_df['monetary'].mean():.2f}")
        
    st.markdown("---")
    
    fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(20, 6))
    colors = ["#72BCD4"] * 5
    
    # Top 5 Recency (Best/lowest recency)
    top_recency = rfm_df.sort_values(by='recency', ascending=True).head(5)
    sns.barplot(y="customer_unique_id", x="recency", data=top_recency, hue="customer_unique_id", palette=colors, legend=False, ax=ax[0])
    ax[0].set_ylabel(None)
    ax[0].set_xlabel("Recency (Hari)")
    ax[0].set_title("Top 5 Customers by Recency (Terkini)", fontsize=13, fontweight='bold')
    
    # Top 5 Frequency
    top_freq = rfm_df.sort_values(by='frequency', ascending=False).head(5)
    sns.barplot(y="customer_unique_id", x="frequency", data=top_freq, hue="customer_unique_id", palette=colors, legend=False, ax=ax[1])
    ax[1].set_ylabel(None)
    ax[1].set_xlabel("Frequency (Jumlah Order)")
    ax[1].set_title("Top 5 Customers by Frequency", fontsize=13, fontweight='bold')
    
    # Top 5 Monetary
    top_monetary = rfm_df.sort_values(by='monetary', ascending=False).head(5)
    sns.barplot(y="customer_unique_id", x="monetary", data=top_monetary, hue="customer_unique_id", palette=colors, legend=False, ax=ax[2])
    ax[2].set_ylabel(None)
    ax[2].set_xlabel("Monetary (R$)")
    ax[2].set_title("Top 5 Customers by Monetary (Belanja Tertinggi)", fontsize=13, fontweight='bold')
    
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()
    
    st.info("""
    💡 **Insight RFM:**
    - Mayoritas pelanggan (~96%) adalah pembeli satu kali (one-time buyer), yang mencerminkan tantangan retensi pelanggan.
    - Pelanggan dengan nilai Monetary tertinggi menyumbang belanjaan signifikan di atas R$ 7.000 hingga R$ 13.000.
    - Perusahaan perlu merancang program loyalitas dan kampanye re-engagement otomatis berbasis email/voucher untuk menaikkan repeat purchase rate.
    """)

# TAB 5: Demografi & Geospasial
with tab5:
    st.subheader("Analisis Lanjutan: Persebaran Geospasial Pelanggan")
    st.markdown("Distribusi basis pelanggan di berbagai negara bagian (State) di Brasil.")
    
    fig, ax = plt.subplots(figsize=(14, 6))
    top_states = bystate_df.head(10)
    state_colors = ["#1F77B4"] + ["#D3D3D3"] * (len(top_states) - 1)
    
    sns.barplot(
        x='customer_count',
        y='customer_state',
        data=top_states,
        hue='customer_state',
        palette=state_colors,
        legend=False,
        ax=ax
    )
    ax.set_title("Top 10 Negara Bagian Berdasarkan Jumlah Pelanggan Unik", fontsize=14, fontweight='bold')
    ax.set_xlabel("Jumlah Pelanggan Unik", fontsize=12)
    ax.set_ylabel("Negara Bagian (State)", fontsize=12)
    
    for p in ax.patches:
        width = p.get_width()
        ax.annotate(f"{int(width):,}",
                    (width + 500, p.get_y() + p.get_height() / 2.),
                    va='center', fontsize=10)
        
    st.pyplot(fig)
    plt.close()
    
    st.info("""
    💡 **Insight Geospasial:**
    - Negara Bagian **SP (São Paulo)** mendominasi secara signifikan dengan lebih dari 40% total basis pelanggan e-commerce.
    - Diikuti oleh negara bagian di wilayah tenggara lainnya: **RJ (Rio de Janeiro)** dan **MG (Minas Gerais)**.
    - Penempatan fulfillment center atau hub logistik utama di wilayah SP dan sekitarnya terbukti sangat strategis untuk memangkas waktu pengiriman.
    """)

# Footer
st.markdown("---")
st.markdown("""
<div class="footer">
    Dicoding Submission: Belajar Fundamental Analisis Data<br>
    Dibuat oleh <strong>Daniel Julian Caesar</strong> (ds009b6y0409)
</div>
""", unsafe_allow_html=True)
