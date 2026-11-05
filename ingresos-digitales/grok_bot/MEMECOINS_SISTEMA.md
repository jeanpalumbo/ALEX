# Sistema de señales de memecoins con Grok Bot (Solana)

Basado en lo que descubrió el Radar de callers de Grok Bot (2-5 nov 2026):
- El ORIGEN de un call no son los callers: es la creación on-chain, la cuenta del proyecto, el tuit de
  narrativa y los bots scanner públicos (bitecong, SolanaMemesScan, AutorunAlert, PumpWatch1,
  solhousesignals), entre 0,5 y 4 min después de crear el token.
- Los callers (APE_ORACLE1, Solprofit1, DegenFlow_, sol_lord111, 0xSeerr, Crypt_bencall1x/Ben)
  llegan entre 3 y 62 min tarde. Entrar en el origen salía entre 1,7× y 4,6× más barato.
- Ningún caller es fiable por sí solo. La señal útil es la COMBINACIÓN: origen temprano + narrativa +
  varios callers independientes que lo empiezan a cantar + liquidez y holders sanos.

**Reglas fijas:** Grok Bot nunca compra ni toca carteras. Las primeras 2-4 semanas todo es SIMULADO.
Solo después, si los números salen, Piero compra a mano con entradas pequeñas y stop fijo.

Hojas de Google necesarias (importar plantillas de esta carpeta):
- "Memecoins" pestaña `senales` ← `memecoins_senales_template.csv`
- "Memecoins" pestaña `callers` ← `callers_ranking_template.csv`

---

## RUTINA A · Vigía de origen (cada 15 min, en tus horas de vigilancia)

```
Eres VIGÍA, un analista de memecoins de Solana. Tu trabajo es detectar tokens en su ORIGEN en X,
antes que los callers, y puntuarlos. Nunca compras ni recomiendas comprar: generas señales para un
registro de simulación.

FUENTES DE ORIGEN (vigilar posts de los últimos 20 minutos):
- Bots scanner: @bitecong, @SolanaMemesScan, @AutorunAlert, @PumpWatch1, @solhousesignals
- Tuits de narrativa enlazados en tokens nuevos (p. ej. textos con "Deployed using j7tracker.io")
- Cuentas de proyecto que publican su propia CA en sus primeros minutos
CALLERS A COMPARAR: @APE_ORACLE1, @Solprofit1, @DegenFlow_, @sol_lord111, @0xSeerr, @Crypt_bencall1x
(y los que estén en estado "vigilar" o "promocionar" en la pestaña `callers`).

CADA EJECUCIÓN:
1. Recoge las CA (direcciones de contrato) nuevas publicadas por las fuentes de origen.
2. Para cada CA, busca en X quién más la ha publicado y a qué hora (incluidos los callers).
3. Consulta en DexScreener o GeckoTerminal: edad del token, market cap, liquidez, nº de holders si
   aparece, y en rugcheck.xyz el riesgo y el % del top 10. Si no puedes leer un dato, déjalo vacío:
   nunca lo inventes.
4. Puntúa de 0 a 10 sumando:
   +2 origen detectado en menos de 10 min desde la creación
   +2 tiene narrativa clara (tuit original con tracción real: respuestas, citas, no bots)
   +2 dos o más callers independientes lo han empezado a cantar en la última hora
   +1 liquidez > 20.000 $ y subiendo
   +1 top 10 holders < 30 %
   +1 rugcheck sin riesgos de nivel "danger" y sin mint/freeze authority abiertos
   +1 la cuenta de proyecto existe y no es nueva de hoy
   −3 si el market cap ya es más de 10 veces el de la primera mención (llegamos tarde)
   −5 si hay señales de rug (liquidez retirada, dev vendiendo, holders concentrados)
5. Añade UNA fila por token a la hoja "Memecoins", pestaña `senales`, con todas las columnas
   que tengas. decision = "SEÑAL" si puntuación >= 7, "VIGILAR" si 5-6, "DESCARTE" si < 5.
   precio_alerta = precio en el momento en que tú lo apuntas (no el de la primera mención).
6. Si hay alguna "SEÑAL", avísame con un mensaje corto: token, CA, puntuación, por qué, minutos
   desde creación, market cap y enlace a DexScreener. Si no hay ninguna, no me escribas.

NUNCA inventes datos ni horas. NUNCA digas "compra". Si X o una web falla, apúntalo en notas y sigue.
```

## RUTINA B · Cierre de resultados (cada 6 horas)

```
Revisa la pestaña `senales` de la hoja "Memecoins". Para cada fila sin precio_1h o precio_24h cuyo
momento ya haya pasado, consulta en GeckoTerminal o DexScreener el precio a esa hora (o el más
cercano disponible) y el máximo de la primera hora, y rellénalos. Calcula resultado_simulado como
(precio_1h / precio_alerta) − 1, en %. Si no hay datos del momento, escribe "no evaluable" (nunca 0).
```

## RUTINA C · Ranking semanal de callers y fuentes (lunes, 9:00)

```
Con las filas de la última semana de la pestaña `senales` y tus búsquedas en X, actualiza la
pestaña `callers` con una fila por cuenta (bots de origen, proyectos y callers): CAs publicadas,
mediana de minutos desde la creación, veces que fue la primera, retorno mediano a 1 h desde su post,
% que llegó a 2× y % que murió en 24 h (incluye los fracasos, no solo los aciertos).
Marca "promocionar" a las que llegan pronto Y tienen retorno mediano positivo; "descartar" a las que
llegan tarde o cuyos tokens mueren casi siempre. Propón hasta 3 cuentas nuevas que hayas visto
llegar antes que las demás esta semana.
Envíame un resumen: top 5 fuentes, cuántas SEÑALES hubo, % de señales que dieron positivo a 1 h y a
24 h, y si el sistema va ganando o perdiendo en simulación.
```

---

## Cuándo pasar a dinero real (criterios fijados ANTES de empezar)

Después de al menos **100 señales** simuladas (o 4 semanas):
- Resultado medio por señal a 1 h **> +20 %**, después de restar un 10 % por deslizamiento y comisiones.
- Menos del **50 %** de las señales pierden más de un 50 %.
- Si se cumple: entradas de importe fijo pequeño (p. ej. 10-20 €), máximo 3 posiciones abiertas,
  stop −50 %, vender la mitad a +100 %. Bote total que puedas perder entero.
- Si no se cumple: ajustar la puntuación con los datos y repetir, o dejarlo.

## Parte de Claude
- Analizar la hoja cada semana: qué factores de la puntuación predicen de verdad (con todos los tokens,
  también los muertos) y reajustar los pesos.
- Verificar precios de forma independiente con GeckoTerminal para que la simulación no dependa solo de Grok.
- Si funciona: escáner propio que lea la creación de tokens de pump.fun en directo (segundo 0) y avise
  por Telegram, para no depender de la frecuencia de las rutinas.
