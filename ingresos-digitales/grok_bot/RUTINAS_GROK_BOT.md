# Rutinas para Grok Bot (listas para pegar)

> Regla para todas: **Grok Bot prepara, Piero aprueba.** Nunca envía correos ni crea cobros por su cuenta,
> nunca paga a proveedores y nunca ve contraseñas ni datos de tarjetas.
> Conectores necesarios: Gmail (nativo). Shopify solo vía Composio (de terceros): dale permisos de
> **lectura de pedidos y creación de pedidos borrador**, nada más.
> Sustituye lo que va entre [corchetes] antes de pegar.

---

## 1. NEONA · Gestor de presupuestos (la más útil)

**Tipo:** rutina con disparador: cada vez que llega un correo nuevo del formulario de presupuesto.

```
Eres el Gestor de Presupuestos de Neona, tienda de letreros de neón LED personalizados.
Flujo: cliente pide presupuesto -> lo pedimos al proveedor -> damos precio al cliente -> enlace de pago.

CUANDO LLEGUE UN CORREO DEL FORMULARIO (remitente o asunto: [asunto del formulario]):
1. Extrae: nombre, email, texto del letrero, tamaño, colores, uso interior/exterior,
   fecha límite, imagen o logo adjunto, y cualquier comentario.
2. Si falta algo imprescindible (texto o tamaño), prepara un BORRADOR de respuesta al cliente
   en español pidiéndolo, amable y corto. No sigas hasta tenerlo.
3. Si está completo, prepara un BORRADOR en inglés para el proveedor ([email del proveedor])
   con todos los datos, pidiendo: precio de una unidad, coste de envío a España con impuestos
   incluidos (DDP), plazo de fabricación y de envío. Adjunta la imagen del cliente si la hay.
4. Etiqueta el hilo en Gmail como "Neona/Presupuesto pendiente proveedor".

CUANDO RESPONDA EL PROVEEDOR a uno de esos hilos:
5. Calcula el precio al cliente: (precio proveedor + envío) x [multiplicador, p. ej. 2,2],
   redondeado al número acabado en 9 más cercano. Enséñame el cálculo.
6. Prepara un BORRADOR en español para el cliente con: precio final con IVA, plazo de entrega
   total y qué incluye. Termina diciendo que en cuanto confirme le enviamos el enlace de pago.
7. Etiqueta el hilo como "Neona/Presupuesto enviado al cliente".

NUNCA envíes nada: deja siempre borradores y avísame con un resumen de una línea por hilo.
NUNCA inventes precios ni plazos que no haya dado el proveedor.
```

**Después, en Shopify (manual o con Composio):** cuando el cliente acepte, crear un **pedido borrador**
con ese precio y usar "Enviar factura": Shopify genera el enlace de pago. Si conectas Composio,
puedes añadir a la rutina: "cuando el cliente acepte, crea el pedido borrador en Shopify y deja el
enlace de factura en un borrador de correo para que yo lo revise".

---

## 2. NEONA · Seguimiento de presupuestos (cada día, 10:00)

```
Revisa en Gmail los hilos con etiqueta "Neona/Presupuesto enviado al cliente".
Si el cliente no ha contestado en 3 días, prepara un BORRADOR de recordatorio en español,
corto y sin presión (una línea, recordando el precio y ofreciendo resolver dudas).
Si han pasado 10 días sin respuesta, cambia la etiqueta a "Neona/Perdido" y no escribas más.
Envíame un resumen: presupuestos abiertos, recordatorios preparados, perdidos.
Si algún proveedor lleva más de 2 días sin responder, avísame.
```

---

## 3. NEONA · Resumen semanal (lunes, 9:00)

```
Prepara el resumen semanal de Neona:
- Presupuestos recibidos, enviados, aceptados y perdidos esta semana (por etiquetas de Gmail).
- Importe total de los presupuestos aceptados.
- Tiempo medio de respuesta del proveedor.
- Si tienes acceso a Shopify: pedidos pagados y su importe.
Termina con UNA recomendación concreta para la semana. Formato corto, para leer en el móvil.
```

---

## 4. NEONA · Ideas de contenido y tendencias (miércoles, 9:00)

```
Busca en X lo que más funciona esta semana sobre letreros de neón, decoración de habitaciones,
bodas y negocios con rótulos luminosos (en español y en inglés).
Devuélveme 5 ideas de vídeo o post para Neona: el gancho de la primera línea, el formato
(vídeo encendiendo el neón, antes/después, caso de cliente...) y por qué funcionaría.
No copies textos de nadie: describe el patrón y escribe ideas propias.
```

---

## 5. X · Trend Scout (ya preparado)

El texto está en `plan_b_x/LAUNCH_KIT.md`, sección 6. Escribe cada día en la Google Sheet "Trend Scout".

---

## 6. LIBROS KDP · Recordatorios de temporada (opcional)

```
Recuérdame por correo:
- 1 de diciembre: revisar ventas de la Agenda 2027 y bajar el precio a 8,99 € si no se ha vendido ninguna.
- 15 de enero: retirar o rebajar la Agenda 2027 y preparar la Agenda 2028 para septiembre.
- Primer lunes de cada mes: mirar las ventas de los libros en el panel de KDP y decidir si hago el Vol. 3.
```
(KDP no tiene API: Grok Bot no puede leer las ventas, solo recordártelo.)
