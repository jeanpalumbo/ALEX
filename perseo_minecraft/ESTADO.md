# Perseo Minecraft — estado
- 15-nov 12:55 (PC) guion.md + guion.py (84 bloques, 16 capítulos incl. gancho/intro/cierre). HECHO.
- 15-nov 12:56 (PC) voz.py -> vo.wav / voz.mp3 (es-MX-JorgeNeural +5 %, 9,33 min, 1.557 palabras), bloques.json (t0/t1 por bloque y frase), palabras.json (WordBoundary: w, t, e, b), env.json (envolvente voz 60 Hz para bocas). HECHO. No hizo falta añadir frases de humor (ya dura 8-10 min).
  - Nota: en este PC aiodns no resuelve DNS; voz.py fuerza aiohttp ThreadedResolver.
  - Intro sin voz de 4,2 s (bloque "intro", 0:22-0:26). Gancho 0:00-0:22.
- 15-nov 13:05 (PC) planos.py -> planos.json: 180 planos, media 3,1 s, máx 4,57 s (ninguno >5 s), con escenario y tipo de cámara sugerido.
- CAMBIO DE PLAN (coordinador, 15-nov 12:59): el RENDER y el montaje se hacen en la NUBE (CPU, Chromium + SwiftShader, como Teseo). En el PC NO se usa la GPU ni GPU_LOCK para Perseo.
- motor/: copia del motor de Hércules largo (motor.js, mundo.js, sets.js, index.html, render.js, render_par.sh, mezcla.py, subs.py, miniatura.html, vendor/three) + escenas_hercules_referencia.js como plantilla. index.html/render.js son los de Hércules: hay que adaptarlos (título "PERSEO", CAP, CTA "PRÓXIMO: TESEO", inventario DOM, ruta de Edge -> Chromium en la nube).

## Falta (en la nube)
1. escenarios/ (sets nuevos, 3 capas): cueva_gorgonas, isla_gorgonas, argos, palacio_argos, torre_bronce, torre_interior, acantilado_argos, mar_tormenta, playa_serifos (amanecer), palacio_serifos, banquete, templo_atenea, cueva_greas (nieve), jardin_ninfas (cascada), vuelo_nubes, vuelo_tormenta, desierto_atlas (atardecer), mapa_africa, acantilado_etiopia, palacio_etiopia, salon_boda, estadio, cielo_estrellas (constelaciones), cielo_titulo. Reutilizables de Hércules: delfos (oráculo).
2. escenas.js de Perseo (84 escenas, nombres en guion.py) con reparto: Perseo (pelo castaño, túnica azul; luego sandalias aladas + casco), Dánae, Acrisio (barba blanca, corona), Polidectes (túnica morada), Dictis, Atenea (casco, búho), Hermes (gorro alado), Greas, Medusa (piel verde, serpientes, ojos brillantes), Pegaso, Atlas, Andrómeda, Casiopea, Ceto.
3. Render, mezcla (EV de efectos por escena + música por capítulo), subtítulos (subs.py; quitar comillas), miniaturas, QC, final/.
