// Perseo y Medusa: reparto, criaturas, objetos y las 84 escenas (acción + cámaras). Misma API que Hércules.
import { THREE, personaje, pose, cara, cuadrupedo, animaCuadrupedo, serpienteCadena, colocaCadena, pajaro, caja, liso, MAT, D, cl, lerp, sm, seg, eout, back, muelle, rnd } from "./motor.js";
import { scene, part } from "./mundo.js";
import { estatua } from "./sets.js";
// ===================== reparto (skins propias)
const P0 = { seed: 151, piel: "#e0a878", pelo: "#6a3a1a", ropa: "#3f6fb5", cinto: "#c48a2c", falda: 1, sandalia: "#5a3a1a", flequillo: 1, brazalete: "#c8a040" };
export const C = {
  PER: personaje(P0, 1.05), PERH: personaje(Object.assign({}, P0, { seed: 152, capa: "#c83a2f", sandalia: "#e8e8e8" }), 1.05),
  PERC: personaje(Object.assign({}, P0, { seed: 153, capa: "#c83a2f", sandalia: "#e8e8e8", casco: "#4a4a5a", cascoPenacho: "#2a2a3a" }), 1.05),
  NINO: personaje(Object.assign({}, P0, { seed: 154, ropa: "#8ab0e0" }), 0.75),
  BEBE: personaje({ seed: 141, piel: "#f2c49a", pelo: "#6a3a1a", ropa: "#ffffff", cinto: "#f0e0c0", falda: 1, flequillo: 1 }, 0.45),
  DANAE: personaje({ seed: 161, piel: "#f0c8a0", pelo: "#c27a3a", ropa: "#d870a0", cinto: "#f2e0a0", faldaLarga: 1, melena: 1, escote: 1, ribete: "#f2e0a0" }, 1),
  ACRI: personaje({ seed: 162, piel: "#e8b88e", pelo: "#e8e8e8", barba: "#f2f2f2", ropa: "#7a2a4a", cinto: "#e0b040", faldaLarga: 1, corona: 1, capa: "#4a1a2a", ribete: "#e0b040" }, 1.05),
  ORAC: personaje({ seed: 163, piel: "#d8b090", pelo: "#2a1a10", ropa: "#6a4aa8", faldaLarga: 1, melena: 1, ojos: "#7a3ab8", laurel: 1 }, 1),
  ZEUS: personaje({ seed: 31, piel: "#e8b88e", pelo: "#e8e8e8", barba: "#f2f2f2", ropa: "#f2efe6", cinto: "#3d6fb5", ribete: "#3d6fb5", faldaLarga: 1, laurel: 1 }, 1.2),
  DICTIS: personaje({ seed: 164, piel: "#c8885a", pelo: "#5a4a3a", barba: "#5a4a3a", ropa: "#8a7a5a", cinto: "#5a3a1a", falda: 1, sandalia: "#5a3a1a", calvo: 1 }, 1),
  DICTISR: personaje({ seed: 165, piel: "#c8885a", pelo: "#5a4a3a", barba: "#5a4a3a", ropa: "#3f6fb5", cinto: "#e0b040", faldaLarga: 1, corona: 1, calvo: 1 }, 1),
  POLI: personaje({ seed: 166, piel: "#e0b08a", pelo: "#1a1a1a", bigote: "#1a1a1a", ropa: "#6a2a8a", cinto: "#e0b040", faldaLarga: 1, corona: 1, capa: "#2a0a3a", ojos: "#2a1a1a" }, 1.05),
  ATENEA: personaje({ seed: 69, piel: "#e8c0a0", pelo: "#2a1a10", ropa: "#c8c8d8", faldaLarga: 1, cascoPenacho: "#3f6fb5", casco: "#c8a040", melena: 1, ojos: "#3a6a9a" }, 1.1),
  HERMES: personaje({ seed: 167, piel: "#e8b88e", pelo: "#c8a040", ropa: "#e8e0c0", cinto: "#5f9e3a", falda: 1, sandalia: "#e8e8e8", casco: "#d9a630", capa: "#5f9e3a" }, 1.05),
  POSE: personaje({ seed: 168, piel: "#7ab0c0", pelo: "#2a6a8a", barba: "#3a8aaa", ropa: "#1a5a7a", faldaLarga: 1, corona: 1, ojos: "#0a2a4a" }, 1.6),
  GREA1: personaje({ seed: 171, piel: "#a8a8a0", pelo: "#d8d8d8", ropa: "#5a5a5a", faldaLarga: 1, melena: 1, ojos: "#a8a8a0" }, 0.95),
  GREA2: personaje({ seed: 172, piel: "#9a9a92", pelo: "#c8c8c8", ropa: "#4a4a50", faldaLarga: 1, melena: 1, ojos: "#9a9a92" }, 0.95),
  GREA3: personaje({ seed: 173, piel: "#b0aaa0", pelo: "#e8e8e8", ropa: "#5a4a4a", faldaLarga: 1, melena: 1, ojos: "#b0aaa0" }, 0.95),
  MEDH: personaje({ seed: 174, piel: "#f0c8a0", pelo: "#e8c050", ropa: "#f2efe6", cinto: "#e0b040", faldaLarga: 1, melena: 1, ojos: "#3a7a5a" }, 1),
  MED: personaje({ seed: 175, piel: "#7aa86a", pelo: "#2a5a2a", ropa: "#2a4a3a", cinto: "#c8a040", faldaLarga: 1, ojos: "#ffe040", calvo: 1, capa: "#1a3a2a" }, 1.05),
  GOR1: personaje({ seed: 176, piel: "#6a8a6a", pelo: "#2a4a2a", ropa: "#3a3a4a", faldaLarga: 1, ojos: "#ff5a2a", calvo: 1 }, 1.15),
  GOR2: personaje({ seed: 177, piel: "#8a9a6a", pelo: "#3a4a2a", ropa: "#4a3a3a", faldaLarga: 1, ojos: "#ff5a2a", calvo: 1 }, 1.15),
  ATLAS: personaje({ seed: 65, piel: "#c88a5a", pelo: "#5a3a1a", barba: "#5a3a1a", ropa: "#5a4a3a", falda: 1, desnudo: 1, cinto: "#3a2a1a" }, 4.2),
  ANDRO: personaje({ seed: 178, piel: "#8a5a3a", pelo: "#1a1a1a", ropa: "#f2efe6", cinto: "#e0b040", faldaLarga: 1, melena: 1, ojos: "#3a2a1a" }, 1),
  CASIO: personaje({ seed: 179, piel: "#9a6a4a", pelo: "#1a1a1a", ropa: "#d9a630", cinto: "#7f2a3a", faldaLarga: 1, melena: 1, corona: 1, ribete: "#7f2a3a" }, 1.05),
  CEFEO: personaje({ seed: 180, piel: "#8a5a3a", pelo: "#2a2a2a", barba: "#3a3a3a", ropa: "#3f6fb5", cinto: "#e0b040", faldaLarga: 1, corona: 1 }, 1.05),
  NINFA1: personaje({ seed: 181, piel: "#f0d0b0", pelo: "#5f9e3a", ropa: "#7fbf4a", faldaLarga: 1, melena: 1, laurel: 1 }, 0.95),
  NINFA2: personaje({ seed: 182, piel: "#e8c0a0", pelo: "#c8a040", ropa: "#5aa08a", faldaLarga: 1, melena: 1, laurel: 1 }, 0.95),
  NOVIO: personaje({ seed: 183, piel: "#a87a5a", pelo: "#1a1a1a", bigote: "#1a1a1a", ropa: "#8a3b3b", peto: "#c8a040", falda: 1, cascoPenacho: "#1a1a1a", casco: "#a8afbd" }, 1.05),
  GUARDIA: personaje({ seed: 184, piel: "#d39a6a", pelo: "#3a2414", ropa: "#8a3b3b", peto: "#c8a040", falda: 1, cascoPenacho: "#c83a2f", casco: "#a8afbd" }, 1),
};
for (const k in C) scene.add(C[k].root);
// fantasma (casco de Hades): copia transparente de Perseo con casco
const PERG = personaje(Object.assign({}, P0, { seed: 153, capa: "#c83a2f", sandalia: "#e8e8e8", casco: "#4a4a5a", cascoPenacho: "#2a2a3a" }), 1.05);
PERG.root.traverse(o => { if (o.isMesh) { const f = m => { const c = m.clone(); c.transparent = true; c.opacity = 0.28; c.emissive = new THREE.Color("#203a6a"); c.depthWrite = false; return c; }; o.material = Array.isArray(o.material) ? o.material.map(f) : f(o.material); } });
PERG.S.cabeza = () => PERG.cabeza.material; C.PERG = PERG; scene.add(PERG.root);
// sandalias aladas
for (const ch of [C.PERH, C.PERC, PERG]) for (const l of [ch.lR, ch.lL]) { const w = new THREE.Group(); w.name = "ala"; for (const s of [-1, 1]) w.add(caja(0.6, 3, 5, liso("#ffffff", 0.04, 4), s * 2.6, -3.4, -1.5)); l.kn.add(w); }
// alas de Gorgona y pelo de serpientes
function alas(ch, col) { const a = []; for (const s of [-1, 1]) { const p = new THREE.Group(); p.position.set(s * 3, 9, -2.4); const ala = caja(18, 1, 12, liso(col, 0.12, 4), s * 9, 0, -2); p.add(ala); ch.torso.add(p); a.push(p); } ch.alas = a; }
alas(C.MED, "#3a6a4a"); alas(C.GOR1, "#c8a040"); alas(C.GOR2, "#b07a3a");
function pelo(ch, n = 9, c1 = "#3f8f3a", c2 = "#d9c040") { ch.serp = []; for (let i = 0; i < n; i++) { const s = serpienteCadena(i % 2 ? c1 : "#2f7a2a", c2, 7, 1.5, 300 + i); ch.cuello.add(s.g); ch.serp.push(s); } }
pelo(C.MED); pelo(C.GOR1, 7, "#4a7a3a"); pelo(C.GOR2, 7, "#5a8a3a");
function aleteo(ch, t, f = 9, amp = 0.5) { if (ch.alas) ch.alas.forEach((a, i) => a.rotation.z = (i ? -1 : 1) * (0.2 + amp * Math.sin(t * f))); }
function serpPelo(ch, t, fur = 0) { if (!ch.serp) return; ch.serp.forEach((s, i) => { const a = (i / ch.serp.length) * Math.PI * 2, bx = Math.sin(a) * 3.6, bz = Math.cos(a) * 3.6 - 0.5;
  colocaCadena(s, u => { const uu = 1 - u, w = Math.sin(t * (3 + fur * 4) + i * 1.7 + u * 5) * (1.5 + fur * 2); return [bx + Math.sin(a) * uu * 6 + w * Math.cos(a), 7.5 + uu * (3 + 2 * Math.sin(i)) + (fur ? Math.sin(t * 9 + i) * 1.5 : 0), bz + Math.cos(a) * uu * 6 - w * Math.sin(a)]; });
  s.lengua.scale.z = Math.max(0, Math.sin(t * 8 + i)); }); }
// ---- criaturas
export const K = {
  PEGASO: cuadrupedo({ seed: 190, color: "#f4f4f8", largo: 22, alto: 11, patas: 15, ancho: 10, melena: "#e8e8ff", cola: 5, hocico: "#e0d8e0", orejas: 1, escala: 1.1 }),
  CABALLO: cuadrupedo({ seed: 191, color: "#8a5a3a", largo: 20, alto: 11, patas: 14, ancho: 9, melena: "#3a2a1a", cola: 5, hocico: "#6a4a3a" }),
};
for (const k in K) scene.add(K[k].g);
{ const p = K.PEGASO; p.alas = []; for (const s of [-1, 1]) { const a = new THREE.Group(); a.position.set(s * 5, 9, 4); a.add(caja(24, 1.2, 12, liso("#ffffff", 0.04, 4), s * 12, 0, 0)); a.add(caja(10, 1.2, 8, liso("#e8eeff", 0.04, 4), s * 28, 0, -2)); p.cuerpo.add(a); p.alas.push(a); } }
// Ceto: monstruo marino de bloques
const CETO = serpienteCadena("#2a4a7a", "#7ab0d0", 20, 16, 195); scene.add(CETO.g); CETO.segs[0].scale.set(1.7, 1.3, 2.0);
for (let k = 0; k < 6; k++) CETO.segs[0].add(caja(1.6, 3.4, 1.6, liso("#fffbe8", 0.03, 4), -4 + k * 1.6, -5, 7));
// Cielo que sujeta Atlas
const CIELOBOLA = new THREE.Group(); { const mt = MAT.brillo("#2a3a8a"); for (let i = -2; i <= 2; i++) for (let j = -2; j <= 2; j++) for (let k = -2; k <= 2; k++) if (i * i + j * j + k * k <= 5) CIELOBOLA.add(caja(10, 10, 10, (i + j + k) % 2 ? mt : MAT.brillo("#3a4aa8"), i * 10, j * 10, k * 10)); for (let s = 0; s < 18; s++) CIELOBOLA.add(caja(2, 2, 2, MAT.brillo("#ffffff"), (rnd(s) - 0.5) * 50, (rnd(s + 3) - 0.5) * 50, 26)); } scene.add(CIELOBOLA);
// objetos
const ESCUDO = new THREE.Group(); ESCUDO.add(caja(12, 12, 1.2, liso("#c89a4a", 0.06, 4), 0, 0, 0)); ESCUDO.add(caja(10, 10, 0.4, MAT.brillo("#e8f0ff"), 0, 0, 0.8)); ESCUDO.position.set(0, -2, 3);
const REFLEJO = caja(9, 9, 0.2, C.MED.S.caras.malvado, 0, 0, 1.1); REFLEJO.visible = false; ESCUDO.add(REFLEJO);
const ESPADA = new THREE.Group(); ESPADA.add(caja(1.4, 14, 0.6, liso("#d0d4dc", 0.05, 4), 0, -9, 0)); ESPADA.add(caja(5, 1.4, 0.6, liso("#d0d4dc", 0.05, 4), 2.4, -16, 0)); ESPADA.add(caja(5, 1.2, 1.2, MAT.oro, 0, -2, 0)); ESPADA.add(caja(1.4, 3, 1.4, MAT.madera, 0, 0, 0)); ESPADA.rotation.x = Math.PI / 2;
const BOLSA = new THREE.Group(); BOLSA.add(caja(8, 9, 6, liso("#8a6a3a", 0.12, 4), 0, -5, 0)); BOLSA.add(caja(5, 2, 4, liso("#c8a040", 0.1, 4), 0, -0.5, 0)); const BOLSALUZ = caja(6, 1, 4, MAT.brillo("#7aff9a"), 0, 0.2, 0); BOLSALUZ.visible = false; BOLSA.add(BOLSALUZ);
const CABEZA = new THREE.Group(); CABEZA.add(caja(8, 8, 8, C.MED.S.cabeza("malvado"), 0, 0, 0)); for (let i = 0; i < 6; i++) { const s = serpienteCadena("#3f8f3a", "#d9c040", 5, 1.4, 320 + i); colocaCadena(s, u => { const a = i; return [Math.sin(a) * (3 + (1 - u) * 4), 4 + (1 - u) * 3, Math.cos(a) * (3 + (1 - u) * 4)]; }); CABEZA.add(s.g); } CABEZA.rotation.y = Math.PI;
const OJO = new THREE.Group(); OJO.add(caja(4, 4, 4, MAT.brillo("#ffffff"))); OJO.add(caja(2, 2, 0.6, MAT.brillo("#3a6ac8"), 0, 0, 2)); OJO.add(caja(1, 1, 0.6, MAT.brillo("#000"), 0, 0, 2.3)); scene.add(OJO);
const COFRE = new THREE.Group(); COFRE.add(caja(30, 12, 18, MAT.madera, 0, 6, 0)); const TAPA = new THREE.Group(); TAPA.position.set(0, 12, -9); TAPA.add(caja(31, 3, 19, liso("#7a5032", 0.1, 8), 0, 1.5, 9)); COFRE.add(TAPA); COFRE.add(caja(4, 4, 1, MAT.oro, 0, 10, 9.2)); scene.add(COFRE);
const DISCO = caja(9, 2, 9, liso("#a8a8b0", 0.08, 4)); scene.add(DISCO);
const ESPEJO = new THREE.Group(); ESPEJO.add(caja(1, 6, 1, MAT.oro, 0, -4, 0)); ESPEJO.add(caja(6, 7, 1, MAT.oro, 0, 2, 0)); ESPEJO.add(caja(4.6, 5.6, 0.4, MAT.brillo("#e8f0ff"), 0, 2, 0.7));
const TRIDENTE = new THREE.Group(); TRIDENTE.add(caja(1.4, 40, 1.4, MAT.oro, 0, -10, 0)); for (const x of [-3, 0, 3]) TRIDENTE.add(caja(1.2, 7, 1.2, MAT.oro, x, 12, 0)); TRIDENTE.add(caja(8, 1.2, 1.2, MAT.oro, 0, 9, 0)); TRIDENTE.rotation.x = Math.PI / 2;
const LANZA = new THREE.Group(); LANZA.add(caja(1.2, 40, 1.2, MAT.madera, 0, -10, 0)); LANZA.add(caja(2.4, 5, 1.2, liso("#d0d4dc", 0.05, 4), 0, 12, 0)); LANZA.rotation.x = Math.PI / 2;
const NUBE = new THREE.Group(); for (let i = 0; i < 5; i++) NUBE.add(caja(14, 9, 12, liso("#4a4a54", 0.05, 4), (i - 2) * 9, (i % 2) * 3, 0)); scene.add(NUBE);
const GOTAS = []; for (let i = 0; i < 24; i++) { const g = caja(0.6, 4, 0.6, MAT.brillo("#8ab0e0")); NUBE.add(g); GOTAS.push(g); }
const CONS = new THREE.Group(); scene.add(CONS);
function constelacion(nombre, pts, cx, cy, col = "#fff6b0") { const g = new THREE.Group(); pts.forEach(([x, y]) => g.add(caja(16, 16, 16, MAT.brillo(col), x, y, 0))); for (let i = 0; i < pts.length - 1; i++) { const [a1, b1] = pts[i], [a2, b2] = pts[i + 1]; for (let k = 1; k < 5; k++) g.add(caja(4, 4, 4, MAT.brillo("#c8d8ff"), a1 + (a2 - a1) * k / 5, b1 + (b2 - b1) * k / 5, 0)); } g.position.set(cx, cy, -650); g.name = nombre; CONS.add(g); return g; }
const KPER = constelacion("perseo", [[0, 0], [30, 60], [10, 120], [60, 160], [-30, 170], [80, 40]], -260, 380), KAND = constelacion("andromeda", [[0, 0], [60, 20], [120, 50], [180, 60], [100, -20]], 40, 460),
  KCAS = constelacion("casiopea", [[0, 0], [40, 50], [80, 0], [120, 50], [160, 0]], 300, 330), KPEG = constelacion("pegaso", [[0, 0], [90, 0], [90, -80], [0, -80], [-60, -120], [150, 40]], -80, 280);
const FL = new THREE.PointLight("#ff8a3a", 0, 400, 1.4); scene.add(FL);
const TODOS = [...Object.values(C).map(c => c.root), ...Object.values(K).map(k => k.g), CETO.g, CIELOBOLA, OJO, COFRE, DISCO, NUBE, CONS];
// materiales sustituidos (petrificar)
const _piedra = liso("#9a968c", 0.14, 8, 501); const PETR = new Set();
function petrifica(ch, q) { const r = ch.root; r.updateMatrixWorld(true); const y0 = r.position.y, H = 32 * (ch.escala || 1), lim = y0 + q * H * 1.15, v = new THREE.Vector3(); PETR.add(ch);
  r.traverse(o => { if (!o.isMesh) return; if (o.userData.m0 === undefined) o.userData.m0 = o.material; o.getWorldPosition(v); o.material = v.y < lim ? _piedra : o.userData.m0; }); }
function despetrifica() { PETR.forEach(ch => ch.root.traverse(o => { if (o.isMesh && o.userData.m0 !== undefined) o.material = o.userData.m0; })); PETR.clear(); }
let CUR_INV = null;
export function ocultaTodo() { despetrifica(); TODOS.forEach(o => o.visible = false); FL.intensity = 0; REFLEJO.visible = false; BOLSALUZ.visible = false; CONS.children.forEach(c => c.visible = false);
  for (const ch of Object.values(C)) { ch.cabeza.visible = true; ch.root.rotation.z = 0; }
  [ESCUDO, ESPADA, BOLSA, CABEZA, ESPEJO, TRIDENTE, LANZA].forEach(o => o.parent && o.parent.remove(o)); for (const o of [OJO, DISCO]) if (o.parent !== scene) scene.add(o); }
function enCodo(ch, obj) { if (obj.parent !== ch.aL.el) ch.aL.el.add(obj); }
function P(ch, p, t, expr) { ch.root.visible = true; pose(ch, p, t); if (expr) cara(ch, expr); return ch; }
function enMano(ch, obj, lado = "R") { const m = lado === "R" ? ch.aR.mano : ch.aL.mano; if (obj.parent !== m) m.add(obj); }
function andar(lt, a, b, t0, t1, extra = {}) { const q = cl((lt - t0) / (t1 - t0)), x = lerp(a[0], b[0], q), z = lerp(a[1], b[1], q), ry = Math.atan2(b[0] - a[0], b[1] - a[1]) / D;
  const mov = lt > t0 && lt < t1; return Object.assign({ x, z, ry, andar: (x + z) / (extra.correr ? 4 : 5.5), amp: mov ? 1 : Math.max(0, 1 - Math.abs(lt - t1) / 0.2) * (lt > t1 ? 0 : 1) }, extra); }
const habla = (X, ch, base = "normal", umbral = 0.35) => cara(ch, X.env(X.t) > umbral ? "habla" : base);
const gestoHabla = (X, k = 0) => ({ bR: [-35 + 25 * Math.sin(X.t * 3.1 + k), 12 + 8 * Math.sin(X.t * 2 + k)], cR: 45 + 20 * Math.sin(X.t * 2.3 + k), bL: [-10 + 10 * Math.sin(X.t * 1.7 + k), -6], cL: 15 });
const golpe = (lt, t0, lado = "R") => { const an = seg(lt, t0 - 0.3, t0, x => x * x), hit = seg(lt, t0, t0 + 0.1, x => x), rec = seg(lt, t0 + 0.4, t0 + 0.9); const b = [lerp(lerp(0, 40, an), -95, hit) * (1 - rec), lerp(lerp(0, 20, an), -8, hit) * (1 - rec)], c = lerp(lerp(10, 110, an), 0, hit) * (1 - rec) + 10;
  return lado === "R" ? { bR: b, cR: c, giro: lerp(lerp(0, 30, an), -20, hit) * (1 - rec), lean: lerp(lerp(0, -6, an), 12, hit) * (1 - rec) } : { bL: [b[0], -b[1]], cL: c, giro: -lerp(lerp(0, 30, an), -20, hit) * (1 - rec), lean: lerp(lerp(0, -6, an), 12, hit) * (1 - rec) }; };
const arriba = (lt, t0, s = 1) => { const q = seg(lt, t0, t0 + 0.3, x => back(x, 2)); return { bR: [-170 * q, 18 * q * s], bL: [-170 * q, -18 * q * s], cR: 15, cL: 15 }; };
const encoge = (lt, t0) => { const q = seg(lt, t0, t0 + 0.25) * (1 - seg(lt, t0 + 1.2, t0 + 1.5)); return { bR: [-40 * q, 55 * q], bL: [-40 * q, -55 * q], cR: 80 * q, cL: 80 * q, cabZ: 10 * q, sq: 1 - 0.04 * q }; };
const brazosCruz = q => ({ bR: [-30 * q, 38 * q], bL: [-30 * q, -38 * q], cR: 95 * q, cL: 95 * q });
const senala = (lt, t0) => { const q = seg(lt, t0, t0 + 0.25, x => back(x, 2)); return { bR: [-90 * q, 10 * q], cR: 0 }; };
const susto = (lt, t0) => { const q = seg(lt, t0, t0 + 0.15, eout), sal = Math.sin(cl((lt - t0) / 0.35) * Math.PI) * 8; return { salto: sal, lean: -14 * q, bR: [-150 * q, 40 * q], bL: [-150 * q, -40 * q], cR: 20, cL: 20 }; };
const hombros = () => ({ bR: [-175, 25], bL: [-175, -25], cR: 50, cL: 50 });          // sujetar algo sobre los hombros/cabeza
const mezcla = (...o) => Object.assign({}, ...o);
function quad(k, x, z, ry, t, v = 0, extra = {}, y = 0) { const c = K[k]; c.g.visible = true; c.g.position.set(x, y, z); c.g.rotation.set(extra.rx || 0, ry * D, extra.rz || 0); animaCuadrupedo(c, t, v, extra); return c; }
const pos = ch => (ch.root || ch.g).position;
const alto = ch => (ch.escala || 1) * 28;
function cara_(ch, d = 34, lado = 0.35, fov = 32, dy = 0) { const p = pos(ch), ry = (ch.root || ch.g).rotation.y, h = p.y + alto(ch) + dy; const dx = Math.sin(ry), dz = Math.cos(ry), sx = Math.cos(ry), sz = -Math.sin(ry), dd = d * 2.1 * (ch.escala || 1);
  return [p.x + dx * dd + sx * dd * lado, h + 2, p.z + dz * dd + sz * dd * lado, p.x, h - 1, p.z, fov]; }
const medio = (ch, lado = 1, d = 70, fov = 38) => () => { const p = pos(ch), h = alto(ch) * 0.75, e = ch.escala || 1; return [p.x + lado * d * 0.45 * e, p.y + h + 4, p.z + d * e, p.x, p.y + h, p.z, fov]; };
const cerca = (ch, d, lado, fov, dy) => () => cara_(ch, d, lado, fov, dy);
const general = (x, z, dist = 200, h = 60, tx = x, ty = 25, fov = 40) => () => [x, h, z + dist, tx, ty, z, fov];
const contra = (ch, lado = -1, d = 60) => () => { const p = pos(ch), e = ch.escala || 1; return [p.x + lado * 30 * e, p.y + 5, p.z + d * e, p.x, p.y + alto(ch) * 1.4, p.z, 46]; };
const picado = (x, z, h = 170, d = 90, fov = 42) => () => [x + 20, h, z + d, x, 0, z, fov];
const fija = (...v) => () => v;
const sigue = (ch, dx, dy, dz, fov = 40, ty = 24) => () => { const p = pos(ch); return [p.x + dx, p.y + dy, p.z + dz, p.x, p.y + ty, p.z, fov]; };
// ---- utilidades propias de Perseo
const med = (ch, p, t, expr, fur = 0, vuelo = 0) => { P(ch, p, t, expr); serpPelo(ch, t, fur); aleteo(ch, t, vuelo ? 9 : 2, vuelo ? 0.5 : 0.08); return ch; };
const vuela = (x, y, z, ry, t, extra = {}) => mezcla({ x, y: y + 2 * Math.sin(t * 2.4), z, ry, rx: 1.05, bR: [-150, 12], bL: [-150, -12], cR: 0, cL: 0, pR: 15, pL: 25, kR: 20, kL: 10, cabX: -45 }, extra);
function alasPies(ch, t, f = 14) { for (const l of [ch.lR, ch.lL]) { const w = l.kn.getObjectByName("ala"); if (w) w.children.forEach((c, i) => c.rotation.y = (i ? -1 : 1) * 0.5 * Math.sin(t * f)); } }
function pegaso(x, y, z, ry, t, v = 0, alas = 1) { const p = K.PEGASO; p.g.visible = true; p.g.position.set(x, y, z); p.g.rotation.set(0, ry * D, 0); animaCuadrupedo(p, t, v); p.alas.forEach((a, i) => a.rotation.z = (i ? -1 : 1) * (alas ? 0.15 + 0.6 * Math.sin(t * 6) : -0.9)); return p; }
function oroLluvia(X, x, y, z) { for (let k = 0; k < Math.floor(X.lt / 0.25); k++) if (X.una("oro" + k)) part.add(X.t0 + k * 0.25, x, y, z, 6, ["#ffd040", "#fff1a0", "#d9a630"], 12, 1.0, 60, 1.8, k % 3 === 0); }
function brillo(X, k, lt0, x, y, z, cols = ["#ffffff", "#fff1a0", "#9ad8ff"], n = 30) { if (X.una(k)) part.add(X.t0 + lt0, x, y, z, Math.round(n * 0.6), cols, 30, 0.9, 10, 1.4, false); }
function cofre(x, y, z, ry, abierto = 0, rz = 0) { COFRE.visible = true; COFRE.position.set(x, y, z); COFRE.rotation.set(0, ry * D, rz); TAPA.rotation.x = -abierto * 1.6; }
function estatuaAux(k) { return k; }
const ojo = (x, y, z, s = 1) => { OJO.visible = true; if (OJO.parent !== scene) scene.add(OJO); OJO.position.set(x, y, z); OJO.scale.setScalar(s); OJO.rotation.y = 0; };
const ojoMano = ch => { OJO.visible = true; if (OJO.parent !== ch.aR.mano) ch.aR.mano.add(OJO); OJO.position.set(0, -1, 2); OJO.scale.setScalar(0.8); };
const W = (X, s, k = 0) => X.w(s, k);
// ===================== ESCENAS
const PE = C.PER, PH = C.PERH, PC = C.PERC, PG = C.PERG;
export const E = {
  // ---------- gancho: la cueva de las estatuas
  gancho_cueva: { set: "cueva_gorgonas", act(X) { const { t, lt } = X; P(PH, mezcla(andar(lt, [-60, 120], [10, 20], 0, 5.5), { bL: [-60, 30], cL: 70, cabY: 25 * Math.sin(t * 0.9) }), t, lt > 3 ? "susto" : "sudor"); enCodo(PH, ESCUDO); enMano(PH, ESPADA); alasPies(PH, t); },
    cams: [() => [lerp(-160, -60, X_lt() / 5), 70, 230, 0, 30, -60, 42], () => [60, 22, 60, -60, 30, -60, 40]] },
  gancho_mirada: { set: "cueva_gorgonas", act(X) { const { t, lt } = X; const g = C.GUARDIA; P(g, { x: -40, z: 0, ry: 20, bR: [-60, 10], cR: 50, cabX: -10 }, t, "sorpresa"); petrifica(g, seg(lt, 1.0, 3.0));
      med(C.MED, { x: 40, z: -60, ry: 0, bR: [-40, 30], cR: 60 }, t, "malvado", 1); },
    cams: [cerca(C.GUARDIA, 34, 0.3, 32), cerca(C.MED, 26, -0.1, 28)] },
  gancho_escudo: { set: "cueva_gorgonas", act(X) { const { t, lt } = X; P(PH, { x: 0, z: 30, ry: 180, bL: [-90, -10], cL: 80, cabY: 10 * Math.sin(t * 2) }, t, "cerrados"); enCodo(PH, ESCUDO); REFLEJO.visible = true; enMano(PH, ESPADA); alasPies(PH, t);
      med(C.MED, { x: 20, z: -70, ry: 10, bR: [-30, 20], cR: 40 }, t, "malvado", 1); },
    cams: [() => [18, 46, 70, 0, 33, 33, 30], () => [-60, 34, 110, 10, 30, -20, 40], cerca(C.MED, 32, 0.2, 30)] },
  gancho_casco: { set: "cueva_gorgonas", act(X) { const { t, lt } = X; const inv = lt > 2.2; if (!inv) { P(PH, mezcla({ x: 0, z: 40, ry: 0 }, arriba(lt, 0.6)), t, "presumido"); enCodo(PH, ESCUDO); }
      else { P(PG, { x: 0, z: 40, ry: 0, bL: [-60, -20], cL: 60 }, t, lt > 4.2 ? "espiral" : "sudor"); brillo(X, "inv", 2.2, 0, 30, 40, ["#9ad8ff", "#ffffff"]); } },
    cams: [medio(PH, 1, 90), cerca(PG, 34, 0.25, 32)] },
  intro: { set: "vuelo_nubes", act(X) { const { t, lt } = X; P(PH, vuela(lerp(-160, 160, lt / 4.2), 230, 0, 90, t), t, "risa"); alasPies(PH, t); X.titulo(lt); },
    cams: [() => [0, 260, 220, 0, 230, 0, 40]] },
  // ---------- capítulo 1
  argos: { set: "tebas", act(X) { const { t, lt } = X; P(C.ACRI, mezcla(andar(lt, [-100, 70], [-20, 60], 0, 3)), t, "presumido"); X.dato("ARGOS · Grecia"); }, cams: [() => [lerp(-120, -40, X_lt() / 3), 70, 150, 0, 30, -60, 42]] },
  acrisio_hijo: { set: "palacio", act(X) { const { t, lt } = X; P(C.ACRI, mezcla({ x: 0, z: -100, ry: 0 }, gestoHabla(X)), t, lt < 4 ? "normal" : "triste"); P(C.DANAE, { x: 50, z: -80, ry: -30, cabY: -10 }, t, lt < 4 ? "risa" : "normal"); },
    cams: [general(0, -100, 180, 50), cerca(C.ACRI, 32, 0.3), medio(C.DANAE, -1, 80)] },
  oraculo: { set: "delfos", act(X) { const { t, lt } = X; P(C.ORAC, { x: -40, z: -60, ry: 20, bR: [-150, 30], bL: [-150, -30], cR: 20, cL: 20, cabZ: 12 * Math.sin(t * 2) }, t, lt > W(X, "nieto") - 0.2 ? "malvado" : "espiral"); P(C.ACRI, { x: 40, z: 20, ry: -150 }, t, lt > W(X, "matar") ? "susto" : "sorpresa"); },
    cams: [() => [-90, 30, 60, -10, 30, -40, 40], cerca(C.ORAC, 32, -0.2), cerca(C.ACRI, 30, 0.3, 30)] },
  oraculo_chiste: { set: "delfos", act(X) { const { t, lt } = X; P(C.ACRI, mezcla({ x: 40, z: 20, ry: 20 }, brazosCruz(seg(lt, 0, 0.4))), t, "enfado"); P(C.ORAC, mezcla({ x: -40, z: -60, ry: 20 }, encoge(lt, 0.8)), t, "presumido"); }, cams: [cerca(C.ACRI, 30, 0.1, 30)] },
  danae_plan: { set: "palacio", act(X) { const { t, lt } = X; P(C.ACRI, mezcla({ x: 0, z: -60, ry: lt < 6 ? 0 : 60 }, lt < 6 ? { bR: [-120, 30], cR: 120, cabX: 10 } : senala(lt, 6.2)), t, lt < 3 ? "normal" : (lt < 6 ? "presumido" : "malvado"));
      P(C.DANAE, mezcla(lt < 6.5 ? { x: 60, z: -30, ry: -40 } : andar(lt, [60, -30], [180, 20], 6.6, 9.6), lt < 6.5 ? {} : {}), t, lt < 6.5 ? "normal" : "triste");
      if (lt > 6.5) P(C.GUARDIA, andar(lt, [40, -30], [160, 20], 6.6, 9.6), t, "normal"); },
    cams: [cerca(C.ACRI, 32, 0.3), medio(C.ACRI, 1, 90), general(80, -20, 200, 60)] },
  torre: { set: "torre", act(X) { const { t, lt } = X; P(C.GUARDIA, { x: -40, z: -60, ry: 0 }, t, "normal"); }, cams: [() => [60, lerp(40, 230, sm(X_lt() / 6.7)), 200, 0, lerp(60, 230, sm(X_lt() / 6.7)), -120, 44], () => [-140, 30, 160, 0, 120, -120, 46]] },
  torre_dentro: { set: "torre_interior", act(X) { const { t, lt } = X; P(C.DANAE, mezcla({ x: -40, z: -60, ry: 20, sentado: lt < 5 ? 1 : 0, y: lt < 5 ? 8 : 0 }, lt > 5 ? andar(lt, [-40, -60], [0, -10], 5, 7.5) : { cabZ: 15 * Math.sin(t * 0.8), bR: [-60, 20], cR: 100 }), t, lt < 5 ? "triste" : "normal"); },
    cams: [() => [0, 60, 140, -10, 30, -40, 44], cerca(C.DANAE, 32, 0.2), () => [10, 10, 60, 0, 140, -10, 44]] },
  lluvia_oro: { set: "torre_interior", act(X) { const { t, lt } = X; oroLluvia(X, 0, 150, -10); P(C.DANAE, mezcla({ x: 0, z: 10, ry: 0, cabX: -30 }, lt > 2.5 ? arriba(lt, 2.6) : {}), t, lt < 2.5 ? "sorpresa" : "amor"); FL.intensity = 500; FL.color.set("#ffd040"); FL.position.set(0, 80, 0); },
    cams: [() => [0, 30, 110, 0, 70, -10, 46], cerca(C.DANAE, 30, 0.2, 30)] },
  nace_perseo: { set: "torre_interior", act(X) { const { t, lt } = X; P(C.DANAE, { x: 0, z: 0, ry: 0, bR: [-50, 30], bL: [-50, -30], cR: 70, cL: 70, cabX: 20 }, t, "amor"); P(C.BEBE, { x: 0, y: 13, z: 9, ry: 0, bR: [-120, 20 * Math.sin(t * 5)], bL: [-120, -20 * Math.sin(t * 5)], salto: 0.5 * Math.sin(t * 6) }, t, "risa");
      if (X.una("cor")) part.add(X.t0 + 0.4, 0, 30, 10, 18, ["#ff8ab0", "#ffffff"], 15, 1.2, 5, 2, true); X.dato("NIETO DE ACRISIO"); },
    cams: [() => [0, 30, 90, 0, 22, 0, 36], cerca(C.BEBE, 40, 0.1, 30)] },
  // ---------- capítulo 2
  acrisio_panico: { set: "torre_interior", act(X) { const { t, lt } = X; P(C.ACRI, mezcla(andar(lt, [80, 60], [40, 20], 0, 1.4), lt > 2 ? { salto: Math.abs(Math.sin(t * 9)) * 2, cabY: 15 * Math.sin(t * 7) } : {}), t, lt < 2 ? "susto" : (lt < 6 ? "sudor" : "malvado"));
      if (lt > 0.9 && lt < 1.4) C.ACRI.extras.position.y = 6 * seg(lt, 0.9, 1.3); else C.ACRI.extras.position.y = lt >= 1.4 && lt < 2.4 ? 6 * (1 - seg(lt, 2, 2.4)) : 0;
      P(C.DANAE, { x: -20, z: -10, ry: 30, bR: [-50, 30], bL: [-50, -30], cR: 70, cL: 70 }, t, "triste"); P(C.BEBE, { x: -16, y: 13, z: -2, ry: 30, bR: [-150, 20], bL: [-150, -20] }, t, "lloro"); },
    cams: [cerca(C.ACRI, 30, 0.3, 30), cerca(C.BEBE, 36, 0.2, 30), medio(C.ACRI, -1, 100)] },
  cofre_mete: { set: "creta", act(X) { const { t, lt } = X; const cerr = seg(lt, 2.8, 3.6); cofre(0, 0, 60, 0, 1 - cerr); if (lt < 3) { P(C.DANAE, { x: 0, z: 60, y: 2, ry: 0, sentado: 1, bR: [-50, 30], bL: [-50, -30], cR: 70, cL: 70 }, t, "lloro"); P(C.BEBE, { x: 2, y: 12, z: 66, ry: 0 }, t, "lloro"); }
      P(C.ACRI, mezcla({ x: -40, z: 50, ry: 70 }, lt > 4 ? { bR: [-90, 0], bL: [-90, 0], cR: 0, cL: 0, lean: 25 } : gestoHabla(X)), t, lt > 4 ? "malvado" : "presumido"); if (lt > 4.4) cofre(lerp(0, 40, seg(lt, 4.4, 6.4)), 0, lerp(60, 140, seg(lt, 4.4, 6.4)), 0, 0); },
    cams: [() => [-60, 40, 200, 0, 15, 60, 40], cerca(C.ACRI, 30, 0.3, 30), () => [80, 30, 200, 20, 10, 100, 42]] },
  cofre_mar: { set: "mar_tormenta", act(X) { const { t, lt } = X; cofre(lerp(-40, 40, lt / 5.6), 4 + 6 * Math.sin(t * 1.6), 0, 20 * Math.sin(t * 0.7), 0, 0.25 * Math.sin(t * 1.3)); X.dato("TÉCNICAMENTE… FUE EL MAR"); },
    cams: [() => [0, 50, 160, 0, 10, 0, 40], () => [80, 20, 70, 0, 10, 0, 34]] },
  zeus_vigila: { set: "olimpo", act(X) { const { t, lt } = X; P(C.ZEUS, mezcla({ x: 0, z: 40, ry: 0, lean: 10, cabX: 25 }, lt < 4.6 ? { bR: [-160, 20], cR: 120 } : senala(lt, 4.8)), t, lt < 4.6 ? "normal" : "risa"); X.dato("ISLA DE SÉRIFOS", 5); },
    cams: [cerca(C.ZEUS, 34, 0.3, 32), () => [-80, 50, 160, 0, 40, 40, 40], () => [60, 30, 120, 0, 40, 40, 36]] },
  dictis_red: { set: "playa_serifos", act(X) { const { t, lt } = X; const ab = seg(lt, 4.6, 5.4); P(C.DICTIS, mezcla({ x: -20, z: 140, ry: 10 }, lt < 4 ? { lean: 20 + 10 * Math.sin(t * 4), bR: [-60 + 20 * Math.sin(t * 4), 10], bL: [-60 + 20 * Math.sin(t * 4), -10], cR: 30, cL: 30 } : {}), t, lt < 4.6 ? "sudor" : "sorpresa");
      cofre(10, 0, lerp(210, 175, seg(lt, 0, 4)), 30, ab); if (lt > 5.3) { P(C.DANAE, { x: 10, y: 8, z: 175, ry: 180, bR: [-60, 30], cR: 70 }, t, "risa"); P(C.BEBE, { x: 6, y: 20, z: 168, ry: 180, bR: [-150, 20 * Math.sin(t * 6)], bL: [-150, -20] }, t, "risa"); } },
    cams: [() => [-120, 40, 230, -10, 15, 160, 42], cerca(C.DICTIS, 30, 0.3, 30), () => [40, 40, 90, 10, 15, 175, 36]] },
  crece: { set: "playa_serifos", act(X) { const { t, lt } = X; const ch = lt < 2.4 ? C.NINO : PE; P(ch, mezcla(andar(lt, [-100, 60], [20, 40], 0, 3.2), lt > 3.6 ? { bR: [-30, 40], bL: [-30, -40], cR: 110, cL: 110 } : {}), t, lt > 3.6 ? "presumido" : "risa");
      if (X.una("pop")) part.add(X.t0 + 2.4, ch.root.position.x, 20, 50, 20, ["#ffffff", "#e8e8e8"], 25, 1.5, 10, 1); },
    cams: [() => [lerp(-140, 0, X_lt() / 3), 30, 160, lerp(-100, 20, X_lt() / 3.2), 20, 40, 40], cerca(PE, 30, 0.2, 30)] },
  // ---------- capítulo 3
  polidectes: { set: "palacio", act(X) { const { t, lt } = X; P(C.POLI, { x: 0, z: -60, ry: 0, bR: [-60, 30 + 10 * Math.sin(t * 8)], bL: [-60, -30 - 10 * Math.sin(t * 8)], cR: 80, cL: 80 }, t, "malvado"); X.dato("POLIDECTES, rey de Sérifos"); },
    cams: [() => [0, 30, 60, 0, 30, -60, 38], cerca(C.POLI, 30, -0.2, 30)] },
  estorbo: { set: "playa_serifos", act(X) { const { t, lt } = X; P(C.DANAE, { x: 0, z: 40, ry: 90 }, t, "normal"); P(C.POLI, mezcla(andar(lt, [140, 40], [50, 40], 0, 2), lt > 3 ? { lean: -10 } : {}), t, lt < 3 ? "amor" : "susto");
      if (lt > 2.2) P(PE, mezcla(andar(lt, [-40, 70], [25, 40], 2.2, 3), brazosCruz(seg(lt, 3, 3.3))), t, "enfado"); },
    cams: [general(40, 40, 170, 40), cerca(C.POLI, 30, 0.3, 30), contra(PE, 1, 60)] },
  plan_banquete: { set: "banquete", act(X) { const { t, lt } = X; P(C.POLI, mezcla({ x: 0, z: -160, ry: 0 }, gestoHabla(X)), t, X.env(X.t) > 0.35 ? "habla" : "malvado"); },
    cams: [() => [0, 50, 160, 0, 20, -80, 44], cerca(C.POLI, 32, 0.3), () => [-150, 30, 90, -150, 12, 60, 40]] },
  sin_caballo: { set: "banquete", act(X) { const { t, lt } = X; P(PE, mezcla(andar(lt, [60, 120], [20, 50], 0, 2), lt > 2.5 ? { bR: [-10, 30], bL: [-10, -30], cR: 10, cL: 10 } : {}, lt > 4 ? encoge(lt, 4) : {}), t, lt < 4 ? "normal" : "triste");
      if (lt > 2.8 && X.una("pol")) part.add(X.t0 + 2.9, 20, 12, 52, 6, ["#c8b890"], 6, 0.8, 30, 1.2); },
    cams: [medio(PE, 1, 90), cerca(PE, 30, -0.2, 30), () => [0, 30, 160, 20, 20, 50, 40]] },
  frase: { set: "banquete", act(X) { const { t, lt } = X; P(PE, mezcla({ x: 20, z: 50, ry: -10, lean: -6 }, arriba(lt, 0.3)), t, X.env(X.t) > 0.35 ? "grito" : "presumido"); }, cams: [contra(PE, -1, 60), cerca(PE, 34, 0.3, 32)] },
  silencio: { set: "banquete", act(X) { const { t, lt } = X; P(PE, { x: 20, z: 50, ry: -10, bR: [-170, 10], bL: [-170, -10] }, t, "presumido"); P(C.POLI, { x: 0, z: -160, ry: 0 }, t, lt > 2 ? "malvado" : "sorpresa"); }, cams: [() => [0, 40, 150, 20, 30, 0, 50], cerca(C.POLI, 28, 0.2, 28)] },
  tarde: { set: "banquete", act(X) { const { t, lt } = X; P(PE, { x: 20, z: 50, ry: -10, bR: [-170 * (1 - seg(lt, 0.6, 1.4)), 10], bL: [-170 * (1 - seg(lt, 0.6, 1.4)), -10] }, t, lt < 1.5 ? "presumido" : (lt < 2.6 ? "susto" : "sudor")); }, cams: [cerca(PE, 30, 0.1, 28)] },
  // ---------- capítulo 4
  gorgonas: { set: "isla_gorgonas", act(X) { const { t, lt } = X; med(C.MED, { x: 0, z: 20, ry: 0, y: 4 * Math.sin(t * 2) }, t, "malvado", 1, 1); med(C.GOR1, { x: -60, y: 30 + 6 * Math.sin(t * 2), z: -10, ry: 20 }, t, "malvado", 0.5, 1); med(C.GOR2, { x: 60, y: 26 + 6 * Math.sin(t * 2 + 1), z: -10, ry: -20 }, t, "risa", 0.5, 1);
      if (lt < W(X, "única") - 0.3) X.dato("ESTENO Y EURÍALE: INMORTALES", W(X, "inmortales") - 0.3); else X.dato("MEDUSA: MORTAL", W(X, "única") - 0.3); },
    cams: [general(0, 0, 200, 50, 0, 35), cerca(C.GOR1, 30, 0.2, 30, 0), cerca(C.MED, 32, 0.2, 30)] },
  sacerdotisa: { set: "templo_atenea", act(X) { const { t, lt } = X; P(C.MEDH, { x: 0, z: -40, ry: 180, bR: [-160, 25], bL: [-160, -25], cR: 20, cL: 20 }, t, "cerrados"); }, cams: [() => [90, 30, 20, 0, 40, -80, 42], cerca(C.MEDH, 40, 0.3, 34)] },
  castigo: { set: "templo_atenea", act(X) { const { t, lt } = X; P(C.MEDH, mezcla(lt < 4 ? andar(lt, [40, -60], [-60, -40], 0.5, 3.5, { correr: 1 }) : { x: -60, z: -40, ry: 30 }), t, lt < 6 ? "susto" : "lloro");
      if (lt < 4.5) { P(C.POSE, mezcla(andar(lt, [140, -80], [10, -60], 0.8, 4.2), { cabY: -10 }), t, "amor"); enMano(C.POSE, TRIDENTE); }
      if (lt > 4.3) { P(C.ATENEA, mezcla({ x: 60, z: -20, ry: -60 }, senala(lt, 4.6)), t, "enfado"); enMano(C.ATENEA, LANZA, "L"); } },
    cams: [general(0, -60, 220, 60), cerca(C.ATENEA, 32, 0.3), cerca(C.MEDH, 30, -0.3, 30)] },
  transforma: { set: "templo_atenea", act(X) { const { t, lt } = X; const tr = lt > 1.2; if (!tr) P(C.MEDH, { x: -60, z: -40, ry: 30, bR: [-120, 40], bL: [-120, -40], cR: 90, cL: 90 }, t, "susto");
      else med(C.MED, { x: -60, z: -40, ry: 30, bR: [-40, 30], cR: 60 }, t, "malvado", 1); brillo(X, "tr", 1.0, -60, 30, -40, ["#7aff9a", "#3f8f3a", "#ffffff"], 50); },
    cams: [cerca(C.MED, 30, 0.2, 30)] },
  petrifica: { set: "isla_gorgonas", act(X) { const { t, lt } = X; const g = C.GUARDIA; P(g, mezcla({ x: 0, z: 40, ry: 180 }, lt < 2 ? { lean: -6 } : {}), t, "susto"); petrifica(g, seg(lt, 1.6, 4.0)); med(C.MED, { x: 0, z: -20, ry: 0 }, t, "malvado", 1);
      if (X.una("crk")) part.add(X.t0 + 2.2, 0, 10, 40, 14, ["#9a968c", "#6d6a64"], 20, 1, 60, 1.4); },
    cams: [() => [50, 20, 110, 0, 20, 40, 36], cerca(C.MED, 28, 0.1, 26)] },
  // ---------- capítulo 5
  perseo_fatal: { set: "playa_serifos", act(X) { const { t, lt } = X; P(PE, { x: 0, z: 40, ry: 10, sentado: 1, y: 8, bR: [-80, 20], bL: [-80, -20], cR: 120, cL: 120, cabX: 20 }, t, "triste");
      NUBE.visible = true; NUBE.position.set(0, 70, 40); GOTAS.forEach((g, i) => { const q = (t * 1.8 + rnd(i)) % 1; g.position.set((rnd(i * 3) - 0.5) * 40, -q * 40, (rnd(i * 7) - 0.5) * 10); }); X.dato("¿DÓNDE VIVE MEDUSA?", 3); },
    cams: [() => [0, 40, 150, 0, 40, 40, 38], cerca(PE, 34, 0.25, 30, -6)] },
  dioses_llegan: { set: "playa_serifos", act(X) { const { t, lt } = X; const a = seg(lt, 0.5, 1.3, back), h = seg(lt, 1.2, 2.0, back);
      if (lt > 0.5) { P(C.ATENEA, { x: -50, z: 20, ry: 30, y: (1 - a) * 60 }, t, "presumido"); enMano(C.ATENEA, LANZA, "L"); } if (lt > 1.2) P(C.HERMES, { x: 50, z: 20, ry: -30, y: (1 - h) * 60 + 3 * Math.sin(t * 5) }, t, "risa");
      P(PE, { x: 0, z: 50, ry: 180, sentado: lt < 3 ? 1 : 0, y: lt < 3 ? 8 : 0 }, t, "sorpresa"); brillo(X, "a", 0.5, -50, 30, 20); brillo(X, "h", 1.2, 50, 30, 20, ["#ffffff", "#ffe040"]); },
    cams: [general(0, 20, 190, 50), cerca(C.HERMES, 30, -0.2, 30)] },
  regalos: { set: "playa_serifos", act(X) { const { t, lt } = X; const t1 = W(X, "escudo") - 0.3, t2 = W(X, "espada") - 0.3;
      P(C.ATENEA, mezcla({ x: -40, z: 20, ry: 40 }, lt < t1 + 1 ? { bR: [-80, 10], cR: 20 } : {}), t, "presumido"); P(C.HERMES, mezcla({ x: 50, z: 20, ry: -40, y: 3 * Math.sin(t * 5) }, lt > t2 - 0.2 && lt < t2 + 1.2 ? { bR: [-80, 10], cR: 20 } : gestoHabla(X, 2)), t, "risa");
      P(PE, mezcla({ x: 0, z: 50, ry: 180 }, lt > t2 + 1 ? { bR: [-150, 10], cR: 10 } : {}), t, lt > t1 ? "risa" : "sorpresa"); if (lt > t1 + 0.6) enCodo(PE, ESCUDO); else enMano(C.ATENEA, ESCUDO);
      if (lt > t2 + 0.8) enMano(PE, ESPADA); else enMano(C.HERMES, ESPADA); brillo(X, "e1", t1 + 0.6, 0, 20, 50, ["#ffe040", "#ffffff"]); brillo(X, "e2", t2 + 0.8, 0, 20, 50, ["#e8f0ff", "#ffffff"]); },
    cams: [cerca(C.ATENEA, 32, 0.3), () => [-40, 30, 150, 0, 25, 40, 36], cerca(C.HERMES, 30, -0.3), contra(PE, 1, 70)] },
  inventario1: { set: "playa_serifos", act(X) { const { t, lt } = X; P(PE, mezcla({ x: 0, z: 40, ry: 0 }, { bR: [-150, 10], cR: 10 }), t, lt < 4 ? "presumido" : "sudor"); enCodo(PE, ESCUDO); enMano(PE, ESPADA); X.inv(lt < 3.5 ? 2 : 2, lt); },
    cams: [() => [70, 30, 120, 0, 30, 40, 36], cerca(PE, 34, -0.2, 30)] },
  ninfas_dir: { set: "playa_serifos", act(X) { const { t, lt } = X; P(PE, mezcla({ x: -20, z: 40, ry: 30 }, encoge(lt, 0.4)), t, "sudor"); P(C.HERMES, mezcla({ x: 40, z: 30, ry: -40, y: 3 * Math.sin(t * 5) }, encoge(lt, 2.2)), t, "risa"); X.dato("DIRECCIÓN: ¿?"); }, cams: [() => [10, 30, 140, 10, 25, 30, 38]] },
  // ---------- capítulo 6: las Greas
  greas: { set: "cueva_greas", act(X) { const { t, lt } = X; [C.GREA1, C.GREA2, C.GREA3].forEach((g, i) => P(g, { x: -40 + i * 40, z: -150 + Math.abs(i - 1) * 14, ry: (i - 1) * -25, sentado: 1, bR: [-40, 10], cR: 40, cabY: 10 * Math.sin(t + i) }, t, i === 1 ? "risa" : "cerrados"));
      if (lt > W(X, "ojo") - 0.4) ojo(0, 22 + 3 * Math.sin(t * 3), -136, 1); X.dato("1 OJO · 1 DIENTE · 3 ABUELAS", W(X, "ojo")); },
    cams: [() => [lerp(-120, 120, X_lt() / 10), 60, 60, 0, 20, -150, 42], cerca(C.GREA2, 30, 0.2, 30), () => [0, 24, -100, 0, 22, -140, 36]] },
  greas_pelea: { set: "cueva_greas", act(X) { const { t, lt } = X; const s = lt < 1.9; P(C.GREA1, { x: -40, z: -136, ry: 25, sentado: 1, bR: [-80, -20], cR: 20 }, t, s ? "grito" : "enfado"); P(C.GREA3, { x: 40, z: -136, ry: -25, sentado: 1, bR: [-80, 20], cR: 20 }, t, s ? "enfado" : "grito"); P(C.GREA2, { x: 0, z: -150, ry: 0, sentado: 1, cabY: 30 * Math.sin(t * 4) }, t, "sudor");
      ojo(lerp(-20, 20, 0.5 + 0.5 * Math.sin(t * 3)), 26, -128, 1); }, cams: [() => [0, 30, -60, 0, 20, -140, 40], cerca(C.GREA1, 28, 0.3, 30)] },
  ojo_robo: { set: "cueva_greas", act(X) { const { t, lt } = X; const z = W(X, "zas") - 0.1; P(C.GREA1, { x: -40, z: -136, ry: 25, sentado: 1, bR: [-80, -20], cR: 20 }, t, "habla"); P(C.GREA3, { x: 40, z: -136, ry: -25, sentado: 1, bR: [-80, 20 + 20 * seg(lt, z, z + 0.3)], cR: 20 }, t, lt > z ? "susto" : "normal"); P(C.GREA2, { x: 0, z: -150, ry: 0, sentado: 1 }, t, "normal");
      P(PH, mezcla(lt < z - 0.4 ? { x: 70, z: -60, ry: -140, lean: 20, sq: 0.9 } : andar(lt, [70, -60], [20, -110], z - 0.4, z, { correr: 1 }), lt > z ? { bR: [-150, 10], cR: 0 } : {}), t, lt < z ? "sudor" : "risa");
      if (lt < z) ojo(lerp(-20, 30, seg(lt, 0, z)), 26, -128, 1); else ojoMano(PH); },
    cams: [() => [100, 30, -10, 30, 20, -110, 40], cerca(PH, 30, 0.3, 30), () => [0, 24, -90, 20, 22, -120, 40]] },
  greas_ciegas: { set: "cueva_greas", act(X) { const { t, lt } = X; [C.GREA1, C.GREA2, C.GREA3].forEach((g, i) => P(g, { x: -50 + i * 50 + 10 * Math.sin(t * 1.5 + i), z: -130, ry: 20 * Math.sin(t + i * 2), bR: [-90, 20 * Math.sin(t * 3 + i)], bL: [-90, -20 * Math.sin(t * 3 + i)], cR: 0, cL: 0, andar: t * 3, amp: 0.4 }, t, i === 1 ? "grito" : "lloro"));
      P(PH, mezcla({ x: 50, z: -60, ry: -150 }, gestoHabla(X)), t, X.env(X.t) > 0.35 ? "habla" : "presumido"); ojoMano(PH); },
    cams: [() => [0, 50, 20, 0, 20, -120, 46], cerca(PH, 30, 0.2, 30), cerca(C.GREA2, 30, -0.2, 30)] },
  // ---------- capítulo 7: equipo completo
  ninfas: { set: "jardin", act(X) { const { t, lt } = X; const ws = [W(X, "sandalias") - 0.2, W(X, "bolsa") - 0.2, W(X, "casco") - 0.2];
      P(C.NINFA1, mezcla({ x: -40, z: -10, ry: 40 }, lt > ws[0] && lt < ws[0] + 1.4 ? { bR: [-80, 0], cR: 10 } : {}), t, "risa"); P(C.NINFA2, mezcla({ x: 40, z: -10, ry: -40 }, lt > ws[2] && lt < ws[2] + 1.4 ? { bR: [-80, 0], cR: 10 } : {}), t, "amor");
      P(lt > ws[0] + 0.6 ? PH : PE, { x: 0, z: 30, ry: 180, salto: lt > ws[2] ? Math.abs(Math.sin(t * 6)) * 3 : 0 }, t, "risa"); if (lt > ws[1] + 0.6) enMano(PH, BOLSA, "L");
      ws.forEach((w, i) => brillo(X, "n" + i, w + 0.6, 0, 20, 30, ["#7aff9a", "#ffffff", "#ffe040"])); X.inv(lt < ws[0] + 0.6 ? 2 : lt < ws[1] + 0.6 ? 3 : lt < ws[2] + 0.6 ? 4 : 5, lt); },
    cams: [general(0, 0, 180, 50), cerca(C.NINFA1, 30, 0.3, 30), cerca(PH, 30, -0.2, 30)] },
  vuelo_arbol: { set: "jardin", act(X) { const { t, lt } = X; const sal = W(X, "salto") - 0.1, choque = W(X, "Directo") - 0.05;
      let p; if (lt < sal) p = { x: -80, z: 20, ry: 120, sq: 1 - 0.1 * seg(lt, sal - 0.5, sal) }; else if (lt < choque) { const q = seg(lt, sal, choque, x => x * x); p = { x: lerp(-80, -10, q), y: lerp(0, 80, q), z: lerp(20, -90, q), ry: 150, rx: 0.9 }; }
      else { const q = seg(lt, choque + 0.4, choque + 1.4, x => x * x); p = { x: -10, y: lerp(80, 0, q), z: -90, ry: 180, rz: 1.4 * seg(lt, choque, choque + 0.3) * (1 - seg(lt, choque + 1.5, choque + 2)) }; }
      P(PH, mezcla(p, lt > choque ? { bR: [-120, 40], bL: [-120, -40] } : { bR: [-170, 10], bL: [-170, -10] }), t, lt < sal ? "presumido" : (lt < choque ? "risa" : (lt < choque + 2 ? "espiral" : "sudor"))); alasPies(PH, t);
      if (X.una("hoj")) part.add(X.t0 + choque, -10, 90, -100, 40, ["#3f8f2e", "#4a9a3a", "#d9a03c"], 30, 1.4, 30, 2.5); },
    cams: [() => [-60, 40, 160, -40, 40, -40, 44], () => [40, 60, 40, -10, 70, -100, 40], cerca(PH, 30, 0.3, 30)] },
  vuelo_nubes: { set: "vuelo_nubes", act(X) { const { t, lt } = X; P(PH, vuela(0, 230, 0, 0, t, { rz: 0.15 * Math.sin(t * 1.3) }), t, "risa"); alasPies(PH, t); enMano(PH, BOLSA, "L"); },
    cams: [(X) => [60 - 20 * X.lt, 236, 70, 0, 238, 0, 40], (X) => [-50, 228, -60 + 10 * X.lt, 0, 240, 0, 40], () => [-70, 232, 40, 0, 240, -20, 36]] },
  // ---------- capítulo 8: la guarida
  isla: { set: "isla_gorgonas", act(X) { const { t, lt } = X; const q = seg(lt, 0.3, 2.6); P(PH, mezcla({ x: lerp(-200, 0, q), y: lerp(140, 0, q), z: lerp(-100, 40, q), ry: 120 }, q < 1 ? { rx: 0.6 * (1 - q) } : {}), t, "sudor"); enCodo(PH, ESCUDO); alasPies(PH, t); },
    cams: [() => [100, 60, 200, -20, 40, 0, 44]] },
  estatuas: { set: "isla_gorgonas", act(X) { const { t, lt } = X; P(PH, mezcla(andar(lt, [-140, 80], [40, -40], 0, 7.2), { bL: [-50, 20], cL: 70, cabY: 30 * Math.sin(t * 0.8) }), t, "susto"); enCodo(PH, ESCUDO); enMano(PH, ESPADA); },
    cams: [sigue(PH, 60, 30, 70, 40), () => [-60, 30, 120, -120, 25, 20, 38], cerca(PH, 30, 0.4, 30)] },
  casco_invisible: { set: "cueva_gorgonas", act(X) { const { t, lt } = X; const c = W(X, "invisible") - 0.6; [C.MED, C.GOR1, C.GOR2].forEach((g, i) => med(g, { x: -50 + i * 50, z: -140, ry: 0, sentado: 1, y: 4, cabX: 25 }, t, "dormido", 0.2));
      if (lt < c) { P(PH, mezcla({ x: 0, z: 60, ry: 0 }, arriba(lt, c - 0.8)), t, "presumido"); enCodo(PH, ESCUDO); } else { P(PG, { x: 0, z: 60, ry: 0 }, t, "risa"); brillo(X, "i", c, 0, 30, 60, ["#9ad8ff", "#ffffff"]); } },
    cams: [() => [0, 40, 140, 0, 20, -80, 44], cerca(PG, 32, 0.2, 30)] },
  reflejo: { set: "cueva_gorgonas", act(X) { const { t, lt } = X; P(PG, mezcla(andar(lt, [0, 60], [0, -40], 0.5, 6.8), { ry: 0, bL: [-90, -10], cL: 80 }), t, "cerrados"); PG.root.rotation.y = 0; enCodo(PG, ESCUDO); REFLEJO.visible = lt > W(X, "reflejo") - 0.5; enMano(PG, ESPADA);
      med(C.MED, { x: 0, z: -140, ry: 0, sentado: 1, y: 4, cabX: 25 }, t, "dormido", 0.3); },
    cams: [sigue(PG, 14, 44, 32, 30, 32), () => [-80, 30, 0, 0, 20, -100, 44]] },
  atras: { set: "cueva_gorgonas", act(X) { const { t, lt } = X; const oj = W(X, "abrió") - 0.3; P(PG, mezcla({ x: 0, z: lerp(-40, -100, seg(lt, 0, oj)), ry: 0, andar: lt * 4, amp: lt < oj ? 0.5 : 0, bL: [-90, -10], cL: 80 }), t, lt < oj ? "cerrados" : "sudor"); enCodo(PG, ESCUDO); REFLEJO.visible = true; enMano(PG, ESPADA);
      med(C.MED, { x: 0, z: -140, ry: 0, sentado: 1, y: 4, cabX: 25 }, t, "dormido", lt > oj ? 1 : 0.3); },
    cams: [() => [40, 20, -40, 0, 20, -140, 34], cerca(C.MED, 22, 0.1, 24), cerca(PG, 28, 0.2, 28)] },
  corte: { set: "cueva_gorgonas", act(X) { const { t, lt } = X; const g = W(X, "golpe") - 0.2; P(PG, mezcla({ x: 0, z: -110, ry: 180 }, golpe(lt, g)), t, "enfado"); enMano(PG, ESPADA); FL.intensity = lt > g && lt < g + 0.25 ? 6000 : 0; FL.color.set("#ffffff"); FL.position.set(0, 40, -100);
      if (lt < g + 0.05) med(C.MED, { x: 0, z: -140, ry: 0, sentado: 1, y: 4, cabX: 25 }, t, "susto", 1); else { med(C.MED, { x: 0, z: -140, ry: 0, sentado: 1, y: 4, cabX: 25 }, t, "dormido", 0); C.MED.cabeza.visible = false; C.MED.serp.forEach(s => s.g.visible = false); }
      if (X.una("c")) part.add(X.t0 + g + 0.05, 0, 30, -140, 30, ["#7aa86a", "#3f8f3a", "#2a5a2a"], 50, 1.2, 60, 1.6); },
    cams: [() => [40, 40, -40, 0, 26, -130, 40]] },
  bolsa: { set: "cueva_gorgonas", act(X) { const { t, lt } = X; const cr = W(X, "Crisaor") - 0.3, pg = W(X, "Pegaso") - 0.3; P(PG, { x: 0, z: -100, ry: 180, bR: [-60, 20], cR: 60, cabY: 60 }, t, "cerrados"); enMano(PG, BOLSA, "L"); BOLSALUZ.visible = true;
      if (lt < 1.4) { enMano(PG, CABEZA); } if (lt > cr) { brillo(X, "cr", cr, 0, 20, -140, ["#ffd040", "#ffffff"], 40); } if (lt > pg) { pegaso(lerp(0, 60, seg(lt, pg, lt + 99)), 0, -150, 30, t, 0, 1); brillo(X, "pg", pg, 0, 20, -140, ["#ffffff", "#9ad8ff"], 40); } },
    cams: [cerca(PG, 30, 0.2, 30), () => [60, 40, -20, 0, 20, -140, 44]] },
  pegaso: { set: "isla_gorgonas", act(X) { const { t, lt } = X; const q = seg(lt, 1.5, 5.8, x => x * x); pegaso(lerp(0, 120, q), lerp(0, 200, q), lerp(0, -200, q), 160, t, lt > 1.5 ? 0 : 0.3, lt > 0.6 ? 1 : 0); if (X.una("p")) part.add(X.t0 + 0.6, 0, 20, 0, 30, ["#ffffff"], 30, 1.2, 10, 1.5, true); },
    cams: [() => [60, 30, 120, 0, 30, 0, 40], () => [-60, 10, 100, lerp(0, 100, seg(X_lt(), 1.5, 5.8)), lerp(20, 180, seg(X_lt(), 1.5, 5.8)), -100, 48]] },
  // ---------- capítulo 9: la huida
  hermanas: { set: "isla_gorgonas", act(X) { const { t, lt } = X; const d = lt > 1; med(C.GOR1, { x: -40 + (d ? 40 * Math.sin(t) : 0), y: d ? 40 + 10 * Math.sin(t * 2) : 0, z: 0, ry: d ? 60 * Math.sin(t * 1.3) : 0, bR: [-150, 30], bL: [-150, -30] }, t, d ? "grito" : "dormido", d ? 1 : 0.2, d);
      med(C.GOR2, { x: 40 - (d ? 40 * Math.sin(t * 1.1) : 0), y: d ? 50 + 10 * Math.sin(t * 2 + 1) : 0, z: -20, ry: d ? -60 * Math.sin(t) : 0, bR: [-150, 30], bL: [-150, -30] }, t, d ? "enfado" : "dormido", d ? 1 : 0.2, d); },
    cams: [() => [0, 30, 170, 0, 40, -10, 44], cerca(C.GOR1, 30, 0.2, 30)] },
  huida: { set: "mar_tormenta", act(X) { const { t, lt } = X; P(PG, vuela(lerp(-100, 100, lt / 5.6), 120, 0, 90, t), t, "sudor"); alasPies(PG, t); enMano(PG, BOLSA, "L"); const c = seg(lt, 2.6, 3.2);
      med(C.GOR1, { x: lerp(-200, 0, c) + (lt > 3.2 ? -10 * seg(lt, 3.2, 3.6) : 0), y: 140, z: -40, ry: 90, rz: lt > 3.2 ? 1.5 * seg(lt, 3.2, 3.6) : 0 }, t, lt > 3.2 ? "espiral" : "enfado", 1, 1); med(C.GOR2, { x: lerp(200, 0, c), y: 140, z: -40, ry: -90, rz: lt > 3.2 ? -1.5 * seg(lt, 3.2, 3.6) : 0 }, t, lt > 3.2 ? "espiral" : "enfado", 1, 1);
      if (X.una("ch")) part.add(X.t0 + 3.2, 0, 150, -40, 20, ["#ffffff", "#ffe040"], 20, 1, 10, 1, true); },
    cams: [() => [0, 150, 160, 0, 130, -20, 44]] },
  arma: { set: "vuelo_nubes", act(X) { const { t, lt } = X; P(PH, vuela(0, 230, 0, 0, t), t, lt > 6 ? "presumido" : "normal"); alasPies(PH, t); enMano(PH, BOLSA, "L"); BOLSALUZ.visible = true; FL.intensity = 400; FL.color.set("#7aff9a"); FL.position.set(8, 215, 0); X.dato("ARMA DEFINITIVA: CABEZA DE MEDUSA", 6); },
    cams: [() => [-70, 235, 70, 0, 228, 0, 36], () => [70, 270, -40, 0, 230, 0, 40], cerca(PH, 30, 0.2, 30, -8), () => [0, 250, 140, 0, 230, 0, 44]] },
  // ---------- capítulo 10: Atlas
  atlas: { set: "desierto_atlas", act(X) { const { t, lt } = X; P(C.ATLAS, { x: 0, z: -200, ry: 0, bR: [-175, 20], bL: [-175, -20], cR: 30, cL: 30, sq: 0.97 + 0.02 * Math.sin(t * 2), lean: 4 }, t, "sudor"); CIELOBOLA.visible = true; CIELOBOLA.position.set(0, 200, -200); CIELOBOLA.scale.setScalar(2.2); CIELOBOLA.rotation.y = t * 0.1;
      P(PH, vuela(lerp(-160, 0, seg(lt, 0, 4)), lerp(140, 30, seg(lt, 0, 5)), 60, 90, t), t, "sorpresa"); alasPies(PH, t); },
    cams: [() => [0, 30, 260, 0, 140, -200, 50], () => [120, 60, 200, 0, 50, 40, 44]] },
  atlas_largo: { set: "desierto_atlas", act(X) { const { t, lt } = X; P(C.ATLAS, { x: 0, z: -200, ry: 0, bR: [-175, 20], bL: [-175, -20], cR: 30, cL: 30, cabX: 25 }, t, lt > 2.4 ? "enfado" : "normal"); CIELOBOLA.visible = true; CIELOBOLA.position.set(0, 200, -200); CIELOBOLA.scale.setScalar(2.2);
      P(PH, mezcla({ x: 0, z: 40, ry: 180 }, gestoHabla(X)), t, lt > 2.8 ? "sudor" : "habla"); enMano(PH, BOLSA, "L"); },
    cams: [() => [40, 20, 120, 0, 40, -120, 40], () => [0, 150, -40, 0, 140, -200, 40]] },
  atlas_piedra: { set: "desierto_atlas", act(X) { const { t, lt } = X; const s = W(X, "sacó") - 0.2; P(C.ATLAS, { x: 0, z: -200, ry: 0, bR: [-175, 20], bL: [-175, -20], cR: 30, cL: 30, cabX: 25 }, t, lt > s + 0.6 ? "susto" : "enfado"); petrifica(C.ATLAS, seg(lt, s + 0.8, s + 3.4)); CIELOBOLA.visible = true; CIELOBOLA.position.set(0, 200, -200); CIELOBOLA.scale.setScalar(2.2);
      P(PH, mezcla({ x: 0, z: 40, ry: 180, cabY: 60 }, lt > s ? { bR: [-150, 0], cR: 0 } : {}), t, "cerrados"); if (lt > s) enMano(PH, CABEZA); if (X.una("p")) part.add(X.t0 + s + 1, 0, 40, -200, 40, ["#9a968c", "#6d6a64"], 50, 3, 40, 2.4); },
    cams: [contra(PH, 1, 70), () => [0, 60, 200, 0, 120, -200, 48]] },
  atlas_mapa: { set: "desierto_atlas", act(X) { const { t, lt } = X; P(C.ATLAS, { x: 0, z: -200, ry: 0, bR: [-175, 20], bL: [-175, -20], cR: 30, cL: 30, cabX: 25 }, t, "susto"); petrifica(C.ATLAS, 1.2); CIELOBOLA.visible = true; CIELOBOLA.position.set(0, 200, -200); CIELOBOLA.scale.setScalar(2.2); X.dato("MONTES ATLAS · Marruecos, África"); },
    cams: [() => [lerp(-200, 200, X_lt() / 4.2), 90, 320, 0, 110, -200, 50]] },
  atlas_chiste: { set: "desierto_atlas", act(X) { const { t, lt } = X; P(C.ATLAS, { x: 0, z: -200, ry: 0, bR: [-175, 20], bL: [-175, -20], cR: 30, cL: 30, cabX: 25 }, t, "risa"); petrifica(C.ATLAS, 1.2); CIELOBOLA.visible = true; CIELOBOLA.position.set(0, 200, -200); CIELOBOLA.scale.setScalar(2.2);
      P(PH, mezcla({ x: 30, z: 40, ry: 160 }, encoge(lt, 3.5)), t, lt < 3.5 ? "normal" : "presumido"); },
    cams: [() => [0, 140, -60, 0, 140, -200, 36], () => [60, 25, 120, 30, 25, 40, 38]] },
  // ---------- capítulo 11: Andrómeda
  andromeda: { set: "acantilado_etiopia", act(X) { const { t, lt } = X; P(C.ANDRO, { x: 30, y: 16, z: -20, ry: -30, bR: [-150, 60], bL: [-150, -60], cR: 10, cL: 10, cabY: 20 * Math.sin(t) }, t, "lloro"); P(PH, vuela(lerp(-200, -60, seg(lt, 0, 5)), 120, 60, 90, t), t, "sorpresa"); alasPies(PH, t); },
    cams: [() => [200, 50, 160, 30, 20, -20, 44], () => [6, 46, 28, 30, 40, -20, 36], () => [-60, 140, 140, -60, 120, 60, 40]] },
  casiopea: { set: "palacio", act(X) { const { t, lt } = X; P(C.CASIO, { x: 0, z: -60, ry: 0, bR: [-110, 20], cR: 90, cabY: 15 * Math.sin(t) }, t, "presumido"); enMano(C.CASIO, ESPEJO); P(C.ANDRO, { x: 40, z: -50, ry: -20 }, t, "sudor"); },
    cams: [cerca(C.CASIO, 30, 0.3, 30), () => [0, 30, 60, 20, 25, -60, 42]] },
  poseidon: { set: "acantilado_etiopia", act(X) { const { t, lt } = X; const sube = seg(lt, 0, 2.5); P(C.POSE, { x: 200, y: lerp(-60, 0, sube), z: -40, ry: -80, bR: [-160, 20], cR: 10 }, t, "enfado"); enMano(C.POSE, TRIDENTE);
      if (lt > 4) { CETO.g.visible = true; colocaCadena(CETO, u => [300 + u * 80, -30 + 20 * Math.sin(t * 2 + u * 6) * (1 - u), -80 + Math.sin(u * 5 + t) * 30]); } P(C.ANDRO, { x: 30, y: 16, z: -20, ry: -30, bR: [-150, 60], bL: [-150, -60], cR: 10, cL: 10 }, t, "lloro"); },
    cams: [() => [100, 40, 140, 200, 40, -40, 44], cerca(C.POSE, 30, 0.2, 30), () => [0, 80, 180, 220, 0, -60, 44]] },
  trato_boda: { set: "acantilado_etiopia", act(X) { const { t, lt } = X; const h = W(X, "Hecho") - 0.2; P(PH, mezcla({ x: -140, z: 0, ry: 90 }, gestoHabla(X)), t, lt < h ? "habla" : "amor"); P(C.CEFEO, mezcla({ x: -200, z: -20, ry: -90 }, lt > h ? arriba(lt, h) : {}), t, lt > h ? "risa" : "sudor");
      P(C.CASIO, mezcla({ x: -200, z: 20, ry: -90 }, lt > h ? arriba(lt, h) : {}), t, lt > h ? "risa" : "triste"); P(C.ANDRO, { x: 30, y: 16, z: -20, ry: -30, bR: [-150, 60], bL: [-150, -60], cR: 10, cL: 10 }, t, lt > h ? "amor" : "lloro"); },
    cams: [() => [-170, 40, 120, -170, 25, 0, 42], cerca(C.CEFEO, 30, -0.3, 30), cerca(C.ANDRO, 30, 0.2, 30)] },
  ceto: { set: "acantilado_etiopia", act(X) { const { t, lt } = X; const s = seg(lt, 0, 1.6, eout); CETO.g.visible = true; colocaCadena(CETO, u => [180 + u * 160, lerp(-120, 110, s) * (1 - u) - 40 * u + 6 * Math.sin(t * 3 + u * 8), -40 + 30 * Math.sin(u * 4)]); if (X.una("spl")) part.add(X.t0 + 0.3, 180, 10, -40, 60, ["#2f6fc0", "#5a9be0", "#ffffff"], 60, 1.6, 80, 1.6); },
    cams: [() => [60, 20, 160, 180, 80, -40, 52]] },
  combate: { set: "acantilado_etiopia", act(X) { const { t, lt } = X; const hund = seg(lt, 5.4, 7.4); CETO.g.visible = true; colocaCadena(CETO, u => [180 + u * 160, lerp(110, -160, hund) * (1 - u) - 40 * u + 14 * Math.sin(t * 4 + u * 8), -40 + 30 * Math.sin(u * 4 + t)]); CETO.segs[0].lookAt(130, 110, 40);
      const a = t * 1.6; P(PH, mezcla(vuela(180 + Math.cos(a) * 70, 110 + 20 * Math.sin(a * 2), -40 + Math.sin(a) * 70, -a / D + 180, t), golpe(lt % 1.4, 0.8)), t, "enfado"); alasPies(PH, t); enMano(PH, ESPADA);
      for (let k = 0; k < 4; k++) if (X.una("g" + k)) part.add(X.t0 + 0.8 + k * 1.4, 180, 110, -40, 20, ["#ffffff", "#7ab0d0"], 30, 1.2, 40, 1, true); P(C.ANDRO, { x: 30, y: 16, z: -20, ry: -30, bR: [-150, 60], bL: [-150, -60], cR: 10, cL: 10 }, t, lt > 6 ? "risa" : "susto"); },
    cams: [() => [40, 80, 200, 180, 100, -40, 50], sigue(PH, 50, 20, 60, 40), cerca(C.ANDRO, 30, 0.2, 30)] },
  boda: { set: "banquete", act(X) { const { t, lt } = X; P(PE, { x: -12, z: 40, ry: 10, bL: [-40, -30], cL: 60 }, t, "amor"); P(C.ANDRO, { x: 12, z: 40, ry: -10, bR: [-40, 30], cR: 60 }, t, "amor"); if (X.una("b")) part.add(X.t0 + 0.4, 0, 50, 40, 40, ["#ff8ab0", "#ffffff", "#ffd040"], 30, 1, 20, 2, true);
      if (lt > W(X, "prometido") - 0.5) P(C.NOVIO, mezcla(andar(lt, [160, 120], [70, 60], W(X, "prometido") - 0.5, W(X, "prometido") + 1.5)), t, "enfado"); },
    cams: [() => [0, 30, 140, 0, 28, 40, 38], () => [100, 30, 150, 60, 25, 60, 40]] },
  boda_cabeza: { set: "banquete", act(X) { const { t, lt } = X; const s = W(X, "sacó") - 0.3; P(C.NOVIO, mezcla({ x: 70, z: 60, ry: -120 }, senala(lt, 0.2)), t, "enfado"); P(PE, mezcla({ x: -12, z: 40, ry: 60 }, lt > s ? { bR: [-90, 0], cR: 0, cabY: -70 } : arriba(lt, 0.3)), t, lt > s ? "cerrados" : "grito"); if (lt > s) enMano(PE, CABEZA);
      P(C.ANDRO, { x: -40, z: 40, ry: 160, bR: [-150, 60], bL: [-150, -60], cR: 120, cL: 120 }, t, "cerrados"); if (lt > s) { FL.intensity = 600; FL.color.set("#7aff9a"); FL.position.set(20, 40, 50); } },
    cams: [contra(PE, 1, 70), cerca(C.NOVIO, 30, 0.2, 30)] },
  boda_chiste: { set: "banquete", act(X) { const { t, lt } = X; P(C.NOVIO, mezcla({ x: 70, z: 60, ry: -120 }, senala(lt, -1)), t, "grito"); petrifica(C.NOVIO, 1.2); P(C.GUARDIA, { x: 100, z: 90, ry: -140, bR: [-150, 30], bL: [-150, -30] }, t, "grito"); petrifica(C.GUARDIA, 1.2); P(C.POLI, { x: 40, z: 100, ry: -150, bR: [-60, 40], cR: 90 }, t, "susto"); petrifica(C.POLI, 1.2); },
    cams: [() => [lerp(160, 40, X_lt() / 3.5), 40, 220, 70, 25, 70, 40]] },
  // ---------- capítulo 12: vuelta a casa
  vuelta: { set: "playa_serifos", act(X) { const { t, lt } = X; const q = seg(lt, 0, 3); P(PH, mezcla(q < 1 ? vuela(lerp(-300, 0, q), lerp(140, 0, q), lerp(200, 60, q), 120, t) : { x: 0, z: 60, ry: 0 }), t, lt < 3 ? "risa" : (lt > 6 ? "enfado" : "sorpresa")); alasPies(PH, t); enMano(PH, BOLSA, "L");
      if (lt > 4) { P(C.DANAE, { x: -90, z: -30, ry: 40, bR: [-80, 30], bL: [-80, -30], cR: 100, cL: 100, sq: 0.92 }, t, "susto"); P(C.DICTIS, { x: -60, z: -40, ry: 30 }, t, "sudor"); P(C.POLI, mezcla(andar(lt, [80, -20], [-30, -10], 4, 8)), t, "malvado"); } },
    cams: [() => [60, 60, 260, 0, 30, 60, 44], () => [-150, 30, 60, -60, 25, -30, 40], cerca(PH, 30, 0.2, 30)] },
  banquete2: { set: "banquete", act(X) { const { t, lt } = X; P(C.POLI, mezcla({ x: 0, z: -160, ry: 0 }, lt > 2 ? { bR: [-30, 40], bL: [-30, -40], cR: 120, cL: 120, lean: -10 } : {}), t, lt > 2 ? "risa" : "malvado"); P(PH, andar(lt, [0, 120], [0, 20], 0, 2.5), t, "enfado"); enMano(PH, BOLSA, "L"); },
    cams: [() => [0, 40, 180, 0, 25, -60, 44], cerca(C.POLI, 30, 0.2, 30)] },
  pues_si: { set: "banquete", act(X) { const { t, lt } = X; P(PH, { x: 0, z: 20, ry: 180, bL: [-90, 0], cL: 0, cabY: 70 }, t, "presumido"); enMano(PH, BOLSA, "L"); BOLSALUZ.visible = true; FL.intensity = 500 * seg(lt, 0.3, 1); FL.color.set("#7aff9a"); FL.position.set(-8, 25, 6); }, cams: [cerca(PH, 26, -0.1, 28)] },
  corte_piedra: { set: "banquete", act(X) { const { t, lt } = X; P(C.POLI, { x: 0, z: -160, ry: 0, bR: [-90, 10], cR: 60 }, t, "susto"); petrifica(C.POLI, seg(lt, 0.2, 2.2)); P(C.GUARDIA, { x: 60, z: -130, ry: -20 }, t, "susto"); petrifica(C.GUARDIA, seg(lt, 0.5, 2.6)); P(C.NOVIO, { x: -60, z: -130, ry: 20, bR: [-60, 30], cR: 90 }, t, "grito"); petrifica(C.NOVIO, seg(lt, 0.4, 2.4));
      if (X.una("p")) part.add(X.t0 + 1, 0, 20, -150, 40, ["#9a968c", "#6d6a64"], 30, 1, 60, 1.6); X.dato("LITERALMENTE"); },
    cams: [() => [0, 40, -40, 0, 25, -150, 44], cerca(C.POLI, 30, 0.2, 30)] },
  dictis_rey: { set: "playa_serifos", act(X) { const { t, lt } = X; P(C.DICTISR, mezcla({ x: 0, z: 40, ry: 0 }, arriba(lt, 0.5)), t, "risa"); P(C.DANAE, { x: -40, z: 30, ry: 30, bR: [-80, 25 + 15 * Math.sin(t * 12)], bL: [-80, -25], cR: 60, cL: 60 }, t, "risa"); P(PE, { x: 40, z: 30, ry: -30 }, t, "presumido"); brillo(X, "c", 0.4, 0, 40, 40, ["#ffd040", "#ffffff"]); },
    cams: [() => [0, 30, 140, 0, 28, 40, 38], cerca(C.DICTISR, 30, 0.2, 30)] },
  devuelve: { set: "templo_atenea", act(X) { const { t, lt } = X; const a = W(X, "Atenea", 0) - 0.3; P(C.HERMES, { x: 60, z: 0, ry: -60, bR: [-80, 10], cR: 20, y: 3 * Math.sin(t * 5) }, t, "risa"); P(PE, mezcla({ x: 0, z: 30, ry: lt < a ? 60 : -60 }, { bR: [-80, 10], cR: 20 }), t, "risa");
      P(C.ATENEA, mezcla({ x: -60, z: 0, ry: 60 }, lt > a + 1 ? { bL: [-90, -20], cL: 80 } : {}), t, lt > a + 1 ? "presumido" : "normal"); if (lt > a + 1) { enCodo(C.ATENEA, ESCUDO); if (!ESCUDO.getObjectByName("cabM")) { const c = caja(6, 6, 1, C.MED.S.caras.malvado, 0, 0, 1.4); c.name = "cabM"; ESCUDO.add(c); } } brillo(X, "sd", 1.5, 60, 20, 0); },
    cams: [general(0, 0, 170, 50), cerca(C.ATENEA, 30, 0.3, 30), cerca(C.HERMES, 30, -0.3, 30)] },
  // ---------- capítulo 13: la profecía
  huye_abuelo: { set: "tebas", act(X) { const { t, lt } = X; P(C.ACRI, mezcla(andar(lt, [-260, 40], [260, 40], 0.3, 6.8, { correr: 1 }), { cabY: -50 }), t, "susto"); if (X.una("p")) for (let k = 0; k < 8; k++) part.add(X.t0 + 0.6 + k * 0.7, -260 + k * 75, 2, 40, 6, ["#d9c290"], 10, 1, 30, 0.8); },
    cams: [sigue(C.ACRI, -40, 30, 100, 40), cerca(C.ACRI, 30, 0.3, 30)] },
  juegos: { set: "estadio", act(X) { const { t, lt } = X; P(PE, mezcla({ x: -20, z: 40, ry: 70 }, { bR: [-40, 30 + 20 * Math.sin(t * 3)], cR: 40 }), t, "presumido"); enMano(PE, ESPADA); ESPADA.visible = false; DISCO.visible = true; if (DISCO.parent !== PE.aR.mano) PE.aR.mano.add(DISCO); DISCO.position.set(0, -1, 0);
      P(C.ACRI, { x: 120, z: -150, y: 2 * BLK, ry: 0, sentado: 1 }, t, "normal"); },
    cams: [() => [0, 40, 260, 0, 30, -60, 46], () => [120, 40, -40, 120, 35, -150, 34], cerca(PE, 30, 0.3, 30)] },
  disco: { set: "estadio", act(X) { const { t, lt } = X; const l = W(X, "lanzó") - 0.2; P(PE, mezcla({ x: -20, z: 40, ry: 70 }, lt < l + 0.3 ? golpe(lt, l) : { bR: [-110, 10], cR: 0 }, { giro: -40 * seg(lt, l - 0.6, l) }), t, lt < l ? "enfado" : "risa");
      if (lt < l) { DISCO.visible = true; if (DISCO.parent !== PE.aR.mano) PE.aR.mano.add(DISCO); DISCO.position.set(0, -1, 0); } else { if (DISCO.parent !== scene) scene.add(DISCO); DISCO.visible = true; const q = seg(lt, l, 5.6); DISCO.position.set(lerp(-10, 140, q) + 60 * Math.sin(q * 3), 40 + 120 * Math.sin(q * 2.6), lerp(40, -100, q)); DISCO.rotation.set(t * 9, t * 4, 0); }
      P(C.ACRI, { x: 120, z: -150, y: 2 * BLK, ry: 0, sentado: 1 }, t, "normal"); },
    cams: [cerca(PE, 32, 0.3, 30), () => [0, 80, 160, DISCO.position.x, DISCO.position.y, DISCO.position.z, 40]] },
  disco_golpe: { set: "estadio", act(X) { const { t, lt } = X; const g = W(X, "Era") - 0.6; P(C.ACRI, { x: 120, z: -150, y: 2 * BLK, ry: 0, sentado: 1, cabX: lt < g ? -40 : 0, rz: lt > g ? 0.3 * seg(lt, g, g + 0.3) : 0 }, t, lt < g ? "sorpresa" : "espiral");
      if (lt < g) { if (DISCO.parent !== scene) scene.add(DISCO); DISCO.visible = true; const q = seg(lt, 0, g); DISCO.position.set(lerp(170, 120, q), lerp(200, 2 * BLK + 36, q), -150); DISCO.rotation.set(t * 9, t * 4, 0); }
      if (X.una("e")) part.add(X.t0 + g, 120, 2 * BLK + 40, -150, 16, ["#ffe040", "#ffffff"], 15, 1.2, 0, 2, true); quietos2(X, [[90, -150, 0], [150, -150, 0], [100, -170, 0]], lt > g ? "tapa" : "susto"); },
    cams: [() => [120, 2 * 16 + 40, -70, 120, 2 * 16 + 30, -150, 34], () => [60, 50, -50, 120, 40, -150, 40]] },
  destino: { set: "estadio", act(X) { const { t, lt } = X; P(PE, mezcla({ x: -20, z: 40, ry: 30 }, lt > 5 ? encoge(lt, 5) : {}), t, lt < 5 ? "triste" : "sudor"); X.dato("EL DESTINO SIEMPRE TE ENCUENTRA", 6.5); },
    cams: [cerca(PE, 32, 0.25, 30), () => [0, 60, 240, -20, 30, 40, 44], () => [-80, 20, 120, -20, 30, 40, 36]] },
  // ---------- cierre
  constelaciones: { set: "cielo_noche", act(X) { const { t, lt } = X; P(PE, { x: -12, z: 40, ry: 0, bL: [-40, -30], cL: 60 }, t, "amor"); P(C.ANDRO, { x: 12, z: 40, ry: 0, bR: [-40, 30], cR: 60 }, t, "amor"); if (lt > 3.5) { brillo(X, "sube", 3.5, 0, 30, 40, ["#fff6b0", "#ffffff"], 50); } },
    cams: [() => [0, 30, 140, 0, 28, 40, 38], () => [0, 20, 160, 0, lerp(30, 300, seg(X_lt(), 3, 6.8)), -100, 46]] },
  estrellas: { set: "cielo_noche", act(X) { const { t, lt } = X; CONS.visible = true; const ws = [W(X, "Perseo"), W(X, "Andrómeda"), W(X, "Casiopea"), W(X, "Pegaso")]; [KPER, KAND, KCAS, KPEG].forEach((k, i) => { k.visible = lt > ws[i] - 0.3; k.children.forEach((m, j) => m.scale.setScalar(k.visible ? seg(lt, ws[i] - 0.3, ws[i] + 0.2, back) * (0.85 + 0.2 * Math.sin(t * 4 + j)) : 0.01)); }); },
    cams: [() => [0, 20, 200, 0, 380, -650, 60]] },
  casiopea_abajo: { set: "cielo_noche", act(X) { const { t, lt } = X; CONS.visible = true; [KPER, KAND, KCAS, KPEG].forEach(k => k.visible = true); KCAS.rotation.z = Math.PI * seg(lt, 1.5, 3.5); P(C.CASIO, { x: 0, y: 250 + 4 * Math.sin(t * 2), z: -200, ry: 0, rz: Math.PI * seg(lt, 1.5, 3.5), bR: [-30, 40], bL: [-30, -40], cR: 60, cL: 60 }, t, lt > 3 ? "sudor" : "presumido"); },
    cams: [() => [0, 262, -110, 0, 264, -200, 40]] },
  cierre: { set: "cielo_noche", act(X) { const { t, lt } = X; CONS.visible = true; [KPER, KAND, KCAS, KPEG].forEach(k => k.visible = true); P(PH, mezcla({ x: -10, z: 40, ry: 0 }, lt > 2.5 && lt < 5 ? { bR: [-170, 20 + 25 * Math.sin(t * 9)], cR: 20 } : (lt > 5 ? arriba(lt, 5.2) : gestoHabla(X))), t, X.env(X.t) > 0.35 ? "habla" : "risa"); pegaso(40, 0, 10, -30, t, 0, 1); X.cta(lt); },
    cams: [() => [0, 34, 130, 10, 30, 30, 38]] },
};
const BLK = 16;
let _lt = 0; export function setLt(v) { _lt = v; } function X_lt() { return _lt; }
// extras de reacción usados en algunas escenas
const _ex = []; let _exUsados = 0; export function resetExtras() { _exUsados = 0; _ex.forEach(e => e.root.visible = false); }
function quietos2(X, lista, accion) { lista.forEach(([x, z, ry], i) => { if (!_ex[_exUsados]) { const e = personaje({ seed: 600 + _exUsados * 7, piel: ["#f0c8a0", "#d39a6a", "#a8704a"][_exUsados % 3], pelo: ["#3a2414", "#1f1b17", "#c27a3a"][_exUsados % 3], ropa: ["#b5452f", "#3f6fb5", "#d9a630", "#5f9e3a"][_exUsados % 4], falda: 1, sandalia: "#5a3a1a" }); scene.add(e.root); _ex.push(e); }
  const e = _ex[_exUsados++], t = X.t, s = Math.sin(t * 12 + i); const p = { x, z, ry, seed: i };
  if (accion === "aplaude") Object.assign(p, { bR: [-80, 25 + 15 * s], bL: [-80, -25 - 15 * s], cR: 60, cL: 60 }); if (accion === "susto") Object.assign(p, { bR: [-150, 30], bL: [-150, -30], cR: 20, cL: 20, salto: Math.abs(s) * 3 });
  if (accion === "tapa") Object.assign(p, { bR: [-150, 70], bL: [-150, -70], cR: 120, cL: 120 }); P(e, p, t, accion === "aplaude" ? "risa" : (accion === "tapa" ? "enfado" : "susto")); }); }
