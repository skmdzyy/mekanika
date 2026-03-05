import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# ========== KONFIGURASI AWAL ==========
st.set_page_config(
    page_title="Game Rudal Balistik",
    page_icon="🚀",
    layout="wide"
)

st.title("🚀 SIMULATOR RUDAL BALISTIK")
st.markdown("""
*Mainkan jadi operator rudal! Tugas lo: mencapai target dengan sudut yang tepat.*
""")

# ========== SIDEBAR: PARAMETER ==========
with st.sidebar:
    st.header("🎛️ KONTROL RUDAL")
    
    # Parameter tetap (bisa diubah kalau mau)
    g = st.number_input("Gravitasi (m/s²)", value=9.8, step=0.1)
    v0 = st.number_input("Kecepatan awal (m/s)", value=3500, step=100)
    R_target = st.number_input("Jarak target (km)", value=1200, step=50) * 1000  # km ke m
    
    st.divider()
    
    # Mode permainan
    mode = st.radio(
        "Mode:",
        ["Coba 2 sudut (37° & 53°)", "Tebak sudut sendiri"]
    )
    
    if mode == "Coba 2 sudut (37° & 53°)":
        alpha1 = 37
        alpha2 = 53
        st.info(f"Sudut 1: {alpha1}°, Sudut 2: {alpha2}°")
    else:
        alpha1 = st.slider("Sudut 1 (derajat)", 0, 90, 30)
        alpha2 = st.slider("Sudut 2 (derajat)", 0, 90, 60)
    
    st.divider()
    
    # Tombol reset
    if st.button("🔄 Reset ke default"):
        st.rerun()

# ========== FUNGSI HITUNG LINTASAN ==========
def hitung_lintasan(alpha_deg, v0, g):
    alpha = np.radians(alpha_deg)
    v0x = v0 * np.cos(alpha)
    v0z = v0 * np.sin(alpha)
    
    # Waktu total di udara
    T = 2 * v0z / g
    
    # Buat array waktu
    t = np.linspace(0, T, num=500)
    
    # Posisi
    x = v0x * t
    z = v0z * t - 0.5 * g * t**2
    
    return t, x, z, T, v0x, v0z

# Hitung untuk kedua sudut
t1, x1, z1, T1, v0x1, v0z1 = hitung_lintasan(alpha1, v0, g)
t2, x2, z2, T2, v0x2, v0z2 = hitung_lintasan(alpha2, v0, g)

# Jarak akhir
jarak1 = x1[-1]
jarak2 = x2[-1]
tinggi_max1 = np.max(z1)
tinggi_max2 = np.max(z2)

# ========== LAYOUT UTAMA ==========
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("📈 LINTASAN RUDAL")
    
    # Plot
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Plot lintasan
    ax.plot(x1/1000, z1/1000, 'b-', linewidth=2, label=f'α = {alpha1}°')
    ax.plot(x2/1000, z2/1000, 'r-', linewidth=2, label=f'α = {alpha2}°')
    
    # Target
    ax.axvline(x=R_target/1000, color='green', linestyle='--', linewidth=2, label=f'Target ({R_target/1000} km)')
    
    # Tanah
    ax.axhline(y=0, color='brown', linewidth=1)
    
    # Titik impact
    if jarak1 <= R_target*1.05 and jarak1 >= R_target*0.95:
        ax.plot(jarak1/1000, 0, 'bo', markersize=10)
    if jarak2 <= R_target*1.05 and jarak2 >= R_target*0.95:
        ax.plot(jarak2/1000, 0, 'ro', markersize=10)
    
    ax.set_xlabel('Jarak horizontal (km)', fontsize=12)
    ax.set_ylabel('Ketinggian (km)', fontsize=12)
    ax.set_title('Lintasan Rudal di Udara', fontsize=14)
    ax.grid(True, alpha=0.3)
    ax.legend()
    ax.set_xlim(0, max(R_target/1000 + 200, max(x1[-1]/1000, x2[-1]/1000) + 100))
    
    st.pyplot(fig)

with col2:
    st.subheader("📊 DATA TEMBAKAN")
    
    # Tabel perbandingan
    data = {
        "Parameter": ["Sudut (°)", "Waktu tempuh (s)", "Waktu tempuh (menit)", 
                      "Tinggi maks (km)", "Jarak tempuh (km)", "Status target"],
        alpha1: [
            f"{alpha1}°",
            f"{T1:.1f}",
            f"{T1/60:.2f}",
            f"{tinggi_max1/1000:.1f}",
            f"{jarak1/1000:.1f}",
            "✅ Tepat!" if abs(jarak1 - R_target) < R_target*0.05 else "❌ Meleset"
        ],
        alpha2: [
            f"{alpha2}°",
            f"{T2:.1f}",
            f"{T2/60:.2f}",
            f"{tinggi_max2/1000:.1f}",
            f"{jarak2/1000:.1f}",
            "✅ Tepat!" if abs(jarak2 - R_target) < R_target*0.05 else "❌ Meleset"
        ]
    }
    
    # Tampilkan tabel
    st.table(data)
    
    # Deteksi radar sederhana
    st.subheader("📡 DETEKSI RADAR")
    batas_radar = 100  # km (asumsi: di atas 100 km kelihatan)
    
    if tinggi_max1/1000 > batas_radar:
        st.markdown(f"🔴 **Sudut {alpha1}°**: Terdeteksi radar! (tinggi {tinggi_max1/1000:.1f} km > {batas_radar} km)")
    else:
        st.markdown(f"🟢 **Sudut {alpha1}°**: Siluman (tinggi {tinggi_max1/1000:.1f} km < {batas_radar} km)")
        
    if tinggi_max2/1000 > batas_radar:
        st.markdown(f"🔴 **Sudut {alpha2}°**: Terdeteksi radar! (tinggi {tinggi_max2/1000:.1f} km > {batas_radar} km)")
    else:
        st.markdown(f"🟢 **Sudut {alpha2}°**: Siluman (tinggi {tinggi_max2/1000:.1f} km < {batas_radar} km)")
    
    # Nilai tambahan
    st.divider()
    st.caption(f"💡 **Info:** Untuk mencapai target {R_target/1000} km dengan v₀ = {v0} m/s, sudut optimal adalah 45° (jarak maks {((v0**2)/g)/1000:.0f} km).")

# ========== REKOMENDASI ==========
st.divider()
st.subheader("🎯 ANALISIS STRATEGI MILITER")

colA, colB, colC = st.columns(3)

with colA:
    st.metric("Sudut 37°", f"{T1/60:.2f} menit", "Lebih cepat")
    st.write("✅ Waktu tempuh minimal")
    st.write("✅ Lebih lama di bawah radar")
    st.write("⚠️ Lintasan rendah")

with colB:
    st.metric("Sudut 53°", f"{T2/60:.2f} menit", "Lebih lambat")
    st.write("❌ Waktu tempuh panjang")
    st.write("❌ Cepat terdeteksi radar")
    st.write("✅ Lintasan tinggi (jika diperlukan)")

with colC:
    if tinggi_max1 < tinggi_max2:
        st.metric("Rekomendasi", "37°", "Untuk hindari radar")
        st.info("🏆 Pilih sudut kecil untuk operasi siluman")
    else:
        st.metric("Rekomendasi", "53°", "Untuk jangkauan")
        st.info("🎯 Pilih sudut besar jika perlu lintasan tinggi")

# ========== FOOTER ==========
st.divider()
st.caption("""
**Catatan:** Simulasi ini menggunakan model proyektil ideal (tanpa hambatan udara).  
Di dunia nyata, faktor seperti drag, angin, dan rotasi bumi mempengaruhi lintasan.
""")