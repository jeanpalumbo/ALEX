import numpy as np
from scipy import ndimage
def pez(a):
    """Peces sobre agua azul: todo lo que no tiene el tono del agua (o es contorno oscuro)."""
    x = a / 255.0; mx = x.max(2); mn = x.min(2); d = np.maximum(mx - mn, 1e-6); r, g, b = x[..., 0], x[..., 1], x[..., 2]
    h = np.where(mx == r, ((g - b) / d) % 6, np.where(mx == g, (b - r) / d + 2, (r - g) / d + 4)) * 60
    f = ((h < 180) | (h > 207) | (mx < 0.33)) & ((mx - mn) / np.maximum(mx, 1e-6) > 0.25)
    f = G._limpia(ndimage.binary_closing(ndimage.binary_opening(f, iterations=1), iterations=3), 800 * G.U * G.U)
    f = ndimage.binary_fill_holes(f)
    return ndimage.gaussian_filter(f.astype(np.float32), 0.8)
# Piezas a mano por imagen (coordenadas de diseño 1280x720) para full_anim.py.
# piezas: nombre -> (polígono, pivote, usa_mascara[, filtro])   anim: nombre -> rot/dy/vel/fase/aleteo/ojos/piel
# orden_atras: piezas que se dibujan DETRÁS del cuerpo (alas). Se va completando plano a plano.
import gancho_anim as G
RIG = {
    # Bakunawa: la cabeza ruge balanceándose
    "07": dict(agua="auto", piezas={"cabeza": ([(400, 80), (880, 80), (880, 300), (760, 340), (700, 410), (540, 420), (400, 380)], (610, 420), True)},
               anim={"cabeza": dict(rot=3.5, vel=1.7, dy=3)}),
    # Beithir: cabeza y cuello que vigilan
    "08": dict(agua="auto", piezas={"cabeza": ([(530, 160), (740, 160), (740, 360), (650, 400), (560, 400), (530, 330)], (600, 395), True)},
               anim={"cabeza": dict(rot=5, vel=1.2, dy=2)}),
    # dragón rojo del pergamino: alas que baten y cabeza
    "26": dict(piezas={"ala_i": ([(150, 20), (545, 20), (560, 130), (560, 210), (510, 320), (150, 320)], (563, 163), True, G.rojo),
                       "ala_d": ([(700, 20), (1100, 20), (1100, 320), (760, 320), (700, 210), (705, 130)], (691, 163), True, G.rojo),
                       "cabeza": ([(515, 10), (700, 10), (705, 150), (640, 185), (560, 180), (515, 140)], (612, 180), True)},
               orden_atras=["ala_i", "ala_d"], cuerpo=(0.45, 0.7, G.rojo_oro),
               anim={"ala_i": dict(rot=-8, vel=7.5, aleteo=0.05), "ala_d": dict(rot=8, vel=7.5, aleteo=0.05), "cabeza": dict(rot=4, vel=2.2, dy=2)}),
    # dragón de agua de Cadmo: la cabeza ruge
    "29": dict(agua="auto", piezas={"cabeza": ([(500, 50), (700, 50), (705, 230), (650, 300), (560, 300), (500, 250)], (600, 295), True)},
               anim={"cabeza": dict(rot=5, vel=2.4, dy=3)}),
    # Hidra: siete cabezas que cabecean cada una a su ritmo
    "09": dict(agua="auto", piezas={f"h{i}": (pol, piv, True) for i, (pol, piv) in enumerate([
                   ([(165, 165), (325, 165), (325, 335), (165, 335)], (290, 335)),
                   ([(340, 95), (478, 95), (478, 262), (340, 262)], (422, 266)),
                   ([(505, 40), (632, 40), (632, 225), (505, 225)], (576, 230)),
                   ([(632, 135), (790, 135), (790, 300), (632, 300)], (691, 305)),
                   ([(800, 120), (950, 120), (950, 252), (800, 252)], (870, 282)),
                   ([(866, 254), (962, 254), (962, 372), (866, 372)], (909, 384)),
                   ([(962, 212), (1130, 212), (1130, 350), (962, 350)], (1011, 358))])},
               anim={f"h{i}": dict(rot=5, vel=1.6 + 0.23 * i, fase=1.3 * i, dy=2) for i in range(7)}),
    # rueda de reconocimiento: cada dragón mueve la cabeza
    "28": dict(piezas={f"d{i}": (pol, piv, True) for i, (pol, piv) in enumerate([
                   ([(30, 225), (210, 225), (210, 390), (30, 390)], (128, 410)),
                   ([(315, 300), (428, 300), (428, 412), (315, 412)], (371, 422)),
                   ([(555, 222), (685, 222), (685, 390), (555, 390)], (614, 422)),
                   ([(760, 262), (902, 262), (902, 400), (760, 400)], (832, 422)),
                   ([(965, 326), (1236, 326), (1236, 466), (965, 466)], (1101, 512))])},
               anim={f"d{i}": dict(rot=5, vel=1.9 + 0.3 * i, fase=1.7 * i, dy=2) for i in range(5)}),
    # dragón chino blanco: cabeza que se balancea (el cuerpo ya ondula)
    "37": dict(piezas={"cabeza": ([(470, 40), (745, 40), (745, 330), (650, 365), (560, 365), (470, 330)], (610, 362), True)},
               anim={"cabeza": dict(rot=4, vel=1.5, dy=3)}),
    # león: parpadea y echa humo por la boca
    "42": dict(piezas={}, borrar=[[(120, 262), (378, 262), (382, 330), (372, 400), (382, 486), (120, 486)]], emisores=[dict(tipo="humo", pos=(386, 368), dir=(-1, -0.15), largo=260, r=34, vel=0.35)]),
    # Belerofonte y la Quimera: alas de Pegaso, fuego vivo, cabezas de cabra y de serpiente
    "43": dict(piezas={"ala_i": ([(0, 0), (330, 0), (345, 150), (380, 250), (300, 330), (170, 420), (0, 420)], (370, 290), True),
                       "ala_d": ([(520, 0), (720, 0), (720, 160), (600, 240), (530, 230)], (555, 235), True),
                       "cabra": ([(840, 190), (990, 190), (990, 325), (840, 325)], (920, 325), True),
                       "serp": ([(1020, 300), (1135, 300), (1135, 435), (1020, 435)], (1100, 440), True)},
               orden_atras=["ala_i", "ala_d"], borrar=[[(632, 418), (812, 420), (818, 470), (808, 545), (632, 545)]],
               emisores=[dict(tipo="fuego", pos=(816, 474), dir=(-1, -0.05), largo=190, r=36, vel=1.4, n=40)],
               anim={"ala_i": dict(rot=-7, vel=6.5, aleteo=0.05), "ala_d": dict(rot=7, vel=6.5, aleteo=0.05),
                     "cabra": dict(rot=6, vel=2.5), "serp": dict(rot=8, vel=3.0, fase=1)}),
    # Tifón contra Zeus: el cuerpo de cabezas ondula y los rayos chisporrotean
    "46": dict(piezas={}, emisores=[dict(tipo="rayo", pos=(818, 192), hacia=(520, 230), n=3)]),
    # Pele: el pelo ondea y parpadea
    "24": dict(piezas={"pelo": ([(700, 0), (1280, 0), (1280, 520), (900, 560), (760, 500), (700, 300)], (720, 250), True)},
               anim={"pelo": dict(onda=dict(amp=6, lam=240, vel=2.2, eje="x", taper=(0, 1)))},
               ojos=[dict(ojos=[(467, 182, 12, 6)], piel=(196, 128, 88), linea=(60, 30, 20))]),
    # niño leyendo con el dragón: los dos parpadean y el dragón se asoma
    "54": dict(piezas={"dragon": ([(614, 40), (900, 40), (900, 345), (760, 360), (640, 330), (614, 250)], (830, 345), True)},
               anim={"dragon": dict(rot=3, vel=1.3, dy=2, ojos=[(723, 234, 12, 13)], piel=(190, 55, 45), linea=(60, 15, 10), cada=3.0)},
               ojos=[dict(ojos=[(525, 323, 8, 9), (570, 323, 8, 9)], piel=(240, 196, 160), semilla=4)]),
    # anciano que cuenta historias: brazos que gesticulan, cabeza y parpadeo
    "17": dict(piezas={"brazo_i": ([(352, 235), (452, 250), (458, 335), (352, 335)], (450, 300), True),
                       "brazo_d": ([(820, 235), (965, 225), (965, 335), (812, 335)], (815, 300), True),
                       "cabeza": ([(570, 60), (740, 60), (745, 250), (700, 300), (600, 300), (565, 250)], (655, 300), True)},
               anim={"brazo_i": dict(rot=7, vel=2.6), "brazo_d": dict(rot=-7, vel=2.6, fase=0.8),
                     "cabeza": dict(rot=3, vel=1.8, ojos=[(623, 208, 9, 10), (669, 206, 9, 10)], piel=(214, 156, 112), cada=2.3)}),
    # anciana aborigen junto al fuego: habla con la voz, parpadea, el fuego crepita
    "20": dict(piezas={}, ojos=[dict(ojos=[(631, 251, 9, 6), (667, 247, 9, 6)], piel=(112, 66, 42), linea=(30, 15, 10), semilla=2)],
               boca=dict(pos=(651, 285), ancho=28, tapa=(15, 8), piel=(112, 66, 42)),
               emisores=[dict(tipo="fuego", pos=(627, 610), dir=(0.03, -1), largo=90, r=16, vel=1.8, n=30)]),
    # Cadmo asustado: parpadea
    "30": dict(piezas={}, ojos=[dict(ojos=[(609, 148, 10, 11), (670, 148, 10, 11)], piel=(190, 126, 84), linea=(40, 25, 15), semilla=5, cada=2.0)]),
    # paleontóloga en las fauces: parpadea
    "35": dict(piezas={}, ojos=[dict(ojos=[(619, 290, 10, 12), (666, 280, 9, 12)], piel=(240, 192, 158), linea=(45, 30, 20), semilla=3)]),
    # paleontólogo y anciana en la tienda china: él habla con la voz, los dos parpadean
    "49": dict(piezas={}, boca=dict(pos=(512, 313), ancho=36, tapa=(20, 10), piel=(232, 172, 124)),
               ojos=[dict(ojos=[(505, 272, 12, 11), (552, 278, 9, 11)], piel=(232, 172, 124), linea=(50, 30, 20), semilla=8),
                     dict(ojos=[(751, 351, 6, 9), (792, 357, 9, 11)], piel=(236, 186, 140), linea=(60, 40, 30), semilla=9, cada=3.1)]),
    # buceadora: los peces nadan
    "53": dict(piezas={"pez1": ([(228, 270), (368, 270), (368, 362), (228, 362)], (298, 316), False, pez),
                       "pez2": ([(318, 375), (418, 375), (418, 440), (318, 440)], (368, 408), False, pez),
                       "pez3": ([(856, 238), (994, 238), (994, 318), (856, 318)], (925, 278), False, pez),
                       "pez4": ([(862, 355), (986, 355), (986, 432), (862, 432)], (924, 394), False, pez)},
               anim={"pez1": dict(dx=22, rot=4, vel=2.4, dy=4), "pez2": dict(dx=16, rot=5, vel=3.0, fase=1, dy=3),
                     "pez3": dict(dx=-24, rot=4, vel=2.2, fase=2, dy=4), "pez4": dict(dx=-18, rot=5, vel=2.8, fase=0.5, dy=3)}),
    # --- planos de paisaje y objetos: algo se mueve siempre
    "10": dict(piezas={}),
    "11": dict(piezas={}, relampago=0.12),
    "12": dict(piezas={"tornado": ([(450, 0), (750, 0), (740, 690), (560, 690), (450, 400)], (640, 690), True)},
               anim={"tornado": dict(onda=dict(amp=16, lam=420, vel=4.5, eje="y", taper=(1.0, 0.15)))}),
    "13": dict(piezas={}, agua="auto", agua_y=0.7, emisores=[dict(tipo="humo", pos=(635, 200), dir=(0.15, -1), largo=260, r=60, vel=0.25, col=(120, 118, 122), n=34),
                                                            dict(tipo="fuego", pos=(635, 210), dir=(0, -1), largo=40, r=12, vel=1.6, n=18)]),
    "14": dict(piezas={}, emisores=[dict(tipo="chorro", pos=(560, 430), largo=150, n=26, vel=0.9, ancho=160, r=2.0, col=(120, 95, 65))]),
    "16": dict(piezas={"serp": ([(860, 625), (1015, 625), (1015, 720), (860, 720)], (935, 710), True)}, agua="auto", agua_y=0.45,
               anim={"serp": dict(onda=dict(amp=4, lam=80, vel=4, eje="x", taper=(1, 0.3)))}),
    "19": dict(piezas={"chica": ([(535, 255), (720, 255), (720, 695), (535, 695)], (628, 690), True)},
               anim={"chica": dict(rot=1.5, vel=1.6, dy=3)}),
    "21": dict(piezas={"meteoro": ([(585, 25), (925, 25), (925, 205), (585, 205)], (750, 115), False)}, agua="auto", agua_y=0.5,
               anim={"meteoro": dict(dx=-18, dy=6, vel=1.5)}),
    "23": dict(piezas={}, emisores=[dict(tipo="chorro", pos=(648, 340), largo=130, n=34, vel=1.4, ancho=5, col=(255, 150, 40))]),
    "25": dict(piezas={}, emisores=[dict(tipo="vapor", pos=(592, 330), dir=(0.05, -1), largo=170, r=30, vel=0.3, n=22),
                                    dict(tipo="vapor", pos=(685, 320), dir=(-0.05, -1), largo=200, r=34, vel=0.27, n=22),
                                    dict(tipo="vapor", pos=(750, 440), dir=(0.1, -1), largo=140, r=26, vel=0.33, n=18)]),
    "31": dict(piezas={"mano_i": ([(250, 0), (570, 0), (570, 300), (250, 300)], (420, 0), True),
                       "mano_d": ([(740, 0), (1090, 0), (1090, 300), (740, 300)], (900, 0), True)},
               anim={"mano_i": dict(rot=3, vel=2.6, dy=7), "mano_d": dict(rot=-3, vel=2.6, dy=7, fase=1.6)}),
    "32": dict(piezas={"pala": ([(900, 165), (1115, 165), (1115, 570), (900, 570)], (1000, 560), True)},
               anim={"pala": dict(rot=5, vel=2.8)}, emisores=[dict(tipo="humo", pos=(1000, 560), dir=(0.3, -0.5), largo=60, r=16, vel=0.8, col=(150, 115, 80), n=14)]),
    "34": dict(piezas={}, agua="auto", agua_y=0.55, emisores=[dict(tipo="pajaros", y=110, vel=60, n=5)]),
    "36": dict(piezas={}),
    "38": dict(piezas={}, emisores=[dict(tipo="pajaros", y=90, vel=-50, x0=1300, n=4)]),
    "39": dict(piezas={}, emisores=[dict(tipo="pajaros", y=170, vel=55, n=6)]),
    "41": dict(piezas={}, agua="auto", agua_y=0.55, emisores=[dict(tipo="vapor", pos=(606, 470), dir=(0.02, -1), largo=260, r=70, vel=0.22, n=34)]),
    "44": dict(piezas={}),
    "45": dict(piezas={}, emisores=[dict(tipo="pajaros", y=120, vel=-45, x0=1300, n=4), dict(tipo="vapor", pos=(635, 250), dir=(0.2, -1), largo=120, r=30, vel=0.25, col=(160, 160, 165), n=16)]),
    "48": dict(piezas={}, emisores=[dict(tipo="pajaros", y=130, vel=50, n=4)]),
    "50": dict(piezas={"dinos": ([(385, 140), (845, 140), (845, 425), (385, 425)], (615, 420), True)}, agua="auto", agua_y=0.4,
               anim={"dinos": dict(dx=14, dy=2, rot=0.8, vel=3.0)}),
    "52": dict(piezas={}, emisores=[dict(tipo="pajaros", y=150, vel=50, n=5)]),
}
