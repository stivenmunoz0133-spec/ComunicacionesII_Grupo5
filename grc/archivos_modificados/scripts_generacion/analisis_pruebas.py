"""Graficas y metricas de las pruebas A-D a partir de los .bin exportados por
S3_Multitrayectoria_BPSK_Grupo5_headless.grc (datos reales de GNU Radio)."""
import numpy as np, matplotlib, csv, json, os, sys
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.signal import welch

DAT, OUT = sys.argv[1], sys.argv[2]
for sub in ('PSD', 'Constelaciones', 'Senales_temporales', 'Ojo', 'Bits', 'Comparacion'):
    os.makedirs(os.path.join(OUT, sub), exist_ok=True)

Rs, Sps = 32000, 8
fs = Rs * Sps
Ts = 1 / Rs
PR = {'A': ('Referencia', 0.0), 'B': ('Suave', 0.2), 'C': ('Media', 0.5), 'D': ('Fuerte', 0.8)}
COL = {'A': '#1f4e79', 'B': '#2e8b57', 'C': '#d08c00', 'D': '#b22222'}
plt.rcParams.update({'font.size': 10, 'axes.grid': True, 'grid.alpha': 0.3, 'figure.dpi': 150,
                     'savefig.bbox': 'tight'})


def ld(t, n, typ):
    return np.fromfile(os.path.join(DAT, f'prueba_{t}_{n}.bin'), typ)


res = {}
psd_all = {}
for t, (nom, a) in PR.items():
    tx = ld(t, 'tx_iq', np.complex64); rx = ld(t, 'rx_iq', np.complex64)
    mf = ld(t, 'filtro_acoplado', np.complex64); sy = ld(t, 'simbolos_rx', np.complex64)
    btx = ld(t, 'bits_tx', np.uint8); brx = ld(t, 'bits_rx', np.uint8); err = ld(t, 'errores', np.uint8)
    n = min(len(tx), len(rx))
    # ruido medido: rx - (tx + a*tx retardado D=Sps)
    ref = tx[:n].astype(np.complex128).copy()
    ref[Sps:] += a * tx[:n - Sps]
    w = rx[:n] - ref
    sig_p = np.mean(np.abs(tx) ** 2)
    rx_p = np.mean(np.abs(rx) ** 2)
    noise_p = np.mean(np.abs(w[Sps:]) ** 2)
    # metricas en el instante de decision (1 muestra por simbolo)
    s = 2.0 * btx[:len(sy)].astype(float) - 1.0
    z = sy.real * s  # proyeccion sobre el simbolo correcto (>0 -> decision correcta)
    # apertura de ojo: diferencia entre el peor "1" y el peor "0" (percentil 0.1 %)
    ones = sy.real[s > 0]; zeros = sy.real[s < 0]
    eye_open = np.percentile(ones, 0.1) - np.percentile(zeros, 99.9)
    eye_th = 2 * (1 - a)  # apertura teorica sin ruido
    evm = np.sqrt(np.mean(np.abs(sy - s) ** 2) / 1.0) * 100
    ebn0 = 10 * np.log10(sig_p / noise_p * fs / Rs)
    sk = 2.0*btx.astype(float)-1; rho1 = float(np.mean(sk[1:]*sk[:-1]))
    res[t] = dict(prueba=t, severidad=nom, alpha=a, retardo_muestras=Sps, retardo_us=Sps / fs * 1e6,
                  noise_amp=0.10, bits=int(len(err)), errores=int(err.sum()), BER=float(err.mean()),
                  P_tx=float(sig_p), P_rx=float(rx_p), rho1_bits=rho1, P_rx_teorica=float(1 + a ** 2 + 2*a*rho1 + noise_p), P_ruido=float(noise_p),
                  EbN0_dB_directo=float(ebn0), apertura_ojo_medida=float(eye_open), apertura_ojo_teorica=float(eye_th),
                  EVM_pct=float(evm), media_z=float(z.mean()), min_z=float(z.min()))

    # ---- PSD (Welch, señal compleja, espectro centrado) ----
    f, Ptx = welch(tx, fs=fs, nperseg=1024, return_onesided=False, scaling='density')
    f, Prx = welch(rx, fs=fs, nperseg=1024, return_onesided=False, scaling='density')
    f = np.fft.fftshift(f); Ptx = np.fft.fftshift(Ptx); Prx = np.fft.fftshift(Prx)
    psd_all[t] = (f, Prx)
    fig, ax = plt.subplots(figsize=(7, 3.6))
    ax.plot(f / 1e3, 10 * np.log10(Ptx), color='0.45', lw=1, label='Tx (sin canal)')
    ax.plot(f / 1e3, 10 * np.log10(Prx), color=COL[t], lw=1, label=f'Rx: eco $|\\alpha|$={a} + AWGN')
    for k in (-2, -1, 1, 2):
        ax.axvline(k * Rs / 1e3, color='k', ls=':', lw=0.7)
    ax.set_xlabel('Frecuencia [kHz]'); ax.set_ylabel('DEP [dB/Hz]')
    ax.set_title(f'Prueba {t} ({nom}): PSD Tx vs Rx  (Rs=32 kBd, fs=256 kS/s)')
    ax.set_xlim(-128, 128); ax.set_ylim(-90, -30); ax.legend(loc='lower center', fontsize=8)
    fig.savefig(os.path.join(OUT, 'PSD', f'PSD_prueba_{t}.png')); plt.close(fig)

    # ---- señal temporal ----
    nsym = 12; m = nsym * Sps; off = 80 * Sps
    tt = np.arange(m) / fs * 1e6
    fig, ax = plt.subplots(figsize=(7, 3.4))
    ax.plot(tt, tx[off:off + m].real, color='0.4', lw=1.2, drawstyle='steps-post', label='Tx  I(t)')
    ax.plot(tt, rx[off:off + m].real, color=COL[t], lw=0.9, drawstyle='steps-post', label='Rx  I(t) (eco + AWGN)')
    ax.plot(tt, mf[off:off + m].real, color='k', lw=1.0, ls='--', label='Salida filtro acoplado')
    di = np.arange(Sps - 1, m, Sps)
    ax.plot(tt[di], mf[off + di].real, 'o', ms=4, color='k', label='Instantes de decisión')
    for k in range(nsym + 1):
        ax.axvline(k * Ts * 1e6, color='k', lw=0.3, alpha=0.4)
    ax.set_xlabel('Tiempo [µs]'); ax.set_ylabel('Amplitud [V]')
    ax.set_title(f'Prueba {t} ({nom}): señal temporal, componente en fase')
    ax.set_ylim(-2.4, 2.4); ax.legend(fontsize=7, ncol=2, loc='lower right')
    fig.savefig(os.path.join(OUT, 'Senales_temporales', f'Temporal_prueba_{t}.png')); plt.close(fig)

    # ---- constelaciones ----
    fig, axs = plt.subplots(1, 2, figsize=(7.4, 3.6))
    ax = axs[0]; k = rx[:40000]
    ax.plot(k.real, k.imag, '.', ms=1, alpha=0.25, color=COL[t])
    ax.set_title('Rx sobremuestreado (8 muestras/símbolo)', fontsize=9)
    ax = axs[1]; k = sy[:20000]
    ax.plot(k.real, k.imag, '.', ms=1.5, alpha=0.4, color=COL[t], label='Muestras de decisión')
    ax.plot([-1, 1], [0, 0], 'kx', ms=9, mew=2, label='Símbolos ideales ±1')
    ax.axvline(0, color='k', lw=0.8, ls='--')
    ax.set_title('Recuperada (1 muestra/símbolo)', fontsize=9); ax.legend(fontsize=7, loc='upper left')
    for ax in axs:
        ax.set_xlim(-2.3, 2.3); ax.set_ylim(-2.3, 2.3); ax.set_aspect('equal')
        ax.set_xlabel('En fase I'); ax.set_ylabel('Cuadratura Q')
    fig.suptitle(f'Prueba {t} ({nom}, $|\\alpha|$={a}): constelación BPSK', fontsize=10)
    fig.savefig(os.path.join(OUT, 'Constelaciones', f'Constelacion_prueba_{t}.png')); plt.close(fig)

    # ---- diagrama de ojo (2 símbolos por traza, centrado en la decisión) ----
    fig, ax = plt.subplots(figsize=(5.2, 3.6))
    y = mf.real
    L = 2 * Sps
    start = Sps - 1 - Sps // 1  # traza de -1 a +1 símbolo alrededor de la decisión
    tr_t = (np.arange(L + 1) - Sps) / Sps
    for i in range(300):
        c0 = (100 + i) * Sps + (Sps - 1) - Sps
        ax.plot(tr_t, y[c0:c0 + L + 1], color=COL[t], lw=0.5, alpha=0.25)
    ax.axvline(0, color='k', ls='--', lw=0.8)
    ax.annotate('', xy=(0.02, np.percentile(ones, 0.1)), xytext=(0.02, np.percentile(zeros, 99.9)),
                arrowprops=dict(arrowstyle='<->', color='k'))
    ax.text(0.06, 0, f'apertura ≈ {eye_open:.2f}\n(teórica sin ruido {eye_th:.1f})', fontsize=8, va='center')
    ax.set_xlabel('Tiempo relativo al instante de decisión [T$_s$]'); ax.set_ylabel('Amplitud [V]')
    ax.set_title(f'Prueba {t} ({nom}): diagrama de ojo, salida filtro acoplado', fontsize=9)
    ax.set_ylim(-2.2, 2.2)
    fig.savefig(os.path.join(OUT, 'Ojo', f'Ojo_prueba_{t}.png')); plt.close(fig)

    # ---- bits Tx vs Rx ----
    fig, ax = plt.subplots(figsize=(7, 2.6))
    nb = 48; i0 = 200
    ax.step(np.arange(nb), btx[i0:i0 + nb], where='post', color='0.3', label='Bits Tx')
    ax.step(np.arange(nb), brx[i0:i0 + nb] + 1.5, where='post', color=COL[t], label='Bits Rx (+1.5)')
    ax.set_yticks([0, 1, 1.5, 2.5]); ax.set_yticklabels(['0', '1', '0', '1'])
    ax.set_xlabel('Índice de bit'); ax.set_title(
        f'Prueba {t}: bits Tx vs Rx — {int(err.sum())} errores en {len(err)} bits (delay_bits=0)', fontsize=9)
    ax.legend(fontsize=7, loc='upper right', ncol=2)
    fig.savefig(os.path.join(OUT, 'Bits', f'Bits_prueba_{t}.png')); plt.close(fig)

# ---- comparación global ----
fig, ax = plt.subplots(figsize=(7, 3.8))
for t, (f, P) in psd_all.items():
    ax.plot(f / 1e3, 10 * np.log10(P), color=COL[t], lw=1, label=f'{t} ({PR[t][0]}) |α|={PR[t][1]}')
ax.set_xlabel('Frecuencia [kHz]'); ax.set_ylabel('DEP [dB/Hz]'); ax.set_xlim(-128, 128); ax.set_ylim(-90, -30)
ax.set_title('PSD recibida en las cuatro pruebas (eco con τ = T$_s$, fase 0°)'); ax.legend(fontsize=8)
fig.savefig(os.path.join(OUT, 'Comparacion', 'PSD_comparacion_ABCD.png')); plt.close(fig)

fig, axs = plt.subplots(1, 4, figsize=(11, 3.0), sharey=True)
for ax, t in zip(axs, PR):
    sy = ld(t, 'simbolos_rx', np.complex64)[:20000]
    ax.plot(sy.real, sy.imag, '.', ms=1.2, alpha=0.4, color=COL[t]); ax.plot([-1, 1], [0, 0], 'kx', ms=8, mew=2)
    ax.axvline(0, color='k', ls='--', lw=0.7); ax.set_xlim(-2.2, 2.2); ax.set_ylim(-1.2, 1.2)
    ax.set_title(f'{t}: |α|={PR[t][1]}', fontsize=9); ax.set_xlabel('I')
axs[0].set_ylabel('Q'); fig.suptitle('Constelación recuperada en las cuatro pruebas', fontsize=10)
fig.savefig(os.path.join(OUT, 'Comparacion', 'Constelaciones_comparacion_ABCD.png')); plt.close(fig)

fig, axs = plt.subplots(1, 4, figsize=(11, 3.0), sharey=True)
for ax, t in zip(axs, PR):
    y = ld(t, 'filtro_acoplado', np.complex64).real
    tr_t = (np.arange(2 * Sps + 1) - Sps) / Sps
    for i in range(200):
        c0 = (100 + i) * Sps - 1
        ax.plot(tr_t, y[c0:c0 + 2 * Sps + 1], color=COL[t], lw=0.5, alpha=0.25)
    ax.axvline(0, color='k', ls='--', lw=0.7); ax.set_title(f'{t}: |α|={PR[t][1]}', fontsize=9)
    ax.set_xlabel('t / T$_s$')
axs[0].set_ylabel('Amplitud [V]'); fig.suptitle('Diagrama de ojo en las cuatro pruebas', fontsize=10)
fig.savefig(os.path.join(OUT, 'Comparacion', 'Ojos_comparacion_ABCD.png')); plt.close(fig)

fig, ax = plt.subplots(figsize=(5.5, 3.4))
al = np.array([res[t]['alpha'] for t in PR]); eo = np.array([res[t]['apertura_ojo_medida'] for t in PR])
aa = np.linspace(0, 1, 50)
ax.plot(aa, 2 * (1 - aa), 'k--', label='Teórica sin ruido: 2(1-|α|)')
ax.plot(al, eo, 'o-', color='#b22222', label='Medida (percentil 0.1 %)')
for t in PR:
    ax.annotate(t, (res[t]['alpha'], res[t]['apertura_ojo_medida']), textcoords='offset points', xytext=(5, 5))
ax.set_xlabel('Magnitud del eco |α|'); ax.set_ylabel('Apertura vertical del ojo [V]')
ax.set_title('Cierre del ojo por ISI de multitrayectoria'); ax.legend(fontsize=8)
fig.savefig(os.path.join(OUT, 'Comparacion', 'Apertura_ojo_vs_alpha.png')); plt.close(fig)

# ---- respuesta en frecuencia del canal: medida (Prx/Ptx) vs teorica ----
fig, ax = plt.subplots(figsize=(7, 3.6))
ff = np.linspace(-fs/2, fs/2, 2000)
for t, (f, P) in psd_all.items():
    a = PR[t][1]
    txx = ld(t, 'tx_iq', np.complex64)
    f2, Pt = welch(txx, fs=fs, nperseg=1024, return_onesided=False, scaling='density')
    Pt = np.fft.fftshift(Pt)
    ax.plot(f / 1e3, 10*np.log10(P/Pt), color=COL[t], lw=0.8, alpha=0.6)
    ax.plot(ff / 1e3, 10*np.log10(np.abs(1 + a*np.exp(-2j*np.pi*ff/Rs))**2), color=COL[t], lw=1.6, ls='--',
            label=f'{t}: |α|={a}  (teórica --, medida —)')
ax.set_xlim(-64, 64); ax.set_ylim(-16, 8)
ax.set_xlabel('Frecuencia [kHz]'); ax.set_ylabel('|H(f)|$^2$ [dB]')
ax.set_title('Respuesta en frecuencia del canal eco: $|1+\\alpha e^{-j2\\pi f T_s}|^2$')
ax.legend(fontsize=7, loc='lower right')
fig.savefig(os.path.join(OUT, 'Comparacion', 'Respuesta_frecuencia_canal.png')); plt.close(fig)

with open(os.path.join(OUT, 'metricas_pruebas.json'), 'w') as fjs:
    json.dump(res, fjs, indent=2, ensure_ascii=False)
with open(os.path.join(OUT, 'tabla_pruebas_ABCD.csv'), 'w', newline='', encoding='utf-8') as fc:
    w = csv.DictWriter(fc, fieldnames=list(res['A'].keys())); w.writeheader(); [w.writerow(res[t]) for t in PR]
for t in PR:
    print({k: (round(v, 4) if isinstance(v, float) else v) for k, v in res[t].items()})
