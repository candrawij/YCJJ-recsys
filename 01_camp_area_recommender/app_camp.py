import streamlit as st
import pandas as pd
import numpy as np
import re
import os
from sklearn.preprocessing import MinMaxScaler
from sklearn.cluster import KMeans

# -----------------------------------------------------------------------------
# HELPER DATA LOADING & FEATURE ENGINEERING
# -----------------------------------------------------------------------------
@st.cache_data
def load_camp_data():
    cleaned_candidates = [
        os.path.join("data", "camp_area_cleaned.csv"),
        os.path.join("..", "data", "camp_area_cleaned.csv"),
        "camp_area_cleaned.csv"
    ]
    cleaned_path = next((p for p in cleaned_candidates if os.path.exists(p)), None)
    
    if cleaned_path:
        df = pd.read_csv(cleaned_path, encoding='utf-8')
        df['HTM_Camp_Num'] = df['HTM_Camp_Rp']
        df['HTM_Parkir_Num'] = df['HTM_Parkir_Rp']
        df['HTM_Total_Num'] = df['Total_HTM_Rp']
        df['Ada_Toilet'] = df['Fasilitas_Toilet']
        df['Ada_Listrik'] = df['Fasilitas_Listrik']
        df['Ada_Warung'] = df['Fasilitas_Warung']
        df['Ada_Mushola'] = df['Fasilitas_Mushola']
        df['Ada_Air'] = df['Fasilitas_Air']
        df['Ada_Wifi'] = df['Fasilitas_Wifi']
        df['Jml_Fasilitas'] = df['Total_Fasilitas']
        df['Tag_View_Gunung'] = df['Tag_Gunung']
        df['Tag_Sunrise'] = df['Tag_Sunrise'] if 'Tag_Sunrise' in df.columns else 0
        df['Tag_Citylight'] = df['Tag_Citylight']
        df['Tag_Pantai'] = df['Tag_Pantai']
        df['Tag_Sungai'] = df['Tag_Sungai']
        df['Tag_Dingin'] = df['Tag_Dingin']
        df['Tag_Family'] = df['Tag_Family']
        df['Tag_Adventure'] = df['Tag_Extreme']
        df['Fasilitas'] = df['Fasilitas_Clean']
        df['Maps'] = df['Maps_Clean']
        df['Lokasi'] = df['Kabupaten']
    else:
        candidate_paths = [
            os.path.join("data", "Database Camp Area ( Jogja -Jateng ) - Camping Ceria.csv"),
            os.path.join("..", "data", "Database Camp Area ( Jogja -Jateng ) - Camping Ceria.csv"),
            "Database Camp Area ( Jogja -Jateng ) - Camping Ceria.csv"
        ]
        path = next((p for p in candidate_paths if os.path.exists(p)), None)
        if not path:
            raise FileNotFoundError("File dataset camp area tidak ditemukan!")

        df_raw = pd.read_csv(path, header=None, skiprows=4, encoding='utf-8')
        df = df_raw.iloc[:, 1:11].copy()
        df.columns = [
            'No', 'Nama', 'col_skip', 'Lokasi',
            'Spot_Menarik', 'Fasilitas', 'HTM_Camp', 'HTM_Parkir',
            'Maps', 'Info_Tambahan'
        ]
        df.drop(columns=['col_skip'], inplace=True)
        df = df[df['Nama'].notna() & (df['Nama'].astype(str).str.strip() != '')].copy()
        df.reset_index(drop=True, inplace=True)

        # Standardisasi HTM & Parkir
        def parse_htm(val):
            if pd.isna(val): return 0.0
            s = str(val).strip().lower()
            if s in ('', '-', 'nan', 'gratis', 'seikhlasnya', '0'): return 0.0
            s = re.sub(r'[rp\s,\-]', '', s).replace('.', '')
            try: return float(s)
            except: return 0.0

        df['HTM_Camp_Num'] = df['HTM_Camp'].apply(parse_htm)
        df['HTM_Parkir_Num'] = df['HTM_Parkir'].apply(parse_htm)
        df['HTM_Total_Num'] = df['HTM_Camp_Num'] + df['HTM_Parkir_Num']

        # Ekstraksi Fitur Fasilitas
        def has_kw(series, kws):
            combined = series.fillna('').astype(str).str.lower()
            return combined.str.contains('|'.join(kws), regex=True).astype(int)

        fas_cols = ['Ada_Toilet', 'Ada_Listrik', 'Ada_Warung', 'Ada_Mushola', 'Ada_Air', 'Ada_Wifi']
        df['Ada_Toilet']  = has_kw(df['Fasilitas'], ['toilet', 'wc'])
        df['Ada_Listrik'] = has_kw(df['Fasilitas'], ['listrik', 'elektrik'])
        df['Ada_Warung']  = has_kw(df['Fasilitas'], ['warung', 'cafe', 'kafe'])
        df['Ada_Mushola'] = has_kw(df['Fasilitas'], ['mushola', 'masjid'])
        df['Ada_Air']     = has_kw(df['Fasilitas'], ['air bersih', 'air', 'sumber air'])
        df['Ada_Wifi']    = has_kw(df['Fasilitas'], ['wifi', 'wi-fi'])
        df['Jml_Fasilitas'] = df[fas_cols].sum(axis=1)

        # Ekstraksi Fitur Suasana
        all_text = df['Spot_Menarik'].fillna('') + ' ' + df['Info_Tambahan'].fillna('')
        df['Tag_View_Gunung'] = has_kw(all_text, ['gunung', 'merapi', 'merbabu', 'sindoro', 'sumbing', 'andong'])
        df['Tag_Sunrise']     = has_kw(all_text, ['sunrise', 'pagi', 'awan'])
        df['Tag_Citylight']   = has_kw(all_text, ['citylight', 'city light', 'lampu kota', 'night view'])
        df['Tag_Pantai']      = has_kw(all_text, ['pantai', 'lautan', 'tebing', 'laut'])
        df['Tag_Sungai']      = has_kw(all_text, ['sungai', 'kali', 'river', 'air terjun', 'curug', 'tubing'])
        df['Tag_Dingin']      = has_kw(all_text, ['dingin', 'sejuk', 'hawa dingin', 'dieng', 'telomoyo', 'gunung'])
        df['Tag_Family']      = has_kw(all_text, ['family', 'keluarga', 'anak', 'glamping'])
        df['Tag_Adventure']   = has_kw(all_text, ['extreme', 'jurang', 'resiko', 'nanjak', 'tracking', 'jalur'])

    # Segmentasi K-Means Clustering
    cluster_features = [
        'HTM_Total_Num', 'Jml_Fasilitas',
        'Ada_Listrik', 'Ada_Air', 'Ada_Wifi', 'Ada_Warung',
        'Tag_View_Gunung', 'Tag_Sunrise', 'Tag_Citylight',
        'Tag_Pantai', 'Tag_Sungai', 'Tag_Dingin',
        'Tag_Family', 'Tag_Adventure'
    ]
    X = df[cluster_features].fillna(0)
    scaler = MinMaxScaler()
    X_scaled = scaler.fit_transform(X)

    km = KMeans(n_clusters=3, random_state=42, n_init=10)
    df['Cluster'] = km.fit_predict(X_scaled)

    centroid_df = pd.DataFrame(scaler.inverse_transform(km.cluster_centers_), columns=cluster_features)
    adv_idx = int(centroid_df['Jml_Fasilitas'].idxmin())
    prem_idx = int(centroid_df['HTM_Total_Num'].idxmax())
    fam_idx = [i for i in range(3) if i not in (adv_idx, prem_idx)][0]

    label_map = {
        adv_idx: 'Adventure & Wild',
        fam_idx: 'Family & Fasilitas Lengkap',
        prem_idx: 'Scenic & Pemandangan'
    }

    df['Tipe_Camp'] = df['Cluster'].map(label_map)
    return df

def generate_packing_checklist(row):
    items = [
        'Tenda & pasak tenda',
        'Matras alas tidur',
        'Lampu senter / headlamp'
    ]
    # Cuaca dingin / ketinggian
    if row['Tag_Dingin'] == 1 or 'dieng' in str(row['Lokasi']).lower() or 'wonosobo' in str(row['Lokasi']).lower():
        items.extend([
            'Sleeping bag hangat (rating dingin/bulu angsa/dacron tebal)',
            'Jaket windproof/tebal & kupluk hangat',
            'Kaos kaki & pakaian hangat cadangan'
        ])
    else:
        items.append('Sleeping bag standar / selimut tipis')

    # Sungai / Curug
    if row['Tag_Sungai'] == 1:
        items.extend([
            'Flysheet cadangan (antisipasi hujan/rembesan)',
            'Dry bag / kantong kedap air untuk HP & dompet',
            'Sandal gunung / alas kaki anti-selip'
        ])

    # Pantai
    if row['Tag_Pantai'] == 1:
        items.extend([
            'Pasak pantai khusus pasir / pasak ekstra panjang',
            'Sunscreen & kacamata hitam',
            'Air tawar ekstra untuk bilas'
        ])

    # Ketersediaan Listrik & Air
    if row['Ada_Listrik'] == 0:
        items.append('Powerbank kapasitas besar (tidak tersedia colokan)')
    else:
        items.append('Kabel rol / colokan ekstensi (tersedia titik listrik)')

    if row['Ada_Air'] == 0:
        items.append('Jeriken / galon air bersih sendiri untuk konsumsi')

    if row['Ada_Warung'] == 0:
        items.append('Logistik makanan & alat masak kompor portabel mandiri')

    return items

# -----------------------------------------------------------------------------
# MAIN APP FUNCTION
# -----------------------------------------------------------------------------
def render_camp_app():
    st.title("🏕️ Sistem Rekomendasi Tempat Kemah")
    st.caption("Eksplorasi destinasi perkemahan Jogja - Jateng berdasarkan preferensi suasana, fasilitas, dan panduan packing mandiri.")

    df_camp = load_camp_data()

    # Sidebar Filter
    st.sidebar.header("🔍 Filter Destinasi Kemah")

    wilayah_list = ["Semua Wilayah"] + sorted(list(df_camp['Lokasi'].dropna().unique()))
    wilayah_terpilih = st.sidebar.selectbox("Pilih Wilayah / Daerah:", wilayah_list)

    max_htm = st.sidebar.slider(
        "Maksimum Tarif Tiket (HTM + Parkir):",
        min_value=0,
        max_value=125000,
        value=50000,
        step=5000,
        format="Rp %d"
    )

    st.sidebar.subheader("Kebutuhan Fasilitas Wajib")
    butuh_toilet = st.sidebar.checkbox("Wajib Ada Toilet", value=True)
    butuh_listrik = st.sidebar.checkbox("Wajib Ada Listrik", value=False)
    butuh_air = st.sidebar.checkbox("Wajib Ada Air Bersih", value=False)
    butuh_warung = st.sidebar.checkbox("Wajib Ada Warung", value=False)
    butuh_wifi = st.sidebar.checkbox("Wajib Ada WiFi", value=False)

    st.sidebar.subheader("Preferensi Suasana Alam")
    suasana_opsi = {
        "View Gunung / Merapi / Merbabu": "Tag_View_Gunung",
        "Hawa Dingin / Sejuk": "Tag_Dingin",
        "Pemandangan City Light": "Tag_Citylight",
        "Tepi Sungai / Curug": "Tag_Sungai",
        "Pemandangan Pantai / Tebing": "Tag_Pantai",
        "Sunrise / Kabut Pagi": "Tag_Sunrise",
        "Family Friendly (Ramah Anak)": "Tag_Family",
        "Adventure / Medan Menantang": "Tag_Adventure"
    }
    suasana_terpilih = st.sidebar.multiselect(
        "Pilih Suasana yang Diinginkan:",
        options=list(suasana_opsi.keys()),
        default=["View Gunung / Merapi / Merbabu", "Hawa Dingin / Sejuk"]
    )

    # Proses Filtering
    filtered = df_camp.copy()
    if wilayah_terpilih != "Semua Wilayah":
        filtered = filtered[filtered['Lokasi'] == wilayah_terpilih]

    filtered = filtered[filtered['HTM_Total_Num'] <= max_htm]
    if butuh_toilet: filtered = filtered[filtered['Ada_Toilet'] == 1]
    if butuh_listrik: filtered = filtered[filtered['Ada_Listrik'] == 1]
    if butuh_air: filtered = filtered[filtered['Ada_Air'] == 1]
    if butuh_warung: filtered = filtered[filtered['Ada_Warung'] == 1]
    if butuh_wifi: filtered = filtered[filtered['Ada_Wifi'] == 1]

    # Scoring Suasana
    filtered['Skor_Kecocokan'] = filtered['Jml_Fasilitas'] * 0.4
    for label in suasana_terpilih:
        col = suasana_opsi[label]
        filtered['Skor_Kecocokan'] += filtered[col] * 2.0

    filtered = filtered.sort_values(by='Skor_Kecocokan', ascending=False)

    # Metrics Summary
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Destinasi Terdata", f"{len(df_camp)} Spot")
    col2.metric("Sesuai Kriteria Filter", f"{len(filtered)} Spot")
    median_htm = filtered['HTM_Total_Num'].median() if not filtered.empty else 0
    col3.metric("Median Biaya Tiket", f"Rp {int(median_htm):,}")
    spot_listrik_pct = (filtered['Ada_Listrik'].mean() * 100) if not filtered.empty else 0
    col4.metric("% Tersedia Listrik", f"{spot_listrik_pct:.1f}%")

    st.markdown("---")

    if filtered.empty:
        st.warning("⚠️ Tidak ada tempat kemah yang memenuhi seluruh kriteria filter. Silakan longgarkan filter budget atau fasilitas.")
        return

    # Tampilkan Hasil Rekomendasi
    st.subheader(f"✨ Hasil Rekomendasi Tempat Kemah ({len(filtered)} Pilihan Terbaik)")

    for rank, (_, row) in enumerate(filtered.head(8).iterrows(), 1):
        with st.expander(f"🏆 #{rank} : {row['Nama']} ({row['Lokasi']}) — Tarif: Rp {int(row['HTM_Total_Num']):,}", expanded=(rank <= 2)):
            col_info, col_pack = st.columns([1.1, 1.0])

            with col_info:
                st.markdown(f"**📍 Wilayah:** `{row['Lokasi']}` | **Kategori:** `{row['Tipe_Camp']}`")
                st.markdown(f"**💰 Tarif:** HTM Camp: `Rp {int(row['HTM_Camp_Num']):,}` | Parkir: `Rp {int(row['HTM_Parkir_Num']):,}`")
                st.markdown(f"**🌄 Daya Tarik:** {row['Spot_Menarik'] if pd.notna(row['Spot_Menarik']) else '-'}")
                st.markdown(f"**🚻 Fasilitas Tercatat:** {row['Fasilitas'] if pd.notna(row['Fasilitas']) else 'Minim / Alami'}")
                if pd.notna(row['Info_Tambahan']) and str(row['Info_Tambahan']).strip():
                    st.info(f"ℹ️ **Catatan Medan:** {row['Info_Tambahan']}")

                if pd.notna(row['Maps']) and str(row['Maps']).startswith("http"):
                    st.link_button("🗺️ Buka di Google Maps", row['Maps'])

            with col_pack:
                st.markdown("#### 🎒 Checklist Barang yang Wajib Dibawa:")
                checklist = generate_packing_checklist(row)
                for item in checklist:
                    st.checkbox(item, key=f"pack_{row['Nama']}_{item[:15]}")

    # Tinjauan Analisis Data Tab
    with st.expander("📊 Tinjauan Analitik & Visualisasi Sebaran Spot"):
        st.write("Visualisasi sebaran karakteristik tempat kemah di Jogja - Jateng:")
        img_candidates = ["eda_camp_01.png", "eda_camp_02.png", "cluster_pca.png"]
        for img in img_candidates:
            p = img if os.path.exists(img) else os.path.join("01_camp_area_recommender", img)
            if os.path.exists(p):
                st.image(p, use_container_width=True)

if __name__ == "__main__":
    st.set_page_config(page_title="Rekomendasi Tempat Kemah", layout="wide", page_icon="🏕️")
    render_camp_app()
