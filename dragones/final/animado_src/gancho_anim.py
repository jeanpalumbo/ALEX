# Muestra animada (cut-out) del gancho de dragones, 15 s, 1920x1080 30 fps, sin Grok:
# piezas recortadas de las imágenes 01-06 (rembg + polígonos), huecos rellenados, y animación por código:
# cabezas que giran y cabecean, alas que baten, cuellos de serpiente que ondulan, lengua, parpadeos dibujados,
# bocas sincronizadas con la voz de Jorge, brazo del monje, interrogación que bota, cola que se mueve,
# silueta->color como el original, partículas, cámara viva. Subtítulos sin solapes (comprobados).
# Uso: python gancho_anim.py [t0 t1 salida.mp4] | hoja t1,t2,... salida.jpg
import os, sys, math, json, subprocess, numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageChops
from scipy import ndimage
os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ".")
from anim_lib import cl, eio, eout, ein, back, lerp, keys, pegar, onda, Boca, parpadeo, silueta, vineta
W, H, FPS = 1920, 1080, 30
U = 2                                    # trabajamos a 2560x1440 (coordenadas de diseño 1280x720 x2)
SW, SH = 1280 * U, 720 * U
PAL = json.load(open("../full/palabras.json", encoding="utf-8"))
BOCA = Boca("../full/vo.wav", PAL)
P = json.load(open("../full/planos.json", encoding="utf-8"))
LEAD = 0.12
T0 = {p["n"]: (0.0 if i == 0 else p["t0"] - LEAD) for i, p in enumerate(P[:8])}
FIN = 15.0
T1 = {}
ks = list(T0)
for i, k in enumerate(ks): T1[k] = T0[ks[i + 1]] if i + 1 < len(ks) else FIN

# ---------------- utilidades de piezas
def img(k): return Image.open(f"../img/{k}.png").convert("RGB").resize((SW, SH), Image.LANCZOS)
def msk(k, lo=0.35, hi=0.6):
    m = np.asarray(Image.open(f"mask/{k}.png").convert("L").resize((SW, SH), Image.LANCZOS)).astype(np.float32) / 255
    return np.clip((m - lo) / (hi - lo), 0, 1)
def poly(pts, feather=2.0):
    m = Image.new("L", (SW, SH), 0); ImageDraw.Draw(m).polygon([(x * U, y * U) for x, y in pts], fill=255)
    return np.asarray(m.filter(ImageFilter.GaussianBlur(feather * U))).astype(np.float32) / 255
def rellenar(a, hueco):
    """Rellena hueco (0..1) con convolución normalizada multiescala (el fondo tapa lo que había debajo)."""
    a = a.astype(np.float32); hb = hueco > 0.02
    known = (~hb).astype(np.float32); fill = a.copy(); hecho = ~hb
    for r in (4, 10, 24, 60, 140):
        num = np.stack([ndimage.gaussian_filter(a[..., k] * known, r) for k in range(3)], -1)
        den = ndimage.gaussian_filter(known, r)
        sel = (~hecho) & (den > 0.08)
        fill[sel] = num[sel] / den[sel][:, None]; hecho |= sel
    return a * (1 - hueco[..., None]) + fill * hueco[..., None]
def plancha(a, alfa):
    """Pieza RGBA recortada a su caja + desplazamiento (x0, y0)."""
    al = (np.clip(alfa, 0, 1) * 255).astype(np.uint8); ys, xs = np.where(al > 4)
    x0, y0, x1, y1 = xs.min(), ys.min(), xs.max() + 1, ys.max() + 1
    rgba = np.dstack([a[y0:y1, x0:x1].astype(np.uint8), al[y0:y1, x0:x1]])
    return Image.fromarray(rgba, "RGBA"), (x0, y0)
class Pieza:
    def __init__(self, a, alfa, piv):
        self.im, (self.x0, self.y0) = plancha(a, alfa); self.piv = (piv[0] * U, piv[1] * U)
        self.lp = (self.piv[0] - self.x0, self.piv[1] - self.y0)      # pivote en coords de la pieza
    def loc(self, x, y): return (x * U - self.x0, y * U - self.y0)
    def dibujar(self, cv, dx=0, dy=0, rot=0, sx=1, sy=1, im=None):
        pegar(cv, im or self.im, self.lp, (self.piv[0] + dx * U, self.piv[1] + dy * U), rot, sx, sy)

def parpado(im, pz, ojos, cierre, piel, linea=(30, 30, 30)):
    """Párpados (cierre 0..1) sobre una copia de la pieza: piel lisa, contorno superior y línea de pestañas."""
    if cierre <= 0.01: return im
    im = im.copy(); d = ImageDraw.Draw(im); lw = max(3, int(1.7 * U))
    for cx, cy, rx, ry in ojos:
        x, y = pz.loc(cx, cy); rx, ry = rx * U * 1.18, ry * U * 1.15
        bot = y - ry + 2 * ry * cierre; caja = [x - rx, y - ry, x + rx, y + ry]
        m = Image.new("L", im.size, 0); ImageDraw.Draw(m).ellipse(caja, fill=255)
        if cierre < 0.98: ImageDraw.Draw(m).rectangle([0, bot, im.width, im.height], fill=0)
        im.paste(Image.new("RGBA", im.size, piel + (255,)), (0, 0), m); d = ImageDraw.Draw(im)
        d.arc(caja, 200, 340, fill=linea, width=lw)                                  # contorno de arriba
        yb = min(bot, y + ry * 0.35)
        d.arc([x - rx * 0.98, yb - ry * 0.75, x + rx * 0.98, yb + ry * 0.25], 20, 160, fill=linea, width=lw + 1)   # pestañas
    return im

def boca(im, pz, cx, cy, ancho, abre, piel, tapa=None, linea=(40, 20, 20), interior=(95, 28, 32), lengua=(205, 95, 95)):
    """Boca de dibujo animado: tapa la boca original (tapa=(rx, ry)) y dibuja una abierta de altura abre (0..1)."""
    im = im.copy(); d = ImageDraw.Draw(im); x, y = pz.loc(cx, cy); w = ancho * U
    if tapa: d.ellipse([x - tapa[0] * U, y - tapa[1] * U, x + tapa[0] * U, y + tapa[1] * U], fill=piel)
    h = (1.2 + 9 * abre) * U
    if abre < 0.08:
        d.arc([x - w / 2, y - 3 * U, x + w / 2, y + 3 * U], 15, 165, fill=linea, width=max(2, int(1.5 * U)))
    else:
        d.ellipse([x - w / 2, y - h * 0.35, x + w / 2, y + h * 0.65], fill=interior, outline=linea, width=max(2, int(1.4 * U)))
        d.chord([x - w * 0.32, y + h * 0.15, x + w * 0.32, y + h * 0.62], 0, 180, fill=lengua)
    return im

# ---------------- escenas
class Escena:
    """Fondo rellenado + lista de piezas. dibujar(t) devuelve (fondo RGBA, capa de personajes RGBA)."""
    def __init__(self, k, cortes, lo=0.35, hi=0.6, cuerpo=(0.45, 0.7), mk=None):
        mk = mk or k
        self.a = np.asarray(img(k)).astype(np.float32); self.m = msk(mk, lo, hi); self.pz = {}
        hueco = np.zeros((SH, SW), np.float32); hbg = np.zeros((SH, SW), np.float32)
        sujeto = ndimage.binary_dilation(self.m > 0.08, iterations=int(5 * U)).astype(np.float32)
        relleno = ndimage.gaussian_filter((ndimage.binary_fill_holes(self.m > 0.5) if mk == k else self.m > 0.5).astype(np.float32), 0.8 * U)
        def alfa(pp, usa_mask, flt):
            al = pp * (relleno if usa_mask else 1.0)
            return al * flt[0](self.a) if flt else al
        for nombre, (pts, piv, usa_mask, *flt) in cortes.items():
            pp = poly(pts, 0.0); hbg = np.maximum(hbg, pp * sujeto if usa_mask else pp)
            al = alfa(pp, usa_mask, flt)                                    # corte duro (para el cuerpo)
            pe = ndimage.maximum_filter(pp, size=int(18 * U))                # la pieza solapa un poco bajo su borde
            self.pz[nombre] = Pieza(self.a, alfa(pe, usa_mask, flt), piv); hueco = np.maximum(hueco, al if usa_mask else pp); hbg = np.maximum(hbg, al)
        if cuerpo:                                   # resto del personaje, fijo (para que la silueta lo cubra entero)
            mc = msk(mk, *cuerpo[:2])
            if mk == k: mc = np.maximum(mc, ndimage.binary_fill_holes(mc > 0.5) * 1.0)
            if len(cuerpo) > 2: mc = mc * cuerpo[2](self.a)
            al = np.clip(mc * (1 - hueco), 0, 1)   # cortes duros y complementarios: sin costuras
            if al.max() > 0.1: self.pz["cuerpo"] = Pieza(self.a, al, (0, 0))
            hbg = np.maximum(hbg, ndimage.binary_dilation(mc > 0.05, iterations=int(3 * U)).astype(np.float32))
        dil = ndimage.maximum_filter(hbg, size=int(4 * U))   # el fondo se queda sin el personaje entero
        self.bg = Image.fromarray(np.clip(rellenar(self.a, dil), 0, 255).astype(np.uint8)).convert("RGBA")

def capa(): return Image.new("RGBA", (SW, SH), (0, 0, 0, 0))

def mezcla_sil(c, q):
    """Personajes: silueta negra -> color (q=0 silueta, 1 color)."""
    if q >= 0.999: return c
    s = silueta(c); return Image.blend(s, c, q) if q > 0 else s

# --- 01 China
E01 = Escena("01", {"cabeza": ([(455, 0), (835, 0), (835, 215), (700, 236), (610, 242), (455, 220)], (640, 226), True)}, cuerpo=(0.4, 0.6), mk="01_dragon")
def china(t):
    lt = t - T0["china"]; e = E01; c = capa(); e.pz["cuerpo"].dibujar(c)
    rot = 4 * math.sin(lt * 5.5) * (1 - 0.5 * eio(lt / 0.8)); dy = -4 * eout(lt / 0.5) + 1.5 * math.sin(lt * 7)
    e.pz["cabeza"].dibujar(c, 0, dy, rot)
    return e.bg, c, dict(cx=0.5, cy=0.42, z=lerp(1.06, 1.11, eio(lt / 1.0)), sil=(0.12, 0.38))
# --- 02 Europa
def _limpia(r, minimo):
    lab, n = ndimage.label(r); sz = ndimage.sum(r, lab, range(1, n + 1))
    return np.isin(lab, [i + 1 for i, v in enumerate(sz) if v > minimo])
def rojo(a, oro=False):
    r = a[..., 0] - np.maximum(a[..., 1], a[..., 2]) > 22
    if oro: r |= (a[..., 0] > 150) & (a[..., 1] > 95) & (a[..., 2] < 120) & (a[..., 0] - a[..., 2] > 60)
    r = ndimage.binary_opening(r, iterations=2)
    cielo = ((a[..., 2] > a[..., 0] + 30) & (a[..., 2] >= a[..., 1])) | (a.min(2) > 195)
    oscuro = ~cielo & ndimage.binary_dilation(r, iterations=int(9 * U))     # contorno y garras junto al rojo
    yy = np.arange(a.shape[0])[:, None] < 230 * U
    r = _limpia(r | oscuro | (yy & ~cielo & (a.max(2) < 235)), 1500 * U * U)
    r = ndimage.binary_closing(r, iterations=2); r = ndimage.binary_dilation(r, iterations=1)
    return ndimage.gaussian_filter(r.astype(np.float32), 0.7)
def rojo_oro(a): return rojo(a, True)
E02 = Escena("02", {"ala_i": ([(0, 0), (505, 0), (512, 140), (585, 150), (590, 222), (540, 240), (470, 300), (400, 430), (0, 430)], (575, 218), True, rojo),
                    "ala_d": ([(720, 0), (1280, 0), (1280, 430), (1060, 430), (900, 330), (820, 250), (760, 232), (720, 225)], (700, 225), True, rojo),
                    "cabeza": ([(515, 10), (665, 10), (670, 210), (600, 232), (520, 205)], (602, 222), True)}, cuerpo=(0.45, 0.7, rojo_oro))
def europa(t):
    lt = t - T0["europa"]; e = E02; c = capa()
    f = math.sin(lt * 2 * math.pi * 2.6)
    e.pz["ala_i"].dibujar(c, 0, 0, -9 * f, 1, 1 - 0.07 * abs(f)); e.pz["ala_d"].dibujar(c, 0, 0, 9 * f, 1, 1 - 0.07 * abs(f))
    e.pz["cuerpo"].dibujar(c, 0, 0, 0, 1, 1 + 0.008 * math.sin(lt * 9))
    e.pz["cabeza"].dibujar(c, 0, -3 * eout(lt / 0.4), -5 * eout(lt / 0.35) + 2 * math.sin(lt * 6))
    return e.bg, c, dict(cx=0.5, cy=0.40, z=lerp(1.05, 1.10, eio(lt / 0.9)), sil=(0.15, 0.38))
# --- 03 México
E03 = Escena("03", {"cabeza": ([(435, 15), (700, 15), (745, 150), (690, 235), (575, 262), (440, 205)], (580, 250), True)}, cuerpo=(0.4, 0.6), mk="03_dragon")
def mexico(t):
    lt = t - T0["mexico"]; e = E03; c = capa(); e.pz["cuerpo"].dibujar(c)
    e.pz["cabeza"].dibujar(c, 3 * math.sin(lt * 4), -5 * eout(lt / 0.45), 6 * math.sin(lt * 4.2 + 0.6))
    return e.bg, c, dict(cx=0.5, cy=0.42, z=lerp(1.05, 1.10, eio(lt / 0.9)), sil=(0.15, 0.38))
# --- 04 Australia
E04 = Escena("04", {"cabeza": ([(330, 55), (470, 45), (565, 105), (565, 180), (470, 185), (330, 180)], (548, 150), True)}, cuerpo=(0.4, 0.6), mk="04_dragon")
def australia(t):
    lt = t - T0["australia"]; e = E04; c = capa(); e.pz["cuerpo"].dibujar(c)
    pz = e.pz["cabeza"]; im = pz.im
    sale = max(0.0, math.sin(cl((lt - 0.35) / 0.35) * math.pi))      # lengua bífida
    if sale > 0:
        im = im.copy(); d = ImageDraw.Draw(im); x, y = pz.loc(352, 113); L = 28 * U * sale
        d.line([x, y, x - L, y + 2 * U], fill=(170, 30, 40), width=int(2.4 * U))
        d.line([x - L, y + 2 * U, x - L - 7 * U * sale, y - 3 * U], fill=(170, 30, 40), width=int(2 * U))
        d.line([x - L, y + 2 * U, x - L - 7 * U * sale, y + 7 * U], fill=(170, 30, 40), width=int(2 * U))
    pz.dibujar(c, -6 * eout(lt / 0.4) + 2 * math.sin(lt * 5), -4 * math.sin(lt * 3.2), -4 * math.sin(lt * 4.4), im=im)
    return e.bg, c, dict(cx=0.48, cy=0.45, z=lerp(1.05, 1.10, eio(lt / 0.9)), sil=(0.15, 0.38))
# --- 05 Gag: los tres sabios
SAB = {"egi": dict(cab=[(290, 135), (440, 135), (445, 290), (380, 275), (300, 292)], piv=(372, 262), ojos=[(372, 204, 8, 9), (399, 202, 8, 9)],
                   piel=(215, 160, 112), boca=(392, 236, 13), tapa=(8, 5)),
       "mon": dict(cab=[(538, 140), (655, 140), (660, 232), (600, 250), (540, 236)], piv=(600, 240), ojos=[(596, 188, 9, 10), (622, 186, 9, 10)],
                   piel=(228, 172, 130), boca=(621, 219, 16), tapa=(10, 7)),
       "chi": dict(cab=[(820, 135), (945, 135), (945, 260), (900, 300), (845, 300), (820, 260)], piv=(872, 262), ojos=[(849, 198, 8, 8), (874, 202, 8, 8)],
                   piel=(222, 170, 130), boca=(853, 234, 11), tapa=(7, 4))}
cortes05 = {n: (s["cab"], s["piv"], True) for n, s in SAB.items()}
cortes05["brazo"] = ([(660, 22), (756, 22), (762, 110), (760, 205), (752, 236), (716, 262), (690, 250), (700, 205), (712, 165), (722, 156), (662, 156)], (712, 242), True)
E05 = Escena("05", cortes05)
DIAL = {"egi": (7.55, 8.45), "mon": (8.5, 9.35), "chi": (10.05, 11.25)}   # quién «dice» cada frase
def gag(t):
    lt = t - T0["gag"]; e = E05; c = capa(); e.pz["cuerpo"].dibujar(c)
    # brazo del monje: busca cobertura en «No había WhatsApp»
    q = cl((t - 10.0) / 0.4); rb = 6 * math.sin(t * 9) * q + (-3 * eout((t - 8.55) / 0.3) if t < 10 else -3)
    e.pz["brazo"].dibujar(c, 0, -10 * eout(q) + 2 * math.sin(t * 3), rb)
    for n, s in SAB.items():
        pz = e.pz[n]
        if n == "egi": rot = keys(t, [(7.6, 0), (7.9, -7), (8.5, -7), (8.8, 0), (10.1, 0), (10.4, 5)])
        elif n == "chi": rot = keys(t, [(7.6, 0), (7.95, 7), (8.5, 7), (8.8, 0), (10.1, 0), (10.4, -4)])
        else: rot = 6 * math.sin((t - 8.6) * 18) * math.exp(-max(0, t - 8.6) * 2.5) if t > 8.6 else 0
        rot += 1.2 * math.sin(t * 2 + len(n))
        im = pz.im
        a, b = DIAL[n]; ab = BOCA.abierta(t, a, b)
        if n == "mon" and 8.55 <= t < 9.6: ab = max(ab, 0.55)               # «¡Imposible!» boca de susto
        im = boca(im, pz, *s["boca"], ab, s["piel"], s["tapa"])
        cerr = parpadeo(t, sum(map(ord, n)), 2.2)
        im = parpado(im, pz, s["ojos"], cerr, s["piel"])
        pz.dibujar(c, 0, -1.5 * abs(math.sin(t * 2.2 + len(n))), rot, im=im)
    z = lerp(1.03, 1.09, eio(lt / 3.8)); cy = keys(t, [(9.9, 0.45), (10.5, 0.36)])
    return e.bg, c, dict(cx=0.5, cy=cy, z=z, sil=None)
# --- 06 Final
def interr_f(a):
    r = (((a[..., 2] - a[..., 1]) < 34) | (a[..., 2] < 200)) & (a[..., 2] > a[..., 0] + 40)
    r = _limpia(ndimage.binary_opening(r, iterations=1), 300 * U * U)
    return ndimage.gaussian_filter(ndimage.binary_dilation(r, iterations=1).astype(np.float32), 0.7)
def sin_interr(a):
    q = interr_f(a); q[int(185 * U):] = 0; return 1 - q
# --- el dragón del globo pregunta
E06 = Escena("06", {"cola": ([(735, 480), (960, 480), (960, 690), (735, 690)], (760, 640), True),
                    "garra_i": ([(434, 296), (458, 276), (500, 272), (534, 284), (538, 314), (508, 334), (460, 348), (434, 338)], (520, 318), True),
                    "garra_d": ([(726, 296), (762, 284), (806, 296), (828, 340), (828, 380), (800, 382), (758, 364), (730, 330)], (742, 320), True),
                    "cabeza": ([(532, 118), (830, 118), (838, 296), (770, 318), (690, 330), (640, 340), (578, 334), (538, 318)], (640, 330), True, sin_interr),
                    "interr": ([(560, 0), (730, 0), (730, 172), (560, 172)], (646, 150), False, interr_f)})
def final(t):
    lt = t - T0["final"]; e = E06; c = capa()
    # cola: onda que viaja hacia la punta
    cola = e.pz["cola"]; ci, P = onda(cola.im, 7 * U, 160 * U, lt * 6, eje="y", taper=(1.0, 0.1))
    pegar(c, ci, (cola.lp[0] + P, cola.lp[1]), (cola.piv[0], cola.piv[1]), 0)
    e.pz["cuerpo"].dibujar(c)
    # garras: tamborilean en «Entonces…»
    for n, fase in (("garra_i", 0), ("garra_d", 1.7)):
        tam = max(0.0, math.sin(t * 13 + fase)) * (1 if 11.4 < t < 12.3 else 0.25)
        e.pz[n].dibujar(c, 0, -4 * tam, 0)
    # cabeza: inclina en «¿de dónde…?», habla, parpadea
    pz = e.pz["cabeza"]
    rot = keys(t, [(11.5, 0), (11.9, 3), (12.4, 3), (12.8, -6), (13.7, -6), (14.1, -2)]) + 1.0 * math.sin(t * 2.4)
    ab = BOCA.abierta(t, 11.3, 13.9)
    im = boca(pz.im, pz, 657, 299, 36, ab * 1.25, (86, 160, 120), tapa=None, linea=(25, 60, 40), interior=(70, 25, 30))
    cerr = max(min(1.0, 2.2 * (1 - abs(2 * (t - b) / 0.16 - 1))) if 0 <= t - b < 0.16 else 0.0 for b in (12.02, 13.82))
    im = parpado(im, pz, [(652, 264, 22, 19), (566, 260, 9, 17)], cerr, (112, 170, 128), linea=(20, 45, 30))
    pz.dibujar(c, 0, -2 * math.sin(t * 2.4), rot, im=im)
    # interrogación: aparece con rebote en «¿de dónde», bota y se balancea
    iq = e.pz["interr"]; s_ = back(cl((t - 12.38) / 0.35), 2.5) if t >= 12.38 else 0.0
    if s_ > 0: iq.dibujar(c, 0, -6 * abs(math.sin(t * 4)), 8 * math.sin(t * 3), s_, s_)
    z = lerp(1.02, 1.08, eio(lt / 3.4))
    return e.bg, c, dict(cx=0.5, cy=0.43, z=z, sil=None)

PLANOS = [("china", china), ("europa", europa), ("mexico", mexico), ("australia", australia)]

# ---------------- mosaico: los cuatro planos vivos en 2x2, entran uno a uno y al final todos a silueta -> color
def mosaico(t):
    """Zoom hacia atrás: empieza con Australia a pantalla completa (continúa del plano anterior) y la cámara
    se aleja hasta descubrir las 4 escenas ya colocadas en 2x2. Nunca hay fondo vacío."""
    lt = t - T0["mosaico"]
    R = 2                                                    # la rejilla se compone al doble para que el zoom no pierda detalle
    g_ = 12; tw, th = (W - 3 * g_) // 2, (H - 3 * g_) // 2
    q = eio(lt / 0.85)                                       # 0: Australia llena la pantalla, 1: rejilla completa
    flash = cl((t - 5.55) / 0.12) * (1 - cl((t - 6.35) / 0.35))   # «dibujaron lo mismo»: todos a silueta
    cv = Image.new("RGB", (W * R, H * R), (16, 20, 28))
    for i, (nom, fn) in enumerate(PLANOS):
        tl = (t if nom == "australia" else T0[nom] + 0.5 + lt * 0.6)   # cada escena sigue viva
        if nom == "australia": tl = T0["australia"] + 0.75 + lt * 0.6
        bg, ch, cam = fn(tl)
        fr = componer(bg, ch, cam, tl - T0[nom], tw * R, th * R, sil_override=1 - flash)
        x = g_ + (i % 2) * (tw + g_); y = g_ + (i // 2) * (th + g_)
        cv.paste(fr, (x * R, y * R))
    # cámara: del hueco de Australia (abajo a la derecha) a la rejilla entera
    ax, ay = g_ + tw + g_ + tw / 2, g_ + th + g_ + th / 2
    z = lerp(W / tw, 1.0, q); cx = lerp(ax, W / 2, q); cy = lerp(ay, H / 2, q)
    vw, vh = W / z, H / z; x0 = cl(cx - vw / 2, 0, W - vw); y0 = cl(cy - vh / 2, 0, H - vh)
    return cv.resize((W, H), Image.LANCZOS, box=(x0 * R, y0 * R, (x0 + vw) * R, (y0 + vh) * R))

def componer(bg, ch, cam, lt, ow=W, oh=H, sil_override=None):
    q = 1.0
    if cam.get("sil"):
        a, d = cam["sil"]; q = eio((lt - a) / d)
    if sil_override is not None: q = min(q, sil_override)
    ch = mezcla_sil(ch, q)
    z = cam["z"]; vw, vh = SW / z, SH / z
    x0 = cl(cam["cx"] * SW - vw / 2, 0, SW - vw); y0 = cl(cam["cy"] * SH - vh / 2, 0, SH - vh)
    # parallax: el fondo se mueve un 85 % de lo que se mueve la cámara
    bz = 1 + (z - 1) * 0.85; bvw, bvh = SW / bz, SH / bz
    bx0 = cl(cam["cx"] * SW - bvw / 2, 0, SW - bvw); by0 = cl(cam["cy"] * SH - bvh / 2, 0, SH - bvh)
    f = bg.resize((ow, oh), Image.BICUBIC, box=(bx0, by0, bx0 + bvw, by0 + bvh))
    f.alpha_composite(ch.resize((ow, oh), Image.BICUBIC, box=(x0, y0, x0 + vw, y0 + vh)))
    return f.convert("RGB")

# ---------------- «¡un dragón!»: el dragón rojo ruge con llamarada, cámara que empuja y tiembla
rngF = np.random.default_rng(3); FUEGO = rngF.random((160, 4))
def dragon(t):
    lt = t - T0["dragon"]; e = E02; c = capa()
    f = math.sin(lt * 2 * math.pi * 3.2)
    e.pz["ala_i"].dibujar(c, 0, 0, -14 * f, 1, 1 - 0.1 * abs(f)); e.pz["ala_d"].dibujar(c, 0, 0, 14 * f, 1, 1 - 0.1 * abs(f))
    e.pz["cuerpo"].dibujar(c)
    e.pz["cabeza"].dibujar(c, -5 * eout(lt / 0.2), 3 * eout(lt / 0.2), -6 * eout(lt / 0.18) + 2 * math.sin(lt * 30) * (1 - cl(lt / 0.7)))
    # llamarada desde la boca (560, 198 en diseño), que sigue el giro de la cabeza, hacia abajo-izquierda
    rc = -6 * eout(lt / 0.18) + 2 * math.sin(lt * 30) * (1 - cl(lt / 0.7)); r = math.radians(rc)
    mx, my = 560 - 602, 198 - 222; ox = (602 - 5 * eout(lt / 0.2) + mx * math.cos(r) - my * math.sin(r)) * U; oy = (222 + 3 * eout(lt / 0.2) + mx * math.sin(r) + my * math.cos(r)) * U
    pot = eout(cl((lt - 0.05) / 0.12)) * (1 - cl((lt - 0.62) / 0.2))
    if pot > 0:
        for capa_, (esc, col, al_) in enumerate([(1.0, (230, 70, 30), 170), (0.7, (255, 150, 40), 200), (0.4, (255, 235, 150), 230)]):
            fu = capa(); d = ImageDraw.Draw(fu)
            for x, y, s_, v in FUEGO:
                k = ((lt * (1.8 + v)) + x) % 1.0; dist = k * 300 * U * pot
                px = ox - dist * 0.80 + (y - 0.5) * 60 * U * k; py = oy + dist * 0.60 + (s_ - 0.5) * 40 * U * k
                rr = (6 + 34 * k) * U * esc * pot
                d.ellipse([px - rr, py - rr, px + rr, py + rr], fill=col + (int(al_ * (1 - k) ** 0.7),))
            c.alpha_composite(fu.filter(ImageFilter.GaussianBlur(1.6 * U)))
    sh = 7 * math.sin(lt * 70) * (1 - cl(lt / 0.5))
    return e.bg, c, dict(cx=0.47 + sh / 2000, cy=0.30, z=lerp(1.35, 1.55, eout(lt / 0.8)), sil=None)

def frame(t):
    if t < T0["mosaico"]:
        for nom, fn in PLANOS:
            if T0[nom] <= t < T1[nom]:
                bg, ch, cam = fn(t); return componer(bg, ch, cam, t - T0[nom])
    if t < T0["dragon"]: return mosaico(t)
    if t < T0["gag"]: bg, ch, cam = dragon(t); return componer(bg, ch, cam, t - T0["dragon"])
    if t < T0["final"]: bg, ch, cam = gag(t); return componer(bg, ch, cam, t - T0["gag"])
    bg, ch, cam = final(t); img_ = componer(bg, ch, cam, t - T0["final"])
    if t > FIN - 0.5: img_ = Image.blend(img_, Image.new("RGB", (W, H)), cl((t - (FIN - 0.5)) / 0.5) * 0.0)
    return img_

def render(a, b, out):
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-preset", "medium", "-crf", "16", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
    for i in range(int(a * FPS), int(b * FPS)):
        p.stdin.write(vineta(frame(i / FPS), 0.18).tobytes())
    p.stdin.close(); p.wait()

if __name__ == "__main__":
    if sys.argv[1] == "hoja":
        ts = [float(x) for x in sys.argv[2].split(",")]; cols = 4; w, h = 640, 360
        S = Image.new("RGB", (cols * w, ((len(ts) + cols - 1) // cols) * (h + 20)), "white"); d = ImageDraw.Draw(S)
        for i, t in enumerate(ts):
            x, y = (i % cols) * w, (i // cols) * (h + 20); S.paste(frame(t).resize((w, h)), (x, y)); d.text((x + 4, y + h + 3), f"{t:.2f}", fill="black")
        S.save(sys.argv[3], quality=88); print("ok", sys.argv[3])
    else:
        render(float(sys.argv[1]), float(sys.argv[2]), sys.argv[3]); print("ok", sys.argv[3])
