import streamlit as st
import pandas as pd
import numpy as np
import re
import os

# -----------------------------------------------------------------------------
# HELPER DATA LOADING & RESHAPING
# -----------------------------------------------------------------------------
@st.cache_data
def load_gear_data():
    cleaned_candidates = [
        os.path.join("data", "gear_equipment_cleaned.csv"),
        os.path.join("..", "data", "gear_equipment_cleaned.csv"),
        "gear_equipment_cleaned.csv"
    ]
    cleaned_path = next((p for p in cleaned_candidates if os.path.exists(p)), None)

    if cleaned_path:
        df = pd.read_csv(cleaned_path, encoding='utf-8')
        df['Harga_Num'] = df['Harga_Rp']
        df['Link'] = df['Link_Toko']
        # Standarisasi label kategori agar kompatibel
        kat_map = {
            'Tenda': 'Tenda / Tarp Tent',
            'Matras': 'Matras',
            'Sleeping Bag': 'Sleeping Bag',
            'Cooking Set': 'Cooking Set',
            'Meja Kursi': 'Meja & Kursi',
            'Lampu': 'Lampu',
            'Carrier': 'Carrier / Tas',
            'Aksesoris': 'Aksesoris & Lainnya'
        }
        df['Kategori'] = df['Kategori'].map(lambda x: kat_map.get(x, x))
        return df

    candidate_paths = [
        os.path.join("data", "Database List Camp Equipment Recomendation - Camp Equitment.csv"),
        os.path.join("..", "data", "Database List Camp Equipment Recomendation - Camp Equitment.csv"),
        "Database List Camp Equipment Recomendation - Camp Equitment.csv"
    ]
    path = next((p for p in candidate_paths if os.path.exists(p)), None)
    if not path:
        raise FileNotFoundError("File dataset gear tidak ditemukan!")

    raw_gear = pd.read_csv(path, header=None, encoding='utf-8')

    def extract_block(raw_df, row_start, col_start, cat):
        records = []
        for i in range(row_start + 1, len(raw_df)):
            row = raw_df.iloc[i]
            nama = str(row.iloc[col_start]).strip()
            if nama in ('', 'nan', 'NaN') or nama.startswith(','):
                break
            harga_raw = str(row.iloc[col_start + 3]).strip()
            if harga_raw in ('nan', 'NaN', ''):
                harga_raw = str(row.iloc[col_start + 4]).strip()
            records.append({
                'Kategori':  cat,
                'Nama':      nama,
                'Ukuran':    str(row.iloc[col_start + 1]).strip(),
                'Material':  str(row.iloc[col_start + 2]).strip(),
                'Harga_Raw': harga_raw,
                'Link':      str(row.iloc[col_start + 4]).strip()
            })
        return records

    blok_config = [
        (3,  1, 'Tenda / Tarp Tent'),
        (3,  7, 'Matras'),
        (23, 1, 'Sleeping Bag'),
        (23, 7, 'Cooking Set'),
        (43, 1, 'Meja & Kursi'),
        (43, 7, 'Lampu'),
        (63, 1, 'Carrier / Tas'),
        (63, 7, 'Aksesoris & Lainnya'),
    ]

    all_gear = []
    for rs, cs, cat in blok_cfg:
        all_gear.extend(extract_block(raw_gear, rs, cs, cat))

    df = pd.DataFrame(all_gear)
    df = df[df['Nama'].notna() & ~df['Nama'].isin(['nan', '', 'NaN', 'Nama', 'Harga'])].reset_index(drop=True)

    # Parsing Harga
    def parse_harga(val):
        if pd.isna(val) or str(val).strip() in ('', 'nan', '-', 'link', 'Link'): return np.nan
        s = str(val).strip().lower()
        multiplier = 1
        if 'jt' in s or 'juta' in s:
            multiplier = 1_000_000
            s = re.sub(r'jut?a?', '', s)
        elif 'k' in s:
            multiplier = 1_000
            s = re.sub(r'k', '', s)

        parts = re.findall(r'[\d]+(?:[\.,][\d]+)?', s)
        if not parts: return np.nan
        nums = []
        for p in parts:
            try: nums.append(float(p.replace(',', '.')))
            except: pass
        if not nums: return np.nan
        return (sum(nums) / len(nums)) * multiplier

    df['Harga_Num'] = df['Harga_Raw'].apply(parse_harga)

    def tier(h):
        if pd.isna(h): return 'Unknown'
        if h <= 100_000: return 'Budget (<100k)'
        if h <= 500_000: return 'Mid-Range (100k-500k)'
        if h <= 1_500_000: return 'Premium (500k-1.5jt)'
        return 'Ultralight / High-End (>1.5jt)'

    df['Tier_Harga'] = df['Harga_Num'].apply(tier)

    # Deteksi Karakteristik Bahan / Bobot
    mat_text = df['Material'].fillna('') + ' ' + df['Ukuran'].fillna('')
    df['Is_Ultralight'] = mat_text.str.lower().str.contains('nylon 20d|titanium|fp 800|bulu angsa|ultralight|25gr|alloy').astype(int)

    return df

# -----------------------------------------------------------------------------
# MAIN APP FUNCTION
# -----------------------------------------------------------------------------
def render_gear_app():
    st.title("🎒 Sistem Rekomendasi Perlengkapan Outdoor (Camp Equipment)")
    st.caption("Katalog analisis spesifikasi teknis peralatan outdoor, pemilihan gear per kategori, dan generator paket belanja (Starter Pack Optimizer).")

    df_gear = load_gear_data()

    tab1, tab2, tab3 = st.tabs([
        "🔍 Pencarian & Rekomendasi Gear",
        "📦 Starter Pack Optimizer (Bundling)",
        "📊 Statistik Harga & Material"
    ])

    # -------------------------------------------------------------------------
    # TAB 1: Pencarian Per Kategori
    # -------------------------------------------------------------------------
    with tab1:
        st.subheader("Filter Katalog Perlengkapan")
        col_f1, col_f2, col_f3 = st.columns(3)

        kategori_list = ["Semua Kategori"] + sorted(list(df_gear['Kategori'].unique()))
        kat_terpilih = col_f1.selectbox("Pilih Kategori Gear:", kategori_list)

        gaya_opsi = col_f2.selectbox("Gaya Camping:", ["Semua Gaya", "⚡ Prioritas Ultralight (Ringan)", "💰 Prioritas Budget (Hemat)"])

        max_harga = col_f3.slider(
            "Batas Harga Maksimum:",
            min_value=10000,
            max_value=2000000,
            value=1700000,
            step=50000,
            format="Rp %d"
        )

        sub_df = df_gear[df_gear['Harga_Num'].notna()].copy()
        if kat_terpilih != "Semua Kategori":
            sub_df = sub_df[sub_df['Kategori'] == kat_terpilih]

        sub_df = sub_df[sub_df['Harga_Num'] <= max_harga]

        if "Ultralight" in gaya_opsi:
            sub_df = sub_df.sort_values(by=['Is_Ultralight', 'Harga_Num'], ascending=[False, True])
        else:
            sub_df = sub_df.sort_values(by='Harga_Num', ascending=True)

        st.markdown(f"**Ditemukan {len(sub_df)} item perlengkapan sesuai kriteria:**")

        for _, item in sub_df.iterrows():
            with st.container():
                col_item1, col_item2 = st.columns([2.5, 1.2])
                with col_item1:
                    tag_ul = "⚡ `Ultralight`" if item['Is_Ultralight'] == 1 else "⛺ `Standar`"
                    st.markdown(f"### {item['Nama']} &nbsp; {tag_ul}")
                    st.markdown(f"**Kategori:** `{item['Kategori']}` &nbsp;|&nbsp; **Tier:** `{item['Tier_Harga']}`")
                    st.markdown(f"**Material:** {item['Material'] if item['Material'] != 'nan' else '-'}")
                    st.markdown(f"**Ukuran/Kapasitas:** {item['Ukuran'] if item['Ukuran'] != 'nan' else '-'}")
                with col_item2:
                    st.metric("Harga Estimasi", f"Rp {int(item['Harga_Num']):,}")
                    link_val = str(item['Link']).strip()
                    if link_val.startswith("http"):
                        st.link_button("🛒 Buka Link Toko", link_val)
                    else:
                        st.caption("Link toko tersedia di katalog")
                st.divider()

    # -------------------------------------------------------------------------
    # TAB 2: Starter Pack Optimizer
    # -------------------------------------------------------------------------
    with tab2:
        st.subheader("📦 Generator Paket Pembelian Peralatan Esensial (Knapsack Optimizer)")
        st.write("Sistem akan memilih kombinasi optimal 4 barang wajib: **Tenda + Sleeping Bag + Matras + Cooking Set** sesuai batas anggaran yang Anda tentukan.")

        col_b1, col_b2 = st.columns([1.5, 1.5])
        target_budget = col_b1.number_input(
            "Masukkan Pagu Anggaran Belanja (Rp):",
            min_value=500000,
            max_value=5000000,
            value=1500000,
            step=100000,
            format="%d"
        )
        strategi = col_b2.selectbox(
            "Pilih Strategi Pembelian:",
            ["Paling Hemat (Maksimal Saldo Sisa)", "Berimbang (Best Value)", "Prioritas Material Ultralight"]
        )

        kategori_wajib = ['Tenda / Tarp Tent', 'Sleeping Bag', 'Matras', 'Cooking Set']
        bundle_items = []
        total_bundle = 0

        for kat in kategori_wajib:
            k_df = df_gear[(df_gear['Kategori'] == kat) & df_gear['Harga_Num'].notna()].copy()
            if strategi == "Prioritas Material Ultralight":
                k_df = k_df.sort_values(by=['Is_Ultralight', 'Harga_Num'], ascending=[False, True])
            elif strategi == "Paling Hemat (Maksimal Saldo Sisa)":
                k_df = k_df.sort_values(by='Harga_Num', ascending=True)
            else: # Berimbang
                median_p = k_df['Harga_Num'].median()
                k_df['selisih'] = (k_df['Harga_Num'] - median_p).abs()
                k_df = k_df.sort_values(by=['selisih', 'Harga_Num'], ascending=[True, True])

            if not k_df.empty:
                pick = k_df.iloc[0]
                bundle_items.append(pick)
                total_bundle += pick['Harga_Num']

        st.markdown("---")
        c1, c2, c3 = st.columns(3)
        c1.metric("Pagu Budget Anda", f"Rp {int(target_budget):,}")
        c2.metric("Total Biaya Paket", f"Rp {int(total_bundle):,}")
        sisa = target_budget - total_bundle
        if sisa >= 0:
            c3.metric("Sisa Saldo Hemat", f"Rp {int(sisa):,}")
            st.success(f"✅ Paket belanja berhasil dirancang! Masih tersisa **Rp {int(sisa):,}** untuk membeli lampu senter, logistik, atau gas.")
        else:
            c3.metric("Over Budget", f"-Rp {int(abs(sisa)):,}", delta_color="inverse")
            st.warning(f"⚠️ Melebihi pagu sebesar **Rp {int(abs(sisa)):,}**. Pertimbangkan opsi sewa atau ganti tenda ke tier budget.")

        st.markdown("#### Rincian Paket Terpilih:")
        bundle_table = []
        for it in bundle_items:
            bundle_table.append({
                "Kategori": it['Kategori'],
                "Nama Produk": it['Nama'],
                "Material": it['Material'],
                "Harga": f"Rp {int(it['Harga_Num']):,}",
                "Tier": it['Tier_Harga'],
                "Link Pembelian": it['Link']
            })
        st.dataframe(pd.DataFrame(bundle_table), use_container_width=True)

    # -------------------------------------------------------------------------
    # TAB 3: Statistik Harga & Material
    # -------------------------------------------------------------------------
    with tab3:
        st.subheader("Distribusi Harga Gear per Kategori")
        st.write("Statistik ringkasan harga pasaran gear camping di dataset:")
        stats = df_gear.groupby('Kategori')['Harga_Num'].agg(['count', 'min', 'median', 'max']).reset_index()
        stats.columns = ['Kategori', 'Jumlah Item', 'Harga Min (Rp)', 'Harga Median (Rp)', 'Harga Max (Rp)']
        for col in ['Harga Min (Rp)', 'Harga Median (Rp)', 'Harga Max (Rp)']:
            stats[col] = stats[col].apply(lambda x: f"Rp {int(x):,}" if pd.notna(x) else "-")
        st.table(stats)

        img_p = "eda_gear_01.png" if os.path.exists("eda_gear_01.png") else os.path.join("02_gear_recommender", "eda_gear_01.png")
        if os.path.exists(img_p):
            st.image(img_p, use_container_width=True)

if __name__ == "__main__":
    st.set_page_config(page_title="Rekomendasi Gear Outdoor", layout="wide", page_icon="🎒")
    render_gear_app()
