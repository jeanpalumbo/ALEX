# Tiempos de producción — Hércules en Minecraft (vídeo largo, 8:44)

PC: CPU de 12 hilos, 16 GB de RAM, GPU NVIDIA GTX 1060 6 GB. Render: three.js (WebGL) en Edge headless controlado por CDP; cada fotograma se captura y se pasa por tubería a ffmpeg (x264). 1080p a 30 fps.

## 1. Render por fotograma (escenarios llenos, 3 capas, sombras, partículas y elementos vivos)
| Configuración | s/fotograma (1 proceso) | Medido en |
|---|---|---|
| Captura PNG + x264 medium, sin postprocesado | ~0,18 (1 proceso) / 6 procesos en paralelo → **19 fps en total** | render completo v1: 8:26 de vídeo en **12 min 26 s** |
| Captura PNG + x264 medium + postprocesado (bloom, bokeh, gradación) | **0,281** | tramo de 10 s (Hidra) |
| Captura **JPEG q95** + x264 medium + postprocesado | **0,120** (2,3 veces más rápido) | mismo tramo |
| NVENC (h264_nvenc) | no funciona: el driver de NVIDIA instalado es demasiado antiguo (pide 570+, hay API 12.2). Actualizar el driver es un cambio de sistema, así que no lo he hecho. | — |

- **Minutos de render por minuto de vídeo:** v1 (PNG): **~1,5 min por cada minuto** con 6 procesos en paralelo. v2 (JPEG + postprocesado): ver la línea «v2 medido» abajo.
- Un solo proceso en serie (PNG): ~9 min de render por minuto de vídeo. En paralelo se gana unas 6 veces.

## 2. Qué limita
- **CPU (96-100 %)** durante el render en paralelo. Se la reparten: (a) la codificación PNG de cada captura dentro de Chrome, (b) la decodificación de esas PNG en ffmpeg, (c) x264 preset medium a CRF 16 con 6 flujos a la vez y (d) el JavaScript de las escenas.
- **GPU (~35 %)**: va sobrada; dibujar la escena en WebGL no es el cuello de botella.
- **Captura por CDP**: con PNG cuesta ~0,15 s por fotograma (codificar y transferir 6 MB). Con JPEG baja a ~0,03 s.
- Conclusión: el límite es la **CPU, por la compresión de imágenes y vídeo**, no el dibujo 3D.

## 3. Tiempo de trabajo (horas del PC, 15-nov)
| Fase | Tiempo |
|---|---|
| Guion (reescritura con chistes, 63 bloques) + voz de Jorge con tiempos por palabra | ~15 min (12:05 → 12:20, con una ampliación para llegar a 8+ min) |
| Motor (rig, 16 expresiones, criaturas), librería de 21 escenarios, 63 escenas con cámaras, intro, rótulos y CTA | ~25 min de escritura + 2 rondas de revisión por fotogramas (~15 min) |
| Render v1 completo | 12,5 min |
| Audio (música por capítulo, efectos, ducking), subtítulos, miniaturas, textos | ~15 min |
| Mejoras (bucles abiertos, rótulos con datos, postprocesado) + render v2 | ver v2 abajo |

## 4. Cómo acelerar (probado / propuesto)
1. **Capturar en JPEG q95 en vez de PNG → probado: 2,3 veces más rápido por proceso.** Sin pérdida visible a 1080p, porque el vídeo final se recomprime de todos modos. **Ya está activado** (`FMT=jpeg` en render_par.sh).
2. **Varios procesos de Edge en paralelo (6) → probado: ~6 veces.** Más procesos no ayudan: la CPU ya está al 100 %.
3. x264 `-preset veryfast` para los segmentos intermedios (la copia final se recodifica igual) → libera CPU. Opción `PRESET=veryfast` en render.js, aún no medida.
4. NVENC: haría falta actualizar el driver de NVIDIA (≥ 570). Le liberaría a la CPU toda la codificación (estimo un 30-40 % más rápido). **Requiere permiso de Piero**, porque es una instalación del sistema.
5. `canvas.toBlob()` o WebCodecs dentro de la página en lugar de capturas por CDP: evita el redibujado de la captura de pantalla. Estimo otro 20-30 %. Sin probar aún.
6. Reutilizar fondos: los escenarios ya se construyen una sola vez por proceso (caché) y solo se dibuja lo visible. Las sombras de 2048 px y el antialias podrían bajarse en los planos generales sin que se note.

## v2 medido
(se completa al terminar el render v2)
