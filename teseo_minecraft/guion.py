# Guion + lista de planos de "Teseo y el Minotauro" (El Bicho Curioso, estilo Minecraft).
# Cada bloque se locuta de una vez (prosodia natural); cada segmento es un plano y lleva su texto.
# Cámara: "tipo:foco:angulo" (tipos: general, medio, primer, picado, contra, travel, orbita, dos, paisaje, cenital, hombro)
# Actor: [nombre, x, z, ry, accion, expresion, extras{to, prop, ico, y, e2, sc}]
import json

def A(n, x, z, ry=0, acc="quieto", e="normal", **k):
    d = {"n": n, "x": x, "z": z, "ry": ry, "acc": acc, "e": e}; d.update(k); return d

def S(tx, set_, spot, cam, actores=(), **k):
    d = {"tx": tx, "set": set_, "spot": spot, "cam": cam if isinstance(cam, list) else [cam], "act": list(actores)}; d.update(k); return d

B = []  # bloques

# ---------------------------------------------------------------- GANCHO (laberinto)
B.append({"id": "gancho", "cap": None, "segs": [
  S("Oscuridad total. Pasillos de piedra que se retuercen como espaguetis.", "laberinto", "pasillo", ["travel:teseo:90", "picado:teseo:20"],
    [A("teseo", -60, 0, 90, "agachado", "susto", to=[20, 0], prop="antorcha")]),
  S("Y en algún lugar ahí dentro, algo respira.", "laberinto", "centro", ["contra:minotauro:10"],
    [A("minotauro", 0, -30, 0, "respirar", "malvado")], fx=["vapor@0.3", "vapor@0.7"]),
  S("Algo grande. Algo con cuernos.", "laberinto", "centro", ["primer:minotauro:-25"],
    [A("minotauro", 0, -30, 0, "rugir", "enfado")], fx=["temblor@0.5"]),
  S("Nadie que haya entrado aquí ha salido jamás.", "laberinto", "pasillo", ["picado:huesos:0"], []),
  S("Pero este chico tiene un plan.", "laberinto", "pasillo", ["primer:teseo:20"],
    [A("teseo", 0, 0, 0, "quieto", "guino", prop="antorcha", ico="!")]),
  S("Una espada... y un ovillo de lana.", "laberinto", "pasillo", ["medio:teseo:-15"],
    [A("teseo", 0, 0, 0, "mostrar", "risa", prop="espada", prop2="ovillo")]),
  S("Sí. De lana. Como tu abuela.", "laberinto", "pasillo", ["primer:teseo:30"],
    [A("teseo", 0, 0, 0, "encoger", "aburrido", prop2="ovillo")]),
  S("¿Cómo acabó aquí? Hoy te lo cuento.", "laberinto", "centro", ["contra:minotauro:0"],
    [A("minotauro", 0, -60, 0, "embestir", "enfado", to=[0, 40])], fx=["temblor@0.4", "rugido@0.2"]),
]})
# tarjeta de título (sin voz)
B.append({"id": "titulo", "pausa": 4.2, "segs": [
  S("", "atenas", "plaza", ["paisaje:spot:0"], [A("teseo", 0, 20, 0, "espada_alto", "risa", prop="espada")], ov="titulo")]})

# ---------------------------------------------------------------- CAP 1
B.append({"id": "c1", "cap": "Una espada bajo una roca", "segs": [
  S("Todo empieza con Egeo, rey de Atenas.", "atenas", "trono", ["general:egeo:0", "primer:egeo:15"],
    [A("egeo", 0, -10, 0, "sentado", "normal", ico="corona")]),
  S("Egeo tenía un problema: no tenía hijos. Y un rey sin hijos es un rey nervioso.", "atenas", "trono", ["medio:egeo:20", "primer:egeo:-20"],
    [A("egeo", -30, 10, 90, "andar", "sudor", to=[30, 10])]),
  S("Así que fue a preguntar al oráculo de Delfos, que era como Google, pero con humo y respuestas en acertijo.", "delfos", "templo", ["paisaje:spot:20", "medio:egeo:30", "primer:pitia:-20"],
    [A("egeo", 0, 30, 180, "arrodillado", "normal"), A("pitia", 0, -10, 0, "hablar", "cerrados")], fx=["humo_tripode"]),
  S("El oráculo le dijo algo rarísimo. Y Egeo, en vez de volver a casa, se fue de visita a Trecén.", "trecen", "camino", ["travel:egeo:90", "primer:egeo:20"],
    [A("egeo", -80, 20, 90, "andar", "normal", to=[60, 20], ico="?")]),
  S("Allí conoció a la princesa Etra. Se gustaron. Pasó lo que tenía que pasar.", "trecen", "roca", ["dos:egeo,etra:0", "paisaje:spot:-30"],
    [A("egeo", -14, 20, 60, "hablar", "enamorado"), A("etra", 14, 20, -60, "quieto", "enamorado")], fx=["corazones@0.3"]),
  S("Pero Egeo tenía que volver a Atenas.", "trecen", "roca", ["medio:egeo:-30"],
    [A("egeo", -10, 20, 200, "mirar", "triste"), A("etra", 20, 30, -40, "quieto", "triste")]),
  S("Antes de irse, escondió su espada y sus sandalias debajo de una roca enorme.", "trecen", "roca", ["medio:roca:30", "contra:egeo:-20"],
    [A("egeo", 0, 6, 180, "empujar", "sudor")], fx=["polvo@0.5"]),
  S("Y le dijo a Etra: si tenemos un hijo, y algún día es capaz de levantar esta roca, que venga a buscarme.", "trecen", "roca", ["dos:egeo,etra:10", "primer:egeo:25", "primer:etra:-25"],
    [A("egeo", -16, 20, 50, "hablar", "normal"), A("etra", 16, 20, -50, "quieto", "normal")]),
  S("Básicamente, la primera prueba de acceso de la historia.", "trecen", "roca", ["orbita:roca:0"], [], ico_roca="?"),
]})

# ---------------------------------------------------------------- CAP 2
B.append({"id": "c2", "cap": "El chico que levantó la roca", "segs": [
  S("Nació un niño. Lo llamaron Teseo.", "trecen", "casa", ["medio:etra:0"],
    [A("etra", 0, 10, 0, "acunar", "risa"), A("bebe", 0, 16, 0, "bebe", "risa", y=16)], fx=["corazones@0.2"]),
  S("Creció fuerte, listo, y bastante cabezota.", "trecen", "casa", ["medio:teseo:20", "primer:teseo:-10"],
    [A("teseo", 0, 10, 0, "musculos", "risa")]),
  S("A los dieciséis años, su madre lo llevó delante de la roca.", "trecen", "roca", ["travel:teseo:70"],
    [A("etra", -70, 40, 90, "andar", "normal", to=[-20, 30]), A("teseo", -90, 30, 90, "andar", "normal", to=[-5, 22])]),
  S("Teseo miró la roca. La roca no le miró a él, porque es una roca.", "trecen", "roca", ["primer:teseo:0", "primer:roca:0"],
    [A("teseo", 0, 22, 180, "pensar", "aburrido")]),
  S("Y la levantó como quien levanta una almohada.", "trecen", "roca", ["contra:teseo:30"],
    [A("teseo", 0, 2, 180, "levantar", "risa", prop="roca")], ocultar=["roca"], fx=["polvo@0.3", "temblor@0.3"]),
  S("Debajo estaban la espada y las sandalias de su padre.", "trecen", "roca", ["picado:espada_suelo:0"], [], ocultar=["roca"], mostrar=["espada_suelo"], fx=["brillo@0.2"]),
  S("Por fin supo quién era su padre: ¡el rey de Atenas!", "trecen", "roca", ["primer:teseo:15", "medio:teseo:-20"],
    [A("teseo", 0, 10, 0, "espada_alto", "sorpresa", prop="espada", ico="!")], ocultar=["roca"]),
  S("Su madre le dijo: ve por mar, hijo, que es más seguro.", "trecen", "roca", ["medio:etra:-25"],
    [A("etra", 12, 20, -60, "hablar", "normal"), A("teseo", -12, 20, 60, "quieto", "aburrido", prop="espada")], ocultar=["roca"]),
  S("Y Teseo dijo: no, mamá. Voy por tierra. Por el camino de los bandidos.", "trecen", "roca", ["primer:teseo:20", "primer:etra:-20"],
    [A("teseo", -12, 20, 60, "hablar", "risa", prop="espada"), A("etra", 12, 20, -60, "facepalm", "enfado")], ocultar=["roca"]),
  S("Porque claro, para qué ir tranquilo, si puedes ir peleando.", "trecen", "camino", ["travel:teseo:-90", "paisaje:teseo:20"],
    [A("teseo", -40, 20, 90, "andar", "risa", to=[120, 20], prop="espada")]),
]})

# ---------------------------------------------------------------- CAP 3
B.append({"id": "c3", "cap": "El camino de los bandidos", "segs": [
  S("El camino a Atenas estaba lleno de criminales, de lo más creativos.", "camino", "maza", ["paisaje:spot:30", "travel:teseo:90"],
    [A("teseo", -70, 30, 90, "andar", "normal", to=[0, 30], prop="espada")]),
  S("Primero, Perifetes, que mataba a la gente con una maza de bronce.", "camino", "maza", ["contra:perifetes:15", "medio:perifetes:-20"],
    [A("perifetes", 20, 10, -40, "maza_golpe", "malvado", prop="maza")], fx=["polvo@0.45", "temblor@0.45"]),
  S("Teseo le quitó la maza... y se la quedó. De recuerdo.", "camino", "maza", ["dos:teseo,perifetes:0", "primer:teseo:20"],
    [A("teseo", -10, 20, 70, "golpe", "enfado"), A("perifetes", 12, 20, -70, "caer", "mareado")], fx=["golpe@0.35", "estrellas@0.4"], e_teseo2="guino"),
  S("Luego vino Sinis, el dobla-pinos.", "camino", "pinos", ["contra:sinis:0", "paisaje:spot:20"],
    [A("sinis", 0, 20, 0, "brazos", "malvado")]),
  S("Ataba a sus víctimas a dos pinos doblados, y los soltaba. Mejor no te explico el resultado.", "camino", "pinos", ["medio:sinis:30", "primer:teseo:-15"],
    [A("sinis", 10, 20, -30, "hablar", "malvado"), A("teseo", -20, 24, 40, "quieto", "sudor", prop="maza")], pinos="doblados"),
  S("Teseo le hizo exactamente lo mismo. Sinis salió volando.", "camino", "pinos", ["general:sinis:0"],
    [A("sinis", 0, 0, 0, "lanzado", "grito", to=[160, -300], h=180), A("teseo", -30, 30, 30, "brazos", "risa", prop="maza")], pinos="soltar", fx=["hojas@0.3"]),
  S("Después, Escirón, que obligaba a los viajeros a lavarle los pies al borde de un acantilado.", "camino", "acantilado", ["paisaje:spot:40", "medio:esciron:10"],
    [A("esciron", 0, -10, 0, "sentado", "malvado"), A("viajero", 0, 6, 180, "arrodillado", "triste")]),
  S("Y cuando se agachaban: ¡patada! Directos al mar, donde esperaba una tortuga gigante.", "camino", "acantilado", ["medio:viajero:60", "picado:tortuga:0"],
    [A("esciron", 0, -10, 0, "patada", "risa"), A("viajero", 0, 6, 180, "lanzado", "grito", to=[0, 180], h=40, y2=-120)], fx=["salpicar_mar@0.8"]),
  S("Teseo se agachó... y le dio la patada a él. La tortuga cenó igual.", "camino", "acantilado", ["medio:teseo:50", "picado:tortuga:0"],
    [A("teseo", 0, 10, 180, "patada", "guino", prop="maza"), A("esciron", 0, -6, 0, "lanzado", "grito", to=[0, -180], h=40, y2=-120)], fx=["salpicar_mar@0.7"]),
  S("Y el último, el peor de todos: Procusto.", "camino", "cama", ["contra:procusto:0", "primer:procusto:20"],
    [A("procusto", 0, 20, 0, "brazos", "malvado")], fx=["trueno@0.2"]),
  S("Procusto tenía una cama para invitados, y una manía: todos tenían que caber exactos.", "camino", "cama", ["medio:cama:20", "primer:procusto:-20"],
    [A("procusto", 30, 10, -50, "hablar", "malvado")]),
  S("Si eras alto, te cortaba lo que sobraba. Si eras bajito, te estiraba.", "camino", "cama", ["picado:cama:0", "primer:viajero:30"],
    [A("viajero", 0, -10, 90, "tumbado", "grito", y=10, sc=[1, 1.35, 1]), A("procusto", 24, 0, -90, "estirar", "malvado")]),
  S("Teseo lo tumbó en su propia cama. Y oye, le sobraba un poco.", "camino", "cama", ["medio:cama:-20", "primer:teseo:15"],
    [A("procusto", 0, -10, 90, "tumbado", "susto", y=10), A("teseo", 30, 14, -40, "brazos", "guino", prop="maza")]),
  S("Cuatro bandidos, cero problemas. Teseo llegó a Atenas siendo ya famoso.", "atenas", "puerta", ["paisaje:spot:0", "medio:teseo:20"],
    [A("teseo", 0, 80, 180, "andar", "risa", to=[0, 10], prop="maza"), A("aldeano1", -40, 0, 30, "celebrar", "risa"), A("aldeano2", 40, 4, -30, "celebrar", "risa"), A("aldeano3", -60, -20, 20, "saludar", "risa")]),
]})

# ---------------------------------------------------------------- CAP 4
B.append({"id": "c4", "cap": "Una copa envenenada", "segs": [
  S("En Atenas, Egeo no tenía ni idea de que aquel chico era su hijo.", "atenas", "trono", ["general:egeo:0", "primer:egeo:20"],
    [A("egeo", 0, -10, 0, "sentado", "aburrido"), A("teseo", 0, 50, 180, "quieto", "normal", prop="espada_cinto")]),
  S("Pero alguien sí lo sabía: Medea, la nueva esposa del rey. Una hechicera.", "atenas", "trono", ["primer:medea:-20", "contra:medea:10"],
    [A("medea", 26, -6, -20, "magia", "malvado"), A("egeo", 0, -10, 0, "sentado", "normal")], fx=["chispas_moradas@0.3"]),
  S("Medea quería el trono para su propio hijo. Así que convenció a Egeo de que el forastero era peligroso.", "atenas", "trono", ["dos:medea,egeo:0", "primer:egeo:15"],
    [A("medea", 12, -8, -80, "susurrar", "malvado"), A("egeo", 0, -10, 0, "sentado", "susto")]),
  S("Y preparó una copa de vino... con veneno.", "atenas", "banquete", ["primer:copa:0", "medio:medea:20"],
    [A("medea", 0, -20, 0, "verter", "malvado", prop="copa")], fx=["veneno@0.4"]),
  S("En el banquete, Egeo le ofreció la copa a Teseo.", "atenas", "banquete", ["general:mesa:0", "dos:egeo,teseo:20"],
    [A("egeo", -20, -14, 60, "ofrecer", "normal", prop="copa"), A("teseo", 20, -14, -60, "quieto", "risa"), A("medea", -40, -30, 30, "quieto", "malvado")]),
  S("Teseo, para cortar la carne, sacó la espada.", "atenas", "banquete", ["medio:teseo:-30"],
    [A("teseo", 20, -14, -60, "sacar_espada", "normal", prop="espada")], fx=["brillo@0.5"]),
  S("Egeo vio la espada... ¡y era la suya!", "atenas", "banquete", ["primer:egeo:20", "primer:espada_teseo:0"],
    [A("egeo", -20, -14, 60, "susto", "sorpresa", ico="!", prop="copa"), A("teseo", 20, -14, -60, "quieto", "normal", prop="espada")], fx=["zoom@0.1"]),
  S("Le tiró la copa de un manotazo, y el veneno se derramó por el suelo.", "atenas", "banquete", ["medio:egeo:40", "picado:veneno_suelo:0"],
    [A("egeo", -20, -14, 60, "manotazo", "grito"), A("teseo", 20, -14, -60, "susto", "susto", prop="espada")], fx=["copa_vuela@0.25", "veneno_suelo@0.5"]),
  S("¡Hijo mío!, gritó Egeo. ¡Papá!, gritó Teseo. Y Medea dijo: bueno, yo me voy.", "atenas", "banquete", ["dos:egeo,teseo:0", "medio:medea:30"],
    [A("egeo", -6, 0, 90, "abrazar", "risa"), A("teseo", 6, 0, -90, "abrazar", "risa"), A("medea", -40, -24, 200, "agachado", "sudor", to=[-90, -40])], fx=["corazones@0.2"]),
  S("Y salió huyendo en un carro tirado por dragones. Literalmente.", "atenas", "plaza", ["contra:medea:0", "paisaje:medea:30"],
    [A("medea", 0, 0, 0, "volar_carro", "malvado", to=[200, -400], h=260)], fx=["chispas_moradas@0.3"]),
]})

# ---------------------------------------------------------------- CAP 5
B.append({"id": "c5", "cap": "El tributo de Creta", "segs": [
  S("Pero la alegría duró poco. Atenas escondía un secreto horrible.", "atenas", "plaza", ["paisaje:spot:20"],
    [A("aldeano1", -30, 20, 20, "triste", "triste"), A("aldeano2", 30, 10, -20, "triste", "triste")], luz="tormenta"),
  S("Años atrás, el hijo de Minos, el rey de Creta, había muerto en Atenas.", "creta", "trono", ["contra:minos:0", "primer:minos:20"],
    [A("minos", 0, -10, 0, "sentado", "triste")]),
  S("Minos, furioso, declaró la guerra a los atenienses, la ganó, y les impuso un castigo.", "creta", "trono", ["medio:minos:20", "primer:minos:-20"],
    [A("minos", 0, 10, 0, "senalar", "enfado"), A("soldado1", -40, 0, 30, "lanza", "enfado"), A("soldado2", 40, 0, -30, "lanza", "enfado")], fx=["temblor@0.3"]),
  S("Cada nueve años, Atenas debía enviar a Creta siete chicos y siete chicas.", "mapa", "mapa", ["cenital:mapa:0", "general:barco_mapa:20"], [], mapa="ruta"),
  S("¿Para qué? Para dárselos de comer al Minotauro.", "laberinto", "centro", ["contra:minotauro:0"],
    [A("minotauro", 0, -10, 0, "rugir", "enfado")], fx=["temblor@0.4", "rugido@0.3"]),
  S("Un monstruo con cuerpo de hombre y cabeza de toro.", "laberinto", "centro", ["orbita:minotauro:0", "primer:minotauro:15"],
    [A("minotauro", 0, -10, 0, "respirar", "malvado")], fx=["vapor@0.4"]),
  S("Vivía encerrado en el Laberinto, construido por Dédalo, el mejor inventor de su época.", "creta", "taller", ["medio:dedalo:20", "cenital:laberinto_vista:0"],
    [A("dedalo", 0, 10, 0, "plano", "risa", prop="plano")]),
  S("Un laberinto tan complicado, que ni el propio Dédalo sabía salir de él.", "laberinto", "pasillo", ["picado:dedalo:0", "primer:dedalo:20"],
    [A("dedalo", 0, 0, 90, "perdido", "mareado", ico="?")]),
  S("Y ese año, otra vez, tocaba.", "atenas", "puerto", ["general:spot:20", "medio:joven1:20"],
    [A("joven1", -30, 30, 180, "andar", "triste", to=[-30, -10]), A("joven2", -10, 40, 180, "andar", "triste", to=[-10, 0]), A("joven3", 10, 34, 180, "andar", "llanto", to=[10, -6]), A("joven4", 30, 44, 180, "andar", "triste", to=[30, 4])], barco="negras", luz="tarde"),
]})

# ---------------------------------------------------------------- CAP 6
B.append({"id": "c6", "cap": "Velas negras", "segs": [
  S("Entonces Teseo dijo: voy yo. Iré como uno de los catorce, y mataré al Minotauro.", "atenas", "trono", ["contra:teseo:10", "primer:teseo:-15"],
    [A("teseo", 0, 20, 0, "espada_alto", "enfado", prop="espada"), A("egeo", 0, -10, 0, "sentado", "susto")], fx=["brillo@0.3"]),
  S("A Egeo casi le da algo.", "atenas", "trono", ["primer:egeo:10"],
    [A("egeo", 0, -10, 0, "desmayo", "mareado")]),
  S("El barco de los jóvenes llevaba velas negras, en señal de luto.", "atenas", "puerto", ["paisaje:barco:30", "contra:barco:0"], [], barco="negras", luz="tarde"),
  S("Así que Egeo le pidió una sola cosa.", "atenas", "puerto", ["dos:egeo,teseo:0"],
    [A("egeo", -12, 20, 70, "hablar", "triste"), A("teseo", 12, 20, -70, "quieto", "normal", prop="espada_cinto")], barco="negras", luz="tarde"),
  S("Si vuelves vivo, cambia las velas negras por unas blancas. Así sabré desde lejos que estás bien.", "atenas", "puerto", ["primer:egeo:20", "medio:vela_blanca:0", "primer:teseo:-20"],
    [A("egeo", -12, 20, 70, "ofrecer", "triste", prop="tela"), A("teseo", 12, 20, -70, "pulgar", "risa", prop="espada_cinto")], barco="negras", luz="tarde"),
  S("Y Teseo dijo: claro, papá. Fácil. Cómo me voy a olvidar.", "atenas", "puerto", ["primer:teseo:15"],
    [A("teseo", 12, 20, -70, "pulgar", "guino", prop="espada_cinto")], barco="negras", luz="tarde"),
  S("Spoiler: se iba a olvidar.", "atenas", "puerto", ["primer:teseo:15"],
    [A("teseo", 12, 20, -70, "pulgar", "guino", prop="espada_cinto")], barco="negras", luz="tarde", ov="spoiler", congelar=True),
  S("Y el barco zarpó rumbo a Creta.", "mar", "barco", ["paisaje:barco:40", "travel:barco:90"],
    [A("teseo", 0, 22, 0, "mirar", "normal", y="cubierta")], barco="negras", luz="tarde"),
]})

# ---------------------------------------------------------------- CAP 7
B.append({"id": "c7", "cap": "Ariadna", "segs": [
  S("En Creta, el rey Minos recibió a los jóvenes en su palacio, con columnas rojas y una sonrisa de malo de película.", "creta", "palacio", ["paisaje:spot:20", "general:minos:10", "primer:minos:-20"],
    [A("minos", 0, -20, 0, "brazos", "malvado"), A("joven1", -30, 40, 180, "quieto", "susto"), A("joven2", -10, 46, 180, "quieto", "triste"), A("teseo", 14, 40, 180, "quieto", "enfado", prop="espada_cinto"), A("joven3", 34, 46, 180, "quieto", "llanto")]),
  S("Teseo se plantó delante de él, y le dijo que era hijo de un rey, y que no le tenía miedo.", "creta", "palacio", ["dos:teseo,minos:0", "primer:teseo:20"],
    [A("teseo", 0, 10, 180, "senalar", "enfado"), A("minos", 0, -20, 0, "brazos", "sorpresa")]),
  S("Pero quien de verdad se fijó en Teseo fue Ariadna, la hija de Minos.", "creta", "palacio", ["primer:ariadna:20", "medio:ariadna:-10"],
    [A("ariadna", 30, -30, -40, "quieto", "enamorado"), A("minos", 0, -20, 0, "brazos", "malvado")], fx=["corazones@0.3"]),
  S("Se enamoró a primera vista. Pero a primera vista, ¿eh? Corazones por todas partes.", "creta", "palacio", ["primer:ariadna:0"],
    [A("ariadna", 30, -30, 0, "suspiro", "enamorado")], fx=["corazones@0.1", "corazones@0.4", "corazones@0.7"]),
  S("Esa noche, fue a verle en secreto.", "creta", "palacio", ["travel:ariadna:90", "picado:ariadna:0"],
    [A("ariadna", -60, 30, 90, "agachado", "normal", to=[20, 30], prop="antorcha")], luz="noche"),
  S("Y le dio dos cosas: una espada escondida, y un ovillo de hilo rojo.", "creta", "palacio", ["dos:ariadna,teseo:0", "primer:ovillo:0"],
    [A("ariadna", 10, 30, -80, "ofrecer", "normal", prop="ovillo"), A("teseo", -10, 30, 80, "quieto", "sorpresa", prop="espada")], luz="noche"),
  S("Ata el hilo a la entrada, le dijo. Ve soltándolo mientras avanzas. Y para salir, solo tienes que seguirlo.", "creta", "palacio", ["primer:ariadna:-20", "primer:teseo:20", "dos:ariadna,teseo:10"],
    [A("ariadna", 10, 30, -80, "hablar", "normal"), A("teseo", -10, 30, 80, "pensar", "normal", prop2="ovillo")], luz="noche"),
  S("La idea, por cierto, se la había dado el propio Dédalo.", "creta", "taller", ["primer:dedalo:20"],
    [A("dedalo", 0, 10, 0, "pulgar", "guino")], luz="noche"),
  S("A cambio, Teseo le prometió llevársela a Atenas, y casarse con ella.", "creta", "palacio", ["dos:ariadna,teseo:0", "primer:ariadna:20"],
    [A("teseo", -10, 30, 80, "mano_pecho", "risa"), A("ariadna", 10, 30, -80, "celebrar", "enamorado")], luz="noche", fx=["corazones@0.5"]),
]})

# ---------------------------------------------------------------- CAP 8
B.append({"id": "c8", "cap": "El Laberinto", "segs": [
  S("A la mañana siguiente, encerraron a los catorce jóvenes en el Laberinto.", "creta", "puerta_lab", ["general:spot:0", "medio:joven1:20"],
    [A("joven1", -20, 10, 0, "susto", "susto"), A("joven2", 0, 16, 0, "quieto", "llanto"), A("teseo", 20, 10, 0, "quieto", "enfado", prop="espada_cinto"), A("soldado1", -50, 40, 180, "lanza", "enfado"), A("soldado2", 50, 40, 180, "lanza", "enfado")], fx=["puerta@0.6"]),
  S("Teseo ató el hilo a la puerta, y entró el primero.", "laberinto", "entrada", ["medio:teseo:30", "travel:teseo:90"],
    [A("teseo", 0, 0, 90, "andar", "normal", to=[90, 0], prop2="ovillo", hilo=1)]),
  S("Giró a la izquierda. A la derecha. Otra vez a la izquierda.", "laberinto", "pasillo", ["travel:teseo:90", "picado:teseo:0", "hombro:teseo:0"],
    [A("teseo", -50, 0, 90, "andar", "normal", to=[60, 0], prop="antorcha", prop2="ovillo", hilo=1)]),
  S("Pasillos y más pasillos. Huesos por el suelo. Muy buena decoración, la verdad.", "laberinto", "pasillo", ["picado:huesos:0", "primer:teseo:20"],
    [A("teseo", 0, 0, 30, "quieto", "sudor", prop="antorcha", hilo=1)]),
  S("Y de repente... silencio.", "laberinto", "pasillo", ["primer:teseo:0"],
    [A("teseo", 0, 0, 0, "quieto", "susto", prop="antorcha", ico="!")], silencio=True),
  S("Un resoplido.", "laberinto", "centro", ["primer:minotauro:0"],
    [A("minotauro", 0, -10, 0, "respirar", "enfado")], fx=["vapor@0.2", "resoplido@0.1"]),
  S("¡El Minotauro!", "laberinto", "centro", ["contra:minotauro:20"],
    [A("minotauro", 0, -10, 0, "rugir", "enfado")], fx=["temblor@0.1", "rugido@0.0"]),
  S("Embistió con los cuernos por delante. Teseo saltó a un lado, y el Minotauro se estampó contra la pared.", "laberinto", "centro", ["general:centro:0", "medio:muro:30"],
    [A("minotauro", 0, 60, 180, "embestir", "enfado", to=[0, -66]), A("teseo", 0, -30, 0, "esquivar", "susto", prop="espada")], fx=["muro@0.75", "temblor@0.75", "estrellas@0.8"]),
  S("Pelearon durante horas. Golpe. Esquiva. Golpe.", "laberinto", "centro", ["medio:teseo:40", "primer:minotauro:-30", "dos:teseo,minotauro:0"],
    [A("teseo", -14, 0, 90, "espadazo", "enfado", prop="espada"), A("minotauro", 16, 0, -90, "pelear", "enfado")], fx=["golpe@0.3", "golpe@0.6", "golpe@0.9"]),
  S("El Minotauro era más fuerte. Pero Teseo era más listo.", "laberinto", "centro", ["primer:minotauro:20", "primer:teseo:-20"],
    [A("minotauro", 16, 0, -90, "musculos", "enfado"), A("teseo", -14, 0, 90, "pensar", "guino", prop="espada")]),
  S("Le agarró por un cuerno, se subió a su espalda...", "laberinto", "centro", ["contra:minotauro:30"],
    [A("minotauro", 0, 0, 0, "sacudir", "enfado"), A("teseo", 0, -4, 0, "montar", "grito", prop="espada")]),
  S("... y con la espada, acabó con él.", "laberinto", "centro", ["contra:minotauro:-10", "general:centro:20"],
    [A("minotauro", 0, 0, 0, "caer_grande", "mareado"), A("teseo", 0, 24, 180, "espada_alto", "enfado", prop="espada")], fx=["flash@0.15", "bloques@0.2", "temblor@0.55"]),
  S("Silencio otra vez. Teseo lo había conseguido.", "laberinto", "centro", ["contra:teseo:0", "orbita:teseo:0"],
    [A("teseo", 0, 20, 0, "espada_alto", "risa", prop="espada")], fx=["rayos"]),
  S("Ahora solo faltaba salir. Y aquí, el ovillo de lana se convierte en el mejor invento de la historia.", "laberinto", "pasillo", ["primer:teseo:20", "travel:teseo:-90", "picado:teseo:0"],
    [A("teseo", 60, 0, -90, "andar", "risa", to=[-60, 0], prop="antorcha", prop2="ovillo", hilo=1)]),
  S("Siguió el hilo, recogió a los demás jóvenes, y salieron todos vivos.", "creta", "puerta_lab", ["general:spot:0", "medio:teseo:20"],
    [A("teseo", 0, -30, 0, "andar", "risa", to=[0, 30], prop="espada"), A("joven1", -20, -50, 0, "correr", "risa", to=[-30, 20]), A("joven2", 20, -55, 0, "correr", "risa", to=[30, 20]), A("joven3", -10, -70, 0, "celebrar", "risa", to=[-10, 10]), A("joven4", 12, -75, 0, "correr", "risa", to=[14, 6])], fx=["rayos"]),
]})

# ---------------------------------------------------------------- CAP 9
B.append({"id": "c9", "cap": "La isla de Naxos", "segs": [
  S("Esa misma noche huyeron de Creta, con Ariadna, antes de que Minos se enterara.", "mar", "barco", ["general:barco:30", "medio:ariadna:20"],
    [A("teseo", -10, 20, 0, "quieto", "risa", y="cubierta"), A("ariadna", 10, 20, 0, "quieto", "enamorado", y="cubierta"), A("joven1", -30, -10, 0, "celebrar", "risa", y="cubierta")], barco="negras", luz="noche"),
  S("Pararon a descansar en la isla de Naxos.", "naxos", "playa", ["paisaje:spot:20"], [A("joven1", -40, 30, 30, "dormir", "cerrados", y=0)], barco="negras", luz="noche"),
  S("Y aquí viene la parte fea de la historia.", "naxos", "playa", ["primer:ariadna:0"],
    [A("ariadna", 0, 10, 0, "dormir", "cerrados")], luz="noche", fx=["zzz"]),
  S("Mientras Ariadna dormía, Teseo se fue. La dejó allí. Sola.", "naxos", "playa", ["travel:teseo:90", "paisaje:barco:20"],
    [A("teseo", -30, 10, 200, "agachado", "sudor", to=[0, -80]), A("ariadna", 30, 20, 0, "dormir", "cerrados")], barco="negras", barco_mueve=1, luz="noche"),
  S("Sí. Después de todo lo que hizo por él. Muy mal, Teseo. Muy mal.", "naxos", "playa", ["primer:ariadna:10", "primer:teseo_barco:0"],
    [A("ariadna", 0, 10, 0, "llorar", "llanto")], luz="amanecer"),
  S("Unos dicen que se lo ordenaron los dioses. Otros, que era un poco sinvergüenza.", "mar", "barco", ["primer:teseo:20"],
    [A("teseo", 0, 20, 0, "encoger", "sudor", y="cubierta")], barco="negras", luz="amanecer"),
  S("Por suerte, Ariadna no lloró mucho tiempo. Apareció el dios Dioniso, se enamoró de ella, y se casaron.", "naxos", "playa", ["medio:dioniso:20", "dos:ariadna,dioniso:0"],
    [A("dioniso", -14, 20, 70, "aparecer", "risa"), A("ariadna", 14, 20, -70, "quieto", "enamorado")], luz="amanecer", fx=["chispas_moradas@0.05", "corazones@0.6"]),
  S("Ariadna acabó siendo diosa. Así que, en el fondo, salió ganando.", "naxos", "playa", ["primer:ariadna:20", "paisaje:spot:0"],
    [A("ariadna", 14, 20, -30, "celebrar", "risa", ico="corona"), A("dioniso", -14, 20, 30, "celebrar", "risa")], luz="dia", fx=["chispas_doradas@0.2"]),
]})

# ---------------------------------------------------------------- CAP 10
B.append({"id": "c10", "cap": "Las velas", "segs": [
  S("Mientras tanto, en Atenas, Egeo subía cada día a lo alto de un acantilado para mirar el mar.", "atenas", "acantilado", ["paisaje:spot:30", "medio:egeo:-20"],
    [A("egeo", 0, 10, 180, "mirar", "triste")], luz="tarde"),
  S("Esperando ver unas velas blancas.", "atenas", "acantilado", ["hombro:egeo:0"],
    [A("egeo", 0, 10, 180, "mirar", "triste")], luz="tarde"),
  S("Y un día, por fin, apareció el barco.", "atenas", "acantilado", ["hombro:egeo:0", "primer:egeo:20"],
    [A("egeo", 0, 10, 180, "celebrar", "risa")], luz="tarde", barco_lejos="negras"),
  S("Con las velas...", "mar", "barco", ["contra:barco:0"], [], barco="negras", luz="tarde"),
  S("negras.", "atenas", "acantilado", ["primer:egeo:0"], [A("egeo", 0, 10, 180, "quieto", "susto")], luz="tarde", fx=["zoom@0.0"]),
  S("Teseo, con la emoción de la victoria, se había olvidado por completo.", "mar", "barco", ["medio:teseo:20", "general:barco:30"],
    [A("teseo", 0, 20, 0, "bailar", "risa", y="cubierta"), A("joven1", -24, 0, 0, "bailar", "risa", y="cubierta"), A("joven2", 24, 4, 0, "celebrar", "risa", y="cubierta")], barco="negras", luz="tarde"),
  S("Egeo pensó que su hijo había muerto. Y, destrozado, se lanzó al mar.", "atenas", "acantilado", ["primer:egeo:20", "general:spot:60"],
    [A("egeo", 0, 10, 180, "caer_acantilado", "llanto")], luz="tarde", fx=["salpicar_mar@0.85"]),
  S("Desde entonces, ese mar se llama así: el mar Egeo.", "mapa", "mapa", ["cenital:mapa:0"], [], mapa="egeo"),
  S("Teseo llegó a casa, y se encontró con que ahora, el rey... era él.", "atenas", "trono", ["medio:teseo:0", "primer:teseo:15"],
    [A("teseo", 0, -10, 0, "sentado", "triste", ico="corona")]),
]})

# ---------------------------------------------------------------- CIERRE
B.append({"id": "cierre", "cap": None, "segs": [
  S("Teseo fue un buen rey. Unió a los pueblos del Ática, y convirtió a Atenas en una gran ciudad.", "atenas", "plaza", ["paisaje:spot:20", "medio:teseo:20"],
    [A("teseo", 0, 10, 0, "saludar", "risa", ico="corona"), A("aldeano1", -40, 30, 160, "celebrar", "risa"), A("aldeano2", 40, 34, 200, "celebrar", "risa"), A("aldeano3", -20, 50, 180, "saludar", "risa"), A("joven1", 20, 50, 180, "celebrar", "risa")], luz="dia"),
  S("Pero nunca olvidó la lección más importante de su vida.", "atenas", "puerto", ["primer:teseo:20"],
    [A("teseo", 0, 20, 0, "pensar", "normal")], barco="blancas", luz="tarde"),
  S("Si tu padre te pide que cambies las velas... cambia las velas.", "atenas", "puerto", ["contra:barco:0", "primer:teseo:-15"],
    [A("teseo", 0, 20, 0, "pulgar", "guino")], barco="blancas", luz="tarde"),
  S("Si te ha gustado esta historia, suscríbete a El Bicho Curioso. En el próximo vídeo: Perseo, el chico que mató a un monstruo... sin mirarlo.", "atenas", "plaza", ["medio:teseo:0"],
    [A("teseo", 0, 10, 0, "saludar", "risa")], ov="suscribete", luz="tarde"),
]})

if __name__ == "__main__":
    json.dump(B, open("guion.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    txt = []
    for b in B:
        if b.get("cap"): txt.append(f"\n## {b['cap']}\n")
        for s in b["segs"]:
            if s["tx"]: txt.append(s["tx"])
    t = "\n".join(txt); open("guion.md", "w", encoding="utf-8").write("# Teseo y el Minotauro (guion)\n" + t + "\n")
    import re; n = len(re.findall(r"\w+", t)); print("palabras", n, "segmentos", sum(len(b["segs"]) for b in B), "≈", round(n / 165, 1), "min")
