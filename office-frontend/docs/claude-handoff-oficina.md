# Instrucciones para Claude: llevar Oficina de agentes a una primera versión

Lee primero `diseno-oficina-agentes.md` y abre `oficina-agentes-demo.html` como referencia visual. Este paquete ya fija el objetivo del producto, estilo, alcance, entidades, estados de conexión, contrato tentativo y criterios de aceptación. Úsalo como punto de partida para inspeccionar el repositorio y avanzar con el máximo trabajo autónomo razonable.

## Objetivo

Implementar una oficina web 2D en pixel art para visualizar siete agentes reales de un backend Python/FastAPI: CEO, Research, Store Ops, Engineering, Finance, Marketing y Diseño. Añadir un avatar y un despacho persistente para el propietario; ese espacio no es un octavo agente. La interfaz refleja solo estados y tareas reales. No construir un juego de simulación.

Dirección visual: oficina cenital por tiles, colorida y acogedora, con la claridad visual de los RPG portátiles clásicos. Crear arte original: no reutilizar sprites, nombres, logotipos, escenarios o personajes de Pokémon ni de otros juegos comerciales. Usa el demo como referencia de composición, no como fuente de backend ni como código de producción.

## Forma de trabajo

1. Inspecciona el repositorio actual antes de crear archivos. Averigua framework frontend, rutas, modelos de agente, mecanismo de eventos, autenticación y almacenamiento de preferencias. Aprovecha lo existente.
2. Devuelve primero un resumen corto de lo encontrado y un plan de implementación concreto. Si puedes avanzar sin una decisión del usuario, elige un valor conservador y documenta el supuesto; no detengas el trabajo por preferencias cosméticas menores.
3. Implementa en incrementos pequeños, completos y ejecutables. Prioriza una vertical slice funcional de extremo a extremo.
4. No inventes contratos que choquen con los modelos existentes. Mapea los modelos reales al contrato de UI propuesto en la especificación. Si el backend carece de algún dato o endpoint, deja un adaptador claro y enumera el trabajo backend pendiente.
5. Mantén la lista de agentes y preferencias tipadas. El ID `owner` representa al usuario y queda excluido de los conteos de agentes.
6. Mantén tareas y estados en DOM accesible; reserva el canvas para escena, sprites y selección visual.
7. Para cada recurso externo, registra fuente, autoría y licencia. Prefiere assets propios o recursos con licencia compatible y atribución clara. No des por hecho que la licencia del editor cubre el arte exportado.

## Decisión técnica inicial

Si el repositorio no tiene frontend, usa React + TypeScript + Vite para el shell HTML y Phaser 3 para la escena 2D. No instales una pila de servicios. Si el repositorio ya usa otra solución web, intégrate con ella y explica por qué Phaser/Canvas encaja. FastAPI sigue siendo la autoridad para datos reales y guardado de personalización.

## Alcance MVP

- Vista compartida con siete puestos identificables, siempre presentes, selección con ratón y teclado y contador de agentes que excluya al propietario.
- Estados mínimos `working` e `idle`; `unknown`/sin conexión es un estado de transporte visual diferente. Un estado `blocked` solo se muestra si backend ya lo ofrece.
- Actualizar la tarea y el indicador al recibir eventos reales, sin recargar ni mover a los personajes.
- Ficha de agente con rol, tarea actual o “Sin tarea activa”, estado textual y hora de actualización.
- Vista separada “Mi oficina”, avatar básico, tema de pared y máximo dos muebles adicionales.
- Preferencias visuales persistidas para usuario y estaciones mediante el backend existente. Si todavía no existe endpoint, define el contrato y crea una interfaz de servicio pequeña; el fallback local solo sirve para el prototipo.
- Responsive, movimiento reducido, foco visible, texto de tarea seleccionable, guardado/cancelación y estados de carga/error.

## Eventos y sincronización

Usa los endpoints existentes si están disponibles. En ausencia de endpoints apropiados, propone este mínimo para acordar con el backend:

```http
GET /api/office/agents
GET /api/office/preferences
PUT /api/office/preferences/{subject_id}
WS  /ws/office
```

Instantánea sugerida:

```json
{
  "server_time": "ISO-8601 UTC",
  "agents": [
    {"agent_id":"research","display_name":"Research","role":"Investigación de producto","status":"working","task":{"id":"task-42","title":"Comparando proveedores"},"updated_at":"ISO-8601 UTC"}
  ]
}
```

Evento sugerido:

```json
{"type":"agent.status_changed","version":1,"event_id":"evt-1","occurred_at":"ISO-8601 UTC","agent":{"agent_id":"research","status":"idle","task":null,"updated_at":"ISO-8601 UTC"}}
```

El navegador carga instantánea REST al entrar, abre WebSocket, ignora IDs desconocidos y eventos atrasados, y no trata `idle` como fallback de conexión. Ante desconexión conserva la última información con su timestamp, indica reconexión y vuelve a pedir instantánea REST al reconectar. Implementa backoff limitado y limpia el socket al desmontar la vista. Si el backend ya publica eventos, adapta un mapper en vez de cambiar el backend sin necesidad.

## Vistas/estados que deben quedar cubiertos

1. Oficina compartida con selección y detalle de agente.
2. “Mi oficina” separada, avatar y controles visuales.
3. Personalización de pared, mobiliario y avatar con vista previa.
4. Carga, conectando, conectado, reconectando, sin conexión, fallo de lectura, fallo de guardado, roster vacío/incompleto y tarea vacía.
5. Preferencia de movimiento reducido y navegación por teclado.

## Criterios de finalización

- Se puede ejecutar localmente siguiendo instrucciones del repositorio.
- La UI recibe o simula datos solo a través de una interfaz de servicio; no mezclar conexiones de red dentro de cada sprite.
- Al cambiar el estado de un agente, solo cambian su sprite/indicador/tarjeta y los conteos derivados.
- `owner` nunca se incluye en el contador de agentes, no recibe estados de trabajo inventados y tiene un espacio propio.
- Se ve claramente la antigüedad del último estado si la conexión cae.
- Cambiar decoración no modifica tareas, estado, rol o configuración funcional del agente.
- La preferencia confirmada sobrevive a recargar cuando hay persistencia backend.
- Los controles tienen nombres accesibles y el color nunca es la única codificación.
- Documenta las variables de entorno, endpoints esperados, cómo conectar el backend y licencias de assets.
- Al acabar, informa qué quedó conectado al backend, qué sigue siendo mock y cualquier limitación real. No declares terminado lo que dependa de endpoints inexistentes.

## Entregables esperados de Claude

- Implementación integrada al repositorio, no solo recomendaciones.
- Un resumen de decisiones técnicas y archivos principales.
- Un mapa explícito de `datos reales` frente a `datos simulados`.
- Lista corta de bloqueos backend, si los hay, con el contrato exacto necesario.
- Captura/preview del resultado y pasos para ejecutarlo.
- No pedir confirmación para elecciones reversibles de UI; consulta solo si una decisión afecta contratos o comportamiento real que no se pueda inferir del código.
