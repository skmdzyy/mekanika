"""
PROYEKTIL NON IDEAL - DENGAN HAMBATAN UDARA LINEAR
Visualisasi 3D untuk komponen kecepatan Vx dan Vz
Dengan rendering simbol LaTeX yang sempurna
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import streamlit as st
import pandas as pd
from mpl_toolkits.mplot3d import Axes3D
import os

# ========== KONFIGURASI STREAMLIT ==========
st.set_page_config(
    page_title="Proyektil Non Ideal 3D",
    page_icon="🚀",
    layout="wide"
)

st.title("🚀 GERAK PROYEKTIL NON IDEAL 3D")
st.markdown(r"""
Visualisasi gerak proyektil dengan hambatan udara linear dalam **3 dimensi**.
Perhatikan bagaimana komponen kecepatan horizontal ($v_x$) dan vertikal ($v_z$) berubah terhadap waktu.

**Parameter penting:**
- $\gamma = \alpha/m$ = faktor redaman (semakin besar, semakin besar hambatan)
- $v_x(t) = v_{0x} e^{-\gamma t}$ (menurun eksponensial)
- $v_z(t) = v_{0z} e^{-\gamma t} - \frac{g}{\gamma}(1 - e^{-\gamma t})$
""")

# ========== SIDEBAR: PARAMETER ==========
with st.sidebar:
    st.header(r"🎛️ **PARAMETER GERAK**")
    
    # Parameter umum
    v0 = st.number_input(r"Kecepatan awal $v_0$ (m/s)", 
                         min_value=1.0, max_value=500.0, value=100.0, step=10.0)
    theta = st.slider(r"Sudut elevasi $\theta$ (derajat)", 0, 90, 45)
    g = st.number_input(r"Gravitasi $g$ (m/s²)", 
                        min_value=1.0, max_value=20.0, value=9.8, step=0.1)
    
    st.divider()
    
    # Parameter hambatan
    st.header(r"💨 **HAMBATAN UDARA**")
    gamma = st.slider(
        r"Faktor redaman $\gamma = \alpha/m$ (1/s)", 
        min_value=0.0, 
        max_value=0.5, 
        value=0.05, 
        step=0.01,
        help="Semakin besar γ, semakin besar hambatan udara"
    )
    
    st.divider()
    
    # Tampilan
    st.header(r"🎨 **TAMPILAN**")
    show_ideal = st.checkbox(r"Tampilkan model ideal ($\gamma=0$)", value=True)
    show_nonideal = st.checkbox(r"Tampilkan model non ideal", value=True)
    show_3d = st.checkbox(r"Tampilkan visualisasi 3D", value=True)
    
    st.divider()
    
    # Tombol reset
    if st.button("🔄 Reset ke default"):
        st.rerun()

# ========== FUNGSI HITUNG ==========
def hitung_ideal(v0, theta, g):
    """Hitung lintasan model ideal (tanpa hambatan)"""
    theta_rad = np.radians(theta)
    v0x = v0 * np.cos(theta_rad)
    v0z = v0 * np.sin(theta_rad)
    
    # Waktu total di udara
    T_total = 2 * v0z / g
    
    # Buat array waktu
    t = np.linspace(0, T_total, 500)
    
    # Posisi
    x = v0x * t
    z = v0z * t - 0.5 * g * t**2
    
    # Kecepatan
    vx = v0x * np.ones_like(t)
    vz = v0z - g * t
    
    return t, x, z, vx, vz, T_total

def hitung_nonideal(v0, theta, g, gamma):
    """Hitung lintasan model non ideal - METODE NUMERIK"""
    theta_rad = np.radians(theta)
    v0x = v0 * np.cos(theta_rad)
    v0z = v0 * np.sin(theta_rad)
    
    # Kalau gamma = 0, pake ideal
    if gamma <= 1e-9:
        t, x, z, vx, vz, T = hitung_ideal(v0, theta, g)
        return t, x, z, vx, vz, T
    
    # METODE NUMERIK (lebih stabil)
    dt = 0.01  # step waktu kecil
    t = [0]
    x = [0]
    z = [0]
    vx = [v0x]
    vz = [v0z]
    
    # Iterasi sampai jatuh atau waktu maksimal
    max_iter = 10000
    i = 0
    
    while z[-1] >= 0 and i < max_iter:
        # Hitung percepatan
        ax = -gamma * vx[-1]
        az = -g - gamma * vz[-1]
        
        # Update kecepatan
        vx_new = vx[-1] + ax * dt
        vz_new = vz[-1] + az * dt
        
        # Update posisi
        x_new = x[-1] + vx[-1] * dt + 0.5 * ax * dt**2
        z_new = z[-1] + vz[-1] * dt + 0.5 * az * dt**2
        
        # Simpan
        t.append(t[-1] + dt)
        x.append(x_new)
        z.append(z_new)
        vx.append(vx_new)
        vz.append(vz_new)
        
        i += 1
    
    # Konversi ke array
    t = np.array(t)
    x = np.array(x)
    z = np.array(z)
    vx = np.array(vx)
    vz = np.array(vz)
    T_total = t[-1]
    
    return t, x, z, vx, vz, T_total

def cari_titik_tertinggi(z, t):
    """Cari waktu dan tinggi maksimum"""
    if len(z) == 0:
        return 0, 0
    idx_max = np.argmax(z)
    return t[idx_max], z[idx_max]

def cari_jarak_terjauh(x, z, t):
    """Cari jarak saat z <= 0 (menyentuh tanah)"""
    if len(z) == 0:
        return 0, 0
    
    # Cari indeks terakhir sebelum z negatif
    # atau indeks dengan z minimum
    idx_land = len(z) - 1
    
    # Cari di mana z berubah tanda (dari positif ke negatif)
    for i in range(1, len(z)):
        if z[i] <= 0 and z[i-1] > 0:
            idx_land = i
            break
    
    # Interpolasi linear untuk estimasi yang lebih akurat
    if idx_land > 0 and idx_land < len(z) and z[idx_land] <= 0 < z[idx_land-1]:
        # Titik sebelum dan sesudah
        x1, x2 = x[idx_land-1], x[idx_land]
        z1, z2 = z[idx_land-1], z[idx_land]
        t1, t2 = t[idx_land-1], t[idx_land]
        
        # Interpolasi saat z = 0
        if z2 - z1 != 0:
            frac = -z1 / (z2 - z1)
            x_land = x1 + frac * (x2 - x1)
            t_land = t1 + frac * (t2 - t1)
            return x_land, t_land
    
    # Fallback: ambil titik terakhir
    return x[idx_land], t[idx_land]

# ========== HITUNG DATA ==========
# Hitung model ideal
t_ideal, x_ideal, z_ideal, vx_ideal, vz_ideal, T_ideal = hitung_ideal(v0, theta, g)

# Hitung model non ideal
if gamma > 0:
    t_non, x_non, z_non, vx_non, vz_non, T_non = hitung_nonideal(v0, theta, g, gamma)
    data_nonideal_valid = len(x_non) > 10 and np.max(x_non) > 1
else:
    t_non, x_non, z_non, vx_non, vz_non = [], [], [], [], []
    data_nonideal_valid = False

# Cari parameter penting - PAKAI FUNGSI YANG SUDAH DIPERBAIKI
tp_ideal, zm_ideal = cari_titik_tertinggi(z_ideal, t_ideal)
xm_ideal, tm_ideal = cari_jarak_terjauh(x_ideal, z_ideal, t_ideal)

if data_nonideal_valid:
    tp_non, zm_non = cari_titik_tertinggi(z_non, t_non)
    xm_non, tm_non = cari_jarak_terjauh(x_non, z_non, t_non)
else:
    tp_non, zm_non, xm_non, tm_non = 0, 0, 0, 0

# DEBUG: tampilkan nilai di terminal (akan muncul di console)
print(f"DEBUG - Ideal: x_max={x_ideal[-1]:.2f}, z_max={zm_ideal:.2f}, T_ideal={T_ideal:.2f}")
print(f"DEBUG - Ideal: xm_ideal={xm_ideal:.2f}, tm_ideal={tm_ideal:.2f}")
if data_nonideal_valid:
    print(f"DEBUG - Non Ideal: x_max={x_non[-1]:.2f}, z_max={zm_non:.2f}")
    print(f"DEBUG - Non Ideal: xm_non={xm_non:.2f}, tm_non={tm_non:.2f}")

# ========== LAYOUT UTAMA ==========
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader(r"📈 **LINTASAN PROYEKTIL**")
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Plot model ideal
    if show_ideal and len(x_ideal) > 0:
        ax.plot(x_ideal, z_ideal, 'b--', linewidth=2, 
                label=r'Ideal ($\gamma=0$)', alpha=0.7)
        ax.plot(x_ideal[0], z_ideal[0], 'bo', markersize=8)
        if xm_ideal > 0:
            ax.plot(xm_ideal, 0, 'bs', markersize=8, markerfacecolor='none',
                   label=f'Jarak: {xm_ideal:.0f} m')
    
    # Plot model non ideal
    if show_nonideal and data_nonideal_valid:
        ax.plot(x_non, z_non, 'r-', linewidth=2, 
                label=rf'Non Ideal ($\gamma={gamma:.3f}$)', alpha=0.8)
        ax.plot(x_non[0], z_non[0], 'ro', markersize=8)
        if xm_non > 0:
            ax.plot(xm_non, 0, 'rs', markersize=8, markerfacecolor='none',
                   label=f'Jarak: {xm_non:.0f} m')
    
    # Garis tanah
    ax.axhline(y=0, color='brown', linewidth=1)
    
    # Hitung batas plot
    x_max = 0
    if show_ideal and len(x_ideal) > 0:
        x_max = max(x_max, x_ideal[-1])
    if show_nonideal and data_nonideal_valid:
        x_max = max(x_max, x_non[-1])
    
    z_min = 0
    z_max = 0
    if show_ideal and len(z_ideal) > 0:
        z_min = min(z_min, z_ideal.min())
        z_max = max(z_max, z_ideal.max())
    if show_nonideal and data_nonideal_valid:
        z_min = min(z_min, z_non.min())
        z_max = max(z_max, z_non.max())
    
    ax.set_xlabel(r'Jarak horizontal $x$ (m)', fontsize=12)
    ax.set_ylabel(r'Ketinggian $z$ (m)', fontsize=12)
    ax.set_title(r'Perbandingan Lintasan: Ideal vs Non Ideal', fontsize=14)
    ax.grid(True, alpha=0.3)
    ax.legend()
    ax.set_xlim(0, x_max * 1.1)
    ax.set_ylim(bottom=min(0, z_min * 1.1), top=z_max * 1.1)
    
    st.pyplot(fig)

with col2:
    st.subheader(r"📊 **PERBANDINGAN PARAMETER**")
    
    # Tabel perbandingan
    data = {
        "Parameter": [
            r"Jarak maks $R$ (m)",
            r"Tinggi maks $H$ (m)",
            r"Waktu ke puncak $t_p$ (s)",
            r"Waktu total $T$ (s)",
            r"Kecepatan awal $v_0$ (m/s)",
            r"Sudut $\theta$ (°)"
        ],
        "Ideal": [
            f"{xm_ideal:.1f}",
            f"{zm_ideal:.1f}",
            f"{tp_ideal:.2f}",
            f"{tm_ideal:.2f}",
            f"{v0:.1f}",
            f"{theta}°"
        ],
        "Non Ideal": [
            f"{xm_non:.1f}" if data_nonideal_valid else "-",
            f"{zm_non:.1f}" if data_nonideal_valid else "-",
            f"{tp_non:.2f}" if data_nonideal_valid else "-",
            f"{tm_non:.2f}" if data_nonideal_valid else "-",
            f"{v0:.1f}",
            f"{theta}°"
        ]
    }
    
    st.table(data)
    
    # Analisis pengaruh hambatan
    st.subheader(r"📉 **ANALISIS PENGARUH HAMBATAN**")
    
    if data_nonideal_valid and xm_ideal > 0:
        reduksi_jarak = (1 - xm_non/xm_ideal) * 100
        reduksi_tinggi = (1 - zm_non/zm_ideal) * 100
    else:
        reduksi_jarak = 0
        reduksi_tinggi = 0
    
    col_a, col_b = st.columns(2)
    with col_a:
        st.metric("Reduksi jarak", f"{reduksi_jarak:.1f}%", 
                  "Lebih pendek" if reduksi_jarak > 0 else "")
    with col_b:
        st.metric("Reduksi tinggi", f"{reduksi_tinggi:.1f}%", 
                  "Lebih rendah" if reduksi_tinggi > 0 else "")
    
    st.divider()
    st.caption(rf"""
    **💡 Catatan Fisika:**
    - $\gamma = {gamma:.3f}$/s adalah faktor redaman
    - $v_x(t) = v_{{0x}} e^{{-\gamma t}}$ (menurun eksponensial)
    - $v_z(t) = v_{{0z}} e^{{-\gamma t}} - \frac{{g}}{{\gamma}}(1 - e^{{-\gamma t}})$
    """)

# ========== DEBUG VISUALIZATION ==========
with st.expander("🔍 DEBUG: Profil Ketinggian vs Waktu"):
    fig_debug, ax_debug = plt.subplots(figsize=(10, 4))
    
    if show_ideal:
        ax_debug.plot(t_ideal, z_ideal, 'b--', label='Ideal')
        # Tandai titik tertinggi
        ax_debug.plot(tp_ideal, zm_ideal, 'bo', markersize=8)
        # Tandai titik jatuh
        ax_debug.plot(tm_ideal, 0, 'bs', markersize=8)
    
    if show_nonideal and data_nonideal_valid:
        ax_debug.plot(t_non, z_non, 'r-', label='Non Ideal')
        ax_debug.plot(tp_non, zm_non, 'ro', markersize=8)
        ax_debug.plot(tm_non, 0, 'rs', markersize=8)
    
    ax_debug.axhline(y=0, color='brown', linestyle='--', alpha=0.5)
    ax_debug.set_xlabel('Waktu (s)')
    ax_debug.set_ylabel('Ketinggian (m)')
    ax_debug.set_title('Profil Ketinggian vs Waktu')
    ax_debug.grid(True, alpha=0.3)
    ax_debug.legend()
    
    st.pyplot(fig_debug)
    
    # Tampilkan nilai numerik
    col_d1, col_d2 = st.columns(2)
    with col_d1:
        st.write("**Ideal:**")
        st.write(f"- x_max: {x_ideal[-1]:.2f} m")
        st.write(f"- z_max: {zm_ideal:.2f} m @ t={tp_ideal:.2f}s")
        st.write(f"- x_land: {xm_ideal:.2f} m @ t={tm_ideal:.2f}s")
    
    with col_d2:
        if data_nonideal_valid:
            st.write("**Non Ideal:**")
            st.write(f"- x_max: {x_non[-1]:.2f} m")
            st.write(f"- z_max: {zm_non:.2f} m @ t={tp_non:.2f}s")
            st.write(f"- x_land: {xm_non:.2f} m @ t={tm_non:.2f}s")

# ========== PLOT KECEPATAN 2D ==========
st.divider()
st.subheader(r"📈 **PROFIL KECEPATAN $v_x(t)$ DAN $v_z(t)$**")

fig2, axes = plt.subplots(1, 2, figsize=(12, 4))

# Kecepatan horizontal
if show_ideal:
    axes[0].plot(t_ideal, vx_ideal, 'b--', label=r'Ideal ($\gamma=0$)', alpha=0.7)
if show_nonideal and data_nonideal_valid:
    axes[0].plot(t_non, vx_non, 'r-', label=rf'Non Ideal ($\gamma={gamma:.3f}$)')

axes[0].set_xlabel(r'Waktu $t$ (s)', fontsize=12)
axes[0].set_ylabel(r'$v_x$ (m/s)', fontsize=12)
axes[0].set_title(r'Kecepatan Horizontal $v_x(t)$', fontsize=14)
axes[0].grid(True, alpha=0.3)
axes[0].legend()

# Kecepatan vertikal
if show_ideal:
    axes[1].plot(t_ideal, vz_ideal, 'b--', label=r'Ideal ($\gamma=0$)', alpha=0.7)
if show_nonideal and data_nonideal_valid:
    axes[1].plot(t_non, vz_non, 'r-', label=rf'Non Ideal ($\gamma={gamma:.3f}$)')

axes[1].axhline(y=0, color='k', linewidth=0.5, linestyle='--', alpha=0.5)
axes[1].set_xlabel(r'Waktu $t$ (s)', fontsize=12)
axes[1].set_ylabel(r'$v_z$ (m/s)', fontsize=12)
axes[1].set_title(r'Kecepatan Vertikal $v_z(t)$', fontsize=14)
axes[1].grid(True, alpha=0.3)
axes[1].legend()

plt.tight_layout()
st.pyplot(fig2)

# ========== VISUALISASI 3D ==========
if show_3d:
    st.divider()
    st.subheader(r"🚀 **VISUALISASI 3D: LINTASAN DAN VEKTOR KECEPATAN**")
    
    fig3 = plt.figure(figsize=(14, 6))
    
    # Plot 3D untuk lintasan dengan vektor
    ax3d = fig3.add_subplot(121, projection='3d')
    
    if show_ideal and len(x_ideal) > 0:
        ax3d.plot(x_ideal, np.zeros_like(x_ideal), z_ideal, 'b--', 
                 label=r'Ideal ($\gamma=0$)', linewidth=2)
        
        # Vektor di beberapa titik
        step = max(1, len(t_ideal) // 8)
        for i in range(0, len(t_ideal), step):
            # Skala vektor untuk visualisasi
            scale = 5
            ax3d.quiver(x_ideal[i], 0, z_ideal[i], 
                       vx_ideal[i]/scale, 0, vz_ideal[i]/scale,
                       color='blue', alpha=0.6, arrow_length_ratio=0.1)
    
    if show_nonideal and data_nonideal_valid:
        ax3d.plot(x_non, np.zeros_like(x_non), z_non, 'r-', 
                 label=rf'Non Ideal ($\gamma={gamma:.3f}$)', linewidth=2)
        
        # Vektor di beberapa titik
        step = max(1, len(t_non) // 8)
        for i in range(0, len(t_non), step):
            scale = 5
            ax3d.quiver(x_non[i], 0, z_non[i], 
                       vx_non[i]/scale, 0, vz_non[i]/scale,
                       color='red', alpha=0.6, arrow_length_ratio=0.1)
    
    # Bidang tanah
    x_plane = np.linspace(0, x_max, 10)
    y_plane = np.zeros_like(x_plane)
    z_plane = np.zeros_like(x_plane)
    X, Y = np.meshgrid(x_plane, [-1, 1])
    Z = np.zeros_like(X)
    ax3d.plot_surface(X, Y, Z, alpha=0.2, color='brown')
    
    ax3d.set_xlabel(r'$x$ (m)', fontsize=12)
    ax3d.set_ylabel(r'$y$ (m)', fontsize=12)
    ax3d.set_zlabel(r'$z$ (m)', fontsize=12)
    ax3d.set_title(r'Lintasan dengan Vektor Kecepatan $(v_x, v_z)$', fontsize=14)
    ax3d.legend()
    ax3d.view_init(elev=20, azim=-60)
    
    # Plot 3D untuk profil kecepatan (ruang fase)
    ax3d2 = fig3.add_subplot(122, projection='3d')
    
    if show_ideal:
        ax3d2.plot(t_ideal, vx_ideal, vz_ideal, 'b--', 
                  label=r'Ideal ($\gamma=0$)', linewidth=2)
        ax3d2.scatter(t_ideal[::20], vx_ideal[::20], vz_ideal[::20], 
                     c='blue', s=20, alpha=0.5)
    
    if show_nonideal and data_nonideal_valid:
        ax3d2.plot(t_non, vx_non, vz_non, 'r-', 
                  label=rf'Non Ideal ($\gamma={gamma:.3f}$)', linewidth=2)
        ax3d2.scatter(t_non[::20], vx_non[::20], vz_non[::20], 
                     c='red', s=20, alpha=0.5)
    
    ax3d2.set_xlabel(r'Waktu $t$ (s)', fontsize=12)
    ax3d2.set_ylabel(r'$v_x$ (m/s)', fontsize=12)
    ax3d2.set_zlabel(r'$v_z$ (m/s)', fontsize=12)
    ax3d2.set_title(r'Ruang Fase: $v_x$ vs $v_z$ vs $t$', fontsize=14)
    ax3d2.legend()
    ax3d2.view_init(elev=20, azim=30)
    
    plt.tight_layout()
    st.pyplot(fig3)
    
    st.markdown(r"""
    **Interpretasi Visual 3D:**
    - **Plot kiri**: Lintasan proyektil di bidang $xz$ dengan vektor kecepatan $(v_x, v_z)$ sebagai panah
    - **Plot kanan**: Ruang fase yang menunjukkan hubungan $v_x$, $v_z$, dan waktu $t$
    - Panah vektor menunjukkan besar dan arah kecepatan di titik tertentu
    - Perhatikan bagaimana $v_x$ menurun pada model non ideal
    """)

# ========== FUNGSI PEMBUAT GIF ==========
def buat_gif_proyektil(x_ideal, z_ideal, x_non, z_non, t_ideal, gamma, 
                       filename="animasi_proyektil.gif", fps=10, hold_at_ground=1.0):
    
    # ========== 1. CARI INDEKS GROUND DENGAN AMAN ==========
    # Pastikan indeks tidak melebihi panjang array
    
    # Ideal - cari ground
    idx_ground_ideal = len(x_ideal) - 1  # default: indeks terakhir
    for i in range(1, len(z_ideal)):
        if z_ideal[i] <= 0 and z_ideal[i-1] > 0:
            idx_ground_ideal = min(i, len(x_ideal) - 1)  # batasi
            break
    
    # Non ideal - cari ground
    idx_ground_non = len(x_non) - 1  # default: indeks terakhir
    for i in range(1, len(z_non)):
        if z_non[i] <= 0 and z_non[i-1] > 0:
            idx_ground_non = min(i, len(x_non) - 1)  # batasi
            break
    
    # Ambil ground yang paling lambat, tapi TIDAK BOLEH MELEBIHI PANJANG ARRAY
    idx_ground = max(idx_ground_ideal, idx_ground_non)
    
    # PASTIKAN TIDAK MELEBIHI PANJANG ARRAY TERPENDEK
    min_length = min(len(x_ideal), len(x_non))
    if idx_ground >= min_length:
        idx_ground = min_length - 1
        st.warning(f"Indeks ground disesuaikan ke {idx_ground} (panjang data: {min_length})")
    
    # ========== 2. CEK APAKAH GROUND DITEMUKAN ==========
    if idx_ground <= 0 or idx_ground >= min_length:
        st.error("Tidak dapat menemukan titik ground. Gunakan data ideal sebagai fallback.")
        idx_ground = len(x_ideal) - 1
    
    # ========== 3. HITUNG JUMLAH FRAME DENGAN AMAN ==========
    stride = 3
    # Pastikan idx_ground cukup besar
    if idx_ground < stride:
        stride = 1
    
    n_frames_move = idx_ground // stride
    # Batasi jumlah frame maksimal
    n_frames_move = min(n_frames_move, 150)
    
    hold_frames = int(fps * hold_at_ground)
    total_frames = n_frames_move + hold_frames
    
    # ========== 4. DEBUG INFO ==========
    print(f"DEBUG - Panjang data ideal: {len(x_ideal)}")
    print(f"DEBUG - Panjang data non ideal: {len(x_non)}")
    print(f"DEBUG - idx_ground_ideal: {idx_ground_ideal}")
    print(f"DEBUG - idx_ground_non: {idx_ground_non}")
    print(f"DEBUG - idx_ground final: {idx_ground}")
    print(f"DEBUG - stride: {stride}, n_frames_move: {n_frames_move}")
    
    # ========== 5. SETUP PLOT ==========
    # Tentukan batas plot dengan aman
    x_max = max(x_ideal[-1] if len(x_ideal) > 0 else 0,
                x_non[-1] if len(x_non) > 0 else 0)
    z_min = min(0, 
                z_ideal.min() if len(z_ideal) > 0 else 0,
                z_non.min() if len(z_non) > 0 else 0)
    z_max = max(z_ideal.max() if len(z_ideal) > 0 else 0,
                z_non.max() if len(z_non) > 0 else 0)
    
    # Buat figure
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.set_xlim(0, x_max * 1.1)
    ax.set_ylim(bottom=z_min * 1.1 if z_min < 0 else 0,
                top=z_max * 1.1)
    ax.set_xlabel(r'Jarak horizontal $x$ (m)', fontsize=12)
    ax.set_ylabel(r'Ketinggian $z$ (m)', fontsize=12)
    ax.set_title(r'Animasi Gerak Proyektil: Ideal vs Non Ideal', fontsize=14)
    ax.grid(True, alpha=0.3)
    ax.axhline(y=0, color='brown', linewidth=1)
    
    # Inisialisasi elemen plot
    line_ideal, = ax.plot([], [], 'b--', linewidth=2, alpha=0.7, 
                          label=r'Ideal ($\gamma=0$)')
    line_non, = ax.plot([], [], 'r-', linewidth=2, 
                        label=rf'Non Ideal ($\gamma={gamma:.3f}$)')
    point_ideal, = ax.plot([], [], 'bo', markersize=10)
    point_non, = ax.plot([], [], 'ro', markersize=10)
    time_text = ax.text(0.02, 0.95, '', transform=ax.transAxes, fontsize=12,
                        bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.8))
    ax.legend(loc='upper right')
    
    # ========== 6. FUNGSI INISIALISASI ==========
    def init():
        line_ideal.set_data([], [])
        line_non.set_data([], [])
        point_ideal.set_data([], [])
        point_non.set_data([], [])
        time_text.set_text('')
        return line_ideal, line_non, point_ideal, point_non, time_text
    
    # ========== 7. FUNGSI ANIMASI DENGAN PENGECEKAN BATAS ==========
    def animate(frame):
        if frame < n_frames_move:
            # FRAME BERGERAK
            idx = min(frame * stride, idx_ground)  # PASTIKAN TIDAK MELEBIHI GROUND
            
            # Pastikan idx tidak melebihi panjang array
            if idx >= len(x_ideal):
                idx = len(x_ideal) - 1
            if idx >= len(x_non):
                idx = len(x_non) - 1
            
            # Update garis ideal
            line_ideal.set_data(x_ideal[:idx], z_ideal[:idx])
            if idx > 0 and idx-1 < len(x_ideal):
                point_ideal.set_data([x_ideal[idx-1]], [z_ideal[idx-1]])
            
            # Update garis non ideal
            line_non.set_data(x_non[:idx], z_non[:idx])
            if idx > 0 and idx-1 < len(x_non):
                point_non.set_data([x_non[idx-1]], [z_non[idx-1]])
            
            # Update teks waktu
            if len(t_ideal) > 0 and idx < len(t_ideal):
                time_text.set_text(f'$t = {t_ideal[idx]:.1f}$ s')
        
        else:
            # FRAME DIAM DI GROUND
            # Gunakan idx_ground yang sudah dibatasi
            safe_idx = min(idx_ground, len(x_ideal)-1, len(x_non)-1)
            
            line_ideal.set_data(x_ideal[:safe_idx], z_ideal[:safe_idx])
            line_non.set_data(x_non[:safe_idx], z_non[:safe_idx])
            
            if safe_idx > 0:
                point_ideal.set_data([x_ideal[safe_idx-1]], [z_ideal[safe_idx-1]])
                point_non.set_data([x_non[safe_idx-1]], [z_non[safe_idx-1]])
            
            if len(t_ideal) > 0 and safe_idx < len(t_ideal):
                time_text.set_text(f'$t = {t_ideal[safe_idx]:.1f}$ s (GROUND)')
            else:
                time_text.set_text('GROUND')
        
        return line_ideal, line_non, point_ideal, point_non, time_text
    
    # ========== 8. BUAT ANIMASI ==========
    anim = FuncAnimation(fig, animate, init_func=init,
                         frames=total_frames, 
                         interval=1000/fps,
                         blit=True, 
                         repeat=True)
    
    # ========== 9. SIMPAN SEBAGAI GIF ==========
    anim.save(filename, writer='pillow', fps=fps, dpi=80)
    plt.close(fig)
    
    return filename

# ========== ANIMASI GIF ==========
st.divider()
st.subheader(r"🎬 **ANIMASI GERAK PROYEKTIL (GIF)**")

col_gif1, col_gif2, col_gif3 = st.columns([1, 2, 1])

with col_gif2:
    st.markdown(r"""
    Klik tombol di bawah untuk membuat animasi perbandingan 
    antara model ideal ($\gamma=0$) dan non ideal ($\gamma>0$).
    
    Animasi akan **loop setelah proyektil menyentuh ground**.
    """)
    
    # Tambah kontrol untuk pengaturan GIF
    col_speed, col_hold = st.columns(2)
    with col_speed:
        gif_speed = st.select_slider(
            "Kecepatan",
            options=["Lambat", "Sedang", "Cepat"],
            value="Sedang"
        )
        speed_map = {"Lambat": 5, "Sedang": 10, "Cepat": 20}
        fps = speed_map[gif_speed]
    
    with col_hold:
        hold_time = st.slider(
            "Diam di ground (detik)",
            min_value=0.0,
            max_value=3.0,
            value=1.0,
            step=0.5
        )
    
    if st.button("🎥 BUAT ANIMASI GIF", use_container_width=True):
        # Cek apakah data valid
        if len(x_ideal) == 0 or len(x_non) == 0:
            st.warning("Data tidak lengkap untuk membuat animasi")
        else:
            with st.spinner("Membuat animasi..."):
                try:
                    # Panggil fungsi pembuat GIF
                    gif_file = buat_gif_proyektil(
                        x_ideal, z_ideal, 
                        x_non, z_non,
                        t_ideal,
                        gamma,
                        filename=f"animasi_gamma_{gamma:.2f}.gif",
                        fps=fps,
                        hold_at_ground=hold_time
                    )
                    
                    # Tampilkan GIF
                    st.image(gif_file, caption=rf"Animasi dengan $\gamma = {gamma:.3f}$/s (loop setelah ground)")
                    
                    # Tombol download
                    with open(gif_file, "rb") as f:
                        gif_bytes = f.read()
                        st.download_button(
                            label="📥 Download GIF",
                            data=gif_bytes,
                            file_name=f"proyektil_ground_loop_{gamma:.2f}.gif",
                            mime="image/gif"
                        )
                    
                    # Bersihin file temporary
                    try:
                        os.remove(gif_file)
                    except:
                        pass
                        
                except Exception as e:
                    st.error(f"Error membuat GIF: {e}")
# ========== EKSPLORASI GAMMA ==========
st.divider()
st.subheader(r"🔬 **EKSPLORASI PENGARUH FAKTOR REDAMAN ($\gamma$)**")

if st.checkbox("Tampilkan perbandingan beberapa nilai $\gamma$"):
    gamma_values = [0.0, 0.02, 0.05, 0.1, 0.2]
    colors = ['blue', 'green', 'red', 'purple', 'orange']
    
    fig4, ax4 = plt.subplots(figsize=(10, 6))
    
    for gamma_val, color in zip(gamma_values, colors):
        if gamma_val == 0:
            # Model ideal
            _, x_temp, z_temp, _, _, _ = hitung_ideal(v0, theta, g)
            label = rf'Ideal ($\gamma=0$)'
            linestyle = '--'
        else:
            # Model non ideal
            try:
                _, x_temp, z_temp, _, _, _ = hitung_nonideal(v0, theta, g, gamma_val)
                label = rf'$\gamma = {gamma_val:.2f}$/s'
                linestyle = '-'
            except:
                continue
        
        # Plot
        if len(x_temp) > 0 and len(z_temp) > 0:
            ax4.plot(x_temp, z_temp, color=color, linestyle=linestyle, 
                    linewidth=2, label=label, alpha=0.8)
    
    ax4.axhline(y=0, color='brown', linewidth=1)
    ax4.set_xlabel(r'Jarak horizontal $x$ (m)', fontsize=12)
    ax4.set_ylabel(r'Ketinggian $z$ (m)', fontsize=12)
    ax4.set_title(r'Pengaruh Faktor Redaman $\gamma$ terhadap Lintasan', fontsize=14)
    ax4.grid(True, alpha=0.3)
    ax4.legend()
    
    st.pyplot(fig4)
    
    st.info(r"""
    **Observasi:**
    - $\gamma = 0$ → lintasan parabola (model ideal)
    - $\gamma$ kecil → sedikit tereduksi
    - $\gamma$ besar → jarak dan tinggi berkurang drastis
    - Lintasan menjadi tidak simetris (bagian turun lebih curam)
    """)

# ========== FOOTER ==========
st.divider()
st.caption(r"""
**Dasar Teori:** PPT Mekanika FIT 203 - Gerak Proyektil Non Ideal 2 Dimensi (Supadi, M.Si)  
**Rumus:** Solusi numerik untuk hambatan linear $F_d = -\alpha \vec{v}$ dengan faktor redaman $\gamma = \alpha/m$

**Persamaan:**
- $v_x(t) = v_{0x} e^{-\gamma t}$
- $v_z(t) = v_{0z} e^{-\gamma t} - \frac{g}{\gamma}(1 - e^{-\gamma t})$
- $x(t) = \frac{v_{0x}}{\gamma} (1 - e^{-\gamma t})$
- $z(t) = \left(\frac{v_{0z}}{\gamma} + \frac{g}{\gamma^2}\right)(1 - e^{-\gamma t}) - \frac{g}{\gamma}t$
""")