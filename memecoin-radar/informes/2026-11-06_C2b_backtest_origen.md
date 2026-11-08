# C2b — ¿Gana entrar en tokens publicados por el propio proyecto? Backtest con precios reales · 2026-11-06

**Autor:** Claude. **Solo simulación.**
**Precios:** GeckoTerminal, velas de 1 min, uniendo la curva de pump.fun y el pool tras graduarse (por minuto, la vela con más volumen).
**Grupos:**
- **G7:** 323 tokens cuya CA publicó el proyecto o un tuit de narrativa en ≤10 min (`data/origen_proyecto.csv`). 186 tienen velas.
- **BASE:** 200 tokens nuevos de pump.fun al azar del recolector (6 nov). 161 tienen velas.

**Entrada:** 2, 5 o 15 min después de la publicación (G7) o de la creación (BASE). Solo cuenta si hay operaciones en esos 5 min; si no, no se habría podido comprar.
**Coste:** 5 % ida y vuelta.
**Scripts:** `investigacion/backtest_origen.py`, `investigacion/analizar_origen.py`, `investigacion/tp_sl.py`.

## Veredicto
**No.** Ninguna variante gana dinero de forma fiable. G7 pierde algo menos que un token al azar en la primera hora, pero sigue en negativo, y a 6 h y 16 h los dos grupos pierden lo mismo.

## Cifras (entrada a los 2 min)
| Estrategia | n | Media | Mediana | % que gana |
|---|---:|---:|---:|---:|
| G7, vender a 1 h | 112 | −3 % | −5 % | 4 % |
| Al azar, vender a 1 h | 65 | −26 % | −9 % | 3 % |
| G7, vender a 6 h | 112 | −18 % | −7 % | 2 % |
| Al azar, vender a 6 h | 65 | −28 % | −11 % | 0 % |
| G7, take-profit ×1,5 / stop ×0,7 (velas en orden) | 112 | −8 % | — | 6 % |
| G7, TP ×3 / stop ×0,5 | 112 | −10 % | — | 4 % |

- La media de G7 a 1 h la sostienen uno o dos tokens. Con un tope de 5x baja a −10 %.
- El "máximo en la primera hora" sí sube (+31 % de media), pero solo se cobra si sabes de antemano cuándo vender. Con reglas reales de take-profit y stop, se pierde.
- Muchos tokens no tienen ninguna operación en el minuto de entrada: la mayoría muere sin liquidez.

## Límites
- Un solo día de datos (6 nov) y muestras pequeñas (n = 65–112).
- No incluye deslizamiento extra en pools de pocos miles de $, que empeoraría el resultado.
- El análisis de 7 días del recolector (hacia el 13 nov) puede buscar otros rasgos, pero con lo visto hasta hoy no hay ventaja.
