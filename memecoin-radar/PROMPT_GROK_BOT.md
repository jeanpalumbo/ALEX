# Mensaje para pegar en Grok Bot

(Antes: en Grok Bot → Plugins, conecta GitHub y dale acceso al repositorio `jeanpalumbo/ALEX`.)

---

Vamos a construir entre tú y Claude (otro agente de IA que programa) un sistema para encontrar
entradas a memecoins de Solana en su ORIGEN. Tú eres el especialista en X; Claude programa y analiza.
Yo (Piero) decido. Nadie compra nada: las primeras semanas todo es simulación.

CONTEXTO
- Todo está en GitHub: repositorio `jeanpalumbo/ALEX`, carpeta `memecoin-radar/`, rama
  `claude/new-session-akjsxp`. Lee primero `memecoin-radar/README.md` y `memecoin-radar/TAREAS.md`.
- Tu propio Radar de callers (radar-de-callers-mcto.pages.grok.bot) ya demostró que el origen de los
  calls son la cuenta del proyecto, el tuit de narrativa y bots scanner públicos (0,5-4 min tras crear
  el token), y que los callers llegan 3-62 min tarde. Partimos de ahí.

CÓMO TRABAJAMOS
- Trabaja en tu propia rama: `grok/memecoin-radar` (créala desde `claude/new-session-akjsxp`).
  Claude la lee y la integra. No toques la rama de Claude ni la carpeta `radar/`.
- Tú escribes SOLO en: `memecoin-radar/data/senales.csv`, `memecoin-radar/data/callers.csv`,
  `memecoin-radar/data/historico_bots.csv`, `memecoin-radar/investigacion/` y tu sección de `TAREAS.md`.
- Respeta EXACTAMENTE las cabeceras de los CSV (Claude los procesa con código).
- Al terminar cada tarea: actualiza su estado en `TAREAS.md` con fecha y una línea de resultado.
- Si necesitas algo de Claude, escríbelo en "Preguntas entre agentes" de `TAREAS.md`.

TUS TAREAS, EN ESTE ORDEN
1. G1: la investigación de `memecoin-radar/investigacion/ENCARGO_G1.md`. Hazla a fondo en X: cada
   dato con su enlace, horas en UTC, CAs completas, DEMOSTRADO / INDICIO / HIPÓTESIS separados, y
   los fracasos incluidos. Si algo no se puede comprobar, dilo. Sin huecos y sin inventar.
2. G5: histórico de 200-500 posts de 3-4 bots de origen (todas sus CAs, también las que murieron) en
   `data/historico_bots.csv` con columnas: fuente, url_post, hora_post_utc, ca, red. Claude hará el
   backtest con precios reales.
3. G2, G3 y G4: las rutinas de vigilancia, resultados y ranking (los textos están en
   `ingresos-digitales/grok_bot/MEMECOINS_SISTEMA.md` del mismo repositorio). Escriben en `data/`.

REGLAS
- El repositorio es PÚBLICO: nunca subas claves, wallets privadas ni datos personales.
- Nunca compres, publiques ni interactúes con cuentas. Nunca digas "compra".
- Nunca inventes horas, precios, cuentas ni CAs. Un dato sin fuente no vale.

Empieza por G1 y avísame cuando el informe esté subido.
