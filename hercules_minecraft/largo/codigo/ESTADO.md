# Hércules Minecraft — vídeo largo (estado)
- 15-nov 12:10 guion.py (59 bloques, 13 capítulos) + voz.py -> vo.wav (8,43 min), bloques.json, palabras.json. HECHO.
- Siguiente: motor (motor.js), escenarios (sets.js), escenas (escenas.js), index.html; render en paralelo (render_par.js); mezcla con música por capítulo; subtítulos; QC; miniaturas; subir a hercules_minecraft/final/.
- Servidor local: python -m http.server 8765 en esta carpeta (render con http://127.0.0.1:8765/index.html).
- 15-nov 13:40 motor.js, sets.js (21 escenarios), mundo.js, escenas.js (59 escenas), index.html listos; 2 rondas de revisión por bloque hechas. Render: bash render_par.sh 6 -> visual.mp4.

## Motor reutilizable (para Teseo/Perseo: COPIAR, no editar aquí)
- `motor.js`: utilidades (easing, rnd), texturas pixel `tex/liso/T/MAT`, 16 expresiones `EXPR` (normal, enfado, risa, cerrados, grito, susto, triste, sudor, espiral, sorpresa, malvado, lloro, presumido, dormido, amor, habla), `personaje(skin, escala)` con rig (hombros, codos, caderas, rodillas, cuello) + `pose(ch, p, t)` + `cara(ch, expr)`, `cuadrupedo(opts)` + `animaCuadrupedo`, `serpienteCadena/colocaCadena`, `pajaro`, `Particulas`.
- `sets.js`: `SETS` (olimpo, cuna, tebas, campo, delfos, palacio, nemea, lerna, cielo_noche, nieve, establos, lago, creta, tracia, amazonas, gibraltar, jardin, atlas, inframundo, pira) con 3 capas + elementos vivos; `CIELOS` (presets de cielo/luz); helpers: templo, casa, roble, pino, montanas, nubes, agua, cascada, antorcha, hoguera, bandada, ambiente (hojas/nieve/cenizas/almas/luciérnagas/esporas), paseantes, quietos, animales, extra(k).
- `mundo.js`: renderer/luces/niebla, `escenario(nombre)`, `vivos(t)`, `mira(...)`, `solSobre(...)`, `part`.
- `escenas.js`: reparto `C` y criaturas `K`, helpers de acción (andar, golpe, arriba, encoge, brazosCruz, senala, susto, hombros, gestoHabla) y cámaras (cerca, medio, general, contra, picado, sigue). `E[esc] = {set, act(X), cams[]}`.
- `index.html`: lee bloques.json/palabras.json/env.json, corta planos cada ~3 s en palabras, rótulos de capítulo, título intro y CTA (DOM).
- Pipeline: `voz.py` (guion.py -> vo.wav, bloques.json, palabras.json) -> env.json -> servidor `python -m http.server 8766` -> `bash render_par.sh 6` (render.js con Edge headless + CDP + ffmpeg; PORT por proceso) -> `mezcla.py` -> `subs.py` -> mux ffmpeg.
- Cerrojo GPU: J:\Max\viral\GPU_LOCK.txt (Hércules tiene prioridad).
