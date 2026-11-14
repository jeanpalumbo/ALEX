# Construye en paralelo la caché de escenas (fondo rellenado + piezas) de las imágenes 07-54.
import sys, os, json
from concurrent.futures import ProcessPoolExecutor
def uno(k):
    import full_anim as F
    F.escena(k); return k
if __name__ == "__main__":
    ks = sys.argv[1].split(",") if len(sys.argv) > 1 else sorted({p["img"] for p in json.load(open("../full/planos.json", encoding="utf-8")) if p["sec"] > 1 and p["img"] != "06"})
    with ProcessPoolExecutor(6) as ex:
        for k in ex.map(uno, ks): print("ok", k, flush=True)
