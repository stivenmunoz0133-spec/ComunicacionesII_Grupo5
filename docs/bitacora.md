# Bitácora de desarrollo — Grupo 5 (S3 multitrayectoria, BPSK)

| Fecha | Actividad | Decisión / resultado | Dificultad | Cómo se resolvió |
|---|---|---|---|---|
| 2026-10-15 | Ficha "Decisión Técnica Ciega" | S3, BPSK, paquete A (Rs = 32 kBd, SPS = 8, fs = 256 kS/s), pulso rectangular, canal directo + eco, variable = ganancia del eco, observables: PSD, constelación, señal temporal, Rb/Rs/BW, ojo y BER | En la ficha quedaron marcados el problema P1 y la hipótesis H1 (perturbación impulsiva), incoherentes con S3 | 2026-11-12: se adoptó explícitamente la hipótesis de multitrayectoria y el ajuste se declaró en el informe |
| 2026-11-12 | Auditoría de `lab.zip` | Se identificaron las guías 1–4, los GRC base, la plantilla BER y la plantilla IEEE. Guía 1 = guía del estudiante | No viene el `..._Base_Tx.grc` (con RRC) de la Guía 2 | Se trabajó sobre el GRC base con AWGN |
| 2026-11-12 | Definición del modelo del eco | τ = Ts (8 muestras), fase 0°, \|α\| ∈ {0; 0,2; 0,5; 0,8}, noise_amp = 0,10 fijo | Un τ físico de bodega (~100 ns) es mucho menor que Ts = 31,25 µs | Se usó un retardo normalizado; el informe explica la equivalencia con Rs ≈ 10 MBd |
| 2026-11-12 | Construcción del GRC S3 | Canal Delay + Multiply Const + Add; receptor con filtro acoplado, Keep 1 in N, slicer y BER | Había que saber qué muestra conserva Keep One in N | Prueba numérica: conserva la muestra 8k+7, que es el pico del filtro acoplado → delay_bits = 0 |
| 2026-11-12 | Pruebas A–D (sin GUI, GR 3.10.9) | Datos de 200 000 bits; 0 errores con el ruido de referencia; el ojo sigue 2(1−\|α\|) | La potencia Rx no coincidía con 1+α² en la prueba D | La fuente del curso repite 1000 bits → ρ₁ ≠ 0; con 1+α²+2αρ₁+σ² el error es menor de 10⁻³ |
| 2026-11-12 | Integración BER Fase 4 | Curvas para los 4 valores de α, 2 barridos de 100 000 bits/punto; con α = 0 coincide con Q(√(2Eb/N0)) a menos de 0,05 dB | GRC rechazaba e_BER_Curve ("No python block class found") y e_BER_CSV ("__file__ is not defined") | gr.sync_decimator → gr.decim_block; respaldo a Path.cwd(); parámetros ligados a las variables |
| 2026-11-12 | Calibración delay_bits | BER = 0 solo con delay_bits = 0 (BER ≈ 0,5 con 1–8) | — | — |
| 2026-11-12 | Copias HackRF (Fase 3) | Osmocom con fc/LO/ganancias del archivo de referencia; remuestreo ×125/16; Rx con AGC, Symbol Sync (Gardner) y Costas (orden 2) | En la primera verificación la señal salía nula | Faltaba modelar el corrimiento −2·lo_off entre los LO de Tx y Rx; con él, 0 errores con 3 kHz y 100 ppm (bits invertidos por la ambigüedad de 180°) |
| 2026-11-12 | Verificación en el PC del grupo (GRC 3.10.12, Windows) | Los GRC finales cargan sin errores y la GUI corre; las pruebas A y C se capturaron; el `curva_BER.csv` generado en el PC coincide con el de Linux | Los bloques se solapaban en el lienzo; los widgets QT se apilaban verticalmente | Se reubicaron los bloques y se añadieron gui_hint en una cuadrícula 3×3 |
| 2026-11-12 | Observación | El QT Vector Sink de la plantilla no redibuja la curva en Windows, pero el CSV sí se actualiza | No se resolvió | Se usa el CSV como evidencia (es lo que exige la guía) y queda documentado |
| 2026-11-12 | Documentación | Informe IEEE (plantilla del curso), README, figuras, tablas y guion de presentación | — | — |

## Reflexión metacognitiva (borrador para validar por el equipo)
- **Qué aprendimos:** el eco no "ensucia" la constelación al azar como el AWGN: la desdobla de forma determinista según el símbolo anterior. En frecuencia, el mismo fenómeno aparece como un canal selectivo. Ver juntos el ojo, la constelación y la PSD hizo evidente que la ISI y el desvanecimiento selectivo son dos caras del mismo canal.
- **Qué cambiaríamos:** marcaríamos en la ficha un problema y una hipótesis coherentes con S3 desde el inicio, y definiríamos antes el retardo del eco y su relación física con Rs.
- **Qué profundizaríamos:** la fase del eco y varios ecos (modelo Saleh–Valenzuela), un ecualizador LMS/DFE para recuperar la penalización y la validación con HackRF por cable con eco emulado.

## Uso de IA
Se usó un asistente de IA (Claude) para generar los GRC a partir de los archivos del curso, ejecutar las simulaciones, producir las gráficas y redactar borradores. Las cifras provienen de ejecuciones de GNU Radio y se contrastaron con la teoría. El equipo debe revisar y asumir las decisiones antes de entregar.
