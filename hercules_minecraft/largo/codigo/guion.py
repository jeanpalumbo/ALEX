# Guion del vídeo largo de Hércules en Minecraft. Cada bloque = (escena, capítulo, texto).
# La escena es una función del motor (escenas.js). El texto lo lee Jorge (edge-tts es-MX-JorgeNeural +5 %).
CAP = {0: "Gancho", 1: "Intro", 2: "Un bebé con problemas", 3: "Juventud y locura", 4: "El león de Nemea", 5: "La Hidra de Lerna",
       6: "La cierva y el jabalí", 7: "Los establos y los pájaros", 8: "El toro y las yeguas", 9: "Amazonas y bueyes",
       10: "Atlas y las manzanas", 11: "Cerbero", 12: "El final de Hércules"}
B = [
 # ---------- 0. gancho en frío
 ("hidra_frio", 0, "Nueve cabezas. Cada vez que le cortas una, le salen dos."),
 ("hidra_frio2", 0, "Y este señor, con un león puesto de sombrero, está a punto de descubrir que las matemáticas no están de su parte."),
 ("tinaja_frio", 0, "¿Cómo acabó el hombre más fuerte de Grecia haciendo doce trabajos imposibles para un primo que se escondía dentro de un jarrón?"),
 ("intro", 1, ""),
 # ---------- 1. nacimiento
 ("olimpo_zeus", 2, "Empecemos por la familia, que es donde empiezan todos los problemas. Hércules era hijo de Zeus, el rey de los dioses, y de una mujer mortal, Alcmena."),
 ("zeus_disfraz", 2, "Y ojo al detalle: para conquistar a Alcmena, Zeus se disfrazó de su marido. El rey de los dioses, el que lanza rayos, y su gran plan fue ponerse un bigote falso. Funcionó, eso sí."),
 ("olimpo_hera", 2, "Zeus estaba casado con Hera. Y Hera, como es lógico, no lo celebró."),
 ("hera_serpientes", 2, "Cuando Hércules era un bebé, Hera le metió dos serpientes en la cuna."),
 ("bebe_serpientes", 2, "El bebé las estranguló. Una en cada mano. Riéndose."),
 ("bebe_juega", 2, "Y luego se puso a jugar con ellas como si fueran sonajeros. Hera tomó nota."),
 ("hera_rabia", 2, "Desde ese día, Hera tuvo un objetivo en la vida: amargarle la existencia a Hércules. Y era una diosa muy constante."),
 # ---------- 2. juventud y locura
 ("lino_lira", 3, "De joven, a Hércules le pusieron profesor de música. Mala idea. Un día el profesor le regañó, y Hércules le dio con la lira en la cabeza."),
 ("lino_chiste", 3, "Fin de la clase. Y fin del profesor. Hércules era fuerte, pero de delicado tenía poco."),
 ("quiron", 3, "Así que lo mandaron al campo, a entrenar con el centauro Quirón. Allí aprendió a luchar, a usar el arco y a no tocar instrumentos musicales. Por seguridad."),
 ("tebas_familia", 3, "Creció, se casó, tuvo hijos y por un tiempo fue feliz en Tebas."),
 ("hera_locura", 3, "Pero Hera tiene paciencia. Le mandó un ataque de locura, y en esa locura Hércules hizo algo terrible contra su propia familia."),
 ("delfos", 3, "Al despertar, fue al oráculo de Delfos a preguntar cómo se arregla algo así. La respuesta: sirviendo diez años al rey Euristeo y haciendo todo lo que te pida."),
 ("euristeo_presenta", 3, "Euristeo era su primo. Era débil, era miedoso y, sobre todo, era el favorito de Hera. Lo que viene a ser trabajar para el sobrino del dueño."),
 ("bucle1", 3, "Y lo que ese primo le iba a pedir… no lo había hecho nadie jamás."),
 # ---------- 3. Nemea
 ("nemea_flechas", 4, "Primer encargo: el león de Nemea. Un león cuya piel no la atravesaba ninguna flecha, ninguna lanza y ninguna espada."),
 ("nemea_cueva", 4, "Hércules lo intentó todo. Y cuando se le acabaron las armas, hizo lo único que le quedaba: lo encerró en su cueva y lo estranguló."),
 ("nemea_piel", 4, "Luego quiso despellejarlo y descubrió un pequeño detalle: la piel tampoco la cortaba un cuchillo. Así que usó las garras del propio león. Y se la puso de abrigo."),
 ("nemea_casco", 4, "A partir de aquí, verás a Hércules siempre con la cabeza del león como casco. Es su look. No lo vamos a discutir."),
 ("nemea_vuelta", 4, "Volvió a casa con el león puesto, orgulloso, desfilando por el camino como si fuera la pasarela de Milán."),
 ("euristeo_miedo", 4, "Cuando volvió, Euristeo se asustó tanto que le prohibió entrar en la ciudad. Desde entonces, los trofeos se dejaban en la puerta."),
 # ---------- 4. Hidra
 ("hidra_llega", 5, "Segundo encargo: la Hidra de Lerna, una serpiente de agua con nueve cabezas, en un pantano que olía exactamente como te imaginas."),
 ("hidra_corta", 5, "Cada vez que cortaba una cabeza, salían dos. Cuanto mejor lo hacía, peor le iba."),
 ("hidra_yolao", 5, "La solución la trajo su sobrino Yolao: después de cada corte, quemaba el cuello con una antorcha para que no volviera a crecer."),
 ("hidra_roca", 5, "La última cabeza era inmortal, así que la enterró debajo de una roca enorme. Problema resuelto. Más o menos."),
 ("cangrejo", 5, "Mientras luchaba, Hera le mandó un cangrejo gigante para que le mordiera el pie. Hércules lo pisó. Y Hera, conmovida, lo subió al cielo: es la constelación de Cáncer."),
 ("cancer_chiste", 5, "Así que si eres Cáncer, tu signo es un cangrejo al que pisaron en su primer día de trabajo."),
 ("bucle2", 5, "Pero los encargos se iban a poner todavía más raros. Y más sucios."),
 # ---------- 5. cierva y jabalí
 ("cierva", 6, "Tercer encargo: la cierva de Cerinea, con cuernos de oro y consagrada a Artemisa. Si le hacías daño, la diosa de la caza te hacía daño a ti."),
 ("cierva_anio", 6, "Así que Hércules la persiguió sin herirla. Durante un año entero. Un año. Detrás de un ciervo."),
 ("jabali", 6, "Cuarto encargo: el jabalí de Erimanto. Hércules lo cansó a gritos, lo metió en la nieve profunda y lo cazó vivo."),
 ("tinaja", 6, "Y aquí aparece la famosa tinaja. Euristeo, al ver entrar a un hombre con un jabalí vivo a hombros, saltó dentro de una tinaja de bronce. Y desde ese día daba las órdenes desde dentro."),
 ("tinaja_chiste", 6, "El hombre más poderoso de Grecia tenía las reuniones con un jarrón."),
 # ---------- 6. establos y pájaros
 ("establos", 7, "Quinto encargo: limpiar los establos del rey Augías. Miles de vacas. Treinta años sin que nadie pasara una escoba. Y había que hacerlo en un solo día."),
 ("rios", 7, "Hércules, en lugar de una pala, usó la geografía: rompió los muros y desvió dos ríos para que pasaran por dentro. En una tarde, limpio."),
 ("no_cuenta", 7, "Pero Euristeo dijo que ese trabajo no contaba, porque le habían pagado. Y la Hidra tampoco, porque le había ayudado Yolao. Por eso los diez trabajos acabaron siendo doce. El castigo vino con letra pequeña."),
 ("pajaros", 7, "Sexto: los pájaros del lago Estínfalo. Atenea le dio unas castañuelas de bronce, Hércules las hizo sonar, los pájaros salieron volando y los fue derribando con flechas. Uno de los mayores héroes de la historia ganó una batalla haciendo ruido."),
 ("pajaros_chiste", 7, "Y no, nadie le pidió un bis."),
 ("bucle3", 7, "Y aún quedaba lo peor: un toro, unas yeguas carnívoras y una suegra disfrazada."),
 # ---------- 7. toro y yeguas
 ("toro", 8, "Séptimo: el toro de Creta. Hércules lo cazó y se lo llevó a Euristeo, que lo soltó. El toro se fue a pasear por Grecia y acabó siendo problema de otro héroe. Externalizar es muy antiguo."),
 ("yeguas", 8, "Octavo: las yeguas del rey Diómedes, que comían carne humana. Hércules derrotó a Diómedes y se lo dio de comer a sus propias yeguas. Después de cenar se volvieron mansas. Probablemente la primera dieta que funcionó."),
 # ---------- 8. amazonas y bueyes
 ("amazonas", 9, "Noveno: el cinturón de Hipólita, la reina de las amazonas. Lo sorprendente es que fue bien: Hipólita le recibió, le cayó bien y aceptó dárselo."),
 ("amazonas_hera", 9, "Entonces apareció Hera disfrazada de amazona diciendo que aquel extranjero venía a secuestrar a la reina. Las amazonas atacaron y todo acabó fatal. Una negociación perfecta, arruinada por una suegra."),
 ("columnas", 9, "Décimo: los bueyes rojos del gigante Gerión, en el fin del mundo. Por el camino, Hércules levantó dos columnas en el estrecho de Gibraltar. Las Columnas de Hércules. Hoy salen en el escudo de España."),
 ("gerion", 9, "Gerión tenía tres cuerpos y un perro de dos cabezas. Hércules se encargó de los dos. Luego tuvo que llevar los bueyes andando hasta Grecia. Imagínate el viaje: medio mundo, a pie, con un rebaño que no quería ir."),
 ("bucle4", 9, "Pero para el último trabajo, Hércules tendría que bajar al mismísimo infierno."),
 # ---------- 9. Atlas
 ("atlas", 10, "Undécimo: las manzanas de oro de las Hespérides. Nadie sabía dónde estaba el jardín, excepto el titán Atlas, condenado a sostener el cielo sobre los hombros."),
 ("atlas_trato", 10, "Hércules le propuso un trato: yo sujeto el cielo un rato y tú vas a por las manzanas. Atlas volvió con ellas, y le dijo que ya las llevaba él. Que Hércules se quedara sujetando, que no tardaba."),
 ("atlas_cojin", 10, "Hércules dijo que vale. Pero que si le aguantaba el cielo un segundo, que se iba a poner un cojín. Atlas lo cogió. Y Hércules se fue con las manzanas. El titán que sostenía el universo cayó en el truco del cojín."),
 # ---------- 10. Cerbero
 ("inframundo", 11, "Duodécimo y último: traer a Cerbero, el perro de tres cabezas que guarda la puerta del inframundo. Hades le dio permiso con una condición: sin armas."),
 ("hades", 11, "Por el camino se cruzó con almas en pena, ríos de fuego y un barquero que cobraba el viaje. Hades, el dios de los muertos, lo recibió con cara de pocos amigos. Normal. Nadie quiere visitas en el inframundo."),
 ("cerbero", 11, "Hércules bajó al reino de los muertos, agarró al perro con las manos y lo subió a la superficie."),
 ("cerbero_tinaja", 11, "Cuando llegó al palacio, Euristeo ya estaba dentro de la tinaja. Le pidió que lo devolviera. Por favor. Ya."),
 # ---------- 11. final
 ("resumen", 12, "Y así acabaron los doce trabajos. Doce años. Un león, una hidra, dos ríos desviados y un primo dentro de un jarrón."),
 ("camisa", 12, "¿Y cómo murió el hombre al que nada podía matar? Con una camisa. Su esposa, Deyanira, la empapó en la sangre de un centauro creyendo que era un filtro de amor. Era veneno."),
 ("pira", 12, "Hércules, ardiendo, construyó su propia pira y se subió a ella. Pero Zeus lo subió al Olimpo y lo convirtió en dios."),
 ("hebe", 12, "Y allí arriba, por fin, Hera hizo las paces con él. Tanto, que lo casó con su hija, Hebe. Después de doce trabajos, la última prueba fue la más dura: tener a Hera de suegra."),
 ("final_chiste", 12, "Moraleja: puedes vencer a un león, a una hidra y a un perro de tres cabezas. Pero la familia política no se vence. Se soporta."),
 ("cierre", 12, "¿Cuál de los doce te parece el peor? Dímelo en comentarios. Y suscríbete a El Bicho Curioso, que el próximo héroe también tiene una suegra complicada."),
]
