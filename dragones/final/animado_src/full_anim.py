# Vídeo completo de dragones animado por recortes (cut-out), 1920x1080 30 fps, 5:02.
# - Gancho (0-14,2 s): el de la muestra (gancho_anim.py).
# - Planos 07-55: cada imagen se separa en fondo rellenado + personaje (rembg) + piezas con pivote (RIG),
#   el personaje respira y se balancea sobre su fondo (parallax), las serpientes ondulan, los personajes parpadean,
#   silueta->color en la primera aparición de cada dragón, partículas, cámara viva, barrido entre secciones,
#   punch-in en los chistes. El plano 55 es el dragón del globo diciendo el cierre (boca sincronizada).
# Uso: python full_anim.py a b salida.mp4      (segundos)      |  python full_anim.py todo   (10 procesos + concat)
#      python full_anim.py hoja t1,t2,... salida.jpg
import os, sys, math, json, subprocess, numpy as np
from PIL import Image, ImageDraw, ImageFilter
AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(AQUI)); sys.path.insert(0, AQUI)
import render_full as RF                      # partículas, hblur, info de máscaras (cambia el cwd a dragones/)
os.chdir(AQUI)
import gancho_anim as G                       # motor cut-out + escenas del gancho (cwd = animado/)
from anim_lib import cl, eio, eout, ein, back, lerp, keys, pegar, onda, parpadeo, vineta
from rig_full import RIG                      # piezas a mano por imagen (cabezas, ojos, alas...)
W, H, FPS, U = G.W, G.H, G.FPS, G.U

# --- imágenes y máscaras de img_full
_img0, _msk0 = G.img, G.msk
def img(k):
    f = f"../img_full/{k}.png"
    return Image.open(f).convert("RGB").resize((G.SW, G.SH), Image.LANCZOS) if os.path.exists(f) else _img0(k)
def msk(k, lo=0.35, hi=0.6):
    if os.path.exists(f"mask/{k}.png"): return _msk0(k, lo, hi)
    m = np.asarray(Image.open(f"../img_full/mask/{k}.png").convert("L").resize((G.SW, G.SH), Image.LANCZOS)).astype(np.float32) / 255
    return np.clip((m - lo) / (hi - lo), 0, 1)
G.img, G.msk = img, msk

P = json.load(open("../full/planos.json", encoding="utf-8"))
FR = json.load(open("../full/frases.json", encoding="utf-8"))
import soundfile as sf
TOTAL = round(sf.info("../full/vo.wav").duration, 3)
LEAD = 0.12
INFO = json.load(open("../img_full/mask/info.json"))
TIPO = {**{k: "criatura" for k in "07 08 09 26 28 29 37 42 43 46".split()},
        **{k: "personaje" for k in "14 15 17 19 20 24 30 31 35 49 52 53 54".split()},
        **{k: "objeto" for k in "23 32 38 40 48".split()}}
ONDA = {"07", "08", "29", "37", "46"}                                  # cuerpos de serpiente que ondulan
DRAGONES = {"08", "09", "11", "26", "29", "37", "43", "46"}
CHISTE = {"09": -1, "22": -1, "27": 0, "33": -1, "40": -1, "42": 0, "47": -1, "51": -1, "54": -1}
FX = RF.FX

# --- planos (como render_full: los de >6,5 s se parten en dos encuadres)
shots = []
for i, p in enumerate(P):
    if p["sec"] == 1: continue
    t0 = max(0.0, p["t0"] - LEAD); t1 = TOTAL if i == len(P) - 1 else P[i + 1]["t0"] - LEAD
    fr = [f for f in FR if f["plano"] == p["n"]]
    base = dict(n=p["n"], img=p["img"], sec=p["sec"], t0=t0, t1=t1, reuso=p["img"] != p["n"], frases=fr, parte=0)
    if t1 - t0 > 6.5 and len(fr) > 1:
        mid = (t0 + t1) / 2; cut = min(fr[1:], key=lambda f: abs(f["t0"] - mid))["t0"] - LEAD
        if 2.2 < cut - t0 and 2.2 < t1 - cut:
            shots.append(dict(base, t1=cut)); shots.append(dict(base, t0=cut, parte=1, reuso=True)); continue
    shots.append(base)
for i, s in enumerate(shots):
    s["i"] = i; s["sec_ini"] = i == 0 or shots[i - 1]["sec"] != s["sec"]; s["sec_fin"] = i < len(shots) - 1 and shots[i + 1]["sec"] != s["sec"]
T_GANCHO = shots[0]["t0"]

# --- escenas (perezosas, con caché pequeña por proceso)
_CACHE = {}
def escena(k):
    if k in _CACHE: return _CACHE[k]
    if len(_CACHE) >= 3: _CACHE.pop(next(iter(_CACHE)))
    r = RIG.get(k, {})
    import pickle, hashlib
    clave = hashlib.md5(repr((sorted((n, v[:3]) for n, v in r.get("piezas", {}).items()), r.get("cuerpo"), r.get("mk"), r.get("agua"), r.get("agua_y"), r.get("borrar"), r.get("nubes", True), "v3",
                              [getattr(v[3], "__name__", "") for v in r.get("piezas", {}).values() if len(v) > 3])).encode()).hexdigest()[:10]
    fc = f"cache/{k}_{clave}.pkl"
    if os.path.exists(fc):
        e = pickle.load(open(fc, "rb")); _CACHE[k] = e; return e
    cortes = {n: tuple(v) for n, v in r.get("piezas", {}).items()}
    e = G.Escena(k, cortes, cuerpo=tuple(r.get("cuerpo", (0.45, 0.7))), mk=r.get("mk"))
    inf = INFO.get(k, {"bbox": [0, 0, 1280, 720], "c": [640, 360]})
    x0, y0, x1, y1 = inf["bbox"]
    if "cuerpo" in e.pz:                                         # pivote del cuerpo: abajo en el centro del sujeto
        pz = e.pz["cuerpo"]; pz.piv = (((x0 + x1) / 2) * U, y1 * U); pz.lp = (pz.piv[0] - pz.x0, pz.piv[1] - pz.y0)
    if r.get("borrar"):                                          # zonas del fondo que se rellenan (p. ej. el humo fijo)
        hz = np.zeros((G.SH, G.SW), np.float32)
        for pol in r["borrar"]: hz = np.maximum(hz, G.poly(pol, 3.0))
        b = np.asarray(e.bg.convert("RGB")).astype(np.float32)
        e.bg = Image.fromarray(np.clip(G.rellenar(b, hz), 0, 255).astype(np.uint8)).convert("RGBA")
    e.nubes = None; e.agua_m = None
    if r.get("agua") == "auto" and e.a is not None:
        from scipy import ndimage
        x = e.a / 255.0; mx = x.max(2); mn = x.min(2); d = np.maximum(mx - mn, 1e-6); rr, gg, bb = x[..., 0], x[..., 1], x[..., 2]
        h = np.where(mx == rr, ((gg - bb) / d) % 6, np.where(mx == gg, (bb - rr) / d + 2, (rr - gg) / d + 4)) * 60
        w = (h > 172) & (h < 222) & ((mx - mn) / np.maximum(mx, 1e-6) > 0.3) & (mx > 0.3)
        w[: int(G.SH * r.get("agua_y", 0.38))] = False
        if e.m is not None: w &= ~(e.m > 0.3)
        w = G._limpia(ndimage.binary_opening(w, iterations=2), 6000 * U * U)
        e.agua_m = ndimage.gaussian_filter(w.astype(np.float32), 2 * U)
    if r.get("nubes", True) and e.a is not None: e.nubes = extraer_nubes(e)
    e.a = None; e.m = None                                       # libera memoria
    os.makedirs("cache", exist_ok=True); pickle.dump(e, open(fc, "wb"))
    _CACHE[k] = e; return e

def extraer_nubes(e):
    """Separa las nubes (blancas, poco saturadas, que tocan cielo) en una capa que se desplaza; el fondo queda con cielo."""
    from scipy import ndimage
    a = e.a; mn = a.min(2); mx = a.max(2); sub = ndimage.binary_dilation(e.m > 0.1, iterations=int(6 * U)) if e.m is not None else False
    cielo = (a[..., 2] > a[..., 0] + 40) & (a[..., 2] > 150) & (mx - mn > 50)
    nube = (mn > 188) & ((mx - mn) < 55) & ~sub
    lab, n = ndimage.label(nube); keep = np.zeros_like(nube)
    for i, sl in enumerate(ndimage.find_objects(lab)):
        comp = lab[sl] == i + 1
        if comp.sum() < 2500 * U * U: continue
        ys0, xs0 = sl[0].start, sl[1].start
        big = (slice(max(0, sl[0].start - 6), sl[0].stop + 6), slice(max(0, sl[1].start - 6), sl[1].stop + 6))
        cb = lab[big] == i + 1; ring = ndimage.binary_dilation(cb, iterations=5) & ~cb
        if ring.sum() and (cielo[big][ring]).mean() > 0.3: keep[big] |= cb
    if keep.sum() < 4000 * U * U: return None
    claro = (mn > 140) & ((mx - mn) < 95) & ~sub
    ext = ndimage.binary_dilation(keep, iterations=int(5 * U), mask=claro)
    al = ndimage.gaussian_filter(ext.astype(np.float32), 1.0 * U)
    pz = G.Pieza(a, al, (0, 0))
    hueco = ndimage.binary_dilation(ext, iterations=int(3 * U)).astype(np.float32)
    b = np.asarray(e.bg.convert("RGB")).astype(np.float32)
    e.bg = Image.fromarray(np.clip(G.rellenar(b, hueco), 0, 255).astype(np.uint8)).convert("RGBA")
    return pz

def fondo_vivo(e, k, t, lt):
    """Fondo del fotograma: nubes que se desplazan y agua con ondas."""
    r = RIG.get(k, {}); bg = e.bg
    agua = r.get("agua") if r.get("agua") != "auto" else None
    if agua or e.nubes is not None or getattr(e, "agua_m", None) is not None: bg = bg.copy()
    if getattr(e, "agua_m", None) is not None:
        A = np.asarray(bg).copy(); m = e.agua_m; ys = np.where(m.max(1) > 0.05)[0]
        if len(ys):
            y0, y1 = ys[0], ys[-1] + 1; reg = A[y0:y1].copy()
            for j in range(reg.shape[0]):
                yy = (y0 + j) / U
                sh = int(round(U * 2.6 * math.sin(yy * 0.23 + t * 3.1) + U * 1.3 * math.sin(yy * 0.061 - t * 1.7)))
                if sh: reg[j] = np.roll(reg[j], sh, axis=0)
            mm = m[y0:y1, :, None]; A[y0:y1] = (reg * mm + A[y0:y1] * (1 - mm)).astype(np.uint8)
        bg = Image.fromarray(A, "RGBA")
    if agua:
        A = np.asarray(bg).copy()
        for pol in agua:
            xs = [p[0] * U for p in pol]; ys = [p[1] * U for p in pol]
            x0, x1, y0, y1 = int(min(xs)), int(max(xs)), int(min(ys)), int(max(ys))
            reg = A[y0:y1, x0:x1].copy()
            for j in range(reg.shape[0]):
                yy = (y0 + j) / U; prof = 0.4 + 0.6 * (j / max(1, reg.shape[0]))
                sh = int(round(U * 3.2 * prof * math.sin(yy * 0.21 + t * 3.1) + U * 1.5 * math.sin(yy * 0.057 - t * 1.7)))
                reg[j] = np.roll(reg[j], sh, axis=0)
            m = np.asarray(G.poly(pol, 2.0))[y0:y1, x0:x1, None]
            A[y0:y1, x0:x1] = (reg * m + A[y0:y1, x0:x1] * (1 - m)).astype(np.uint8)
        bg = Image.fromarray(A, "RGBA")
    if e.nubes is not None:
        nb = e.nubes; vel = r.get("vel_nubes", 9.0)
        pegar(bg, nb.im, (0, 0), (nb.x0 + vel * U * t % (40 * U) * 0 + vel * U * lt, nb.y0), 0)
    return bg

def camara(s):
    """Cámara casi fija (como TED-Ed): una deriva mínima; el movimiento lo ponen los personajes."""
    v = (s["i"] * 7 + (int(s["img"]) if s["img"].isdigit() else 0)) % 4
    dx = (-8, 8, -5, 5)[v]
    if s.get("parte") == 1: return (640 + dx, 360, 1.06), (640, 358, 1.075)
    return (640 - dx, 362, 1.03), (640 + dx, 360, 1.045)

def personaje(e, k, t, lt, s):
    """Capa de personajes animada para la imagen k."""
    c = G.capa(); r = RIG.get(k, {}); tipo = TIPO.get(k, "paisaje"); fase = (int(k) if k.isdigit() else 3) * 0.7
    ab = {"criatura": (0.012, 0.8), "personaje": (0.010, 0.6), "objeto": (0.006, 0.0)}.get(tipo, (0.0, 0.0))
    for nombre in r.get("orden_atras", []): _pieza(e, r, nombre, t, lt, c)
    if "cuerpo" in e.pz:
        pz = e.pz["cuerpo"]; im = pz.im
        if k in ONDA:
            im, Pd = onda(pz.im, 2.6 * U, 260 * U, t * 3.2 + fase, eje="x", taper=(1.0, 0.4))
            pegar(c, im, (pz.lp[0], pz.lp[1] + Pd), pz.piv, ab[1] * math.sin(t * 1.1 + fase), 1, 1 + ab[0] * math.sin(t * 2.0 + fase))
        else:
            if r.get("ojos"):
                for o in r["ojos"]:
                    cierre = parpadeo(t, o.get("semilla", 7), o.get("cada", 2.6))
                    im = G.parpado(im, pz, [tuple(x) for x in o["ojos"]], cierre, tuple(o["piel"]), tuple(o.get("linea", (30, 30, 30))))
            if r.get("boca"):
                b = r["boca"]; im = G.boca(im, pz, *b["pos"], b["ancho"], G.BOCA.abierta(t), tuple(b["piel"]), tuple(b["tapa"]))
            dy = -3 * math.sin(t * 1.6 + fase) if tipo == "objeto" else 0
            pz.dibujar(c, 0, dy, ab[1] * math.sin(t * 1.1 + fase), 1, 1 + ab[0] * math.sin(t * 2.0 + fase), im=im)
    for nombre in [n for n in r.get("piezas", {}) if n not in r.get("orden_atras", [])]: _pieza(e, r, nombre, t, lt, c)
    for em in r.get("emisores", []): emisor(c, em, t)
    return c

_RNG = np.random.default_rng(21); _PART = _RNG.random((60, 4))
def emisor(c, em, t):
    """Humo o fuego que sale de un punto (coords de diseño) en una dirección, con bocanadas que crecen y se desvanecen."""
    if em.get("tipo") == "rayo": return rayo(c, em, t)
    if em.get("tipo") == "pajaros": return pajaros(c, em, t)
    if em.get("tipo") == "chorro": return chorro(c, em, t)
    if em.get("tipo") == "vapor": em = dict(em, tipo="humo", col=em.get("col", (245, 248, 250)))
    tipo = em.get("tipo", "humo"); ox, oy = em["pos"]; dx, dy = em.get("dir", (-1, 0)); L = em.get("largo", 200); n = em.get("n", 26)
    capa_ = G.capa(); d = ImageDraw.Draw(capa_)
    for x, y, s_, v in _PART[:n]:
        k = ((t * em.get("vel", 0.45) * (0.8 + 0.4 * v)) + x) % 1.0
        px = ox + dx * L * k + (y - 0.5) * 50 * k + 10 * math.sin(t * 2 + x * 9); py = oy + dy * L * k + (s_ - 0.5) * 40 * k - (25 * k * k if tipo == "humo" else 0)
        r = (6 + em.get("r", 30) * k) * U
        if tipo == "humo": col = tuple(em.get("col", (200, 175, 235))) + (int(150 * (1 - k) ** 1.2),)
        else: col = (255, int(230 - 160 * k), int(90 - 80 * k), int(220 * (1 - k)))
        d.ellipse([px * U - r, py * U - r, px * U + r, py * U + r], fill=col)
    c.alpha_composite(capa_.filter(ImageFilter.GaussianBlur((4 if tipo == "humo" else 2) * U)))

def _pieza(e, r, nombre, t, lt, c):
    pz = e.pz[nombre]; a = r.get("anim", {}).get(nombre, {}); im = pz.im
    rot = a.get("rot", 0) * math.sin(t * a.get("vel", 2.0) + a.get("fase", 0))
    dy = a.get("dy", 0) * math.sin(t * a.get("vel", 2.0) * 1.3 + a.get("fase", 0))
    dx = a.get("dx", 0) * math.sin(t * a.get("vel", 2.0) * 0.5 + a.get("fase", 0))
    sy = 1 - a.get("aleteo", 0) * abs(math.sin(t * a.get("vel", 2.0) + a.get("fase", 0)))
    if "boca" in a:
        b = a["boca"]; im = G.boca(im, pz, *b["pos"], b["ancho"], G.BOCA.abierta(t), tuple(b["piel"]), tuple(b["tapa"]))
    if "ojos" in a:
        cierre = parpadeo(t, sum(map(ord, nombre)) + int(r.get("semilla", 0)), a.get("cada", 2.4))
        im = G.parpado(im, pz, a["ojos"], cierre, tuple(a["piel"]), tuple(a.get("linea", (30, 30, 30))))
    if "onda" in a:
        o = a["onda"]; im, Pd = onda(im, o["amp"] * U, o["lam"] * U, t * o.get("vel", 3) + a.get("fase", 0), eje=o.get("eje", "x"), taper=tuple(o.get("taper", (0, 1))))
        lp = (pz.lp[0], pz.lp[1] + Pd) if o.get("eje", "x") == "x" else (pz.lp[0] + Pd, pz.lp[1])
        pegar(c, im, lp, (pz.piv[0], pz.piv[1] + dy * U), rot, 1, sy); return
    pz.dibujar(c, dx, dy, rot, 1, sy, im=im)

def plano(s, t):
    k = s["img"]; e = escena(k); lt = t - s["t0"]; d = s["t1"] - s["t0"]
    (ax, ay, az), (bx, by, bz) = camara(s); q = eio(lt / d)
    cx, cy, z = lerp(ax, bx, q), lerp(ay, by, q), lerp(az, bz, q)
    ytop = INFO.get(k, {"bbox": [0, 0, 1280, 720]})["bbox"][1]          # que la cabeza no se salga por arriba
    vh = 720 / z; cy = min(cy, max(vh / 2, ytop - 25 + vh / 2))
    if s["reuso"] and s.get("parte", 0) == 0 or s["n"] in CHISTE:          # punch-in
        fr = s["frases"]; tp = s["t0"] if (s["reuso"] and s.get("parte", 0) == 0) else (fr[CHISTE[s["n"]]]["t0"] - 0.05 if fr else s["t0"])
        if t >= tp: z *= 1 + 0.035 * eout((t - tp) / 0.22) - 0.01 * eout((t - tp - 0.22) / 0.6)
    ch = personaje(e, k, t, lt, s)
    sil = (0.35, 0.45) if (k in DRAGONES and s.get("parte", 0) == 0 and not s["reuso"]) else None
    cam = dict(cx=cx / 1280, cy=cy / 720, z=z, sil=sil)
    return G.componer(fondo_vivo(e, k, t, lt), ch, cam, lt)

def final55(s, t):
    """El dragón del globo dice el cierre: boca con la voz, parpadeos, cabeza que se inclina, interrogación que bota."""
    e = G.E06; c = G.capa(); lt = t - s["t0"]
    cola = e.pz["cola"]; ci, Pd = onda(cola.im, 7 * U, 160 * U, lt * 6, eje="y", taper=(1.0, 0.1))
    pegar(c, ci, (cola.lp[0] + Pd, cola.lp[1]), cola.piv, 0); e.pz["cuerpo"].dibujar(c)
    for n, f in (("garra_i", 0), ("garra_d", 1.7)): e.pz[n].dibujar(c, 0, -3 * max(0.0, math.sin(t * 9 + f)) * (1 if 296.0 < t < 297.3 else 0.2), 0)
    pz = e.pz["cabeza"]; rot = 3 * math.sin(lt * 1.7) + keys(t, [(295.9, 0), (296.3, -5), (297.4, -5), (297.8, 2)])
    ab = G.BOCA.abierta(t, s["t0"], s["t1"])
    im = G.boca(pz.im, pz, 657, 299, 36, ab * 1.25, (86, 160, 120), tapa=None, linea=(25, 60, 40), interior=(70, 25, 30))
    cerr = max(min(1.0, 2.2 * (1 - abs(2 * (t - b) / 0.16 - 1))) if 0 <= t - b < 0.16 else 0.0 for b in (295.4, 297.6, 300.9))
    im = G.parpado(im, pz, [(652, 264, 22, 19), (566, 260, 9, 17)], cerr, (112, 170, 128), linea=(20, 45, 30))
    pz.dibujar(c, 0, -2 * math.sin(t * 2.4), rot, im=im)
    e.pz["interr"].dibujar(c, 0, -6 * abs(math.sin(t * 4)), 8 * math.sin(t * 3))
    img_ = G.componer(e.bg, c, dict(cx=0.5, cy=0.43, z=lerp(1.02, 1.1, eio(lt / (s["t1"] - s["t0"])))), lt)
    if t > TOTAL - 0.8: img_ = Image.blend(img_, Image.new("RGB", (W, H)), cl((t - (TOTAL - 0.8)) / 0.8))
    return img_

def rayo(c, em, t):
    """Rayos quebrados que salen de una mano hacia un objetivo, cambian cada 3 fotogramas y parpadean."""
    k = int(t * 10); rng = np.random.default_rng(k * 7 + 3); (ox, oy), (tx, ty) = em["pos"], em["hacia"]
    if rng.random() < 0.25: return
    capa_ = G.capa(); d = ImageDraw.Draw(capa_)
    for _ in range(em.get("n", 3)):
        pts = [(ox, oy)]; n = 9
        ex, ey = tx + rng.normal(0, 40), ty + rng.normal(0, 70)
        for j in range(1, n + 1):
            f = j / n; pts.append((ox + (ex - ox) * f + rng.normal(0, 14), oy + (ey - oy) * f + rng.normal(0, 14)))
        P_ = [(x * U, y * U) for x, y in pts]
        d.line(P_, fill=tuple(em.get("col", (200, 120, 255))) + (150,), width=int(9 * U)); d.line(P_, fill=(255, 255, 255, 235), width=int(2.4 * U))
    c.alpha_composite(capa_.filter(ImageFilter.GaussianBlur(1.2 * U)))

def pajaros(c, em, t):
    """Bandada de pájaros (uves que aletean) cruzando el cielo."""
    capa_ = G.capa(); d = ImageDraw.Draw(capa_); y0 = em.get("y", 120); vel = em.get("vel", 55); n = em.get("n", 5)
    for i in range(n):
        x = (em.get("x0", -80) + vel * t + i * 38 * (1 + 0.3 * math.sin(i))) % 1500 - 110
        y = y0 + 22 * math.sin(i * 1.7) + 6 * math.sin(t * 1.3 + i)
        a = 9 * math.sin(t * 9 + i * 1.1); w = 11
        P_ = [((x - w) * U, (y - a) * U), (x * U, y * U), ((x + w) * U, (y - a) * U)]
        d.line(P_, fill=(40, 45, 55, 230), width=int(2.2 * U), joint="curve")
    c.alpha_composite(capa_)

def chorro(c, em, t):
    """Partículas que caen en chorro (arena del reloj...)."""
    capa_ = G.capa(); d = ImageDraw.Draw(capa_); (ox, oy), L = em["pos"], em.get("largo", 140); col = tuple(em.get("col", (255, 170, 60)))
    for x, y, s_, v in _PART[:em.get("n", 40)]:
        k = ((t * em.get("vel", 1.2) * (0.8 + 0.4 * v)) + x) % 1.0
        px = ox + (y - 0.5) * em.get("ancho", 6); py = oy + L * k * k * 0.5 + L * k * 0.5; r = em.get("r", 2.4) * U
        d.ellipse([px * U - r, py * U - r, px * U + r, py * U + r], fill=col + (235,))
    c.alpha_composite(capa_)

WHIP = 0.14
def frame(t):
    if t < T_GANCHO: return G.frame(t)
    s = next((x for x in shots if x["t0"] <= t < x["t1"]), shots[-1])
    img_ = final55(s, t) if s["n"] == "55" else plano(s, t)
    lt = t - s["t0"]; d = s["t1"] - s["t0"]; sh = bl = 0.0
    if s["sec_fin"] and lt > d - WHIP: q = ein((lt - (d - WHIP)) / WHIP); sh = -q * 0.4 * W; bl = 60 * q
    if s["sec_ini"] and lt < WHIP and s["i"] > 0: q = 1 - eout(lt / WHIP); sh = q * 0.4 * W; bl = 60 * q
    if sh:
        a = np.asarray(img_); img_ = Image.fromarray(np.roll(a, int(sh), axis=1)); img_ = RF.R.hblur(img_, bl)
    img_ = RF.particulas(img_, FX.get(s["img"], "ninguno"), t, lt)
    fl = RIG.get(s["img"], {}).get("relampago")
    if fl:
        k = int(t * 12); g = np.random.default_rng(k)
        if g.random() < fl: img_ = Image.blend(img_, Image.new("RGB", img_.size, (235, 240, 255)), 0.22 + 0.2 * g.random())
    return img_

def render(a, b, out):
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-preset", "medium", "-crf", "16", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
    for i in range(a, b): p.stdin.write(vineta(frame(i / FPS), 0.18).tobytes())
    p.stdin.close(); p.wait()

if __name__ == "__main__":
    n = int(round(TOTAL * FPS))
    if sys.argv[1] == "hoja":
        ts = [float(x) for x in sys.argv[2].split(",")]; cols = 6; w, h = 480, 270
        S = Image.new("RGB", (cols * w, ((len(ts) + cols - 1) // cols) * (h + 18)), "white"); d = ImageDraw.Draw(S)
        for i, t in enumerate(ts):
            x, y = (i % cols) * w, (i // cols) * (h + 18); S.paste(frame(t).resize((w, h)), (x, y)); d.text((x + 4, y + h + 2), f"{t:.2f}", fill="black")
        S.save(sys.argv[3], quality=85); print("ok", sys.argv[3])
    elif sys.argv[1] == "todo":
        os.makedirs("seg", exist_ok=True); NP = int(sys.argv[2]) if len(sys.argv) > 2 else 10
        cuts = [round(n * j / NP) for j in range(NP + 1)]; segs = [f"seg/s{j:02d}.mp4" for j in range(NP)]
        procs = [subprocess.Popen([sys.executable, __file__, str(cuts[j] / FPS), str(cuts[j + 1] / FPS), segs[j]]) for j in range(NP)]
        for pr in procs: pr.wait()
        open("seg/lista.txt", "w").write("".join(f"file '{os.path.basename(s)}'\n" for s in segs))
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", "seg/lista.txt", "-c", "copy", "visual_full.mp4"])
        print("ok visual_full.mp4")
    else:
        a, b = int(round(float(sys.argv[1]) * FPS)), int(round(float(sys.argv[2]) * FPS)); render(a, min(b, n), sys.argv[3]); print("ok", sys.argv[3])
