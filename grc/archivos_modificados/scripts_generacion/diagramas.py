"""Diagramas tecnicos del Grupo 5 (escenario S3, Tx-canal-Rx, instrumentacion BER, enlace HackRF)."""
import os, sys, numpy as np, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyBboxPatch, FancyArrowPatch, Polygon, Circle
OUT = sys.argv[1]; os.makedirs(OUT, exist_ok=True)
plt.rcParams.update({'font.size': 9, 'savefig.bbox': 'tight', 'figure.dpi': 170})

# ============================ 1. ESCENARIO ===================================
fig, ax = plt.subplots(figsize=(10, 6.4))
W, H = 40, 24
ax.add_patch(Rectangle((0, 0), W, H, fill=False, lw=4, ec='#444'))                       # muros
ax.add_patch(Rectangle((17, -0.4), 5, 0.8, fc='white', ec='white'))                        # puerta
ax.text(19.5, -1.3, 'Puerta de carga', ha='center', fontsize=8)
# estanterias metalicas (racks)
racks = [(4, 2, 1.4, 11, 'Estantería\nmetálica 1'), (10, 2, 1.4, 9, 'Estantería\nmetálica 2'),
         (21, 20, 13, 1.4, 'Estantería metálica 3 (cara reflectora)'), (23, 1.6, 10, 1.4, 'Estantería metálica 4')]
for (x, y, w, h, lab) in racks:
    ax.add_patch(Rectangle((x, y), w, h, fc='#b0b7c3', ec='#4a5568', lw=1.2, hatch='///'))
    if w < h:
        ax.text(x + w / 2, y + h + 0.5, lab, ha='center', fontsize=7)
    else:
        ax.text(x + w / 2, y + h + 0.4, lab, ha='center', fontsize=7)
for (x, y) in [(15, 6), (17.2, 6), (15, 8.2)]:
    ax.add_patch(Rectangle((x, y), 2, 2, fc='#d9b382', ec='#8b5a2b'))
ax.text(17.2, 10.8, 'Pallets', ha='center', fontsize=7)
ax.add_patch(Rectangle((35.5, 1), 3.5, 4, fc='#e2e8f0', ec='#4a5568'))
ax.text(37.25, 3.0, 'Oficina\ntécnica', ha='center', va='center', fontsize=7)
tx = np.array([7.6, 17.5]); rx = np.array([36.5, 8.2])
def antena(p, c):
    ax.plot([p[0], p[0]], [p[1], p[1] + 1.6], color=c, lw=2)
    ax.add_patch(Polygon([[p[0] - .6, p[1] + 1.6], [p[0] + .6, p[1] + 1.6], [p[0], p[1] + 2.4]], color=c))
ax.add_patch(FancyBboxPatch(tx - [1.1, .8], 2.2, 1.6, boxstyle='round,pad=0.1', fc='#1f4e79', ec='k'))
ax.text(*tx, 'Tx', color='white', ha='center', va='center', weight='bold')
antena(tx + [0, .8], '#1f4e79')
ax.text(tx[0] - 4.6, tx[1] + 1.4, 'Nodo sensor (Tx)\nBPSK, Rs = 32 kBd', fontsize=7.5, ha='center')
ax.add_patch(FancyBboxPatch(rx - [1.1, .8], 2.2, 1.6, boxstyle='round,pad=0.1', fc='#b22222', ec='k'))
ax.text(*rx, 'Rx', color='white', ha='center', va='center', weight='bold')
antena(rx + [0, .8], '#b22222')
ax.text(rx[0] - 4.2, rx[1] - 1.6, 'Estación de\nsupervisión (Rx)', fontsize=7.5, ha='center')
# camino directo (linea de vista despejada)
ax.annotate('', xy=rx + [-1.2, .2], xytext=tx + [1.2, -.3], arrowprops=dict(arrowstyle='-|>', color='#2e8b57', lw=2.6))
ax.text(19.5, 10.6, 'Camino directo  d$_0$ (línea de vista)\nganancia 1, retardo 0', color='#2e8b57', fontsize=8, weight='bold', rotation=-17)
# eco modelado: reflexion en la cara inferior de la estanteria 3
refl = np.array([25.5, 20.0])
ax.plot([tx[0] + 0.6, refl[0]], [tx[1] + 0.9, refl[1]], color='#d08c00', lw=2.2, ls='--')
ax.annotate('', xy=rx + [-0.2, 1.0], xytext=refl, arrowprops=dict(arrowstyle='-|>', color='#d08c00', lw=2.2, ls='--'))
ax.plot(*refl, marker='*', ms=16, color='#d08c00', mec='k')
ax.text(10.8, 21.0, 'Eco  d$_1$ > d$_0$\nganancia α = |α|e$^{jφ}$\nretardo τ = (d$_1$−d$_0$)/c', color='#8a5a00', fontsize=8, weight='bold')
# reflexion secundaria (fuera del modelo)
r2 = np.array([25.5, 3.0])
ax.plot([tx[0] + 0.8, r2[0]], [tx[1] - .8, r2[1]], color='#b22222', lw=1.2, ls=':')
ax.annotate('', xy=rx + [-1.0, -0.4], xytext=r2, arrowprops=dict(arrowstyle='-|>', color='#b22222', lw=1.2, ls=':'))
ax.text(23.0, 0.5, 'Reflexión secundaria en estantería 4 (no modelada)', color='#b22222', fontsize=7)
# leyenda
from matplotlib.lines import Line2D
leg = [Line2D([0], [0], color='#2e8b57', lw=2.6, label='Camino directo'),
       Line2D([0], [0], color='#d08c00', lw=2.2, ls='--', label='Camino reflejado (eco modelado)'),
       Line2D([0], [0], color='#b22222', lw=1.2, ls=':', label='Otras reflexiones (fuera del modelo)'),
       Rectangle((0, 0), 1, 1, fc='#b0b7c3', ec='#4a5568', hatch='///', label='Estantería metálica'),
       Rectangle((0, 0), 1, 1, fc='#d9b382', ec='#8b5a2b', label='Pallets / carga')]
ax.legend(handles=leg, loc='upper center', bbox_to_anchor=(0.5, -0.06), ncol=3, fontsize=7.5, frameon=False)
ax.text(0.5, H + 2.6, 'Modelo de canal en banda base:  r(t) = s(t) + α·s(t − τ) + w(t)    —    en simulación τ = T$_s$ = 31,25 µs (8 muestras), '
        '|α| ∈ {0; 0,2; 0,5; 0,8}', fontsize=8.5, weight='bold')
ax.text(W, -1.3, 'Escala indicativa: 40 m × 24 m', fontsize=7, ha='right', color='0.3')
ax.set_xlim(-1, W + 1); ax.set_ylim(-2, H + 3.5); ax.set_aspect('equal'); ax.axis('off')
ax.set_title('Figura 1. Escenario S3 — bodega con multitrayectoria (vista en planta)', fontsize=11, weight='bold', pad=22)
fig.savefig(os.path.join(OUT, 'Fig1_Escenario_S3_bodega.png')); plt.close(fig)


# ===================== utilidades diagrama de bloques ========================
def box(ax, x, y, w, h, txt, fc='#e8f0fa', ec='#1f4e79', fs=8, bold=False):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0.02,rounding_size=0.08', fc=fc, ec=ec, lw=1.3))
    ax.text(x + w / 2, y + h / 2, txt, ha='center', va='center', fontsize=fs, weight='bold' if bold else 'normal')
def arr(ax, p, q, txt='', c='k', off=(0, 0.12), fs=7, ls='-'):
    ax.add_patch(FancyArrowPatch(p, q, arrowstyle='-|>', mutation_scale=11, color=c, lw=1.2, ls=ls))
    if txt:
        ax.text((p[0] + q[0]) / 2 + off[0], (p[1] + q[1]) / 2 + off[1], txt, ha='center', fontsize=fs, color=c)

# ===================== 2. DIAGRAMA Tx - CANAL - Rx ===========================
fig, ax = plt.subplots(figsize=(12, 5.6))
ax.set_xlim(0, 12); ax.set_ylim(0, 5.6); ax.axis('off')
ax.add_patch(Rectangle((0.1, 3.0), 4.5, 2.2, fill=False, ls='--', ec='#1f4e79')); ax.text(0.2, 5.05, 'TRANSMISOR', color='#1f4e79', weight='bold')
ax.add_patch(Rectangle((4.8, 3.0), 3.0, 2.2, fill=False, ls='--', ec='#d08c00')); ax.text(4.9, 5.05, 'CANAL (S3)', color='#d08c00', weight='bold')
ax.add_patch(Rectangle((0.1, 0.2), 11.8, 2.4, fill=False, ls='--', ec='#b22222')); ax.text(0.2, 2.45, 'RECEPTOR (diseño del equipo, Guía 2)', color='#b22222', weight='bold')
box(ax, 0.25, 3.5, 1.0, 1.0, 'Fuente\nbits\n(Random\nSource)')
box(ax, 1.4, 3.5, 1.0, 1.0, 'Mapeo\nBPSK\n0→−1, 1→+1')
box(ax, 2.55, 3.5, 1.0, 1.0, 'Conformador\nrect. h=[1]×8\n(Interp FIR)')
box(ax, 3.7, 3.5, 0.8, 1.0, 'Throttle\nfs')
arr(ax, (1.25, 4), (1.4, 4)); arr(ax, (2.4, 4), (2.55, 4)); arr(ax, (3.55, 4), (3.7, 4))
ax.text(1.9, 3.25, 'Rb = 32 kb/s', ha='center', fontsize=7); ax.text(3.05, 3.25, 'fs = 256 kS/s', ha='center', fontsize=7)
box(ax, 5.0, 4.15, 1.1, 0.75, 'Retardo\nD_eco = 8 m.\n(τ = Ts)', fc='#fff3dc', ec='#d08c00')
box(ax, 6.25, 4.15, 0.75, 0.75, '× α\n|α|e$^{jφ}$', fc='#fff3dc', ec='#d08c00')
ax.add_patch(Circle((7.35, 3.85), 0.22, fc='white', ec='k')); ax.text(7.35, 3.85, '+', ha='center', va='center', fontsize=12)
arr(ax, (4.5, 4), (7.13, 3.85), 'directo', c='#2e8b57', off=(0, -0.25))
arr(ax, (4.75, 4.0), (5.0, 4.5)); arr(ax, (6.1, 4.52), (6.25, 4.52)); arr(ax, (7.0, 4.5), (7.3, 4.07))
ax.add_patch(Circle((8.3, 3.85), 0.22, fc='white', ec='k')); ax.text(8.3, 3.85, '+', ha='center', va='center', fontsize=12)
box(ax, 7.95, 4.55, 0.75, 0.6, 'AWGN\nnoise_amp', fc='#f2f2f2', ec='0.4', fs=7)
arr(ax, (7.57, 3.85), (8.08, 3.85)); arr(ax, (8.32, 4.55), (8.3, 4.07))
box(ax, 9.0, 3.45, 2.8, 0.85, 'Visualización Rx: PSD Tx vs Rx,\nenvolvente, I-Q sobremuestreado', fc='#f7f7f7', ec='0.4', fs=7)
arr(ax, (8.52, 3.85), (9.0, 3.85), 'r[n]')
# receptor
arr(ax, (8.3, 3.63), (8.3, 1.85)); ax.plot([8.3, 0.75], [1.85, 1.85], color='k', lw=1.2)
arr(ax, (0.75, 1.85), (0.75, 1.55))
box(ax, 0.25, 0.75, 1.3, 0.8, 'Filtro acoplado\nh$_{mf}$=[1/8]×8\n(FIR)', fc='#fbe9e9', ec='#b22222')
box(ax, 2.0, 0.75, 1.3, 0.8, 'Keep One in N\nN = Sps = 8\n(muestra 8k+7)', fc='#fbe9e9', ec='#b22222')
box(ax, 3.75, 0.75, 1.2, 0.8, 'Re{·}\n(Complex\nto Real)', fc='#fbe9e9', ec='#b22222')
box(ax, 5.4, 0.75, 1.2, 0.8, 'Decisión\nBinary Slicer\numbral 0', fc='#fbe9e9', ec='#b22222')
box(ax, 7.1, 0.75, 1.5, 0.8, 'BER = XOR(bits Tx\nretardados, bits Rx)\npromedio N_ber', fc='#fbe9e9', ec='#b22222')
arr(ax, (1.55, 1.15), (2.0, 1.15)); arr(ax, (3.3, 1.15), (3.75, 1.15)); arr(ax, (4.95, 1.15), (5.4, 1.15)); arr(ax, (6.6, 1.15), (7.1, 1.15), 'bits Rx')
box(ax, 1.0, 0.27, 1.6, 0.38, 'Diagrama de ojo (Eye Sink)', fc='white', ec='0.5', fs=7)
box(ax, 2.95, 0.27, 2.0, 0.38, 'Constelación recuperada', fc='white', ec='0.5', fs=7)
arr(ax, (1.0, 0.75), (1.3, 0.65), c='0.5'); arr(ax, (2.7, 0.75), (3.3, 0.65), c='0.5')
ax.plot([0.75, 0.75, 9.3, 9.3], [3.5, 2.9, 2.9, 1.55], color='0.4', ls=':', lw=1)
ax.text(5.0, 2.95, 'bits Tx de referencia (antes del mapeo) → Delay delay_bits = 0', fontsize=7, color='0.3')
arr(ax, (9.3, 1.55), (8.6, 1.3), c='0.4')
box(ax, 9.0, 0.45, 2.75, 1.4, 'Parámetros\nModulación BPSK, M=2, k=1\nRs = 32 kBd, Rb = 32 kb/s\nSps = 8, fs = 256 kS/s\nBW (nulo a nulo) = 2Rs = 64 kHz\nnoise_amp = 0,10', fc='#f0f7ee', ec='#2e8b57', fs=7.3)
ax.set_title('Figura 2. Diagrama técnico Tx – canal multitrayectoria – Rx  (S3_Multitrayectoria_BPSK_Grupo5.grc)', fontsize=10.5, weight='bold')
fig.savefig(os.path.join(OUT, 'Fig2_Diagrama_Tx_Canal_Rx.png')); plt.close(fig)

# ===================== 3. INSTRUMENTACION BER ================================
fig, ax = plt.subplots(figsize=(11, 3.8)); ax.set_xlim(0, 11); ax.set_ylim(0, 3.8); ax.axis('off')
box(ax, 0.2, 2.2, 1.4, 0.9, 'Tx BPSK\n(bits, mapeo,\nconformador)')
box(ax, 1.9, 2.2, 1.6, 0.9, 'Canal eco\n(sustituye al\nenlace SDR)', fc='#fff3dc', ec='#d08c00')
box(ax, 3.8, 2.2, 1.7, 0.9, 'e_EbN0_Sweep\nAWGN controlado\n0→14 dB, paso 1 dB', fc='#efe6fb', ec='#6b46c1', bold=True)
box(ax, 5.8, 2.2, 2.0, 0.9, 'Rx digital del equipo\n(FA → muestreo →\ndecisión)', fc='#fbe9e9', ec='#b22222')
box(ax, 5.8, 0.4, 2.0, 0.9, 'e_BER_Curve\nin0 bits Tx, in1 bits Rx\ndelay_bits = 0', fc='#efe6fb', ec='#6b46c1', bold=True)
box(ax, 8.3, 1.2, 2.4, 0.7, 'QT Vector Sink\nlog10(BER) vs Eb/N0', fc='white', ec='0.4')
box(ax, 8.3, 0.25, 2.4, 0.7, 'e_BER_CSV → curva_BER.csv', fc='white', ec='0.4')
arr(ax, (1.6, 2.65), (1.9, 2.65)); arr(ax, (3.5, 2.65), (3.8, 2.65), 'bb_rate\n256 kS/s', off=(0, 0.18))
arr(ax, (5.5, 2.65), (5.8, 2.65)); arr(ax, (6.8, 2.2), (6.8, 1.3), 'bits Rx', off=(0.35, 0))
ax.plot([0.9, 0.9, 5.4], [2.2, 0.85, 0.85], color='k', lw=1.2); arr(ax, (5.4, 0.85), (5.8, 0.85)); ax.text(2.5, 0.95, 'bits Tx (antes del mapeo)', fontsize=7)
arr(ax, (7.8, 0.95), (8.3, 1.5), 'log10 BER', off=(0.1, 0.1)); arr(ax, (7.8, 0.7), (8.3, 0.6))
ax.text(5.5, 3.5, 'Parámetros: Rb = 32 000 b/s, bb_rate = 256 000 S/s, EbN0_min = 0, EbN0_max = 14, EbN0_step = 1 dB, bits_por_punto = 100 000, bits_guardia = 1 000, update_every = 1 000',
        ha='center', fontsize=7.5)
ax.set_title('Figura 3. Integración de la instrumentación BER (Fase 4) — ejecutada en SIMULACIÓN', fontsize=10.5, weight='bold')
fig.savefig(os.path.join(OUT, 'Fig3_Instrumentacion_BER.png')); plt.close(fig)

# ===================== 4. ENLACE HACKRF (FASE 3) =============================
fig, ax = plt.subplots(figsize=(11, 3.6)); ax.set_xlim(0, 11); ax.set_ylim(0, 3.6); ax.axis('off')
box(ax, 0.2, 1.4, 1.6, 1.0, 'PC Tx\nGRC TX BPSK\n256 kS/s')
box(ax, 2.1, 1.4, 1.6, 1.0, 'Rational Resampler\n×125/16\n→ 2 MS/s', fc='#f2f2f2', ec='0.4')
box(ax, 4.0, 1.4, 1.3, 1.0, 'HackRF One\n(Osmocom Sink)\nLO = fc − 200 kHz', fc='#e6f2ff', ec='#1f4e79', fs=7)
box(ax, 5.6, 1.55, 1.1, 0.7, 'Atenuador\n30–40 dB', fc='#fff3dc', ec='#d08c00')
box(ax, 7.0, 1.4, 1.3, 1.0, 'HackRF One\n(Osmocom Source)\nLO = fc + 200 kHz', fc='#e6f2ff', ec='#1f4e79', fs=6.5)
box(ax, 8.6, 1.4, 2.2, 1.0, 'PC Rx: ×16/125 → AGC → FA\n→ Symbol Sync (Gardner)\n→ Costas (2) → decisión', fc='#fbe9e9', ec='#b22222', fs=7)
for p, q in [((1.8, 1.9), (2.1, 1.9)), ((3.7, 1.9), (4.0, 1.9)), ((8.3, 1.9), (8.6, 1.9))]:
    arr(ax, p, q)
ax.plot([5.3, 5.6], [1.9, 1.9], color='k', lw=2); ax.plot([6.7, 7.0], [1.9, 1.9], color='k', lw=2)
ax.text(5.45, 2.05, 'SMA', fontsize=6.5, ha='center'); ax.text(6.85, 2.05, 'SMA', fontsize=6.5, ha='center')
ax.text(6.15, 2.6, 'Prueba conducida por coaxial (sin radiar)', fontsize=7.5, ha='center', color='#8a5a00')
ax.text(5.5, 0.8, 'fc = 960 MHz (tomada del archivo de referencia del curso; confirmar autorización) — radio_rate = 2 MS/s — USB 2.0 — sin Throttle',
        fontsize=7.5, ha='center')
ax.text(5.5, 0.4, 'Archivos preparados y compilados; NO probados con hardware (no disponible). Cadena de sincronización verificada en simulación.', fontsize=7.5, ha='center', color='#b22222')
ax.set_title('Figura 4. Enlace físico propuesto para la Fase 3 (HackRF One)', fontsize=10.5, weight='bold')
fig.savefig(os.path.join(OUT, 'Fig4_Enlace_HackRF_Fase3.png')); plt.close(fig)

# ===================== 5. constelacion ideal y modelo del eco =================
fig, axs = plt.subplots(1, 2, figsize=(9, 3.4))
ax = axs[0]
ax.plot([-1, 1], [0, 0], 'o', ms=12, color='#1f4e79'); ax.axhline(0, color='k', lw=.5); ax.axvline(0, color='k', lw=.5, ls='--')
ax.text(-1, 0.25, "bit 0 → −1", ha='center'); ax.text(1, 0.25, "bit 1 → +1", ha='center')
ax.text(0.05, -0.6, 'umbral de\ndecisión', fontsize=7); ax.set_xlim(-2, 2); ax.set_ylim(-1, 1); ax.set_aspect('equal')
ax.set_title('Constelación BPSK ideal (tabla (−1+0j, 1+0j))', fontsize=9); ax.set_xlabel('I'); ax.set_ylabel('Q')
ax = axs[1]
ax.stem([0, 1], [1, 0.5], basefmt=' ', linefmt='C0-', markerfmt='C0o'); ax.set_xticks([0, 1]); ax.set_xticklabels(['0', 'τ = T$_s$'])
ax.text(0, 1.05, 'directo: 1', ha='center'); ax.text(1, 0.55, 'eco: α', ha='center'); ax.set_ylim(0, 1.3)
ax.set_title('Respuesta al impulso del canal h(t) = δ(t) + α δ(t − τ)', fontsize=9); ax.set_xlabel('Retardo'); ax.set_ylabel('|h|')
fig.savefig(os.path.join(OUT, 'Fig5_Constelacion_ideal_y_h_canal.png')); plt.close(fig)
print('ok')
