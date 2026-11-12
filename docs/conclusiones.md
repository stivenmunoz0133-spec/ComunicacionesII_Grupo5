# Conclusiones

1. Con BPSK y pulso rectangular (Rs = 32 kBd, Rb = 32 kb/s, SPS = 8, fs = 256 kS/s, BW nulo-nulo = 64 kHz), el único mecanismo de degradación observado fue el eco, lo que permitió atribuirle cada cambio en las evidencias.
2. Un eco con τ = Ts es ISI de un símbolo: desdobla la constelación en ±1±α y cierra el ojo según 2(1−|α|) (medido: 1,84 / 1,46 / 0,86 / 0,26 V). En frecuencia aparece el peine |1+αe^{−j2πfTs}|², con mínimos de hasta −14 dB.
3. El receptor de filtro acoplado, con muestreo en 8k+7 y umbral cero, no produjo errores en las cuatro pruebas con el ruido de referencia y reprodujo la BPSK teórica en AWGN (diferencia de 0,01 dB a BER 10⁻³).
4. Penalización a BER 10⁻³: 1,4 dB (|α| = 0,2), 6,3 dB (|α| = 0,5) y más de 14 dB (|α| = 0,8; 15,5 dB teórico). Con el criterio de 2 dB, solo el eco suave es aceptable sin ecualización.
5. En una bodega real (τ ≈ 100 ns) este efecto aparece con Rs del orden de 10 MBd. A esas tasas, o con ecos fuertes, se necesita ecualización adaptativa (LMS/DFE) o una modulación multiportadora.

**Hipótesis:** se confirma la hipótesis de multitrayectoria adoptada (ver el ajuste a la ficha en el informe).

**Trabajo futuro:** validar con HackRF One los archivos ya preparados; estudiar la fase del eco y varios ecos; implementar un ecualizador.
