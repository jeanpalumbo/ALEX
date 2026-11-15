# Lista de planos desde los tiempos palabra a palabra: cortes cada ~3 s (2-4,4 s) al inicio de una palabra,
# mismo algoritmo que index.html. Cada plano lleva escenario, tipo de cámara (rotando) y texto que suena.
import json
from guion import CAP
B = json.load(open("bloques.json", encoding="utf-8")); P = json.load(open("palabras.json", encoding="utf-8"))
SET = {  # escena -> escenario (librería escenarios/ + sets de Hércules reutilizables)
 "gancho_cueva": "cueva_gorgonas", "gancho_mirada": "cueva_gorgonas", "gancho_escudo": "cueva_gorgonas", "gancho_casco": "cueva_gorgonas", "intro": "cielo_titulo",
 "argos": "argos", "acrisio_hijo": "palacio_argos", "oraculo": "delfos", "oraculo_chiste": "delfos", "danae_plan": "palacio_argos", "torre": "torre_bronce",
 "torre_dentro": "torre_interior", "lluvia_oro": "torre_interior", "nace_perseo": "torre_interior",
 "acrisio_panico": "palacio_argos", "cofre_mete": "acantilado_argos", "cofre_mar": "mar_tormenta", "zeus_vigila": "mar_tormenta", "dictis_red": "playa_serifos", "crece": "playa_serifos",
 "polidectes": "palacio_serifos", "estorbo": "playa_serifos", "plan_banquete": "banquete", "sin_caballo": "banquete", "frase": "banquete", "silencio": "banquete", "tarde": "banquete",
 "gorgonas": "isla_gorgonas", "sacerdotisa": "templo_atenea", "castigo": "templo_atenea", "transforma": "templo_atenea", "petrifica": "isla_gorgonas",
 "perseo_fatal": "playa_serifos", "dioses_llegan": "playa_serifos", "regalos": "playa_serifos", "inventario1": "playa_serifos", "ninfas_dir": "playa_serifos",
 "greas": "cueva_greas", "greas_pelea": "cueva_greas", "ojo_robo": "cueva_greas", "greas_ciegas": "cueva_greas",
 "ninfas": "jardin_ninfas", "vuelo_arbol": "jardin_ninfas", "vuelo_nubes": "vuelo_nubes",
 "isla": "isla_gorgonas", "estatuas": "isla_gorgonas", "casco_invisible": "cueva_gorgonas", "reflejo": "cueva_gorgonas", "atras": "cueva_gorgonas", "corte": "cueva_gorgonas", "bolsa": "cueva_gorgonas", "pegaso": "isla_gorgonas",
 "hermanas": "isla_gorgonas", "huida": "vuelo_tormenta", "arma": "vuelo_nubes",
 "atlas": "desierto_atlas", "atlas_largo": "desierto_atlas", "atlas_piedra": "desierto_atlas", "atlas_mapa": "mapa_africa", "atlas_chiste": "desierto_atlas",
 "andromeda": "acantilado_etiopia", "casiopea": "palacio_etiopia", "poseidon": "acantilado_etiopia", "trato_boda": "acantilado_etiopia", "ceto": "acantilado_etiopia", "combate": "acantilado_etiopia",
 "boda": "salon_boda", "boda_cabeza": "salon_boda", "boda_chiste": "salon_boda",
 "vuelta": "playa_serifos", "banquete2": "banquete", "pues_si": "banquete", "corte_piedra": "banquete", "dictis_rey": "playa_serifos", "devuelve": "templo_atenea",
 "huye_abuelo": "argos", "juegos": "estadio", "disco": "estadio", "disco_golpe": "estadio", "destino": "estadio",
 "constelaciones": "cielo_estrellas", "estrellas": "cielo_estrellas", "casiopea_abajo": "cielo_estrellas", "cierre": "cielo_estrellas"}
CAMS = ["general", "medio", "primer_plano_cara", "contrapicado", "travelling", "picado", "medio_otro_lado", "primer_plano_reaccion"]
planos, n = [], 0
for b in B:
    ws = [w for w in P if w["b"] == b["i"]]; cuts = [b["t0"]]; cur = b["t0"]
    while b["t1"] - cur > 4.6:
        obj = cur + 3.0; cand = [w["t"] for w in ws if cur + 2.0 < w["t"] < cur + 4.4 and b["t1"] - w["t"] > 1.6]
        cur = (min(cand, key=lambda w: abs(w - obj)) - 0.08) if cand else obj; cuts.append(cur)
    for k, a in enumerate(cuts):
        z = cuts[k + 1] if k + 1 < len(cuts) else b["t1"]
        txt = " ".join(w["w"] for w in ws if a <= w["t"] < z)
        planos.append(dict(n=n, bloque=b["i"], escena=b["esc"], capitulo=CAP[b["cap"]], escenario=SET[b["esc"]], t0=round(a, 2), t1=round(z, 2),
                           dur=round(z - a, 2), camara=CAMS[(n + b["i"]) % len(CAMS)] if b["esc"] != "intro" else "orbita_titulo", texto=txt)); n += 1
json.dump(planos, open("planos.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
d = [p["dur"] for p in planos]; print(len(planos), "planos; dur media", round(sum(d) / len(d), 2), "máx", max(d), "min", min(d))
caps = {}
for b in B: caps.setdefault(b["cap"], b["t0"])
for c, t in caps.items(): print(f"{int(t // 60)}:{int(t % 60):02d} {CAP[c]}")
