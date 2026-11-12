"""Construye los flujogramas del Grupo 5 (S3 multitrayectoria, BPSK) a partir de
los archivos de referencia del curso. Uso:
  python3.12 build_grc.py <dir_lab_original> <dir_salida>
"""
import copy, sys, yaml, os

SRC, OUT = sys.argv[1], sys.argv[2]
os.makedirs(OUT, exist_ok=True)
BASE = os.path.join(SRC, '2', 'Modulaciones_basadas_en_constelaciones_AWGN.grc')
BERBASE = os.path.join(SRC, '4', 'archivos_para_fase4', 'BER_SDR_INSTRUMENTACION_BASE.grc')


def st(x, y, state='enabled', rot=0):
    return {'bus_sink': False, 'bus_source': False, 'bus_structure': None,
            'coordinate': [x, y], 'rotation': rot, 'state': state}


def blk(name, bid, params, x, y, state='enabled', rot=0):
    p = {'affinity': '', 'alias': '', 'comment': '', 'maxoutbuf': '0', 'minoutbuf': '0'}
    if bid.startswith('variable') or bid in ('parameter', 'import'):
        p = {'comment': ''}
    p.update({k: str(v) for k, v in params.items()})
    return {'name': name, 'id': bid, 'parameters': p, 'states': st(x, y, state, rot)}


def load(p):
    with open(p, encoding='utf-8') as f:
        return yaml.safe_load(f)


def save(d, name):
    path = os.path.join(OUT, name)
    with open(path, 'w', encoding='utf-8') as f:
        yaml.safe_dump(d, f, allow_unicode=True, sort_keys=False, width=200)
    print('escrito', path)


def find(d, name):
    for b in d['blocks']:
        if b['name'] == name:
            return b
    raise KeyError(name)


def drop(d, names):
    d['blocks'] = [b for b in d['blocks'] if b['name'] not in names]
    d['connections'] = [c for c in d['connections'] if c[0] not in names and c[2] not in names]


def qt_style(n):
    """parámetros por defecto de estilo para sinks QT (n trazas)."""
    cols = ['blue', 'red', 'green', 'black', 'cyan', 'magenta', 'yellow', 'dark red', 'dark green', 'dark blue']
    p = {}
    for i in range(1, 11):
        p.update({f'alpha{i}': '1.0', f'color{i}': cols[i-1], f'width{i}': '1',
                  f'style{i}': '1', f'marker{i}': '-1', f'label{i}': f'Signal {i}'})
    return p


def fix_curve(src):
    assert 'gr.sync_decimator' in src
    src = src.replace('class blk(gr.sync_decimator):', 'class blk(gr.decim_block):  # CORRECCION G5: gr.sync_decimator no es bloque Python en GR 3.10')
    return src.replace('gr.sync_decimator.__init__(', 'gr.decim_block.__init__(')


def fix_csv(src):
    old = 'self.carpeta = Path(__file__).resolve().parent'
    assert old in src
    new = ('try:\n            self.carpeta = Path(__file__).resolve().parent\n'
           '        except NameError:  # CORRECCION G5: GRC instancia el bloque sin __file__ al validarlo\n'
           '            self.carpeta = Path.cwd()')
    return src.replace(old, new)



LAYOUT = {
 'options': (8, 8),
 'Rs': (220, 8), 'Sps': (310, 8), 'M': (400, 8), 'bps': (480, 8), 'Rb': (560, 8), 'samp_rate': (650, 8),
 'tabla_de_verdad_constelacion': (770, 8), 'h': (990, 8), 'import_0': (1190, 8), 'noise_amp': (1350, 8),
 'D_eco': (220, 120), 'eco_fase_deg': (320, 120), 'alpha_c': (470, 120), 'h_mf': (590, 120), 'delay_bits': (820, 120), 'N_ber': (940, 120),
 'eco_alpha': (1600, 8),
 'analog_random_source_x_0': (8, 330), 'blocks_pack_k_bits_bb_0': (190, 346), 'blocks_packed_to_unpacked_xx_0': (320, 330),
 'digital_chunks_to_symbols_xx_0': (620, 338), 'interp_fir_filter_xxx_0': (820, 330), 'throttle_0': (1030, 338),
 'canal_eco_retardo': (1030, 460), 'canal_eco_ganancia': (1150, 460), 'canal_suma_eco': (1320, 350),
 'analog_noise_source_x_0': (1320, 480), 'blocks_add_xx_0': (1500, 366),
 'qtgui_const_sink_x_0': (1620, 300), 'qtgui_freq_sink_x_0': (1620, 430), 'qtgui_time_sink_x_0': (1620, 560),
 'rx_filtro_acoplado': (100, 720), 'rx_muestreo': (400, 720), 'rx_constelacion': (590, 660), 'rx_real_decision': (590, 800),
 'rx_decision': (800, 800), 'rx_real_ojo': (400, 900), 'rx_ojo': (590, 900),
 'ber_retardo_tx': (590, 1040), 'ber_xor': (1000, 860), 'ber_a_float': (1120, 868), 'ber_promedio': (1290, 852), 'ber_medidor': (1500, 840),
 'bits_tx_float': (800, 1050), 'bits_rx_float': (1000, 1000), 'bits_rx_offset': (1150, 1000), 'bits_tx_rx': (1350, 1000),
 'e_EbN0_Sweep': (1480, 330), 'null_ebn0': (1840, 760), 'e_BER_Curve': (1000, 1000), 'curva_ber': (1350, 1000), 'e_BER_CSV': (1350, 1150),
 'EbN0_min': (100, 1180), 'EbN0_max': (220, 1180), 'EbN0_step': (340, 1180), 'N_EbN0': (460, 1180), 'bb_rate': (640, 1180), 'Rb_ber': (760, 1180),
 'bits_por_punto': (100, 1270), 'bits_guardia': (250, 1270), 'update_every': (400, 1270),
}


GUI_HINT = {'eco_alpha': '0,0,1,1', 'noise_amp': '0,1,1,1', 'ber_medidor': '0,2,1,1',
            'qtgui_freq_sink_x_0': '1,0,1,1', 'qtgui_const_sink_x_0': '1,1,1,1', 'qtgui_time_sink_x_0': '1,2,1,1',
            'rx_ojo': '2,0,1,1', 'rx_constelacion': '2,1,1,1', 'bits_tx_rx': '2,2,1,1', 'curva_ber': '0,2,1,1'}


def apply_layout(d):
    for b in d['blocks']:
        if b['name'] in GUI_HINT and 'gui_hint' in b['parameters']:
            b['parameters']['gui_hint'] = GUI_HINT[b['name']]
    for b in d['blocks']:
        if b['name'] in LAYOUT:
            b['states']['coordinate'] = list(LAYOUT[b['name']])
    d['options']['states']['coordinate'] = list(LAYOUT['options'])


def headless_fix(s, num_items):
    """Quita el Throttle (une interp -> consumidores) e inserta Head tras la fuente de bits."""
    s['options']['parameters']['run_options'] = 'run'
    s['options']['parameters']['generate_options'] = 'no_gui'
    for cn in s['connections']:
        if cn[0] == 'throttle_0':
            cn[0] = 'interp_fir_filter_xxx_0'
    drop(s, ['throttle_0'])
    s['connections'] = [c for c in s['connections'] if not (c[0] == 'analog_random_source_x_0')]
    s['blocks'].append(blk('limite_bits', 'blocks_head', {'type': 'byte', 'num_items': num_items, 'vlen': '1'}, 120, 300))
    s['connections'] += [['analog_random_source_x_0', '0', 'limite_bits', '0'], ['limite_bits', '0', 'blocks_pack_k_bits_bb_0', '0']]


# ----------------------------------------------------------------------------
# 1) GRC principal (QT): Tx BPSK -> canal eco + AWGN -> receptor
# ----------------------------------------------------------------------------
d = load(BASE)
o = d['options']['parameters']
o['id'] = 'S3_Multitrayectoria_BPSK_Grupo5'
o['title'] = 'S3 Multitrayectoria BPSK - Grupo 5 (Tx-canal eco-Rx)'
o['author'] = 'Grupo 5: Elkin Largo, Stiven Muñoz, Minuk Lee'
o['description'] = ('Copia modificada de Modulaciones_basadas_en_constelaciones_AWGN.grc. '
                    'BPSK, pulso rectangular, canal camino directo + eco (retardo D_eco, ganancia compleja alpha) '
                    '+ AWGN y receptor: filtro acoplado, diagrama de ojo, muestreo 1 de Sps, decision y BER.')
o['window_size'] = '(1600,1000)'

find(d, 'tabla_de_verdad_constelacion')['parameters']['value'] = '(-1+0j, 1+0j)'
find(d, 'import_0')['parameters']['imports'] = 'import math, cmath'

# nuevas variables del canal / receptor
d['blocks'] += [
    blk('D_eco', 'variable', {'value': 'Sps'}, 232, 92),
    blk('eco_fase_deg', 'variable', {'value': '0'}, 336, 92),
    blk('alpha_c', 'variable', {'value': 'eco_alpha*cmath.exp(1j*math.radians(eco_fase_deg))'}, 464, 92),
    blk('h_mf', 'variable', {'value': '[1.0/Sps]*Sps'}, 664, 92),
    blk('delay_bits', 'variable', {'value': '0'}, 776, 92),
    blk('N_ber', 'variable', {'value': '20000'}, 880, 92),
    blk('eco_alpha', 'variable_qtgui_chooser', {
        'label': '"Prueba (|alpha| del eco)"', 'type': 'real', 'num_opts': '4',
        'options': '[0, 1, 2]', 'labels': '[]', 'value': '0',
        'option0': '0', 'label0': '"A Referencia |a|=0"', 'option1': '0.2', 'label1': '"B Suave |a|=0.2"',
        'option2': '0.5', 'label2': '"C Media |a|=0.5"', 'option3': '0.8', 'label3': '"D Fuerte |a|=0.8"',
        'option4': '4', 'label4': '""', 'widget': 'radio_buttons', 'orient': 'Qt.QHBoxLayout', 'gui_hint': ''},
        1408, 92),
]

# canal multitrayectoria: throttle -> (directo) add_eco:0 ; throttle -> delay -> alpha -> add_eco:1
d['blocks'] += [
    blk('canal_eco_retardo', 'blocks_delay', {'type': 'complex', 'delay': 'D_eco', 'num_ports': '1', 'vlen': '1', 'showports': 'False'}, 1048, 300),
    blk('canal_eco_ganancia', 'blocks_multiply_const_vxx', {'type': 'complex', 'const': 'alpha_c', 'vlen': '1'}, 1200, 300),
    blk('canal_suma_eco', 'blocks_add_xx', {'type': 'complex', 'num_inputs': '2', 'vlen': '1'}, 1376, 232),
]
find(d, 'throttle_0')['states']['coordinate'] = [1048, 216]
find(d, 'analog_noise_source_x_0')['states']['coordinate'] = [1360, 380]
find(d, 'blocks_add_xx_0')['states']['coordinate'] = [1576, 248]
d['connections'] = [c for c in d['connections'] if not (c[0] == 'throttle_0' and c[2] == 'blocks_add_xx_0')]
d['connections'] += [
    ['throttle_0', '0', 'canal_suma_eco', '0'],
    ['throttle_0', '0', 'canal_eco_retardo', '0'],
    ['canal_eco_retardo', '0', 'canal_eco_ganancia', '0'],
    ['canal_eco_ganancia', '0', 'canal_suma_eco', '1'],
    ['canal_suma_eco', '0', 'blocks_add_xx_0', '0'],
]

# sinks existentes: renombrar y reubicar; PSD compara Tx vs Rx
c = find(d, 'qtgui_const_sink_x_0')['parameters']
c.update({'name': '"Plano I-Q Rx sobremuestreado (antes del receptor)"', 'label1': '"Rx (Sps muestras/simbolo)"'})
find(d, 'qtgui_const_sink_x_0')['states']['coordinate'] = [1784, 120]
f = find(d, 'qtgui_freq_sink_x_0')['parameters']
f.update({'name': '"PSD Tx vs Rx"', 'nconnections': '2', 'label1': 'Tx (salida conformador)', 'label2': 'Rx (eco + AWGN)',
          'average': '0.2', 'ymin': '-80', 'ymax': '10'})
find(d, 'qtgui_freq_sink_x_0')['states']['coordinate'] = [1784, 260]
d['connections'] += [['throttle_0', '0', 'qtgui_freq_sink_x_0', '0']]
d['connections'] = [c for c in d['connections'] if not (c[0] == 'blocks_add_xx_0' and c[2] == 'qtgui_freq_sink_x_0')]
d['connections'] += [['blocks_add_xx_0', '0', 'qtgui_freq_sink_x_0', '1']]
t = find(d, 'qtgui_time_sink_x_0')['parameters']
t.update({'name': '"Envolvente compleja Rx (eco + AWGN)"', 'label1': 'I Rx', 'label2': 'Q Rx', 'size': '256',
          'ylabel': 'Amplitud', 'yunit': '"V"', 'ymin': '-2.5', 'ymax': '2.5'})
find(d, 'qtgui_time_sink_x_0')['states']['coordinate'] = [1784, 420]

# receptor
eye = qt_style(1)
eye.update({'type': 'float', 'ylabel': '"Amplitud"', 'yunit': '""', 'size': '2048', 'samp_per_symbol': 'Sps',
            'srate': 'samp_rate', 'grid': 'True', 'autoscale': 'False', 'ymin': '-2', 'ymax': '2', 'nconnections': '1',
            'update_time': '0.10', 'entags': 'False', 'gui_hint': '', 'tr_mode': 'qtgui.TRIG_MODE_FREE',
            'tr_slope': 'qtgui.TRIG_SLOPE_POS', 'tr_level': '0.0', 'tr_delay': '0', 'tr_chan': '0', 'tr_tag': '""',
            'ctrlpanel': 'False', 'legend': 'True', 'axislabels': 'True', 'label1': 'Re{salida filtro acoplado}',
            'name': '"Diagrama de ojo (salida filtro acoplado, parte real)"'})
constd = find(d, 'qtgui_const_sink_x_0')['parameters'].copy()
constd.update({'name': '"Constelacion recuperada (1 muestra/simbolo)"', 'label1': '"Decision"', 'size': '1024',
               'autoscale': 'False', 'xmin': '-2', 'xmax': '2', 'ymin': '-2', 'ymax': '2'})
tbits = find(d, 'qtgui_time_sink_x_0')['parameters'].copy()
tbits.update({'type': 'float', 'name': '"Bits Tx vs bits Rx"', 'nconnections': '2', 'size': '64', 'srate': 'Rb',
              'label1': 'Bits Tx (retardados delay_bits)', 'label2': 'Bits Rx + 1.5 (desplazados)', 'ylabel': 'Bit',
              'yunit': '""', 'ymin': '-0.5', 'ymax': '3', 'autoscale': 'False', 'style1': '1', 'style2': '1'})
d['blocks'] += [
    blk('rx_filtro_acoplado', 'fir_filter_xxx', {'type': 'ccf', 'decim': '1', 'taps': 'h_mf', 'samp_delay': '0'}, 248, 540),
    blk('rx_real_ojo', 'blocks_complex_to_real', {'vlen': '1'}, 480, 640),
    blk('rx_ojo', 'qtgui_eye_sink_x', eye, 664, 620),
    blk('rx_muestreo', 'blocks_keep_one_in_n', {'type': 'complex', 'n': 'Sps', 'vlen': '1'}, 480, 540),
    blk('rx_constelacion', 'qtgui_const_sink_x', constd, 704, 500),
    blk('rx_real_decision', 'blocks_complex_to_real', {'vlen': '1'}, 704, 760),
    blk('rx_decision', 'digital_binary_slicer_fb', {}, 888, 760),
    blk('ber_retardo_tx', 'blocks_delay', {'type': 'byte', 'delay': 'delay_bits', 'num_ports': '1', 'vlen': '1', 'showports': 'False'}, 704, 860),
    blk('ber_xor', 'blocks_xor_xx', {'type': 'byte', 'num_inputs': '2', 'vlen': '1'}, 1080, 820),
    blk('ber_a_float', 'blocks_char_to_float', {'vlen': '1', 'scale': '1'}, 1232, 828),
    blk('ber_promedio', 'blocks_moving_average_xx', {'type': 'float', 'length': 'N_ber', 'scale': '1.0/N_ber', 'max_iter': '4000', 'vlen': '1'}, 1408, 812),
    blk('ber_medidor', 'qtgui_number_sink', {'name': '"BER (ventana N_ber bits)"', 'type': 'float', 'autoscale': 'False', 'avg': '0',
        'graph_type': 'qtgui.NUM_GRAPH_HORIZ', 'nconnections': '1', 'min': '0', 'max': '0.5', 'update_time': '0.20', 'gui_hint': '',
        'label1': '"BER"', 'unit1': '""', 'color1': '("black", "black")', 'factor1': '1',
        **{f'{k}{i}': v for i in range(2, 11) for k, v in (('label', '""'), ('unit', '""'), ('color', '("black", "black")'), ('factor', '1'))}},
        1632, 812),
    blk('bits_tx_float', 'blocks_char_to_float', {'vlen': '1', 'scale': '1'}, 888, 940),
    blk('bits_rx_float', 'blocks_char_to_float', {'vlen': '1', 'scale': '1'}, 1080, 940),
    blk('bits_rx_offset', 'blocks_add_const_vxx', {'type': 'float', 'const': '1.5', 'vlen': '1'}, 1232, 940),
    blk('bits_tx_rx', 'qtgui_time_sink_x', tbits, 1408, 920),
]
d['connections'] += [
    ['blocks_add_xx_0', '0', 'rx_filtro_acoplado', '0'],
    ['rx_filtro_acoplado', '0', 'rx_real_ojo', '0'],
    ['rx_real_ojo', '0', 'rx_ojo', '0'],
    ['rx_filtro_acoplado', '0', 'rx_muestreo', '0'],
    ['rx_muestreo', '0', 'rx_constelacion', '0'],
    ['rx_muestreo', '0', 'rx_real_decision', '0'],
    ['rx_real_decision', '0', 'rx_decision', '0'],
    ['blocks_packed_to_unpacked_xx_0', '0', 'ber_retardo_tx', '0'],
    ['ber_retardo_tx', '0', 'ber_xor', '0'],
    ['rx_decision', '0', 'ber_xor', '1'],
    ['ber_xor', '0', 'ber_a_float', '0'],
    ['ber_a_float', '0', 'ber_promedio', '0'],
    ['ber_promedio', '0', 'ber_medidor', '0'],
    ['ber_retardo_tx', '0', 'bits_tx_float', '0'],
    ['rx_decision', '0', 'bits_rx_float', '0'],
    ['bits_rx_float', '0', 'bits_rx_offset', '0'],
    ['bits_tx_float', '0', 'bits_tx_rx', '0'],
    ['bits_rx_offset', '0', 'bits_tx_rx', '1'],
]
apply_layout(d)
qt_main = copy.deepcopy(d)
save(d, 'S3_Multitrayectoria_BPSK_Grupo5.grc')

# ----------------------------------------------------------------------------
# 2) Version sin GUI para exportar datos (mismo flujograma, sinks a archivo)
# ----------------------------------------------------------------------------
h = copy.deepcopy(qt_main)
o = h['options']['parameters']
o['id'] = 'S3_Multitrayectoria_BPSK_Grupo5_headless'
o['title'] = 'S3 Multitrayectoria BPSK - Grupo 5 (exportacion de datos, sin GUI)'
o['generate_options'] = 'no_gui'
o['description'] = 'Mismo sistema que S3_Multitrayectoria_BPSK_Grupo5.grc; los sinks QT se sustituyen por File Sinks para exportar datos crudos. Sin Throttle (no hay GUI que sincronizar).'
qtn = [b['name'] for b in h['blocks'] if b['id'].startswith('qtgui')]
drop(h, qtn + ['rx_real_ojo', 'eco_alpha', 'noise_amp', 'bits_tx_float', 'bits_rx_float', 'bits_rx_offset', 'ber_a_float', 'ber_promedio'])
headless_fix(h, '8*(n_simbolos//8)')
h['blocks'] += [
    blk('eco_alpha', 'parameter', {'label': 'Magnitud del eco', 'short_id': 'a', 'type': 'eng_float', 'value': '0', 'hide': 'none'}, 1408, 92),
    blk('noise_amp', 'parameter', {'label': 'Amplitud AWGN', 'short_id': 'n', 'type': 'eng_float', 'value': '0.10', 'hide': 'none'}, 1184, 4),
    blk('n_simbolos', 'parameter', {'label': 'Simbolos a simular', 'short_id': 's', 'type': 'intx', 'value': '200000', 'hide': 'none'}, 1600, 4),
    blk('salida', 'parameter', {'label': 'Prefijo archivos', 'short_id': 'o', 'type': 'str', 'value': 'prueba', 'hide': 'none'}, 1600, 92),
]
fs = []
def fsink(name, typ, fname, x, y):
    fs.append(blk(name, 'blocks_file_sink', {'file': f'salida+"_{fname}.bin"', 'type': typ, 'vlen': '1', 'unbuffered': 'False', 'append': 'False'}, x, y))
fsink('f_tx_iq', 'complex', 'tx_iq', 1240, 140)
fsink('f_rx_iq', 'complex', 'rx_iq', 1784, 260)
fsink('f_mf', 'complex', 'filtro_acoplado', 664, 620)
fsink('f_simbolos', 'complex', 'simbolos_rx', 704, 500)
fsink('f_bits_tx', 'byte', 'bits_tx', 888, 940)
fsink('f_bits_rx', 'byte', 'bits_rx', 1080, 940)
fsink('f_err', 'byte', 'errores', 1232, 828)
h['blocks'] += fs
h['connections'] += [
    ['interp_fir_filter_xxx_0', '0', 'f_tx_iq', '0'], ['blocks_add_xx_0', '0', 'f_rx_iq', '0'],
    ['rx_filtro_acoplado', '0', 'f_mf', '0'], ['rx_muestreo', '0', 'f_simbolos', '0'],
    ['ber_retardo_tx', '0', 'f_bits_tx', '0'], ['rx_decision', '0', 'f_bits_rx', '0'], ['ber_xor', '0', 'f_err', '0'],
]
save(h, 'S3_Multitrayectoria_BPSK_Grupo5_headless.grc')

# ----------------------------------------------------------------------------
# 3) Plantilla BER corregida (parametros ligados a variables)
# ----------------------------------------------------------------------------
b = load(BERBASE)
eb = find(b, 'e_BER_Curve')
eb['parameters']['_source_code'] = fix_curve(eb['parameters']['_source_code'])
find(b, 'e_BER_CSV')['parameters']['_source_code'] = fix_csv(find(b, 'e_BER_CSV')['parameters']['_source_code'])
eb['parameters'].update({'EbN0_min': 'EbN0_min', 'EbN0_max': 'EbN0_max', 'EbN0_step': 'EbN0_step',
                         'bits_por_punto': 'bits_por_punto', 'bits_guardia': 'bits_guardia',
                         'delay_bits': 'delay_bits', 'update_every': 'update_every'})
b['options']['parameters']['description'] += ' [Corregido por Grupo 5: parametros de e_BER_Curve ligados a las variables.]'
EPY = {n: copy.deepcopy(find(b, n)) for n in ('e_EbN0_Sweep', 'e_BER_Curve', 'e_BER_CSV', 'curva_ber')}
BERVARS = {n: copy.deepcopy(find(b, n)) for n in ('EbN0_min', 'EbN0_max', 'EbN0_step', 'N_EbN0', 'bits_por_punto', 'bits_guardia', 'delay_bits', 'update_every')}
save(b, 'BER_SDR_INSTRUMENTACION_BASE_corregido.grc')

# ----------------------------------------------------------------------------
# 4) Sistema + instrumentacion BER (simulacion: el canal simulado reemplaza al SDR)
# ----------------------------------------------------------------------------
def ber_system(gui):
    s = copy.deepcopy(qt_main)
    o = s['options']['parameters']
    o['id'] = 'S3_BER_Multitrayectoria_BPSK_Grupo5' + ('' if gui else '_headless')
    o['title'] = 'S3 BER vs Eb/N0 - BPSK + eco - Grupo 5 (SIMULACION)'
    o['description'] = ('Integracion del instrumento BER de la Fase 4 sobre el sistema simulado. '
                        'e_EbN0_Sweep sustituye a la fuente AWGN fija y se ubica justo antes del receptor (bb_rate=samp_rate). '
                        'NO es una medicion SDR: el enlace fisico se reemplaza por el canal eco simulado.')
    # quitar AWGN fijo: el barrido agrega el ruido (primero reconectar sus salidas al barrido)
    for cn in s['connections']:
        if cn[0] == 'blocks_add_xx_0':
            cn[0] = 'e_EbN0_Sweep'
    drop(s, ['analog_noise_source_x_0', 'blocks_add_xx_0', 'noise_amp', 'ber_xor', 'ber_a_float', 'ber_promedio',
             'ber_medidor', 'bits_tx_float', 'bits_rx_float', 'bits_rx_offset', 'bits_tx_rx', 'delay_bits'])
    for n, v in BERVARS.items():
        s['blocks'].append(copy.deepcopy(v))
    for n, (x, y) in {'EbN0_min': (232, 1040), 'EbN0_max': (344, 1040), 'EbN0_step': (456, 1040), 'N_EbN0': (568, 1040),
                      'bits_por_punto': (232, 1120), 'bits_guardia': (376, 1120), 'delay_bits': (504, 1120), 'update_every': (632, 1120)}.items():
        find(s, n)['states']['coordinate'] = [x, y]
    s['blocks'] += [blk('bb_rate', 'variable', {'value': 'samp_rate'}, 760, 1040),
                    blk('Rb_ber', 'variable', {'value': 'Rb'}, 864, 1040)]
    sw = copy.deepcopy(EPY['e_EbN0_Sweep']); sw['parameters'].update({'samp_rate': 'bb_rate', 'bit_rate': 'Rb_ber', 'seed': '2026'})
    sw['states']['coordinate'] = [1576, 232]
    bc = copy.deepcopy(find(b, 'e_BER_Curve')); bc['states']['coordinate'] = [1080, 840]
    cs = copy.deepcopy(EPY['e_BER_CSV']); cs['states']['coordinate'] = [1408, 960]
    s['blocks'] += [sw, bc, cs,
                    blk('null_ebn0', 'blocks_null_sink', {'type': 'float', 'vlen': '1', 'num_inputs': '1', 'bus_structure_sink': '[[0,],]'}, 1784, 340)]
    s['connections'] += [
        ['canal_suma_eco', '0', 'e_EbN0_Sweep', '0'],
        ['e_EbN0_Sweep', '1', 'null_ebn0', '0'],
        ['ber_retardo_tx', '0', 'e_BER_Curve', '0'],
        ['rx_decision', '0', 'e_BER_Curve', '1'],
        ['e_BER_Curve', '0', 'e_BER_CSV', '0'],
        ['e_BER_Curve', '1', 'e_BER_CSV', '1'],
    ]
    # ber_retardo_tx usa delay 0 (la alineacion la hace e_BER_Curve.delay_bits)
    find(s, 'ber_retardo_tx')['parameters']['delay'] = '0'
    # sinks Rx pasan a la salida del barrido
    for cn in s['connections']:
        if cn[0] == 'blocks_add_xx_0':
            cn[0] = 'e_EbN0_Sweep'
    s['connections'] = [c for c in s['connections'] if not (c[0] == 'e_EbN0_Sweep' and c[1] == '0' and False)]
    if gui:
        cv = copy.deepcopy(EPY['curva_ber']); cv['states']['coordinate'] = [1408, 840]
        s['blocks'].append(cv)
        s['connections'].append(['e_BER_Curve', '1', 'curva_ber', '0'])
    else:
        o['generate_options'] = 'no_gui'
        qtn = [x['name'] for x in s['blocks'] if x['id'].startswith('qtgui')]
        drop(s, qtn + ['eco_alpha', 'rx_real_ojo'])
        headless_fix(s, 'int(8*((n_barridos*N_EbN0*(bits_por_punto+bits_guardia)+10*update_every)//8))')
        s['blocks'] += [
            blk('eco_alpha', 'parameter', {'label': 'Magnitud del eco', 'short_id': 'a', 'type': 'eng_float', 'value': '0', 'hide': 'none'}, 1408, 92),
            blk('n_barridos', 'parameter', {'label': 'Barridos completos', 'short_id': 'b', 'type': 'eng_float', 'value': '1', 'hide': 'none'}, 1600, 4),
        ]
        find(s, 'bits_por_punto')['parameters']['value'] = 'bits_por_punto_p'
        s['blocks'].append(blk('bits_por_punto_p', 'parameter', {'label': 'Bits por punto', 'short_id': 'p', 'type': 'intx', 'value': '100000', 'hide': 'none'}, 1600, 92))
        find(s, 'delay_bits')['parameters']['value'] = 'delay_bits_p'
        s['blocks'].append(blk('delay_bits_p', 'parameter', {'label': 'delay_bits', 'short_id': 'd', 'type': 'intx', 'value': '0', 'hide': 'none'}, 1760, 92))
    return s

bs = ber_system(True); apply_layout(bs)
find(bs, 'delay_bits')['states']['coordinate'] = [560, 1270]
for n, y in (('qtgui_const_sink_x_0', 300), ('qtgui_freq_sink_x_0', 430), ('qtgui_time_sink_x_0', 560)):
    find(bs, n)['states']['coordinate'] = [1840, y]
save(bs, 'S3_BER_Multitrayectoria_BPSK_Grupo5.grc')
save(ber_system(False), 'S3_BER_Multitrayectoria_BPSK_Grupo5_headless.grc')
