# Diseño de producto: Oficina de agentes

## Objetivo

Crear una oficina 2D en pixel art como capa visual de la empresa de ecommerce. La oficina representa a siete agentes reales del backend y también al propietario, que tiene un avatar y un despacho propios. Los estados y tareas mostrados proceden del sistema real. La oficina no simula una empresa ni inventa actividad.

## Dirección visual

- Vista cenital 2D, organizada por cuadrícula, con la lectura clara de un RPG portátil clásico: escenarios cálidos, paleta alegre, siluetas legibles, píxel marcado y animaciones cortas.
- Referencia de tono: juegos de aventura portátil de finales de los 90 y principios de los 2000. Crear personajes, tiles, interfaz, iconos y nombres originales; no usar personajes, sprites, logotipos, mapas ni recursos de Pokémon.
- Escenario luminoso, acogedor y ordenado. Suelos y paredes diferenciados, ventanas, plantas, alfombras, librerías y escritorios personalizados.
- El espacio debe leerse primero como una oficina real y después como una escena de pixel art. Evitar HUD de combate, estadísticas ficticias, monedas, niveles, misiones inventadas y elementos de captura.
- Pixel art nítido: escala base sugerida de 16 px por tile, renderizado con escalado entero cuando sea posible y sin suavizado. Mantener la misma proporción entre personajes, muebles y puertas.
- Paleta base sugerida: crema cálido para superficies, madera miel, verdes de plantas, azul petróleo para UI y acentos lavanda/coral/mostaza por agente. No depender solo del color para comunicar estados.

## Pantalla principal: oficina compartida

### Composición de escritorio

1. **Barra superior** (56–64 px): marca “Oficina de agentes”, estado de conexión discreto, acceso a preferencias y avatar del propietario.
2. **Escena** (aprox. 70 % del ancho): planta de oficina en cuadrícula con ocho espacios reconocibles: CEO, Research, Store Ops, Engineering, Finance, Marketing, Diseño y Propietario. Los siete primeros son agentes; el Propietario representa al usuario y no se cuenta como agente automático.
3. **Panel contextual** (aprox. 30 %): aparece al seleccionar personaje o despacho. Incluye nombre, rol, estado, tarea vigente y acciones disponibles. En el primer render, seleccionar Research como en el ejemplo visual.
4. **Resumen compacto**: “7 agentes · 3 trabajando · 4 inactivos” calculado desde el estado real; aclarar que el avatar del usuario no altera ese recuento.

En escritorio la escena debe conservar una vista general de los ocho puestos sin exigir desplazamiento. En pantallas pequeñas, usar vista de escena desplazable y el panel contextual como hoja inferior o pantalla de detalle.

### Personajes

- Ocho personajes persistentes: CEO, Research, Store Ops, Engineering, Finance, Marketing, Diseño y el usuario.
- Cada personaje tiene asiento o posición fija identificable. Los agentes no desaparecen cuando están inactivos.
- Cada agente tiene un acento visual y un escritorio reconocible; los rasgos no deben ser el único método para distinguirlo.
- El avatar del propietario se crea durante la configuración inicial y se puede editar después. Debe poder elegirse apariencia básica (tono de piel, pelo, ropa y accesorio), sin un editor de miles de combinaciones.
- Añadir una etiqueta con nombre al seleccionar o enfocar el personaje; en reposo puede mostrarse un rótulo discreto sobre la estación.

### Estados reales de los agentes

| Estado del backend | Presentación | Texto accesible |
|---|---|---|
| `working` | Animación corta de tecleo / luz cálida en pantalla | “Trabajando” |
| `idle` | Postura de reposo; indicador neutro | “Inactivo” |
| `blocked` (opcional si el backend lo conoce) | Icono de pausa/alerta; no usar color rojo como única señal | “Bloqueado” |
| `unknown` o conexión perdida | Mantener último estado con marca de antigüedad | “Sin actualización” |

Usar 2–4 cuadros por animación; limitar movimiento a tecleo, parpadeo, cambio de postura o actividad de pantalla. No simular caminar por la oficina si eso puede sugerir una acción que el agente no realizó. La oficina representa estado, no reproduce una cronología ficticia.

### Tarjeta de agente

Al seleccionar un personaje, mostrar:

- Nombre y especialidad.
- Estado en texto y con distintivo visual.
- Tarea actual con texto procedente del backend; si no hay tarea, “Sin tarea activa”.
- “Actualizado hace …” para que el usuario pueda valorar la vigencia del dato.
- Acciones de UI: “Ver detalle” (si existe página real), “Personalizar oficina” y “Editar avatar”. No representar botones de ejecución o control si el backend todavía no ofrece esas acciones.

## Oficina del usuario

El usuario tiene su propio despacho en una zona visible y conectada con la oficina común. No se considera empleado ni suma a los siete agentes. Su personaje puede estar sentado, trabajando en su portátil o de pie junto a su escritorio como pose estética; estas poses son decoración y no deben inferirse como estado de trabajo de los agentes.

Al seleccionar su personaje, el panel muestra “Tu espacio” y opciones para:

- Crear o cambiar avatar: cuerpo/piel, pelo, ropa y un accesorio de una lista corta.
- Elegir color o tema de pared.
- Elegir hasta dos piezas de mobiliario (por ejemplo, sillón, planta, pizarra o estantería).
- Elegir posición/preferencia de ubicación dentro de un conjunto acotado.
- Guardar y restablecer la apariencia.

Las modificaciones son persistentes por usuario. Debe existir vista previa antes de guardar y confirmación visible después. No permitir que la personalización oculte estaciones ni indicadores esenciales.

## Personalización de agentes y espacios

Mantener el alcance deliberadamente pequeño:

- 4–6 paletas de pared predefinidas o selector de color con muestra inmediata.
- 4–8 muebles compatibles por oficina; máximo dos muebles extra seleccionables además del escritorio base.
- Apariencia con pocos componentes modulares: base/cuerpo, pelo, ropa y accesorio.
- Guardado automático con opción de “Restablecer valores iniciales”.
- Mostrar claramente quién puede editar qué; la personalización no cambia rol, estado, prioridad, permisos ni comportamiento del agente.

## Flujos principales

### Primera visita

1. Cargar la instantánea de agentes reales.
2. Mostrar las siete estaciones y el despacho del usuario.
3. Pedir al usuario crear un avatar básico y elegir un tema inicial; permitir “Ahora no”.
4. Guardar preferencias y volver a la oficina.

### Consultar actividad

1. El usuario selecciona una estación.
2. El panel abre la tarjeta del agente seleccionado.
3. La tarjeta presenta estado, tarea actual y marca temporal provenientes del backend.
4. Al llegar un evento nuevo, se actualiza el indicador y la tarea sin mover la estación ni interrumpir la selección.

### Personalizar

1. Abrir “Personalizar oficina” o “Editar avatar”.
2. Elegir entre las opciones acotadas con previsualización en la escena.
3. Guardar o cancelar. La preferencia se persiste en el backend (o en el almacén de preferencias que el producto ya tenga).

## Interacción, accesibilidad y movimiento

- Clic/tap y teclado seleccionan estaciones; Tab recorre los puntos interactivos y Enter abre el detalle.
- Mostrar foco visible alrededor de la estación seleccionada.
- Nombre y estado deben existir como texto HTML accesible, no solo dentro del canvas.
- Combinar color con etiqueta, icono o forma para distinguir estados.
- Respetar `prefers-reduced-motion`; ofrecer una opción para reducir o desactivar animaciones.
- Mantener texto de tarea seleccionable y copiable en el panel HTML.
- Mostrar reconexión y antigüedad del último dato si el WebSocket se corta.

## Modelo mínimo de datos de diseño

```json
{
  "agent_id": "research",
  "display_name": "Research",
  "role": "Investigación de producto",
  "status": "working",
  "task": "Comparando proveedores para el producto X",
  "updated_at": "2026-10-04T12:30:00Z"
}
```

Preferencias separadas de los datos reales:

```json
{
  "owner_user_id": "user-123",
  "subject_id": "research",
  "wall_theme": "sage",
  "furniture": ["plant_small", "rug_blue"],
  "avatar": { "hair": "short_02", "clothes": "shirt_teal", "accessory": "glasses_round" }
}
```

Usar una entidad equivalente para `subject_id: "owner"`. Los valores de `status`, `task` y `updated_at` vienen del backend; las preferencias visuales no deben sobrescribirlos.

## Alcance de primera versión

**Incluir:** escena fija, ocho puestos (siete agentes + usuario), dos estados reales (`working`, `idle`), selección de agente, tarjeta de tarea, avatar sencillo del usuario, color de pared, hasta dos muebles, persistencia de preferencias, estados de conexión y una animación por estado.

**Dejar para después:** caminar libremente, habitaciones adicionales, mascotas, chat, economía o puntuaciones, sistema de logros, editor de mapas, inventario, generación ilimitada de prendas y telemetría que el backend no proporcione.

## Criterios visuales para revisar con Claude

- ¿Se reconocen los ocho puestos sin leer la ficha lateral?
- ¿La oficina se siente acogedora y aventurera, pero sigue pareciendo una herramienta de trabajo?
- ¿Se identifica al instante quién está trabajando, quién está inactivo y cuándo se perdió la conexión?
- ¿El usuario entiende que su despacho es propio y no un octavo agente de IA?
- ¿La tarea real tiene suficiente espacio y no queda enterrada en decoración?
- ¿La paleta y los sprites mantienen legibilidad en tamaño de ventana y en pantalla pequeña?
- ¿Todas las piezas gráficas son originales y sus licencias quedan documentadas?

## Prompt listo para continuar en Claude

Quiero que perfecciones este diseño de producto para una oficina web 2D en pixel art. Usa el documento completo como especificación. El aspecto debe recordar visualmente a los RPG portátiles clásicos: vista cenital por tiles, colores vivos, personajes pequeños y expresivos, escenarios acogedores; crea recursos originales y no copies Pokémon ni otros juegos. La aplicación representa siete agentes reales de mi backend FastAPI (CEO, Research, Store Ops, Engineering, Finance, Marketing y Diseño), y además mi propio avatar y mi despacho personal, que no cuentan como agente. Sus estados y tareas deben ser reales; no inventes mecánicas de juego ni datos. Mantén la primera versión acotada: estados trabajando/inactivo, ficha de tarea, avatar sencillo, cambios persistentes de pared/mobiliario/apariencia. Entrega una propuesta visual mejorada, identifica decisiones de diseño que necesitan mi opinión y luego prepara un backlog implementable por pasos. No amplíes el alcance a un juego completo.

## Decisiones técnicas recomendadas para iniciar implementación

- Frontend web con **React + TypeScript + Vite** para navegación, formularios y paneles HTML; **Phaser 3** como lienzo de la escena 2D. Mantener la capa de escena encapsulada para poder reemplazar Phaser por Canvas si la prueba inicial demuestra que basta.
- Backend existente **FastAPI** conserva la autoridad sobre roster, tareas, estado y preferencias persistidas. No trasladar la lógica del negocio al cliente.
- Carga inicial por REST; cambios en vivo por WebSocket. Si el socket se pierde, mantener visualmente la última instantánea, marcar su antigüedad y reconectar con espera incremental; al reconectar, pedir una instantánea REST para corregir cualquier evento perdido.
- UI HTML accesible para texto de tareas, controles, menús y selección. Phaser solo representa el espacio, muebles, sprites y hit targets; no convertir el texto esencial en bitmap.
- Primera entrega del frontend sin dependencia de cuentas externas. En desarrollo usar el endpoint local de FastAPI; en producción usar HTTPS/WSS en el mismo origen o configurar CORS y orígenes permitidos de forma explícita.

### Contrato de API propuesto (adaptar a rutas existentes antes de duplicarlas)

```http
GET /api/office/agents
GET /api/office/preferences
PUT /api/office/preferences/{subject_id}
WS  /ws/office
```

Instantánea REST:

```json
{
  "server_time": "2026-10-04T12:30:00Z",
  "agents": [
    {
      "agent_id": "research",
      "display_name": "Research",
      "role": "Investigación de producto",
      "status": "working",
      "task": {"id": "task-42", "title": "Comparando proveedores para el producto X"},
      "updated_at": "2026-10-04T12:29:40Z"
    }
  ]
}
```

Evento WebSocket versionado:

```json
{
  "type": "agent.status_changed",
  "version": 1,
  "event_id": "evt-1082",
  "occurred_at": "2026-10-04T12:30:05Z",
  "agent": {
    "agent_id": "research",
    "status": "idle",
    "task": null,
    "updated_at": "2026-10-04T12:30:05Z"
  }
}
```

Preferir eventos que transporten el estado actualizado completo del agente, no un delta ambiguo. El cliente debe ignorar eventos para IDs desconocidos, tolerar campos opcionales, evitar aplicar dos veces el mismo `event_id` cuando sea sencillo y no aceptar marcas temporales anteriores a la última actualización aplicada. El mensaje inicial del socket puede ser `office.snapshot` si el backend ya puede compartir la instantánea por esa vía.

Preferencias:

```json
{
  "subject_id": "owner",
  "wall_theme": "sage",
  "furniture": ["plant_small", "rug_blue"],
  "avatar": {"body": "skin_03", "hair": "short_02", "clothes": "shirt_teal", "accessory": "glasses_round"},
  "updated_at": "2026-10-04T12:20:00Z"
}
```

`subject_id` acepta los IDs de agentes o `owner`; el servidor valida la identidad del usuario y que tenga permiso para modificar esa preferencia. Preferencias y estados operativos deben almacenarse y actualizarse por separado. Al guardar, el servidor responde con la configuración canónica validada.

### Manejo de conexión y datos incompletos

- Estados UI del transporte: conectando, conectado, reconectando y sin conexión.
- No mostrar nunca “inactivo” como sustituto de un error de conexión. Conservar el último estado y añadir “Dato de hace X” / “Sin actualización”.
- La desconexión no debe borrar tarea, preferencias ni selección.
- Tras reconectar, solicitar instantánea completa y reemplazar el estado local; evita confiar en que el navegador haya recibido todos los eventos.
- Si un agente no tiene tarea, `task: null` se presenta como “Sin tarea activa”. Si falta un agente esperado en la respuesta, mostrar aviso de roster incompleto en lugar de inventarlo como inactivo.
- El resumen superior cuenta solo los siete agentes y excluye `owner`.

### Pantallas y estados que debe entregar la implementación

1. Oficina compartida con vista completa y siete puestos.
2. Tarjeta lateral de agente seleccionado con tarea, estado y fecha de actualización.
3. Vista separada “Mi oficina”, con avatar del usuario, despacho propio y controles de personalización.
4. Editor compacto de avatar con pocas opciones, vista previa y botones Guardar / Cancelar / Restablecer.
5. Personalización de despacho y de estaciones de agentes, con límite visible de dos muebles extra.
6. Primera visita con configuración inicial opcional y posibilidad de omitirla.
7. Estados de conexión, carga, roster vacío/incompleto, error de lectura y error de guardado.
8. Confirmación de guardado y opción de deshacer/restablecer si no complica la persistencia.

### Criterios de aceptación del MVP

- La pantalla presenta exactamente siete agentes del servidor más un espacio identificado para el usuario.
- Una actualización de FastAPI cambia estado y tarea del agente correcto sin recargar la página ni cambiar de asiento.
- Un evento duplicado o atrasado no revierte la interfaz a datos anteriores.
- Al perder la conexión, se ve la antigüedad de los datos y no se confunde con el estado `idle`; al volver, la instantánea REST resincroniza la pantalla.
- Seleccionar por ratón o teclado un puesto abre una ficha HTML accesible con nombre, estado, tarea y vigencia.
- La personalización del usuario persiste tras recargar; el flujo muestra error recuperable si el guardado falla.
- Personalizar la escena nunca modifica los datos ni el estado del agente.
- El diseño sigue siendo usable con movimiento reducido, pantalla pequeña y sin depender del color como único indicador.
- Toda imagen, spritesheet, tileset, fuente o icono externo tiene origen y licencia documentados; no se reutiliza arte protegido de juegos comerciales.

### Fases de trabajo para Claude

1. **Inspección del repo**: localizar modelos, eventos, autenticación, endpoints y convenciones frontend actuales. Reutilizar lo existente y enumerar las diferencias con el contrato propuesto.
2. **Vertical slice**: obtener roster real por REST, mostrar siete puestos, seleccionar uno y enseñar tarea/estado. Añadir una sola animación por estado.
3. **Tiempo real robusto**: WebSocket, reconexión, resincronización REST, estados de transporte, timestamps y tolerancia a eventos duplicados/antiguos.
4. **Mi oficina**: crear avatar inicial, vista del despacho personal y edición básica.
5. **Persistencia de decoración**: guardar preferencias de usuario y agentes, manejar errores y valores por defecto.
6. **Pulido**: teclado, etiquetas accesibles, responsive, movimiento reducido, créditos de assets y documentación para ejecutar.

En cada fase entregar cambios pequeños y ejecutables, explicar archivos tocados y decisiones abiertas. No construir fases posteriores antes de verificar que el contrato real del backend encaja.
