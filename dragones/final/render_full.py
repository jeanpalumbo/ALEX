# Capa visual (sin texto ni voz) del vídeo completo de dragones -> full/capa_visual_full.mp4 (1920x1080, 30 fps).
# Gancho: el montaje de los 15 s (render.py) reajustado en el tiempo a la voz nueva.
# Resto: un plano por bloque de voz (los de >6,5 s se parten en dos encuadres), Ken Burns con easing y deriva,
# parallax (sujeto recortado con rembg sobre fondo rellenado), silueta->color en la primera aparición de cada dragón,
# partículas por escena, whip-pan entre secciones y punch-in en los chistes.
# Uso: python render_full.py [desde_s hasta_s] [salida]      (por defecto todo; se reparte en procesos)
import sys, os, json, math, subprocess, numpy as np
from PIL import Image, ImageFilter
os.chdir(os.path.dirname(os.path.abspath(__file__)))
import render as R                                   # gancho, cam_img, partículas, hblur, viñeta
W, H, FPS = 1920, 1080, 30
SW, SH, UP = R.SW, R.SH, R.UP
P = json.load(open("full/planos.json", encoding="utf-8"))
FR = json.load(open("full/frases.json", encoding="utf-8"))
INFO = json.load(open("img_full/mask/info.json"))
import soundfile as sf
TOTAL = round(sf.info("full/vo.wav").duration, 3)
LEAD = 0.12                                          # el corte llega un pelín antes que la voz

# ---------- planos visuales
R.CAM["final"] = ((640, 380, 1.07), (630, 330, 1.22))
OLD = {s["k"]: (s["t0"], s["t1"]) for s in R.TL["shots"]}
DRAGONES = {"08", "09", "11", "26", "29", "37", "43", "46"}           # silueta -> color en su primera aparición
CHISTE = {"09": -1, "22": -1, "27": 0, "33": -1, "40": -1, "42": 0, "47": -1, "51": -1, "54": -1}   # frase (índice) donde va el punch-in
FX = {"07": "niebla", "08": "niebla", "09": "hojas", "11": "lluvia", "12": "polvo", "13": "humo", "14": "polvo", "16": "niebla",
      "17": "polvo", "19": "polvo", "20": "brasas", "21": "estrellas", "22": "polvo", "24": "brasas", "25": "humo", "29": "niebla",
      "31": "polvo", "32": "polvo", "34": "niebla", "35": "polvo", "37": "niebla", "38": "polvo", "39": "polvo", "40": "destellos",
      "41": "humo", "42": "humo", "43": "brasas", "44": "brasas", "45": "humo", "46": "lluvia", "47": "brasas", "48": "hojas",
      "50": "niebla", "51": "polvo", "52": "hojas", "53": "burbujas", "54": "polvo", "06": "humo"}
shots = []
for i, p in enumerate(P):
    t0 = 0.0 if i == 0 else max(0.0, p["t0"] - LEAD)
    t1 = TOTAL if i == len(P) - 1 else P[i + 1]["t0"] - LEAD
    base = dict(n=p["n"], img=p["img"], sec=p["sec"], t0=t0, t1=t1, reuso=p["img"] != p["n"])
    fr = [f for f in FR if f["plano"] == p["n"]]
    base["frases"] = fr
    if p["sec"] == 1:
        base["hook"] = True; shots.append(base); continue
    if t1 - t0 > 6.5 and len(fr) > 1:                # se parte en dos encuadres en la frase más cercana a la mitad
        mid = (t0 + t1) / 2; cut = min(fr[1:], key=lambda f: abs(f["t0"] - mid))["t0"] - LEAD
        if 2.2 < cut - t0 and 2.2 < t1 - cut:
            shots.append(dict(base, t1=cut, parte=0)); shots.append(dict(base, t0=cut, parte=1, reuso=True)); continue
    shots.append(dict(base, parte=0))
for i, s in enumerate(shots):
    s["i"] = i
    s["sec_ini"] = i > 0 and shots[i - 1]["sec"] != s["sec"]
    s["sec_fin"] = i < len(shots) - 1 and shots[i + 1]["sec"] != s["sec"]

# ---------- imágenes: originales, máscara, fondo rellenado (para parallax) y silueta
def up(im): return im.resize((SW * UP, SH * UP), Image.LANCZOS)
MK, BGF = {}, {}
def cargar(k):
    if k in R.IM and k in MK: return
    f = f"img_full/{k}.png" if os.path.exists(f"img_full/{k}.png") else f"img/{k}.png"
    if not os.path.exists(f):                         # aún no ha llegado: marcador gris
        im = Image.new("RGB", (SW, SH), (90, 100, 110)); m = Image.new("L", (SW, SH), 0)
    else:
        im = Image.open(f).convert("RGB").resize((SW, SH), Image.LANCZOS)
        mf = f"img_full/mask/{k}.png" if os.path.exists(f"img_full/mask/{k}.png") else f"mask/{k}.png"
        m = Image.open(mf).convert("L") if os.path.exists(mf) else Image.new("L", (SW, SH), 0)
        m = Image.fromarray((np.clip((np.asarray(m).astype(np.float32) / 255 - 0.4) / 0.25, 0, 1) * 255).astype(np.uint8))   # borde firme: sin halo
    a = np.asarray(im).astype(np.float32); mm = np.asarray(m).astype(np.float32)[..., None] / 255
    hole = np.clip(np.asarray(m.filter(ImageFilter.MaxFilter(25))).astype(np.float32)[..., None] / 255 * 1.5, 0, 1)
    known = 1 - hole; fill = a.copy()
    under = np.asarray(m.filter(ImageFilter.MaxFilter(9))).astype(np.float32)[..., None] / 255   # solo se rellena bajo el sujeto
    for r in (8, 24, 64):                              # relleno por convolución normalizada (el fondo tapa el hueco del sujeto)
        num = np.asarray(Image.fromarray(np.clip(a * known, 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(r))).astype(np.float32)
        den = np.asarray(Image.fromarray((known[..., 0] * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(r))).astype(np.float32)[..., None] / 255
        est = num / np.maximum(den, 1e-3); fill = np.where(under > 0.5, np.where(den > 0.05, est, fill), fill)
    R.IM[k] = up(im); BGF[k] = up(Image.fromarray(np.clip(fill, 0, 255).astype(np.uint8)))
    MK[k] = up(m.filter(ImageFilter.GaussianBlur(0.6)).convert("RGB"))
    if k in DRAGONES:
        R.SIL[k] = Image.composite(Image.new("RGB", (SW * UP, SH * UP), (10, 12, 18)), R.IM[k], up(m))

def cl(x, a=0.0, b=1.0): return max(a, min(b, x))
def eio(x): x = cl(x); return 3 * x * x - 2 * x ** 3
def eout(x): x = cl(x); return 1 - (1 - x) ** 4
def ein(x): x = cl(x); return x ** 3

# ---------- movimiento de cámara por plano: (cx, cy, z) inicio -> fin en coords 1280x720
def camara(s):
    k = s["img"]; inf = INFO.get(k, {"c": [640, 360], "bbox": [0, 0, 1280, 720], "area": 0.3})
    cx, cy = inf["c"]; x0, y0, x1, y1 = inf["bbox"]
    bw, bh = max(80, x1 - x0), max(80, y1 - y0)
    zfit = cl(min(1280 / (bw * 1.25), 720 / (bh * 1.25)), 1.05, 1.9)     # encuadre cerrado sobre el sujeto
    v = (s["i"] * 7 + int(k) if k.isdigit() else s["i"]) % 4
    if s.get("parte") == 1 or s["reuso"]:              # segundo encuadre: más cerca del sujeto
        return (cx, cy, zfit * 1.02), (cx + (12 if v % 2 else -12), cy - 6, zfit * 1.12)
    if v == 0: return (640, 360, 1.04), (cx, cy, min(1.22, zfit))                      # empuje lento hacia el sujeto
    if v == 1: return (cx, cy, min(1.25, zfit)), (640, 360, 1.06)                      # se abre
    if v == 2: return (cx - 70, cy, 1.18), (cx + 70, cy, 1.24)                         # paneo a la derecha
    return (cx + 70, cy - 10, 1.24), (cx - 70, cy + 10, 1.18)                          # paneo a la izquierda

def remap_hook(s, t):
    o0, o1 = OLD[s["n"]]; x = (t - s["t0"]) / (s["t1"] - s["t0"]); return o0 + x * (o1 - o0)

# ---------- partículas extra (las de render.py + lluvia, estrellas, destellos, burbujas)
rng = np.random.default_rng(11); PX = rng.random((90, 5))
from PIL import ImageDraw
def particulas(img, fx, t, lt):
    if fx in ("niebla", "brasas", "hojas", "polvo", "humo"): return R.particulas(img, fx, t, lt)
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    if fx == "lluvia":
        for x, y, s_, v, ph in PX:
            X = (x * W * 1.2 + t * 260) % (W * 1.2) - W * 0.1; Y = (y * H + t * (900 + 500 * v)) % H
            d.line([X, Y, X - 14, Y + 46], fill=(220, 230, 255, 110), width=2)
    elif fx == "estrellas":
        for x, y, s_, v, ph in PX[:60]:
            a = int(60 + 150 * (0.5 + 0.5 * math.sin(t * (2 + 3 * v) + ph * 9)))
            X, Y, r = x * W, y * H * 0.55, 1.5 + 2 * s_; d.ellipse([X - r, Y - r, X + r, Y + r], fill=(255, 255, 230, a))
    elif fx == "destellos":
        for x, y, s_, v, ph in PX[:25]:
            q = math.sin(t * (1.5 + 2 * v) + ph * 7) ** 8; X, Y, r = W * (0.3 + 0.4 * x), H * (0.25 + 0.5 * y), 4 + 16 * s_ * q
            d.line([X - r, Y, X + r, Y], fill=(255, 255, 240, int(220 * q)), width=2); d.line([X, Y - r, X, Y + r], fill=(255, 255, 240, int(220 * q)), width=2)
    elif fx == "burbujas":
        for x, y, s_, v, ph in PX[:40]:
            X = x * W + 12 * math.sin(t * 2 + ph * 6); Y = H - ((y * H + t * (60 + 90 * v)) % (H * 1.1)); r = 3 + 8 * s_
            d.ellipse([X - r, Y - r, X + r, Y + r], outline=(235, 250, 255, 170), width=2)
    base = img.convert("RGBA"); base.alpha_composite(ov); return base.convert("RGB")

WHIP = 0.14
def frame(t):
    s = next((x for x in shots if x["t0"] <= t < x["t1"]), shots[-1])
    if s.get("hook"):
        if s["n"] == "final" and False: pass
        return R.frame(remap_hook(s, t))
    k = s["img"]; cargar(k)
    lt = t - s["t0"]; d = s["t1"] - s["t0"]; x = lt / d
    (ax, ay, az), (bx, by, bz) = camara(s)
    e = eio(x); cx, cy, z = ax + (bx - ax) * e, ay + (by - ay) * e, az + (bz - az) * e
    rot = 0.003 * math.sin(t * 0.8)
    if s["reuso"] and s.get("parte", 0) == 0 or s["n"] in CHISTE:             # punch-in (entrada frenando o en la frase del chiste)
        fr = s["frases"]; tp = s["t0"] if s["reuso"] and s.get("parte", 0) == 0 else (fr[CHISTE[s["n"]]]["t0"] - 0.05 if fr else s["t0"])
        if tp >= s["t0"] and t >= tp: z *= 1 + 0.10 * eout((t - tp) / 0.22) - 0.03 * eout((t - tp - 0.22) / 0.6)
    shift = blur = 0.0
    if s["sec_fin"] and lt > d - WHIP: q = ein((lt - (d - WHIP)) / WHIP); shift = -q * 0.45 * W; blur = 60 * q
    if s["sec_ini"] and lt < WHIP: q = 1 - eout(lt / WHIP); shift = q * 0.45 * W; blur = 60 * q
    sx = shift / (z * W / SW)
    # sin capas separadas: el recorte con rembg dejaba halo; la vida la dan cámara, deriva y partículas
    img = R.cam_img(k, cx - sx, cy, z, rot)
    if k in DRAGONES and s.get("parte", 0) == 0 and not s["reuso"]:        # silueta -> color
        q = eio((lt - 0.35) / 0.45)
        if q < 1:
            img = Image.blend(R.cam_img(k, cx - sx, cy, z, rot, src=R.SIL), img, q)
    img = R.hblur(img, blur)
    img = particulas(img, FX.get(k, "ninguno"), t, lt)
    if s["i"] == len(shots) - 1 and t > TOTAL - 0.8:                      # fundido final
        img = Image.blend(img, Image.new("RGB", (W, H), (0, 0, 0)), cl((t - (TOTAL - 0.8)) / 0.8))
    return img

def render(a, b, out):
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-preset", "medium", "-crf", "16", "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
    for i in range(a, b):
        p.stdin.write(R.vignette(frame(i / FPS)).tobytes())
    p.stdin.close(); p.wait()

if __name__ == "__main__":
    n = int(TOTAL * FPS)
    if len(sys.argv) >= 4 and sys.argv[1] != "todo":
        a, b = int(float(sys.argv[1]) * FPS), int(float(sys.argv[2]) * FPS); render(a, min(b, n), sys.argv[3]); print("ok", sys.argv[3]); sys.exit()
    from concurrent.futures import ProcessPoolExecutor
    os.makedirs("full/seg", exist_ok=True)
    NP = 10; cuts = [round(n * j / NP) for j in range(NP + 1)]
    segs = [f"full/seg/s{j:02d}.mp4" for j in range(NP)]
    procs = [subprocess.Popen([sys.executable, __file__, str(cuts[j] / FPS), str(cuts[j + 1] / FPS), segs[j]]) for j in range(NP)]
    for pr in procs: pr.wait()
    open("full/seg/lista.txt", "w").write("".join(f"file '{os.path.basename(s)}'\n" for s in segs))
    out = sys.argv[1] if len(sys.argv) == 2 else "full/capa_visual_full.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", "full/seg/lista.txt", "-c", "copy", out])
    print("ok", out, len(shots), "planos")
