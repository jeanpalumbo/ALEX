# Rabbitz Aprende

App web instalable (PWA) para aprender jugando con Rabbitz, el conejo de RabbitzFeed.

- **Aprender**: lecciones de 6 ejercicios (elegir, verdad o bulo, emparejar y ordenar) por temas (ciencia, espacio, historia, economía, internet), con racha diaria, XP, niveles y energía.
- **Duelos**: 1 contra 1 contra un bot IA cuya dificultad sube con tus victorias (Fácil, Normal, Difícil, Experto).
- **Zanahorias**: la moneda del juego. Se ganan en lecciones y duelos.
- **Rabbitz**: todos empiezan igual (sudadera negra) y compran sudaderas, gorras, gafas y más con zanahorias.
- **Reto del día**: 5 preguntas iguales para todos cada día; resultado compartible en X como cuadrícula.
- **Reta a un amigo**: enlace `#duelo-semilla-aciertos-segundos` con las mismas preguntas (se comparte en X o se copia el enlace).
- **Racha**: cofre de regalo diario y premios a los 3, 7, 14 y 30 días (medalla y aureola exclusivas).

## Archivos
- `src.html`: código de la app. `units.js`: preguntas. `hero.js`: imagen de portada.
- `python3 build.py` genera `index.html` (la app instalable) y `app.html` (vista previa).
- El progreso se guarda en el navegador de cada persona (localStorage).
