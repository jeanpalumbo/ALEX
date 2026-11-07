# Rabbitz Aprende

App web instalable (PWA) para aprender jugando con Rabbitz, el conejo de RabbitzFeed.

- **Aprender**: lecciones de 5 preguntas por temas (ciencia, espacio, historia, economía, internet), con racha diaria, XP, niveles y energía.
- **Duelos**: 1 contra 1 contra un bot IA cuya dificultad sube con tus victorias (Fácil, Normal, Difícil, Experto).
- **Zanahorias**: la moneda del juego. Se ganan en lecciones y duelos.
- **Rabbitz**: todos empiezan igual (sudadera negra) y compran sudaderas, gorras, gafas y más con zanahorias.

## Archivos
- `src.html`: código de la app. `units.js`: preguntas. `hero.js`: imagen de portada.
- `python3 build.py` genera `index.html` (la app instalable) y `app.html` (vista previa).
- El progreso se guarda en el navegador de cada persona (localStorage).
