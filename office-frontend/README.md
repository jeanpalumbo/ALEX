# Oficina de agentes — frontend

Visualización 2D de los agentes reales de `ai-commerce-os`. Construida sobre
el documento de diseño que Jean entregó (`diseno-oficina-agentes.md` /
`claude-handoff-oficina.md`), pero es la **versión funcional básica (vertical
slice)**, no el producto completo descrito ahí.

## Qué es real y qué es simulado

**Real, conectado al backend FastAPI:**
- Los 8 agentes (CEO + 7 especialistas) y sus nombres/roles reales.
- `status` (`working`/`idle`): se deriva estrictamente de si el agente tiene
  una tarea real `in_progress` en `TaskBoard` (`aicommerce/brain/tasks.py`).
  No se inventa ni se simula.
- La tarea mostrada y su `updated_at` son datos reales de esa tarea.

**Todavía simulado / no implementado (a diferencia del documento completo):**
- **Arte**: son rectángulos de color con iniciales, dibujados con Phaser
  Graphics — no hay sprites pixel-art reales todavía. Documentado así para
  no fingir un arte terminado que no existe. Sin assets externos: cero
  problema de licencias por ahora.
- **Tiempo real por WebSocket**: no implementado. La app hace polling REST
  cada 5 segundos (`POLL_INTERVAL_MS` en `src/App.tsx`). Fase 3 del
  documento de diseño original, pendiente.
- **"Mi oficina" (avatar/despacho del propietario)**: no implementado.
- **Personalización (paredes, muebles, avatar)**: no implementado.
- **Estado `blocked`**: el backend no lo expone todavía vía este endpoint,
  solo `working`/`idle`.

## Cómo ejecutarlo

1. El backend real debe estar corriendo (`python run_ceo_console.py` desde
   la raíz de `ai-commerce-os`, puerto 8420 por defecto).
2. Copia el `CONSOLE_TOKEN` real de `ai-commerce-os/.env` a
   `office-frontend/.env.local` como `VITE_CONSOLE_TOKEN=...` (archivo ya
   gitignored vía `*.local`).
3. `npm install`
4. `npm run dev` — abre en `http://localhost:5173`. El proxy de Vite
   (`vite.config.ts`) reenvía `/api/*` a `http://127.0.0.1:8420`.

## Limitación real conocida (no oculta)

El `VITE_CONSOLE_TOKEN` en `.env.local` es un mecanismo **solo para
desarrollo local**. Para producción, este frontend debería recibir el token
inyectado desde el servidor igual que `aicommerce/webapp/static/index.html`
lo hace hoy (reemplazo server-side de `__CONSOLE_TOKEN__`), no embebido en un
build estático público. Ese trabajo de empaquetado/despliegue no está hecho
todavía.

## Endpoint backend usado

```
GET /api/office/agents
```
Implementado en `aicommerce/webapp/office.py` (lógica de mapeo real) +
`aicommerce/webapp/server.py` (ruta). Ver `tests/test_office.py` en el repo
principal para la cobertura de pruebas.

## Próximos pasos (no hechos todavía)

En el orden que recomienda el documento de diseño original:
1. WebSocket en vivo con reconexión/backoff.
2. Vista "Mi oficina" con avatar y despacho del propietario.
3. Persistencia de decoración (paredes/muebles) vía backend real.
4. Arte pixel-art real (sprites originales, con licencia documentada).
5. Pulido de accesibilidad adicional y responsive para pantallas pequeñas.
