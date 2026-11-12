# Ficha técnica del sistema — Grupo 5 (S3)

## Respuestas a las 13 preguntas previas (Guía 1, §1.2)
1. **Situación profesional:** telemetría de un nodo sensor hacia una estación de supervisión dentro de una bodega con estanterías metálicas.
2. **Fenómeno físico:** multitrayectoria; una réplica reflejada y retardada se suma a la señal directa (ISI y desvanecimiento selectivo).
3. **Información transmitida:** variables de baja tasa (estado, temperatura, vibración) en forma de flujo binario.
4. **Modulación y razón:** BPSK, por su máxima separación entre símbolos (d = 2 con energía unitaria) y su decisión binaria simple; aísla el efecto del eco.
5. **Alternativa descartada:** QPSK. Duplica Rb con la misma Rs, pero el eco con fase arbitraria mezcla I/Q y complica atribuir la degradación.
6. **Rs** = 32 000 símbolos/s (paquete A del curso; Ts = 31,25 µs).
7. **Rb** = Rs·log₂M = 32 000 × 1 = 32 kb/s.
8. **SPS** = 8.
9. **fs** = Rs·SPS = 256 000 muestras/s (`samp_rate`).
10. **Ancho de banda:** pulso rectangular → sinc²; lóbulo principal ±Rs → BW nulo-nulo = 2Rs = 64 kHz (no aplica (1+β)Rs porque no hay RRC).
11. **Variable del experimento:** magnitud del eco |α| (0; 0,2; 0,5; 0,8), con retardo 8 muestras, fase 0° y AWGN fijo.
12. **Evidencias:** constelación recuperada y diagrama de ojo (ISI), PSD (selectividad), señal temporal y BER vs. Eb/N0.
13. **Expectativa previa:** al aumentar |α| la constelación se desdobla en ±1±α, el ojo se cierra según 1−|α| y la BER empeora para un mismo Eb/N0.

## Ajuste respecto a la ficha enviada
En la ficha quedaron marcados el problema **P1** y la hipótesis **H1** (perturbación impulsiva), que no corresponden a S3. Se adopta la hipótesis de multitrayectoria del punto 13 y el ajuste queda declarado en el informe.

## Cálculos de verificación
- Eb/N0 de la condición base (respecto al camino directo): Ps = 1, σ² = noise_amp² = 0,01 → Eb/N0 = (Ps/σ²)·(fs/Rb) = 100 × 8 → 29,0 dB.
- Después del filtro acoplado, la desviación del ruido por componente es σ = √(0,005/8) ≈ 0,025 V; con D (margen 0,2 V) el margen es de unos 8σ → no se esperan errores (se midieron 0).
- Instrumento BER: Pn = Ps·fs/(Rb·Eb/N0); Ps medido incluye el eco (1+α²+2αρ₁).
- Hardware: radio_rate = 256 000 × 125/16 = 2 000 000 S/s; Rs no cambia.
