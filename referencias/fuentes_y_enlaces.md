# Fuentes y enlaces (formato IEEE)

[1] EIEET-UIS, "Proyecto Integrador de Comunicaciones II: diseño, simulación y comunicación técnica de un sistema digital en GNU Radio — Guía del estudiante," UIS, 2026.
[2] O. Tíjaro y R. Zamora, "Fase 2: Modelado y simulación (Guía 2)," UIS, 2026.
[3] O. Tíjaro y R. Zamora, "Fase 3: Implementación experimental en hardware SDR (Guía 3)," UIS, 2026.
[4] O. Tíjaro y R. Zamora, "Fase 4: Validación final, ajuste y comparación experimental (Guía 4)," UIS, 2026.
[5] J. G. Proakis y M. Salehi, *Digital Communications*, 5th ed. New York, NY, USA: McGraw-Hill, 2008.
[6] T. S. Rappaport, *Wireless Communications: Principles and Practice*, 2nd ed. Upper Saddle River, NJ, USA: Prentice Hall, 2002.
[7] A. A. M. Saleh y R. A. Valenzuela, "A statistical model for indoor multipath propagation," *IEEE J. Sel. Areas Commun.*, vol. 5, no. 2, pp. 128–137, Feb. 1987, doi: 10.1109/JSAC.1987.1146527.
[8] H. Hashemi, "The indoor radio propagation channel," *Proc. IEEE*, vol. 81, no. 7, pp. 943–968, Jul. 1993, doi: 10.1109/5.231342.
[9] T. S. Rappaport, "Characterization of UHF multipath radio channels in factory buildings," *IEEE Trans. Antennas Propag.*, vol. 37, no. 8, pp. 1058–1069, Aug. 1989.
[10] GNU Radio Project, "Symbol Sync," GNU Radio Wiki. https://wiki.gnuradio.org/index.php/Symbol_Sync
[11] Great Scott Gadgets, "HackRF One," documentación oficial (citada en la Guía 3). https://hackrf.readthedocs.io/en/stable/hackrf_one.html

## Para qué se usó cada fuente
- [7], [8], [9]: magnitud física del fenómeno. En interiores, la dispersión de retardo eficaz llega a unos 50 ns en oficinas [7]; en fábricas se midieron valores de 30 a 300 ns, afectados por el inventario y los materiales [9]. Se usó para justificar la normalización τ = Ts.
- [5], [6]: modelo de canal de dos rayos, filtro acoplado y BER de BPSK.
- [10]: bloque Symbol Sync usado en el Rx de hardware.
- [1]–[4]: requisitos, parámetros de referencia e instrumentación.

Software: GNU Radio 3.10.12 (radioconda, Windows) y GNU Radio 3.10.9 (Ubuntu 24.04).
