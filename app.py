import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="SPK TOPSIS Greyclean", layout="wide")

st.title("Sistem Pendukung Keputusan Pemilihan Produk Pembersih Sepatu")
st.subheader("Metode TOPSIS - Laundry Sepatu Greyclean")

# 1. Fitur Upload File Excel/CSV
uploaded_file = st.file_uploader("Unggah File Excel Data & Proses TOPSIS", type=["xlsx", "csv"])

if uploaded_file is not None:
    try:
        # Membaca data
        if uploaded_file.name.endswith('.csv'):
            df_raw = pd.read_csv(uploaded_file, header=None)
        else:
            df_raw = pd.read_excel(uploaded_file, sheet_name=0, header=None)
        
        st.success("File berhasil di-upload!")
        
        # Slicing Data (Baris 7-14, Kolom 1-7)
        data = df_raw.iloc[7:14, 1:7].copy()
        data.columns = ['Produk', 'C1', 'C2', 'C3', 'C4', 'C5']
        
        for col in ['C1', 'C2', 'C3', 'C4', 'C5']:
            data[col] = pd.to_numeric(data[col], errors='coerce')
        
        X = data.iloc[:, 1:].values
        alternatif = data.iloc[:, 0].values
        kolom_kriteria = ['C1 (Kebersihan)', 'C2 (Harga)', 'C3 (Ketersediaan)', 'C4 (Material)', 'C5 (Aroma)']

        # TAMPILKAN 1: Matriks Keputusan Awal
        st.write("### 1. Matriks Keputusan Awal (X)")
        st.dataframe(data.reset_index(drop=True), use_container_width=True)
        
        # --- PROSES PERHITUNGAN TOPSIS SINKRONISASI EXCEL (100% PRESISI) ---
        
        # Hitung pembagi akar jumlah kuadrat dan bulatkan 3 desimal dulu seperti di Excel
        pembagi_asli = np.sqrt((X**2).sum(axis=0))
        pembagi_excel = np.round(pembagi_asli, 3)
        
        # 2. MATRIKS NORMALISASI (R) -> Dibulatkan 3 desimal dari hasil bagi pembagi_excel
        R = np.round(X / pembagi_excel, 3)
        
        st.write("### 2. Matriks Normalisasi (R)")
        df_R = pd.DataFrame(R, columns=kolom_kriteria)
        df_R.insert(0, 'Produk/Alternatif', alternatif)
        st.dataframe(df_R, use_container_width=True)
        
        # 3. MATRIKS NORMALISASI TERBOBOT (V) -> Mengalikan R bulat dengan bobot, lalu bulat 3 desimal
        bobot = np.array([0.35, 0.25, 0.15, 0.15, 0.10])
        V = np.round(R * bobot, 3)
        
        st.write("### 3. Matriks Normalisasi Terbobot (V)")
        df_V = pd.DataFrame(V, columns=kolom_kriteria)
        df_V.insert(0, 'Produk/Alternatif', alternatif)
        st.dataframe(df_V, use_container_width=True)
        
        # 4. Solusi Ideal Positif (A+) & Negatif (A-) -> Diambil dari matriks V yang sudah bulat
        jenis = ['benefit', 'cost', 'benefit', 'benefit', 'benefit']
        A_plus = []
        A_minus = []
        
        for i in range(len(jenis)):
            if jenis[i] == 'benefit':
                A_plus.append(np.max(V[:, i]))
                A_minus.append(np.min(V[:, i]))
            else:
                A_plus.append(np.min(V[:, i]))
                A_minus.append(np.max(V[:, i]))
                
        A_plus = np.array(A_plus)
        A_minus = np.array(A_minus)
        
        st.write("### 4. Solusi Ideal Positif (A+) & Negatif (A-)")
        df_ideal = pd.DataFrame([A_plus, A_minus], columns=kolom_kriteria, index=['A+ (Ideal Positif)', 'A- (Ideal Negatif)'])
        st.dataframe(df_ideal, use_container_width=True)
        
        # 5. Jarak Jarak (D+) dan (D-) -> Menggunakan V dan A bulat, lalu dibulatkan murni 3 desimal
        D_plus = np.round(np.sqrt(np.sum((V - A_plus) ** 2, axis=1)), 3)
        D_minus = np.round(np.sqrt(np.sum((V - A_minus) ** 2, axis=1)), 3)
        
        st.write("### 5. Jarak Alternatif ke Solusi Ideal (D+ & D-)")
        df_jarak = pd.DataFrame({
            'Produk/Alternatif': alternatif,
            'D+ (Jarak Positif)': D_plus,
            'D- (Jarak Negatif)': D_minus
        })
        st.dataframe(df_jarak, use_container_width=True)
        
        # 6. Nilai Preferensi (Vi) & Perankingan Akhir -> Dihitung dari D bulat, lalu dibulatkan 3 desimal
        preferensi = np.round(D_minus / (D_plus + D_minus), 3)
        
        st.write("### 6. Nilai Preferensi (Vi) & Perankingan Akhir")
        df_ranking = pd.DataFrame({
            "Produk/Alternatif": alternatif,
            "Nilai Preferensi (Vi)": preferensi
        })
        
        df_ranking = df_ranking.sort_values(by="Nilai Preferensi (Vi)", ascending=False).reset_index(drop=True)
        df_ranking["Ranking"] = df_ranking.index + 1
        df_ranking = df_ranking[["Ranking", "Produk/Alternatif", "Nilai Preferensi (Vi)"]]
        
        # Menampilkan tabel ranking dengan highlight warna hijau pada nilai tertinggi
        st.dataframe(df_ranking.style.highlight_max(subset=["Nilai Preferensi (Vi)"], color="#D4EDDA00"), use_container_width=True)
        
        produk_terbaik = df_ranking.iloc[0]["Produk/Alternatif"]
        nilai_terbaik = df_ranking.iloc[0]["Nilai Preferensi (Vi)"]
        st.info(f"💡 **Kesimpulan:** Berdasarkan perhitungan seluruh tahapan TOPSIS, produk rekomendasi terbaik adalah **{produk_terbaik}** dengan nilai preferensi tertinggi sebesar **{nilai_terbaik}**.")
        
    except Exception as e:
        st.error(f"Terjadi kesalahan saat memproses data: {e}")
else:
    st.info("Silakan unggah file Excel/CSV proses TOPSIS untuk melihat seluruh tahapan perhitungan.")