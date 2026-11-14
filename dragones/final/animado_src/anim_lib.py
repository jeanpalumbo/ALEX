# Motor de animación por recortes (cut-out) en Python: piezas RGBA con pivote, transformaciones afines,
# ondulación de cuerpos de serpiente, parpadeo, bocas sincronizadas con la voz, silueta->color y cámara con parallax.
import math, json, numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage

W, H, FPS = 1920, 1080, 30

# ---------------- easing
def cl(x, a=0.0, b=1.0): return max(a, min(b, x))
def eio(x): x = cl(x); return 3 * x * x - 2 * x ** 3
def eout(x): x = cl(x); return 1 - (1 - x) ** 4
def ein(x): x = cl(x); return x ** 3
def back(x, s=1.8): x = cl(x) - 1; return 1 + (s + 1) * x ** 3 + s * x ** 2
def lerp(a, b, x): return a + (b - a) * x
def keys(t, ks, ease=eio):
    """Interpola una lista de claves [(t, valor), ...] con easing entre cada par."""
    if t <= ks[0][0]: return ks[0][1]
    for (t0, v0), (t1, v1) in zip(ks, ks[1:]):
        if t < t1:
            x = ease((t - t0) / (t1 - t0))
            return tuple(lerp(a, b, x) for a, b in zip(v0, v1)) if isinstance(v0, tuple) else lerp(v0, v1, x)
    return ks[-1][1]

# ---------------- piezas
def recortar_blanco(im, th=238, borde=1):
    """Quita el fondo blanco liso conectado al borde (los blancos interiores, como ojos, se quedan)."""
    a = np.asarray(im.convert("RGB")).astype(np.int16)
    claro = (a.min(2) >= th) & ((a.max(2) - a.min(2)) < 18)
    lab, n = ndimage.label(claro)
    bordes = set(np.unique(np.r_[lab[0], lab[-1], lab[:, 0], lab[:, -1]])) - {0}
    fondo = np.isin(lab, list(bordes))
    m = ~fondo
    m = ndimage.binary_opening(m, iterations=1)
    lab2, n2 = ndimage.label(m)
    if n2 > 1:                                            # fuera motas sueltas
        s = ndimage.sum(m, lab2, range(1, n2 + 1)); keep = np.isin(lab2, [i + 1 for i, v in enumerate(s) if v > 0.002 * m.size])
        m &= keep
    if borde: m = ndimage.binary_erosion(m, iterations=borde)
    alpha = Image.fromarray((m * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.8))
    out = im.convert("RGBA"); out.putalpha(alpha)
    return out

def recortar_bbox(im, pad=4):
    bb = im.getchannel("A").point(lambda v: 255 if v > 8 else 0).getbbox()
    if not bb: return im, (0, 0)
    x0, y0, x1, y1 = bb; x0, y0 = max(0, x0 - pad), max(0, y0 - pad); x1, y1 = min(im.width, x1 + pad), min(im.height, y1 + pad)
    return im.crop((x0, y0, x1, y1)), (x0, y0)

def pieza(path, escala=1.0, th=238):
    im = Image.open(path).convert("RGB")
    p, _ = recortar_bbox(recortar_blanco(im, th))
    if escala != 1.0: p = p.resize((max(1, int(p.width * escala)), max(1, int(p.height * escala))), Image.LANCZOS)
    return p

def piezas_en_fila(path, n, escala=1.0, th=238):
    """Hoja con n piezas en fila (p. ej. 3 cabezas): devuelve las n piezas de izquierda a derecha."""
    im = recortar_blanco(Image.open(path).convert("RGB"), th)
    a = np.asarray(im.getchannel("A")) > 8
    lab, k = ndimage.label(ndimage.binary_dilation(a, iterations=6))
    objs = ndimage.find_objects(lab)
    sizes = [(ndimage.sum(a, lab, i + 1), i) for i in range(k)]
    top = sorted([i for _, i in sorted(sizes, reverse=True)[:n]], key=lambda i: objs[i][1].start)
    out = []
    for i in top:
        sl = objs[i]; c = im.crop((sl[1].start, sl[0].start, sl[1].stop, sl[0].stop))
        msk = Image.fromarray(((lab[sl] == i + 1) * 255).astype(np.uint8))
        c.putalpha(Image.fromarray(np.minimum(np.asarray(c.getchannel("A")), np.asarray(msk))))
        if escala != 1.0: c = c.resize((int(c.width * escala), int(c.height * escala)), Image.LANCZOS)
        out.append(c)
    return out

def igualar(piezas_):
    """Pone varias piezas (variantes de una cabeza) en el mismo lienzo, alineadas por el centro inferior."""
    w = max(p.width for p in piezas_); h = max(p.height for p in piezas_)
    res = []
    for p in piezas_:
        c = Image.new("RGBA", (w, h), (0, 0, 0, 0)); c.alpha_composite(p, ((w - p.width) // 2, h - p.height)); res.append(c)
    return res

def silueta(p, col=(12, 14, 20)):
    s = Image.new("RGBA", p.size, col + (255,)); s.putalpha(p.getchannel("A")); return s

# ---------------- dibujo con transformación
def pegar(canvas, p, piv, pos, rot=0.0, sx=1.0, sy=1.0, alpha=1.0):
    """Pega la pieza p con su punto pivote piv (px de la pieza) en pos (px del lienzo), girada rot grados y escalada."""
    if alpha <= 0.003 or sx <= 0 or sy <= 0: return
    r = math.radians(rot); c, s = math.cos(r), math.sin(r)
    # matriz directa (pieza -> lienzo): pos + R*S*(q - piv)
    def fwd(x, y):
        dx, dy = (x - piv[0]) * sx, (y - piv[1]) * sy
        return pos[0] + c * dx - s * dy, pos[1] + s * dx + c * dy
    cs = [fwd(0, 0), fwd(p.width, 0), fwd(0, p.height), fwd(p.width, p.height)]
    x0, y0 = math.floor(min(x for x, _ in cs)), math.floor(min(y for _, y in cs))
    x1, y1 = math.ceil(max(x for x, _ in cs)), math.ceil(max(y for _, y in cs))
    if x1 < 0 or y1 < 0 or x0 > canvas.width or y0 > canvas.height: return
    ow, oh = x1 - x0, y1 - y0
    # inversa (lienzo local -> pieza)
    a, b = c / sx, s / sx; d, e = -s / sy, c / sy
    ox, oy = x0 - pos[0], y0 - pos[1]
    coef = (a, b, a * ox + b * oy + piv[0], d, e, d * ox + e * oy + piv[1])
    t = p.transform((ow, oh), Image.AFFINE, coef, resample=Image.BICUBIC)
    if alpha < 1: t.putalpha(t.getchannel("A").point(lambda v: int(v * alpha)))
    canvas.alpha_composite(t, (x0, y0)) if x0 >= 0 and y0 >= 0 and x1 <= canvas.width and y1 <= canvas.height else _pegar_recortado(canvas, t, x0, y0)

def _pegar_recortado(canvas, t, x0, y0):
    cx0, cy0 = max(0, -x0), max(0, -y0)
    cx1, cy1 = min(t.width, canvas.width - x0), min(t.height, canvas.height - y0)
    if cx1 <= cx0 or cy1 <= cy0: return
    canvas.alpha_composite(t.crop((cx0, cy0, cx1, cy1)), (x0 + cx0, y0 + cy0))

# ---------------- ondulación (serpientes, colas)
def onda(p, amp, lam, fase, eje="x", taper=(0.0, 1.0), extra=None):
    """Desplaza cada columna (eje x) o fila (eje y) con una onda senoidal que viaja: cuerpo de serpiente vivo.
    taper: (amplitud relativa en el inicio, en el final) a lo largo del eje. extra(u) -> desplazamiento adicional."""
    a = np.asarray(p).astype(np.float32)
    h, w = a.shape[:2]; P = int(abs(amp) * 1.2 + 4)
    if eje == "x":
        a = np.pad(a, ((P, P), (0, 0), (0, 0))); hh = h + 2 * P
        u = np.arange(w) / max(1, w - 1); env = taper[0] + (taper[1] - taper[0]) * u
        d = amp * env * np.sin(2 * math.pi * np.arange(w) / lam - fase)
        if extra is not None: d = d + extra(u)
        yy, xx = np.mgrid[0:hh, 0:w].astype(np.float32); yy = yy - d[None, :]
    else:
        a = np.pad(a, ((0, 0), (P, P), (0, 0))); ww = w + 2 * P
        u = np.arange(h) / max(1, h - 1); env = taper[0] + (taper[1] - taper[0]) * u
        d = amp * env * np.sin(2 * math.pi * np.arange(h) / lam - fase)
        if extra is not None: d = d + extra(u)
        yy, xx = np.mgrid[0:h, 0:ww].astype(np.float32); xx = xx - d[:, None]
    out = np.stack([ndimage.map_coordinates(a[..., k], [yy, xx], order=1, mode="constant") for k in range(4)], -1)
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8), "RGBA"), P

# ---------------- voz: envolvente para la boca
class Boca:
    def __init__(self, wav, palabras):
        import soundfile as sf
        v, sr = sf.read(wav, dtype="float32")
        if v.ndim > 1: v = v.mean(1)
        hop = sr // 60; n = len(v) // hop
        e = np.sqrt(np.mean(v[: n * hop].reshape(n, hop) ** 2, 1))
        self.e = np.convolve(e, np.ones(3) / 3, "same") / (np.percentile(e, 97) + 1e-9); self.hop = 60
        self.P = palabras
    def abierta(self, t, desde=-1e9, hasta=1e9):
        """0..1 cuánto abre la boca en t (solo dentro de [desde, hasta) y si hay palabra)."""
        if not (desde <= t < hasta): return 0.0
        if not any(w["t"] - 0.03 <= t < w["e"] + 0.02 for w in self.P): return 0.0
        i = int(t * self.hop)
        return cl((self.e[i] if i < len(self.e) else 0) * 1.3 - 0.15)

def parpadeo(t, semilla=0, cada=2.6):
    """True si los ojos están cerrados en t (parpadeos de 0,12 s con intervalos irregulares)."""
    rng = np.random.default_rng(semilla); ts, x = [], 0.3 + rng.random() * cada
    while x < 400: ts.append(x); x += cada * (0.6 + 0.8 * rng.random())
    v = 0.0
    for b in ts:
        x = (t - b) / 0.16
        if 0 <= x < 1: v = max(v, min(1.0, 2.2 * (1 - abs(2 * x - 1))))   # cierra, aguanta un instante y abre
    return v

# ---------------- fondo con cámara
def fondo_cam(bg, cx, cy, z, ow=W, oh=H):
    """Recorta del fondo (cualquier tamaño, 16:9) una ventana centrada en (cx, cy) fracciones, con zoom z>=1."""
    bw, bh = bg.size; vw, vh = bw / z, bh / z
    x0 = cl(cx * bw - vw / 2, 0, bw - vw); y0 = cl(cy * bh - vh / 2, 0, bh - vh)
    return bg.resize((ow, oh), Image.BICUBIC, box=(x0, y0, x0 + vw, y0 + vh))

def vineta(img, k=0.22):
    global _VIG
    try: _VIG
    except NameError:
        yy, xx = np.mgrid[0:H, 0:W]; r = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
        _VIG = Image.fromarray((np.clip(1 - k * np.clip(r - 0.55, 0, 1) ** 1.6, 0, 1) * 255).astype(np.uint8))
    z = Image.new("RGB", img.size, (0, 0, 0)); return Image.composite(img, z, _VIG)
