"""Copias para hardware (Fase 3) del sistema BPSK del Grupo 5, a partir de
S3_Multitrayectoria_BPSK_Grupo5.grc y de los bloques osmosdr del archivo de
referencia LAB_TX/RX_16QAM_HackRF_MEJORADO.grc. Ademas genera una version de
verificacion por simulacion del receptor (canal con offset de frecuencia y reloj)."""
import copy, sys, os, yaml
sys.path.insert(0, os.path.dirname(__file__))
SRC, GRC, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
L = lambda p: yaml.safe_load(open(p, encoding='utf-8'))
def S(d, n):
    yaml.safe_dump(d, open(os.path.join(OUT, n), 'w', encoding='utf-8'), allow_unicode=True, sort_keys=False, width=200); print('escrito', n)
def F(d, n): return next(b for b in d['blocks'] if b['name'] == n)
def drop(d, names):
    d['blocks'] = [b for b in d['blocks'] if b['name'] not in names]
    d['connections'] = [c for c in d['connections'] if c[0] not in names and c[2] not in names]
def st(x, y, s='enabled'):
    return {'bus_sink': False, 'bus_source': False, 'bus_structure': None, 'coordinate': [x, y], 'rotation': 0, 'state': s}
def blk(name, bid, params, x, y, s='enabled'):
    p = {'comment': ''} if bid.startswith('variable') or bid in ('parameter', 'import') else {'affinity': '', 'alias': '', 'comment': '', 'maxoutbuf': '0', 'minoutbuf': '0'}
    p.update({k: str(v) for k, v in params.items()}); return {'name': name, 'id': bid, 'parameters': p, 'states': st(x, y, s)}

main = L(os.path.join(GRC, 'S3_Multitrayectoria_BPSK_Grupo5.grc'))
rtx = L(os.path.join(SRC, '4', 'LAB_TX_16QAM_HackRF_MEJORADO.grc'))
rrx = L(os.path.join(SRC, '4', 'LAB_RX_16QAM_HackRF_MEJORADO.grc'))
HW_VARS = [blk('fc', 'variable', {'value': '960e6'}, 1000, 92), blk('lo_off', 'variable', {'value': '200e3'}, 1088, 92),
           blk('radio_rate', 'variable', {'value': '2e6'}, 1184, 92), blk('bb_rate', 'variable', {'value': 'samp_rate'}, 1288, 92),
           blk('interp_hw', 'variable', {'value': '125'}, 1384, 92), blk('decim_hw', 'variable', {'value': '16'}, 1480, 92)]

# ------------------------------ TX ----------------------------------------
tx = copy.deepcopy(main)
o = tx['options']['parameters']
o.update({'id': 'S3_BPSK_Grupo5_HackRF_TX', 'title': 'S3 BPSK Grupo 5 - TX HackRF One (Fase 3, NO validado en hardware)',
          'description': 'Copia para hardware del transmisor. radio_rate = bb_rate*125/16 = 2 MS/s. LO desplazado lo_off para alejar la senal del spur DC. '
                         'El canal eco puede EMULARSE digitalmente (eco_alpha) para pruebas conducidas por cable; con eco_alpha=0 se transmite la senal limpia.'})
rx_side = ['analog_noise_source_x_0', 'blocks_add_xx_0', 'noise_amp', 'qtgui_const_sink_x_0', 'qtgui_time_sink_x_0', 'rx_filtro_acoplado', 'rx_real_ojo', 'rx_ojo',
           'rx_muestreo', 'rx_constelacion', 'rx_real_decision', 'rx_decision', 'ber_retardo_tx', 'ber_xor', 'ber_a_float', 'ber_promedio', 'ber_medidor',
           'bits_tx_float', 'bits_rx_float', 'bits_rx_offset', 'bits_tx_rx', 'delay_bits', 'N_ber', 'h_mf', 'throttle_0']
for cn in tx['connections']:
    if cn[0] == 'throttle_0': cn[0] = 'interp_fir_filter_xxx_0'
drop(tx, rx_side)
F(tx, 'qtgui_freq_sink_x_0')['parameters'].update({'nconnections': '1', 'name': '"PSD Tx banda base (bb_rate)"', 'label1': 'Tx emulado'})
tx['connections'] = [c for c in tx['connections'] if not (c[2] == 'qtgui_freq_sink_x_0' and c[3] == '1')]
tx['connections'] = [c for c in tx['connections'] if not (c[0] == 'interp_fir_filter_xxx_0' and c[2] == 'qtgui_freq_sink_x_0')]
sink = copy.deepcopy(F(rtx, 'hackrf_sink')); sink['states']['coordinate'] = [2120, 236]
sink['parameters']['comment'] = 'ATENCION: fc tomada del archivo de referencia del curso. Transmitir SOLO por cable con atenuacion o en frecuencia autorizada.'
res = copy.deepcopy(F(rtx, 'rational_resampler_xxx_0')); res['parameters'].update({'interp': 'interp_hw', 'decim': 'decim_hw', 'comment': '256 kS/s x 125/16 = 2 MS/s'})
res['states']['coordinate'] = [1760, 220]
xl = copy.deepcopy(F(rtx, 'tx_desplaza')); xl['states']['coordinate'] = [1928, 236]
tx['blocks'] += HW_VARS + [res, xl, sink,
    blk('tx_amp', 'variable', {'value': '0.5'}, 1584, 92),
    blk('tx_vga', 'variable', {'value': '20'}, 1672, 92),
    blk('tx_escala', 'blocks_multiply_const_vxx', {'type': 'complex', 'const': 'tx_amp', 'vlen': '1'}, 1576, 236)]
tx['blocks'] = [b for b in tx['blocks'] if b['name'] != 'eco_alpha'] + [blk('eco_alpha', 'variable', {'value': '0'}, 1408, 92)]
tx['connections'] += [['canal_suma_eco', '0', 'tx_escala', '0'], ['tx_escala', '0', 'rational_resampler_xxx_0', '0'],
                      ['rational_resampler_xxx_0', '0', 'tx_desplaza', '0'], ['tx_desplaza', '0', 'hackrf_sink', '0'],
                      ['canal_suma_eco', '0', 'qtgui_freq_sink_x_0', '0']]
S(tx, 'S3_BPSK_Grupo5_HackRF_TX.grc')

# ------------------------------ RX ----------------------------------------
def rx_chain(d, x0=200, y0=520):
    """receptor con sincronizacion para hardware, entrada en 'rx_bb' (bb_rate)."""
    d['blocks'] += [
        blk('rx_agc', 'analog_agc_xx', {'type': 'complex', 'rate': '1e-3', 'reference': '1.0', 'gain': '1.0', 'max_gain': '65536'}, x0, y0),
        blk('rx_filtro_acoplado', 'fir_filter_xxx', {'type': 'ccf', 'decim': '1', 'taps': 'h_mf', 'samp_delay': '0'}, x0 + 170, y0),
        blk('rx_sync_simbolo', 'digital_symbol_sync_xx', {'type': 'cc', 'ted_type': 'digital.TED_GARDNER', 'constellation': 'digital.constellation_bpsk().base()',
            'sps': 'Sps', 'ted_gain': '1.0', 'loop_bw': '0.01', 'damping': '1.0', 'max_dev': '1.5', 'osps': '1',
            'resamp_type': 'digital.IR_MMSE_8TAP', 'nfilters': '128', 'pfb_mf_taps': '[]'}, x0 + 360, y0),
        blk('rx_costas', 'digital_costas_loop_cc', {'w': '2*math.pi/200', 'order': '2', 'use_snr': 'False'}, x0 + 580, y0),
        blk('rx_real_decision', 'blocks_complex_to_real', {'vlen': '1'}, x0 + 760, y0),
        blk('rx_decision', 'digital_binary_slicer_fb', {}, x0 + 920, y0),
    ]
    d['connections'] += [['rx_bb', '0', 'rx_agc', '0'], ['rx_agc', '0', 'rx_filtro_acoplado', '0'], ['rx_filtro_acoplado', '0', 'rx_sync_simbolo', '0'],
                         ['rx_sync_simbolo', '0', 'rx_costas', '0'], ['rx_costas', '0', 'rx_real_decision', '0'], ['rx_real_decision', '0', 'rx_decision', '0']]

const_p = copy.deepcopy(F(main, 'rx_constelacion')['parameters'])
eye_p = copy.deepcopy(F(main, 'rx_ojo')['parameters'])
fq_p = copy.deepcopy(F(main, 'qtgui_freq_sink_x_0')['parameters'])

rx = {'options': copy.deepcopy(main['options']), 'blocks': [], 'connections': [], 'metadata': main['metadata']}
rx['options']['parameters'].update({'id': 'S3_BPSK_Grupo5_HackRF_RX', 'title': 'S3 BPSK Grupo 5 - RX HackRF One (Fase 3, NO validado en hardware)',
    'description': 'Osmocom Source -> desplazamiento LO -> remuestreo 2 MS/s x 16/125 = 256 kS/s (bb_rate) -> AGC -> filtro acoplado -> Symbol Sync (Gardner) -> Costas (orden 2) -> decision. '
                   'Ambiguedad de fase 180 grados de BPSK: los bits pueden salir invertidos; se resuelve con secuencia conocida.'})
for n in ('Rs', 'Sps', 'samp_rate', 'h_mf', 'import_0', 'tabla_de_verdad_constelacion', 'M', 'bps', 'Rb'):
    rx['blocks'].append(copy.deepcopy(F(main, n)))
src = copy.deepcopy(F(rrx, 'hackrf_source')); src['states']['coordinate'] = [16, 300]
src['parameters']['comment'] = 'fc y ganancias tomadas del archivo de referencia del curso; verificar con el equipo real.'
xr = copy.deepcopy(F(rrx, 'rx_desplaza')); xr['states']['coordinate'] = [260, 316]
rr = copy.deepcopy(F(rrx, 'rational_resampler_xxx_0_0')); rr['parameters'].update({'interp': 'decim_hw', 'decim': 'interp_hw', 'comment': '2 MS/s x 16/125 = 256 kS/s'})
rr['name'] = 'rx_bb'; rr['states']['coordinate'] = [470, 300]
rx['blocks'] += HW_VARS + [src, xr, rr, blk('rx_lna', 'variable', {'value': '16'}, 1584, 92), blk('rx_vga', 'variable', {'value': '20'}, 1672, 92)]
rx['connections'] += [['hackrf_source', '0', 'rx_desplaza', '0'], ['rx_desplaza', '0', 'rx_bb', '0']]
rx_chain(rx)
fq = copy.deepcopy(fq_p); fq.update({'nconnections': '1', 'name': '"Espectro recibido a radio_rate"', 'bw': 'radio_rate', 'label1': 'Rx radio', 'ymin': '-120', 'ymax': '0'})
cst = copy.deepcopy(const_p); cst.update({'name': '"Constelacion tras Symbol Sync + Costas"'})
eye = copy.deepcopy(eye_p)
rx['blocks'] += [blk('rx_espectro', 'qtgui_freq_sink_x', fq, 470, 160), blk('rx_constelacion', 'qtgui_const_sink_x', cst, 980, 420),
                 blk('rx_real_ojo', 'blocks_complex_to_real', {'vlen': '1'}, 560, 660), blk('rx_ojo', 'qtgui_eye_sink_x', eye, 760, 660),
                 blk('bits_rx_archivo', 'blocks_file_sink', {'file': '"bits_rx_hackrf.bin"', 'type': 'byte', 'vlen': '1', 'unbuffered': 'False', 'append': 'False'}, 1300, 520)]
rx['connections'] += [['rx_desplaza', '0', 'rx_espectro', '0'], ['rx_costas', '0', 'rx_constelacion', '0'],
                      ['rx_filtro_acoplado', '0', 'rx_real_ojo', '0'], ['rx_real_ojo', '0', 'rx_ojo', '0'], ['rx_decision', '0', 'bits_rx_archivo', '0']]
S(rx, 'S3_BPSK_Grupo5_HackRF_RX.grc')

# --------- verificacion por simulacion de la cadena de sincronizacion -----------
v = copy.deepcopy(tx)
v['options']['parameters'].update({'id': 'S3_BPSK_Grupo5_verif_sync', 'title': 'Verificacion en simulacion del RX de hardware (offset de frecuencia y reloj)',
                                   'generate_options': 'no_gui', 'run_options': 'run'})
drop(v, ['hackrf_sink', 'qtgui_freq_sink_x_0'])
v['blocks'] += [blk('cfo_hz', 'parameter', {'label': 'offset frecuencia Hz', 'short_id': 'f', 'type': 'eng_float', 'value': '1500', 'hide': 'none'}, 16, 900),
                blk('eps_ppm', 'parameter', {'label': 'error reloj ppm', 'short_id': 'e', 'type': 'eng_float', 'value': '50', 'hide': 'none'}, 160, 900),
                blk('ruido_v', 'parameter', {'label': 'ruido', 'short_id': 'n', 'type': 'eng_float', 'value': '0.05', 'hide': 'none'}, 300, 900),
                blk('canal_hw', 'channels_channel_model', {'noise_voltage': 'ruido_v', 'freq_offset': '(cfo_hz-2*lo_off)/radio_rate', 'comment': 'incluye el corrimiento neto -2*lo_off entre LO de Tx (fc-lo_off) y Rx (fc+lo_off)', 'epsilon': '1+eps_ppm*1e-6', 'taps': '[1.0]', 'seed': '7', 'block_tags': 'False'}, 2120, 236),
                blk('limite_bits', 'blocks_head', {'type': 'byte', 'num_items': '160000', 'vlen': '1'}, 120, 300)]
v['connections'] = [c for c in v['connections'] if c[0] != 'analog_random_source_x_0']
v['connections'] += [['analog_random_source_x_0', '0', 'limite_bits', '0'], ['limite_bits', '0', 'blocks_pack_k_bits_bb_0', '0'], ['tx_desplaza', '0', 'canal_hw', '0']]
for n in ('h_mf',):
    v['blocks'].append(copy.deepcopy(F(main, n)))
xr2 = copy.deepcopy(xr); xr2['states']['coordinate'] = [2300, 300]
rr2 = copy.deepcopy(rr)
v['blocks'] += [xr2, rr2]
v['connections'] += [['canal_hw', '0', 'rx_desplaza', '0'], ['rx_desplaza', '0', 'rx_bb', '0']]
rx_chain(v)
v['blocks'] += [blk('f_bits_tx', 'blocks_file_sink', {'file': '"verif_bits_tx.bin"', 'type': 'byte', 'vlen': '1', 'unbuffered': 'False', 'append': 'False'}, 700, 900),
                blk('f_bits_rx', 'blocks_file_sink', {'file': '"verif_bits_rx.bin"', 'type': 'byte', 'vlen': '1', 'unbuffered': 'False', 'append': 'False'}, 900, 900),
                blk('f_sym', 'blocks_file_sink', {'file': '"verif_simbolos.bin"', 'type': 'complex', 'vlen': '1', 'unbuffered': 'False', 'append': 'False'}, 1100, 900)]
v['connections'] += [['blocks_packed_to_unpacked_xx_0', '0', 'f_bits_tx', '0'], ['rx_decision', '0', 'f_bits_rx', '0'], ['rx_costas', '0', 'f_sym', '0']]
S(v, 'S3_BPSK_Grupo5_verif_sync_hw.grc')
