"""Curva BER vs Eb/N0 a partir de los curva_BER.csv generados por el instrumento
de la Fase 4 (sin modificar) y comparacion con la teoria BPSK + eco."""
import numpy as np, matplotlib, csv, json, os, sys
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.special import erfc

BER, DAT, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
os.makedirs(OUT, exist_ok=True)
Q = lambda x: 0.5 * erfc(x / np.sqrt(2))
AL = [0.0, 0.2, 0.5, 0.8]
NAME = {0.0: 'A Referencia', 0.2: 'B Suave', 0.5: 'C Media', 0.8: 'D Fuerte'}
COL = {0.0: '#1f4e79', 0.2: '#2e8b57', 0.5: '#d08c00', 0.8: '#b22222'}
plt.rcParams.update({'font.size': 10, 'axes.grid': True, 'grid.alpha': 0.3, 'figure.dpi': 150, 'savefig.bbox': 'tight'})


def teoria(g_db, a, rho=0.0):
    g = 10 ** (g_db / 10)
    P = 1 + a * a + 2 * a * rho          # potencia medida por e_EbN0_Sweep (incluye el eco)
    ps = (1 + rho) / 2                    # fraccion de pares de simbolos iguales
    k = np.sqrt(2 * g / P)
    return ps * Q(k * (1 + a)) + (1 - ps) * Q(k * (1 - a))


def ebn0_at(ber_target, x, y):
    """interpolacion log-lineal del Eb/N0 para el BER objetivo (None si no se alcanza)."""
    ly = np.log10(np.maximum(y, 1e-12))
    lt = np.log10(ber_target)
    for i in range(len(x) - 1):
        if y[i] > 0 and y[i + 1] > 0 and ly[i] >= lt >= ly[i + 1]:
            return float(x[i] + (lt - ly[i]) * (x[i + 1] - x[i]) / (ly[i + 1] - ly[i]))
    return None


g = np.linspace(0, 14, 300)
fig, ax = plt.subplots(figsize=(7, 4.6))
resumen = {}
for a in AL:
    d = np.genfromtxt(os.path.join(BER, ('alpha_0' if a == 0 else f'alpha_{a}'), 'curva_BER.csv'), delimiter=',', names=True)
    x, b = d['EbN0_dB'], d['BER']
    nz = b > 0
    ax.semilogy(x[nz], b[nz], 'o', color=COL[a], ms=5, label=f'Medida {NAME[a]} (|α|={a})')
    if (~nz).any():
        ax.semilogy(x[~nz], 10 ** d['log10_BER'][~nz], 'v', color=COL[a], ms=5, mfc='none')
    ax.semilogy(g, teoria(g, a), '-', color=COL[a], lw=1.1)
    eb_m = ebn0_at(1e-3, x, b)
    eb_t = ebn0_at(1e-3, g, teoria(g, a))
    resumen[a] = {'EbN0_1e-3_medido_dB': eb_m, 'EbN0_1e-3_teorico_dB': eb_t,
                  'puntos_sin_errores': [float(v) for v in x[~nz]],
                  'BER_0dB': float(b[0]), 'BER_14dB': float(b[-1])}
ax.semilogy(g, Q(np.sqrt(2 * 10 ** (g / 10))), 'k--', lw=1, label='Teoría BPSK AWGN  Q(√(2Eb/N0))')
ax.axhline(1e-3, color='0.5', lw=0.8, ls=':')
ax.text(0.2, 1.25e-3, 'BER = 10$^{-3}$ (criterio del proyecto)', fontsize=7, color='0.3')
ax.set_ylim(1e-6, 0.5); ax.set_xlim(0, 14)
ax.set_xlabel('E$_b$/N$_0$ [dB]  (E$_b$ medido con la potencia total recibida, incluye el eco)')
ax.set_ylabel('BER')
ax.set_title('BER vs E$_b$/N$_0$ — BPSK con eco (τ = T$_s$) — instrumento Fase 4 en SIMULACIÓN', fontsize=10)
ax.legend(fontsize=7, loc='lower left')
ax.text(13.9, 2e-6, 'Líneas: teoría con eco; ▽: sin errores (cota 3/N)', fontsize=7, ha='right')
fig.savefig(os.path.join(OUT, 'BER_vs_EbN0_eco.png')); plt.close(fig)

# log10(BER) como en el QT Vector Sink del instrumento
fig, ax = plt.subplots(figsize=(7, 4))
for a in AL:
    d = np.genfromtxt(os.path.join(BER, ('alpha_0' if a == 0 else f'alpha_{a}'), 'curva_BER.csv'), delimiter=',', names=True)
    ax.plot(d['EbN0_dB'], d['log10_BER'], 'o-', color=COL[a], ms=4, label=f'|α|={a}')
ax.set_xlabel('E$_b$/N$_0$ [dB]'); ax.set_ylabel('log$_{10}$(BER)')
ax.set_title('Salida log10(BER) de e_BER_Curve (formato del QT Vector Sink)', fontsize=10)
ax.legend(fontsize=8)
fig.savefig(os.path.join(OUT, 'log10BER_formato_instrumento.png')); plt.close(fig)

# calibracion de delay_bits en condicion limpia (prueba A, sin eco, Eb/N0 ~ 29 dB)
btx = np.fromfile(os.path.join(DAT, 'prueba_A_bits_tx.bin'), np.uint8)
brx = np.fromfile(os.path.join(DAT, 'prueba_A_bits_rx.bin'), np.uint8)
cal = []
for dly in range(0, 9):
    n = len(brx) - dly
    cal.append((dly, float(np.mean(brx[dly:dly + n] != btx[:n]))))
with open(os.path.join(OUT, 'calibracion_delay_bits.csv'), 'w', newline='') as f:
    w = csv.writer(f); w.writerow(['delay_bits', 'BER_condicion_limpia']); w.writerows(cal)
fig, ax = plt.subplots(figsize=(5, 3))
ax.bar([c[0] for c in cal], [c[1] for c in cal], color=['#2e8b57' if c[1] == 0 else '0.6' for c in cal])
ax.set_xlabel('delay_bits'); ax.set_ylabel('BER (prueba A, sin eco)')
ax.set_title('Calibración de delay_bits: BER=0 sólo con delay_bits=0', fontsize=9)
fig.savefig(os.path.join(OUT, 'calibracion_delay_bits.png')); plt.close(fig)

for a in AL:
    r = resumen[a]
    if r['EbN0_1e-3_medido_dB'] is not None and resumen[0.0]['EbN0_1e-3_medido_dB'] is not None:
        r['penalizacion_vs_referencia_dB'] = r['EbN0_1e-3_medido_dB'] - resumen[0.0]['EbN0_1e-3_medido_dB']
    if r['EbN0_1e-3_medido_dB'] is not None and r['EbN0_1e-3_teorico_dB'] is not None:
        r['diferencia_medido_teorico_dB'] = r['EbN0_1e-3_medido_dB'] - r['EbN0_1e-3_teorico_dB']
r_awgn = ebn0_at(1e-3, g, Q(np.sqrt(2 * 10 ** (g / 10))))
out = {'EbN0_1e-3_BPSK_AWGN_teorico_dB': r_awgn, 'por_alpha': {str(k): v for k, v in resumen.items()}, 'calibracion': cal}
json.dump(out, open(os.path.join(OUT, 'resumen_BER.json'), 'w'), indent=2)
print(json.dumps(out, indent=1))
