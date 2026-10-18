# Ingresos digitales

Proyecto de Piero: libros KDP, plantillas Etsy y borradores para X. Regla de oro:
**nada se publica solo**; el sistema prepara y Piero revisa y sube a mano.

El plan completo está en el documento de encargo (`PLAN_CLAUDE_CODE.md`). Este README
recoge lo que **funciona hoy**.

## Estado (18 oct 2026)

| Pieza | Estado |
|---|---|
| `plan_c_kdp/` — libro Vol. 1 "Recuerdos de España" | ✅ Interior, portada y ficha generados y con tests |
| `shared/` — config, SQLite, wrapper de Anthropic con coste | ✅ Base lista (aún no se usa: los temas se escribieron en sesión) |
| `plan_b_x/` — borradores para X | ⏳ Semana 2, cuando Trend Scout escriba en la Google Sheet |
| `plan_a_etsy/`, `plan_e_pinterest/` | ⏳ Después del lanzamiento del Vol. 1 |

## Instalación

```bash
cd ingresos-digitales
pip install -e ".[dev]"        # añade ".[llm]" cuando haga falta la API de Anthropic
cp .env.example .env           # solo necesario para los planes con API
```

## Libro KDP: generar todo

```bash
python -m plan_c_kdp.build
```

Salida en `build/vol1/` (no se sube al repo):

- `vol1_interior.pdf` — 134 páginas, 8.5×11 in sin sangrado, fuentes incrustadas.
- `vol1_cover.pdf` — portada completa (trasera + lomo + delantera), CMYK, tamaño exacto
  según la fórmula de KDP para 134 páginas en papel blanco.
- `listing.md` — título, subtítulo, descripción, 7 palabras clave, categorías, precio,
  declaración de IA y checklist de subida.

Opciones: `--paper cream` (cambia el ancho del lomo), `--cover-image assets/portada.png`
(ilustración propia en la portada; se convierte a CMYK y avisa si baja de 300 ppp).

### Cambiar temas o palabras

Editar `plan_c_kdp/themes/vol1_recuerdos_de_espana.yaml` y volver a ejecutar el build.
El programa rechaza con un mensaje claro cualquier lista que no pueda dar una solución
única (palabra dentro de otra, palíndromos, palabras de más de 15 letras, etc.).

### Decisiones de diseño

- **Mayúsculas sin tildes, con Ñ.** La palabra de la lista se escribe igual que en la
  cuadrícula (BALON, no BALÓN), para no confundir. La Ñ se mantiene porque es una letra
  propia del español (ESPAÑA). El relleno no usa Ñ, K ni W.
- **Direcciones:** horizontal (izq.→der.), vertical (arriba→abajo) y las dos diagonales que
  se leen de izquierda a derecha. Ninguna palabra al revés. Predominan horizontal y vertical.
- **Solución verificable:** cada palabra aparece exactamente una vez en la cuadrícula
  (comprobado en las 8 direcciones) y las celdas de la solución la deletrean. El relleno no
  forma palabras malsonantes de una lista negra.
- **Letra:** Atkinson Hyperlegible (diseñada para baja visión, licencia OFL): cuadrícula de
  15×15 a 24 pt, lista de palabras a 18 pt (el plan pide ≥ 16 pt). Portada con Abril Fatface (OFL).
- **Márgenes:** interior 0.75 in, exterior 0.5 in, superior 0.55 in, inferior 0.6 in.
  KDP exige como mínimo 0.375 in de margen interior (24-150 páginas) y 0.25 in en el resto.
- **Especificaciones KDP** verificadas el 18 oct 2026 en la ayuda oficial; las fuentes están
  en `plan_c_kdp/kdp_specs.py`. Revisarlas antes de cada volumen nuevo.
- **Sin copyright ajeno:** sin letras de canciones ni marcas; los nombres de cantantes
  aparecen solo como palabras del pasatiempo (tema "Voces de la canción").

## Tests

```bash
python -m pytest -q
```

Comprueban, entre otras cosas, que cada palabra de las 100 sopas está una sola vez en su
cuadrícula y en la solución, que todas las fuentes están incrustadas, que la portada mide
lo que pide KDP y es solo CMYK, y que la ficha respeta los límites de KDP.
