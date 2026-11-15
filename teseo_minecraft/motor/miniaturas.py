from PIL import Image, ImageFilter, ImageDraw, ImageFont, ImageEnhance, ImageChops
import numpy as np
W, H = 1280, 720
F = "fonts/LilitaOne-Regular.ttf"
def recorte(path):
    im = np.array(Image.open(path).convert("RGB")).astype(np.int16)
    r, g, b = im[..., 0], im[..., 1], im[..., 2]
    verde = (g > 140) & (g - np.maximum(r, b) > 60)
    a = np.where(verde, 0, 255).astype(np.uint8)
    im[..., 1] = np.minimum(g, np.maximum(r, b) + 10)  # quitar halo verde
    out = Image.fromarray(np.dstack([im.clip(0, 255).astype(np.uint8), a]), "RGBA")
    out = out.crop(out.getbbox()); return out
def fondo(path, tinte=(255, 140, 40)):
    bg = Image.open(path).convert("RGB").resize((W, H)).filter(ImageFilter.GaussianBlur(5))
    bg = ImageEnhance.Brightness(bg).enhance(0.75)
    tint = Image.new("RGB", (W, H), tinte); bg = Image.blend(bg, tint, 0.18)
    # viñeta
    y, x = np.ogrid[:H, :W]; d = np.sqrt(((x - W / 2) / (W / 2)) ** 2 + ((y - H / 2) / (H / 2)) ** 2)
    v = np.clip(1.15 - 0.55 * d, 0.3, 1)[..., None]; bg = Image.fromarray((np.array(bg) * v).astype(np.uint8)); return bg
def pegar(bg, cut, alto, cx, base, brillo=1.0, borde=(255, 220, 120)):
    k = alto / cut.height; c = cut.resize((int(cut.width * k), alto), Image.LANCZOS)
    if brillo != 1: c = Image.merge("RGBA", (*ImageEnhance.Brightness(c.convert("RGB")).enhance(brillo).split(), c.split()[3]))
    # contorno brillante (estilo miniatura)
    al = c.split()[3].filter(ImageFilter.MaxFilter(13)); glow = Image.new("RGBA", c.size, borde + (0,)); glow.putalpha(al)
    x, y = int(cx - c.width / 2), int(base - c.height)
    bg.paste(glow, (x, y), glow); bg.paste(c, (x, y), c)
def texto(bg, s, xy, size, col, ang=0, borde=12):
    f = ImageFont.truetype(F, size); d = ImageDraw.Draw(bg)
    capa = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dc = ImageDraw.Draw(capa)
    dc.text((xy[0] + 8, xy[1] + 10), s, font=f, fill=(0, 0, 0, 200), stroke_width=borde, stroke_fill=(0, 0, 0, 200))
    dc.text(xy, s, font=f, fill=col, stroke_width=borde, stroke_fill=(0, 0, 0))
    if ang: capa = capa.rotate(ang, center=(xy[0], xy[1]), resample=Image.BICUBIC)
    bg.paste(capa, (0, 0), capa)
mino, tes, ovi = recorte("mini/cut_minotauro.png"), recorte("mini/cut_teseo_espada.png"), recorte("mini/cut_teseo_ovillo.png")
# --- A: Teseo VS Minotauro
A = fondo("mini/plate_lab.png")
pegar(A, mino, 860, 1000, 900, 1.15, (255, 80, 30))
pegar(A, tes, 640, 270, 745, 1.05)
texto(A, "TESEO", (40, 20), 150, (255, 220, 40), 4)
texto(A, "VS", (500, 70), 90, (255, 70, 50), 4, 10)
texto(A, "MINOTAURO", (500, 575), 125, (255, 255, 255), 3)
A.save("miniatura_a.jpg", quality=92)
# --- B: ¿con un ovillo?
B = fondo("mini/plate_lab.png", (60, 80, 200))
sombra = mino.copy(); sombra = Image.merge("RGBA", (*ImageEnhance.Brightness(sombra.convert("RGB")).enhance(0.25).split(), sombra.split()[3]))
pegar(B, sombra, 700, 1050, 760, 1.0, (200, 30, 30))
d = ImageDraw.Draw(B)
for k in range(3): d.line([(390, 330 + k), (760, 420 + k * 3), (1280, 380 + k)], fill=(230, 20, 30), width=7, joint="curve")
pegar(B, ovi, 760, 360, 800, 1.1)
texto(B, "¿CON UN", (640, 40), 115, (255, 255, 255), -4)
texto(B, "OVILLO?", (620, 165), 158, (255, 220, 40), -4)
B.save("miniatura_b.jpg", quality=92)
