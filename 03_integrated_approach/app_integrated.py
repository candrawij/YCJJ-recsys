import streamlit as st
import pandas as pd
import numpy as np
import os
import sys

# Import helper loader dari modul 1 & 2
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, ".."))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

try:
    from importlib import import_module
    camp_module = import_module("01_camp_area_recommender.app_camp")
    gear_module = import_module("02_gear_recommender.app_gear")
    load_camp_data = camp_module.load_camp_data
    generate_packing_checklist = camp_module.generate_packing_checklist
    load_gear_data = gear_module.load_gear_data
except Exception:
    # Fallback import jika dijalankan langsung dari folder
    sys.path.append(os.path.join(parent_dir, "01_camp_area_recommender"))
    sys.path.append(os.path.join(parent_dir, "02_gear_recommender"))
    from app_camp import load_camp_data, generate_packing_checklist
    from app_gear import load_gear_data

def render_integrated_app():
    st.title("🏕️ Smart Camping Planner Terpadu (Jogja - Jateng)")
    st.caption("Perencanaan liburan kemah holistik: Temukan destinasi yang cocok, dapatkan checklist barang yang wajib dibawa, dan hitung estimasi total anggaran perjalanan.")

    df_camp = load_camp_data()
    df_gear = load_gear_data()

    # Form Perencanaan Perjalanan
    with st.form("planner_form"):
        st.subheader("1. Preferensi Tempat & Wisata")
        c1, c2, c3 = st.columns(3)

        wilayah_list = ["Semua Wilayah"] + sorted(list(df_camp['Lokasi'].dropna().unique()))
        lokasi_pilih = c1.selectbox("Destinasi Wilayah:", wilayah_list)

        budget_tiket = c2.slider("Batas Tarif Tiket per Orang (HTM + Parkir):", 0, 100000, 35000, 5000, format="Rp %d")
        jumlah_orang = c3.number_input("Jumlah Peserta Kemah (Orang):", 1, 20, 2)

        st.subheader("2. Suasana & Karakteristik yang Diinginkan")
        suasana_opsi = {
            "Pemandangan Gunung (Merapi/Merbabu/Lawu)": "Tag_View_Gunung",
            "Hawa Dingin Pegunungan": "Tag_Dingin",
            "City Light Malam Hari": "Tag_Citylight",
            "Tepi Sungai / Suasana Air": "Tag_Sungai",
            "Pantai & Laut": "Tag_Pantai",
            "Family-Friendly (Ramah Anak)": "Tag_Family"
        }
        suasana_pilih = st.multiselect("Pilih Karakter Tempat:", list(suasana_opsi.keys()), default=["Pemandangan Gunung (Merapi/Merbabu/Lawu)"])

        st.subheader("3. Status Perlengkapan Camping")
        status_gear = st.radio(
            "Apakah Anda sudah memiliki perlengkapan sendiri?",
            ["Sudah punya (Hanya butuh checklist barang yang harus dibawa)",
             "Belum punya / Perlu rekomendasi pengadaan paket gear baru"],
            index=0
        )

        submit_btn = st.form_submit_button("🚀 Rancang Perjalanan Camping", type="primary")

    if submit_btn or "has_run" in st.session_state:
        st.session_state["has_run"] = True

        # Filter Camp
        filtered = df_camp.copy()
        if lokasi_pilih != "Semua Wilayah":
            filtered = filtered[filtered['Lokasi'] == lokasi_pilih]
        filtered = filtered[filtered['HTM_Total_Num'] <= budget_tiket]

        filtered['Skor'] = filtered['Jml_Fasilitas'] * 0.5
        for s in suasana_pilih:
            filtered['Skor'] += filtered[suasana_opsi[s]] * 2.0

        filtered = filtered.sort_values(by='Skor', ascending=False)

        if filtered.empty:
            st.error("❌ Tidak ada destinasi yang cocok dengan kriteria filter. Silakan naikkan batas budget tiket atau pilih 'Semua Wilayah'.")
            return

        top_spot = filtered.iloc[0]

        st.markdown("---")
        st.subheader(f"🏆 Rekomendasi Destinasi Utama: **{top_spot['Nama']}** ({top_spot['Lokasi']})")

        col_spot, col_budget = st.columns([1.4, 1.0])

        with col_spot:
            st.markdown(f"**🏷️ Tipe Spot:** `{top_spot['Tipe_Camp']}`")
            st.markdown(f"**💰 Tarif:** HTM Camp: `Rp {int(top_spot['HTM_Camp_Num']):,}` | Parkir: `Rp {int(top_spot['HTM_Parkir_Num']):,}` per orang")
            st.markdown(f"**✨ Daya Tarik:** {top_spot['Spot_Menarik']}")
            st.markdown(f"**🚻 Fasilitas:** {top_spot['Fasilitas']}")
            if pd.notna(top_spot['Info_Tambahan']) and str(top_spot['Info_Tambahan']).strip():
                st.info(f"ℹ️ {top_spot['Info_Tambahan']}")
            if pd.notna(top_spot['Maps']) and str(top_spot['Maps']).startswith("http"):
                st.link_button("🗺️ Buka Titik Lokasi di Google Maps", top_spot['Maps'])

        with col_budget:
            st.markdown("### 💵 Estimasi Biaya Wisata")
            biaya_tiket_total = top_spot['HTM_Total_Num'] * jumlah_orang
            biaya_konsumsi_est = 75000 * jumlah_orang  # estimasi konsumsi makan/minum per orang
            st.write(f"• Tiket & Parkir ({jumlah_orang} org): **Rp {int(biaya_tiket_total):,}**")
            st.write(f"• Estimasi Makan & Minum: **Rp {int(biaya_konsumsi_est):,}**")
            total_operasional = biaya_tiket_total + biaya_konsumsi_est
            st.metric("Total Biaya Operasional", f"Rp {int(total_operasional):,}")

        st.markdown("---")
        col_pack, col_gear = st.columns(2)

        with col_pack:
            st.markdown("### 🎒 Checklist Barang Bawaan (Packing List)")
            st.caption("Barang esensial yang harus disiapkan dari rumah:")
            checklist = generate_packing_checklist(top_spot)
            for item in checklist:
                st.checkbox(item, value=True, key=f"int_pack_{item[:12]}")

        with col_gear:
            if "Belum punya" in status_gear:
                st.markdown("### 🛒 Rekomendasi Paket Belanja Gear Esensial")
                st.caption("Pilihan gear hemat berkualitas untuk pemula:")
                kategori_inti = ['Tenda / Tarp Tent', 'Sleeping Bag', 'Matras', 'Cooking Set']
                total_gear_beli = 0
                for kat in kategori_inti:
                    k_sub = df_gear[(df_gear['Kategori'] == kat) & df_gear['Harga_Num'].notna()].sort_values('Harga_Num')
                    if not k_sub.empty:
                        item_gear = k_sub.iloc[0]
                        total_gear_beli += item_gear['Harga_Num']
                        st.markdown(f"• **{kat}:** {item_gear['Nama']} — `Rp {int(item_gear['Harga_Num']):,}`")
                st.metric("Estimasi Investasi Alat", f"Rp {int(total_gear_beli):,}")
                st.caption("💡 Tips: Jika budget terbatas, perlengkapan di atas bisa disewa di rental outdoor terdekat.")
            else:
                st.markdown("### 👍 Perlengkapan Sudah Siap!")
                st.success("Anda sudah memiliki perlengkapan sendiri. Pastikan seluruh barang pada checklist di sebelah kiri telah masuk ke dalam ransel sebelum berangkat!")

if __name__ == "__main__":
    st.set_page_config(page_title="Smart Camping Planner", layout="wide", page_icon="🏕️")
    render_integrated_app()
