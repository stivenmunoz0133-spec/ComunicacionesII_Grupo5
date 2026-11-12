# Análisis de resultados

Origen de los datos: `S3_Multitrayectoria_BPSK_Grupo5_headless.grc` (GNU Radio 3.10.9, 200 000 bits por prueba) y `S3_BER_Multitrayectoria_BPSK_Grupo5_headless.grc` (2 barridos × 100 000 bits/punto). La GUI se verificó en GRC 3.10.12 del equipo del grupo.

## Prueba A — Referencia (|α| = 0)
- **Variables:** eco_alpha = 0, D_eco = 8, eco_fase_deg = 0, noise_amp = 0,10.
- **Qué cambió:** nada respecto al canal ideal; solo actúa el AWGN.
- **Qué se observa:** dos nubes compactas en ±1 (EVM 3,5 %), un ojo abierto de 1,84 V y una PSD sinc² con nulos cada 32 kHz.
- **Relación con el escenario:** es el enlace con línea de vista y sin reflexión dominante; sirve de línea base del receptor.

## Prueba B — Suave (|α| = 0,2)
- **Qué cambió:** se suma una réplica atenuada al 20 %, retardada un símbolo.
- **Por qué:** y_k = s_k + 0,2·s_{k−1}; cada nube se divide en ±1±0,2 y el ojo baja a 1,46 V (teórico 1,6).
- **PSD:** ondulación de ±1,6/−1,9 dB con período de 32 kHz.
- **Escenario:** una reflexión débil, por ejemplo en carga de cartón o a gran distancia. Se mantiene 0 errores, y la penalización a BER 10⁻³ es de 1,44 dB (aceptable con el criterio de 2 dB).

## Prueba C — Media (|α| = 0,5), condición principal
- **Qué cambió:** el eco tiene la mitad de la amplitud de la señal directa.
- **Por qué:** se forman cuatro niveles bien definidos (±0,5 y ±1,5); el ojo se reduce a 0,86 V (teórico 1,0).
- **PSD:** mínimos de −6 dB en ±16 kHz, porque el eco llega en contrafase a f = 1/(2τ).
- **Escenario:** una reflexión en una estantería metálica cercana. Con el ruido de referencia todavía no hay errores, pero la penalización a BER 10⁻³ es de 6,31 dB: el sistema necesita unos 6 dB más de potencia o un ecualizador.

## Prueba D — Fuerte (|α| = 0,8)
- **Qué cambió:** el eco es casi tan fuerte como la señal directa.
- **Por qué:** los niveles internos ±0,2 quedan a 0,2 V del umbral; el ojo casi se cierra (0,26 V).
- **PSD:** mínimos de −14 dB en ±16 kHz, un desvanecimiento selectivo profundo.
- **Escenario:** una superficie metálica grande muy cerca del trayecto. En el barrido de 0–14 dB la BER no baja de 6,8×10⁻²; la teoría indica que se requieren 22,3 dB para llegar a 10⁻³ (unos 15,5 dB de penalización). El enlace no es viable sin ecualización.

## Comparación global
| Métrica | A | B | C | D | Tendencia |
|---|---|---|---|---|---|
| Ojo medido [V] | 1,84 | 1,46 | 0,86 | 0,26 | ≈ 2(1−\|α\|) − 0,15 |
| EVM [%] | 3,5 | 20,3 | 50,1 | 80,1 | ≈ 100·\|α\| |
| Mínimo de \|H(f)\|² [dB] | 0 | −1,9 | −6,0 | −14,0 | 20·log₁₀(1−\|α\|) |
| Eb/N0 @ 10⁻³ [dB] | 6,80 | 8,24 | 13,11 | > 14 (22,3 teórico) | Ec. (6) del informe |

## Validación del instrumento BER
- α = 0: la BER medida coincide con Q(√(2Eb/N0)) (6,80 frente a 6,79 dB a 10⁻³).
- Con eco, la diferencia entre medición y teoría es de ±0,05 dB.
- delay_bits = 0 es el único valor con BER = 0 en condición limpia.
- Los puntos sin errores se grafican con la cota 3/N; no se reportan como BER = 0.
- Una ejecución independiente en Windows (GRC 3.10.12) reprodujo la curva para α = 0.
