# Oficina

Aquí se coordina el trabajo entre **Piero** (dueño), **Claude** (gestor) y **Grok Bot** (empleado con
ordenador propio en la nube: X, edición, clips, scripts 24/7).

## Cómo funciona
1. Piero cuenta sus ideas a Claude.
2. Claude las convierte en tareas concretas en `grok/TAREAS.md`: qué hacer, cómo, qué entregar y
   cómo se comprueba que salió bien.
3. Grok Bot revisa esta oficina **cada 2 horas** (rutina automática), hace sus tareas PENDIENTE y
   deja un informe en `grok/informes/AAAA-MM-DD_<tarea>.md` con datos, enlaces y problemas.
4. Claude revisa los informes **cada 6 horas**, comprueba los datos por su cuenta, escribe su
   revisión en `claude/revisiones/` y pone las siguientes tareas.
5. Las decisiones con dinero, cuentas o publicaciones nuevas las aprueba Piero.

## Ramas
- Claude escribe en `claude/new-session-akjsxp` (rama de la oficina: léela siempre de aquí).
- Grok Bot escribe en `grok/oficina` y solo toca: `oficina/grok/informes/`, la columna Estado y
  Resultado de sus filas en `oficina/grok/TAREAS.md`, y las carpetas de datos que diga cada tarea.
- Claude fusiona `grok/oficina` en su rama en cada revisión.

## Reglas para Grok Bot
- Datos reales con fuente o captura; si algo no se pudo comprobar, se escribe "NO COMPROBADO".
- Nada de inventar cifras ni rellenar huecos.
- Si una tarea no se puede hacer, se marca BLOQUEADO con el motivo exacto; no se cambia la tarea.
- No gastar dinero, no crear cuentas nuevas y no publicar en canales nuevos sin aprobación de Piero.
- Respetar las normas de cada plataforma (YouTube, X): nada de spam, bots de interacción ni
  contenido ajeno resubido sin transformación propia.

## Proyectos
Ver `PROYECTOS.md`.
