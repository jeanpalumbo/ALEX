// Reparto, criaturas y las 59 escenas (acción + cámaras). Cada escena: { set, init(X)?, act(X), cams: [f(X) -> [px,py,pz,tx,ty,tz,fov]] }
import { THREE, personaje, pose, cara, cuadrupedo, animaCuadrupedo, serpienteCadena, colocaCadena, pajaro, caja, liso, MAT, D, cl, lerp, sm, seg, eout, back, muelle, rnd } from "./motor.js";
import { scene, part } from "./mundo.js";
// ===================== reparto (skins propias)
const H0 = { seed: 51, piel: "#d39a6a", pelo: "#3a2414", ropa: "#7a4a2a", cinto: "#c48a2c", desnudo: 1, falda: 1, brazalete: "#d9a630", sandalia: "#5a3a1a", flequillo: 1 };
export const C = {
  HERC: personaje(H0, 1.15), HERCL: personaje(Object.assign({}, H0, { leon: 1, seed: 52 }), 1.15), NINO: personaje(Object.assign({}, H0, { seed: 53, desnudo: 0, ropa: "#e9dcc0" }), 0.78),
  BEBE: personaje({ seed: 41, piel: "#f2c49a", pelo: "#c27a3a", ropa: "#ffffff", cinto: "#f0e0c0", falda: 1, flequillo: 1 }, 0.55),
  HERA: personaje({ seed: 21, piel: "#f0c8a0", pelo: "#3b2414", ropa: "#7f5aa8", cinto: "#e0b040", escote: 1, faldaLarga: 1, melena: 1, corona: 1, ojos: "#4a2a6a", ribete: "#e0b040", brazalete: "#e0b040" }, 1.05),
  ZEUS: personaje({ seed: 31, piel: "#e8b88e", pelo: "#e8e8e8", barba: "#f2f2f2", ropa: "#f2efe6", cinto: "#3d6fb5", ribete: "#3d6fb5", faldaLarga: 1, laurel: 1 }, 1.15),
  ZEUSB: personaje({ seed: 32, piel: "#e8b88e", pelo: "#3a2414", bigote: "#2a1a0a", ropa: "#8a5a3a", cinto: "#5a3a1a", falda: 1, sandalia: "#5a3a1a" }, 1.1),
  ALCM: personaje({ seed: 33, piel: "#f0c8a0", pelo: "#7a3a1a", ropa: "#3f8f8a", cinto: "#e0b040", faldaLarga: 1, melena: 1 }, 1),
  EURI: personaje({ seed: 61, piel: "#f2d0b0", pelo: "#c8a040", ropa: "#a83a8a", cinto: "#e0b040", corona: 1, faldaLarga: 1, capa: "#5a2a6a", bigote: "#c8a040", ojos: "#2a4a8a" }, 0.85),
  YOLAO: personaje({ seed: 62, piel: "#e0a878", pelo: "#2a1a10", ropa: "#3f6fb5", cinto: "#6b4424", falda: 1, sandalia: "#5a3a1a" }, 0.95),
  LINO: personaje({ seed: 63, piel: "#e8c0a0", pelo: "#e8e8e8", barba: "#f2f2f2", ropa: "#5a7a3a", faldaLarga: 1, calvo: 1 }, 1),
  HADES: personaje({ seed: 64, piel: "#a8b0c0", pelo: "#1a1a2a", ropa: "#1a1a24", faldaLarga: 1, capa: "#3a0a0a", corona: 1, barba: "#1a1a2a", ojos: "#c83a1a" }, 1.2),
  ATLAS: personaje({ seed: 65, piel: "#c88a5a", pelo: "#5a3a1a", barba: "#5a3a1a", ropa: "#5a4a3a", falda: 1, desnudo: 1, cinto: "#3a2a1a" }, 2.8),
  HIPO: personaje({ seed: 66, piel: "#d8a070", pelo: "#1a1a1a", ropa: "#c83a2f", cinto: "#e0b040", falda: 1, melena: 1, corona: 1, cascoPenacho: undefined, brazalete: "#e0b040" }, 1.05),
  DEYA: personaje({ seed: 67, piel: "#f0c8a0", pelo: "#c27a3a", ropa: "#d870a0", cinto: "#f2e0a0", faldaLarga: 1, melena: 1 }, 1),
  HEBE: personaje({ seed: 68, piel: "#f2d0b0", pelo: "#e8c050", ropa: "#f2f2ff", cinto: "#e0b040", faldaLarga: 1, melena: 1, corona: 1 }, 1),
  ATENEA: personaje({ seed: 69, piel: "#e8c0a0", pelo: "#2a1a10", ropa: "#c8c8d8", faldaLarga: 1, cascoPenacho: "#3f6fb5", casco: "#c8a040", melena: 1 }, 1.05),
  DIOM: personaje({ seed: 70, piel: "#c88a6a", pelo: "#1a1a1a", barba: "#1a1a1a", ropa: "#3a3a3a", falda: 1, capa: "#6a1a1a", corona: 1 }, 1.05),
  AUGIAS: personaje({ seed: 71, piel: "#e8b88e", pelo: "#8a6a3a", barba: "#8a6a3a", ropa: "#c8a040", faldaLarga: 1, corona: 1 }, 1),
  AMA1: personaje({ seed: 72, piel: "#c88a5a", pelo: "#1a1a1a", ropa: "#c83a2f", falda: 1, melena: 1, cascoPenacho: "#1a1a1a", casco: "#c8a040", brazalete: "#e0b040" }, 1),
  AMA2: personaje({ seed: 73, piel: "#e0b08a", pelo: "#7a3a1a", ropa: "#c83a2f", falda: 1, melena: 1, cascoPenacho: "#1a1a1a", casco: "#c8a040" }, 1),
  HERAD: personaje({ seed: 74, piel: "#f0c8a0", pelo: "#3b2414", ropa: "#c83a2f", falda: 1, melena: 1, cascoPenacho: "#7f5aa8", casco: "#c8a040", ojos: "#4a2a6a" }, 1.05),
};
// centauro Quirón: torso humano sobre cuerpo de caballo
const QH = personaje({ seed: 75, piel: "#d8a878", pelo: "#8a8a8a", barba: "#a8a8a8", ropa: "#d8a878", desnudo: 1 }, 1.05);
const QC = cuadrupedo({ seed: 76, color: "#8a5a3a", largo: 22, alto: 11, patas: 14, ancho: 10, cola: 5, melena: "#3a2a1a" }); QC.cabezas.forEach(h => h.visible = false);
const QUIRON = new THREE.Group(); QUIRON.add(QC.g); QH.root.position.set(0, 14, 7); QH.lR.hp.visible = QH.lL.hp.visible = false; QUIRON.add(QH.root); C.QUIRON = { root: QUIRON, h: QH, c: QC };
for (const k in C) scene.add(C[k].root);
// ---- criaturas
export const K = {
  LEON: cuadrupedo({ seed: 80, color: "#d4a14a", largo: 24, alto: 12, patas: 12, ancho: 12, melena: "#8a5220", cola: 6, dientes: 1, hocico: "#e0b860" }),
  CIERVA: cuadrupedo({ seed: 81, color: "#b07a4a", largo: 18, alto: 9, patas: 15, ancho: 8, astas: "#f2c84a", orejas: 1, cola: 2, hocico: "#d0a070" }),
  JABALI: cuadrupedo({ seed: 82, color: "#5a3a2a", largo: 22, alto: 13, patas: 8, ancho: 13, colmillos: 1, lomo: "#3a2418", orejas: 1, cola: 2, hocico: "#a07060", ojosRojos: 1 }),
  TORO: cuadrupedo({ seed: 83, color: "#f2f2f2", largo: 26, alto: 14, patas: 11, ancho: 14, cuernos: "#f2e8c8", hocico: "#e8a0a0", cola: 5, ojosRojos: 1 }),
  YEG1: cuadrupedo({ seed: 84, color: "#2a2a2a", largo: 20, alto: 11, patas: 14, ancho: 9, ojosRojos: 1, dientes: 1, melena: "#1a1a1a", cola: 5, hocico: "#3a3a3a" }),
  YEG2: cuadrupedo({ seed: 85, color: "#4a3a3a", largo: 20, alto: 11, patas: 14, ancho: 9, ojosRojos: 1, dientes: 1, melena: "#1a1a1a", cola: 5, hocico: "#5a4a4a" }),
  CERB: cuadrupedo({ seed: 86, color: "#2a2228", largo: 26, alto: 14, patas: 13, ancho: 16, cabezas: 3, ojosRojos: 1, dientes: 1, orejas: 1, cola: 6, hocico: "#3a2a30", escala: 1.6 }),
  BUEY: cuadrupedo({ seed: 87, color: "#a83a2a", largo: 22, alto: 12, patas: 10, ancho: 12, cuernos: "#e8e0c8", hocico: "#d07070", cola: 4 }),
  PERRO: cuadrupedo({ seed: 88, color: "#5a4a3a", largo: 16, alto: 8, patas: 8, ancho: 7, cabezas: 2, ojosRojos: 1, dientes: 1, orejas: 1, cola: 4 }),
};
for (const k in K) scene.add(K[k].g);
// Hidra: cuerpo en el agua + hasta 14 cuellos
const HID = new THREE.Group(); scene.add(HID); const hidCuerpo = caja(40, 16, 30, liso("#3f7a5a", 0.14, 8, 91), 0, 4, 0); HID.add(hidCuerpo);
const CUELLOS = []; for (let i = 0; i < 14; i++) { const s = serpienteCadena(i % 2 ? "#3f7a5a" : "#4f8a5a", "#2a5a3a", 16, 5, 92 + i); HID.add(s.g); CUELLOS.push(s); }
K.HIDRA = { g: HID };
// Cangrejo
const CANG = new THREE.Group(); scene.add(CANG); const cm = liso("#d0402a", 0.12, 8, 95); CANG.add(caja(22, 8, 16, cm, 0, 6, 0)); const pinzas = []; for (const s of [-1, 1]) { const p = new THREE.Group(); p.position.set(s * 13, 8, 8); p.add(caja(6, 5, 8, cm, 0, 0, 4)); CANG.add(p); pinzas.push(p); }
for (const s of [-1, 1]) for (let i = 0; i < 3; i++) CANG.add(caja(10, 2, 2, cm, s * 14, 2, -4 + i * 5)); for (const s of [-1, 1]) CANG.add(caja(2, 6, 2, cm, s * 4, 12, 6)), CANG.add(caja(3, 3, 3, MAT.brillo("#111"), s * 4, 15, 6));
K.CANG = { g: CANG, pinzas };
// Pájaros de bronce
const PAJ = []; for (let i = 0; i < 14; i++) { const p = pajaro("#b07a3a"); p.g.scale.setScalar(2.2); scene.add(p.g); PAJ.push(p); }
// Tinaja de bronce móvil (para escenas fuera del palacio)
const TIN = new THREE.Group(); const br = liso("#b07a3a", 0.12, 8, 69); TIN.add(caja(22, 18, 22, br, 0, 9, 0)); TIN.add(caja(18, 4, 18, br, 0, 20, 0)); TIN.add(caja(24, 2, 24, liso("#8a5a2a", 0.1, 8), 0, 22, 0)); scene.add(TIN);
// Objetos de mano
const LIRA = new THREE.Group(); LIRA.add(caja(1.4, 8, 1.4, MAT.oro, -2, 0, 0)); LIRA.add(caja(1.4, 8, 1.4, MAT.oro, 2, 0, 0)); LIRA.add(caja(6, 1.4, 1.4, MAT.oro, 0, 4, 0)); for (const x of [-0.8, 0, 0.8]) LIRA.add(caja(0.3, 7, 0.3, MAT.brillo("#fff"), x, 0, 0));
const ARCO = new THREE.Group(); ARCO.add(caja(1, 16, 1, MAT.madera, 0, 0, 0)); ARCO.add(caja(1, 4, 1, MAT.madera, 0, 9, -1.5)); ARCO.add(caja(1, 4, 1, MAT.madera, 0, -9, -1.5)); ARCO.add(caja(0.3, 22, 0.3, MAT.brillo("#eee"), 0, 0, -3));
const ESPADA = new THREE.Group(); ESPADA.add(caja(1.4, 16, 0.6, liso("#d0d4dc", 0.05, 4), 0, -10, 0)); ESPADA.add(caja(5, 1.2, 1.2, MAT.oro, 0, -2, 0)); ESPADA.add(caja(1.4, 3, 1.4, MAT.madera, 0, 0, 0)); ESPADA.rotation.x = Math.PI / 2;
const ANTOR = new THREE.Group(); ANTOR.add(caja(1.6, 12, 1.6, MAT.madera, 0, -4, 0)); const aLlama = caja(3, 4, 3, MAT.brillo("#ffb347"), 0, 3, 0); ANTOR.add(aLlama); ANTOR.rotation.x = Math.PI / 2;
const CASTA = new THREE.Group(); CASTA.add(caja(3, 1, 3, MAT.oro)); const CASTA2 = CASTA.clone();
const MANZ = new THREE.Group(); for (let i = 0; i < 3; i++) MANZ.add(caja(3, 3, 3, MAT.brillo("#ffcf3a"), (i - 1) * 3.2, 0, 0));
const ROCA = caja(40, 26, 34, MAT.piedra, 0, 13, 0); scene.add(ROCA);
const CIELOBOLA = new THREE.Group(); { const mt = MAT.brillo("#2a3a8a"); for (let i = -2; i <= 2; i++) for (let j = -2; j <= 2; j++) for (let k = -2; k <= 2; k++) if (i * i + j * j + k * k <= 5) CIELOBOLA.add(caja(10, 10, 10, (i + j + k) % 2 ? mt : MAT.brillo("#3a4aa8"), i * 10, j * 10, k * 10)); for (let s = 0; s < 18; s++) CIELOBOLA.add(caja(2, 2, 2, MAT.brillo("#ffffff"), (rnd(s) - 0.5) * 50, (rnd(s + 3) - 0.5) * 50, 26)); } scene.add(CIELOBOLA);
const COJIN = caja(16, 4, 10, liso("#c83a5a", 0.1, 4), 0, 0, 0); scene.add(COJIN);
const CAMISA = caja(10, 12, 5, liso("#e0e0d0", 0.06, 4), 0, 0, 0); scene.add(CAMISA);
const RAYO = new THREE.Group(); for (let k = 0; k < 6; k++) RAYO.add(caja(2, 10, 2, MAT.brillo("#fff6a0"), (k % 2 ? 3 : -3), k * 9, 0)); scene.add(RAYO);
const SERP = [serpienteCadena("#3f8f3a", "#1f5a20", 16, 3.2, 61), serpienteCadena("#5aa04a", "#2c6a2a", 16, 3.2, 62)]; SERP.forEach(s => scene.add(s.g));
const ALMAS = []; for (let i = 0; i < 6; i++) { const a = personaje({ seed: 500 + i, piel: "#bfe8ff", pelo: "#9ad0f0", ropa: "#bfe8ff", faldaLarga: 1 }, 0.9); a.root.traverse(o => { if (o.material && !Array.isArray(o.material)) { o.material = o.material.clone(); o.material.transparent = true; o.material.opacity = 0.55; } else if (Array.isArray(o.material)) o.material = o.material.map(m => { const c = m.clone(); c.transparent = true; c.opacity = 0.55; return c; }); }); scene.add(a.root); ALMAS.push(a); }
const PIRA_FUEGO = new THREE.Group(); for (let i = 0; i < 14; i++) PIRA_FUEGO.add(caja(6, 10, 6, MAT.brillo(i % 2 ? "#ffb347" : "#ff6a2a"), (rnd(i) - 0.5) * 50, 10, (rnd(i + 5) - 0.5) * 50)); scene.add(PIRA_FUEGO);
const FL = new THREE.PointLight("#ff8a3a", 0, 400, 1.4); scene.add(FL);
// ===================== utilidades de acción
const TODOS = [...Object.values(C).map(c => c.root), ...Object.values(K).map(k => k.g), ...PAJ.map(p => p.g), TIN, ROCA, CIELOBOLA, COJIN, CAMISA, RAYO, ...SERP.map(s => s.g), ...ALMAS.map(a => a.root), PIRA_FUEGO];
export function ocultaTodo() { TODOS.forEach(o => o.visible = false); FL.intensity = 0; [LIRA, ARCO, ESPADA, ANTOR, CASTA, CASTA2, MANZ].forEach(o => o.parent && o.parent.remove(o)); }
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
function quiron(x, z, ry, t, extra = {}) { const q = C.QUIRON; q.root.visible = true; q.root.position.set(x, 0, z); q.root.rotation.y = ry * D; animaCuadrupedo(q.c, t, extra.v || 0); pose(q.h, mezcla({ y: 14, z: 7 }, extra), t); q.h.root.position.set(0, 14 + (q.c.cuerpo.position.y - 14), 7); cara(q.h, extra.expr || "normal"); }
function hidra(t, n, x, z, opts = {}) { HID.visible = true; HID.position.set(x, 0, z); hidCuerpo.position.y = 4 + Math.sin(t * 1.5) * 1.5;
  CUELLOS.forEach((s, i) => { s.g.visible = i < n; if (i >= n) return; const ang = (i - (n - 1) / 2) * (1.9 / Math.max(1, n - 1)) * (n > 1 ? 1 : 0), len = 46 + (i % 3) * 8, fase = t * 2.4 + i * 1.3;
    const ata = opts.ataca ? Math.max(0, Math.sin(t * 3 + i)) * 18 : 0, nuevo = opts.nace && i >= opts.nace[0] ? cl((t - opts.nace[1]) / 0.5) : 1;
    colocaCadena(s, u => { const uu = 1 - u, L = len * nuevo; return [Math.sin(ang) * uu * L + Math.sin(fase + u * 4) * 5 * uu, 8 + uu * L * 0.9 + Math.sin(fase * 0.8 + u * 3) * 4, Math.cos(ang) * uu * L * 0.35 + uu * ata]; });
    s.lengua.scale.z = Math.max(0, Math.sin(t * 9 + i)); s.g.scale.setScalar(nuevo > 0 ? 1 : 0.001); }); }
function serpientes(t, f0, f1) { SERP.forEach((s, i) => { s.g.visible = true; colocaCadena(s, u => i ? f1(u, t) : f0(u, t)); s.lengua.scale.z = Math.max(0, Math.sin(t * 9 + i)); }); }
function pajaros(t, n, cx, cy, cz, r, caen = -1) { PAJ.forEach((p, i) => { p.g.visible = i < n; if (i >= n) return; const a = t * 0.9 + i * 0.7, cae = caen >= 0 && i < Math.floor((t - caen) * 4) ? 1 : 0;
  if (cae) { const tc = t - caen - i / 4; p.g.position.set(cx + Math.cos(a) * r, Math.max(2, cy - tc * tc * 80), cz + Math.sin(a) * r * 0.5); p.g.rotation.z = tc * 6; }
  else { p.g.position.set(cx + Math.cos(a) * r, cy + Math.sin(t * 2 + i) * 14, cz + Math.sin(a) * r * 0.5); p.g.rotation.set(0, -a, 0.3); }
  const w = 0.7 * Math.sin(t * 14 + i); p.aL.rotation.z = w; p.aR.rotation.z = -w; }); }
// ---- cámaras: funciones que se evalúan DESPUÉS de las poses
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
// ===================== ESCENAS
const H = C.HERC, HL = C.HERCL;
export const E = {
  // ---------- gancho en frío: Hércules contra la Hidra
  hidra_frio: { set: "lerna", act(X) { const { t, lt } = X; hidra(t, lt < 2.2 ? 9 : 11, 0, -60, { ataca: 1, nace: [9, 2.2] });
      P(HL, mezcla({ x: 0, z: 40, ry: 180, seed: 1 }, golpe(lt, 1.6), lt > 2.4 ? { lean: -10, salto: Math.max(0, Math.sin((lt - 2.4) * 6)) * 4 } : {}), t, lt < 2.2 ? "enfado" : "susto"); enMano(HL, ESPADA);
      if (X.una("c1")) part.add(X.t0 + 1.7, 0, 40, -20, 30, ["#3f7a5a", "#2a5a3a", "#8ad08a"], 40); },
    cams: [() => [60, 30, 140, 0, 50, -40, 45], cerca(HL, 30, 0.4, 32, 0), contra(HL, 1, 70)] },
  hidra_frio2: { set: "lerna", act(X) { const { t, lt } = X; hidra(t, 13, 0, -60, { ataca: 1 }); P(HL, mezcla({ x: 6, z: 46, ry: 180 }, encoge(lt, 2.5), { cabY: 15 * Math.sin(t * 2) }), t, lt < 2.5 ? "sorpresa" : (lt < 4.5 ? "sudor" : "espiral")); enMano(HL, ESPADA); },
    cams: [() => [-70, 20, 130, 0, 50, -50, 42], cerca(HL, 28, -0.3, 30, 0), picado(0, -10, 200, 110)] },
  tinaja_frio: { set: "palacio", act(X) { const { t, lt } = X; const tq = cl((lt - 4.0) / 0.4); P(C.EURI, { x: 70, z: -70 + 4, ry: 0, y: lerp(0, 2, eout(tq)) + muelle(lt, 4.4, 2), cabY: 20 * Math.sin(t * 7), bR: [-150, 20], bL: [-150, -20], cR: 30, cL: 30 }, t, "susto");
      P(HL, mezcla(andar(lt, [-120, 60], [-10, -20], 0.3, 4.2), { cabY: 10 * Math.sin(t) }), t, lt > 4 ? "presumido" : "normal"); },
    cams: [general(0, -40, 220, 80, 0, 25, 42), medio(HL, 1, 80), () => [110, 34, -10, 70, 14, -70, 36], cerca(C.EURI, 30, 0.2, 32, -10)] },
  intro: { set: "olimpo", act(X) { const { t, lt } = X; P(HL, mezcla({ x: 0, z: 30, ry: lerp(-40, 0, seg(lt, 0, 1.5)) }, arriba(lt, 1.2)), t, "risa"); X.titulo(lt); },
    cams: [() => { const a = -0.6 + X_lt() * 0.25; return [Math.sin(a) * 140, 30 + X_lt() * 6, 30 + Math.cos(a) * 140, 0, 40, 30, 40]; }] },
  // ---------- nacimiento
  olimpo_zeus: { set: "olimpo", act(X) { const { t, lt } = X; P(C.ZEUS, mezcla({ x: 0, z: -10, ry: 0 }, X.cerca("rayos") ? {} : {}, lt > 2.5 && lt < 4 ? { bR: [-160, 10], cR: 0 } : gestoHabla(X)), t, lt > 2.5 && lt < 4 ? "presumido" : "risa");
      if (lt > 2.5 && lt < 4) { RAYO.visible = true; RAYO.position.set(-12, 70 + Math.sin(t * 40) * 2, -10); RAYO.rotation.z = Math.sin(t * 30) * 0.2; FL.intensity = 4000 * (0.5 + 0.5 * Math.sin(t * 50)); FL.position.set(-12, 80, 20); }
      P(C.ALCM, mezcla(andar(lt, [160, 40], [50, 10], 4.6, 7), { cabY: -20 }), t, lt > 7 ? "sorpresa" : "normal"); },
    cams: [general(0, -30, 230, 70), contra(C.ZEUS, -1, 70), () => [120, 30, 80, 60, 26, 10, 38], cerca(C.ZEUS, 34, 0.3)] },
  zeus_disfraz: { set: "tebas", act(X) { const { t, lt } = X; const ent = seg(lt, 0, 1.4); P(C.ZEUS, { x: -60, z: 30, ry: 90, sq: 1 - 0.2 * Math.sin(cl((lt - 4) / 0.4) * Math.PI) }, t, "malvado"); C.ZEUS.root.visible = lt < 4.2;
      if (X.una("humo")) part.add(X.t0 + 4.1, -60, 30, 30, 40, ["#ffffff", "#e0e0f0"], 25, 1.6, 10, 1.4);
      P(C.ZEUSB, mezcla({ x: -60, z: 30, ry: 90 }, lt > 4.2 ? mezcla(andar(lt, [-60, 30], [10, 30], 5.5, 8), lt > 8.6 ? { bR: [-90, 20], cR: 60, ry: 90 } : {}) : {}), t, lt > 9 ? "risa" : "presumido"); C.ZEUSB.root.visible = lt >= 4.2;
      P(C.ALCM, { x: 40, z: 30, ry: -90, cabY: Math.sin(t) * 10, bR: lt > 9 ? [-40, 30] : [0, 0], cR: lt > 9 ? 90 : 10 }, t, lt > 9.5 ? "amor" : (lt > 6 ? "sorpresa" : "normal")); },
    cams: [medio(C.ZEUS, -1, 80), cerca(C.ZEUS, 30, 0.5, 30), () => [0, 30, 120, 0, 26, 30, 36], cerca(C.ZEUSB, 26, 0.4, 28), cerca(C.ALCM, 28, -0.4, 30)] },
  olimpo_hera: { set: "olimpo", act(X) { const { t, lt } = X; P(C.HERA, mezcla(andar(lt, [-140, 60], [-30, 30], 0, 1.6), lt > 1.7 ? brazosCruz(seg(lt, 1.7, 2)) : {}, { cabY: lt > 2 ? 10 * Math.sin(t * 2) : 0 }), t, lt > 1.6 ? "enfado" : "normal");
      P(C.ZEUS, { x: 30, z: -20, ry: -40, cabY: lerp(0, -30, seg(lt, 2.4, 2.8)) }, t, lt > 2.5 ? "sudor" : "risa"); },
    cams: [general(0, 0, 220, 50), cerca(C.HERA, 30, 0.2, 30, -1), cerca(C.ZEUS, 30, -0.4, 30)] },
  hera_serpientes: { set: "olimpo", act(X) { const { t, lt } = X; const q = seg(lt, 0.8, 1.1, x => back(x, 3)); P(C.HERA, { x: -30, z: 20, ry: 20, bR: [-150 * q, 20 * q], cR: 20, bL: [-30, -20], cL: 40, lean: -6 * q, cabX: -10 * q }, t, lt > 1 ? "malvado" : "enfado");
      if (X.una("magia")) part.add(X.t0 + 1.0, -40, 60, 30, 50, ["#c9a0ff", "#ffffff", "#8a5ad8"], 34, 0.9, 30, 1.6, true);
      serpientes(t, (u, t) => [-40 + Math.sin(u * 8 + t * 5) * 4, 70 - u * 30 + Math.max(0, lt - 1.2) * -40, 30 + u * 20], (u, t) => [-20 + Math.sin(u * 8 + t * 5 + 2) * 4, 76 - u * 30 + Math.max(0, lt - 1.4) * -40, 30 + u * 20]); },
    cams: [() => [-110, 14, 90, -30, 46, 20, 44], cerca(C.HERA, 26, -0.2, 30, -1)] },
  bebe_serpientes: { set: "cuna", act(X) { const { t, lt } = X; const ag = seg(lt, 1.0, 1.3, x => back(x, 2)), pop = 2.2;
      P(C.BEBE, { x: 0, z: 0, y: 12, ry: 0, lean: -10, pR: -80, pL: -80, kR: 20, kL: 20, bR: [-100 * ag, 40 * ag], bL: [-100 * ag, -40 * ag], cR: 30 * ag + (lt < pop ? 10 * Math.sin(lt * 30) * ag : 0), cL: 30 * ag, salto: lt > pop ? Math.abs(Math.sin(t * 9)) * 1.6 : 0 }, t, lt < 1 ? "sorpresa" : (lt < pop ? "enfado" : "risa")); C.BEBE.root.position.y = 12;
      if (lt < pop) serpientes(t, (u, tt) => [-16 + u * -10 + Math.sin(u * 7 + tt * 6) * 2, 30 - u * 22, Math.cos(u * 7 + tt * 6) * 2], (u, tt) => [16 + u * 10 + Math.sin(u * 7 + tt * 6 + 1) * 2, 30 - u * 22, Math.cos(u * 7 + tt * 6) * 2]);
      if (X.una("pop")) { part.add(X.t0 + pop, -10, 26, 2, 40, ["#3f8f3a", "#2c6a2a", "#5aa04a"], 38); part.add(X.t0 + pop + 0.12, 10, 26, 2, 40, ["#5aa04a", "#2c6a2a", "#a0d070"], 38); } },
    cams: [() => [50, 46, 90, 0, 18, 0, 34], cerca(C.BEBE, 70, 0.05, 36, -2), () => [-30, 32, 40, 0, 26, 0, 38]] },
  bebe_juega: { set: "cuna", act(X) { const { t, lt } = X; P(C.BEBE, { x: 0, z: 0, y: 12, lean: -10, pR: -80 + 25 * Math.sin(t * 18), pL: -80 + 25 * Math.sin(t * 18 + 2), bR: [-130 + 30 * Math.sin(t * 10), 40], bL: [-130 + 30 * Math.sin(t * 10 + 2), -40], cR: 20, cL: 20 }, t, "risa"); C.BEBE.root.position.y = 12;
      serpientes(t, (u, tt) => [-12 + Math.sin(u * 3 + tt * 10) * 6, 34 + Math.cos(u * 3 + tt * 10) * 6 - u * 8, 4], (u, tt) => [12 + Math.sin(u * 3 + tt * 10 + 2) * 6, 34 + Math.cos(u * 3 + tt * 10 + 2) * 6 - u * 8, 4]);
      SERP.forEach(s => s.segs[0].scale.set(1.5, 0.4, 1.7)); },
    cams: [cerca(C.BEBE, 70, 0.1, 34, -2), () => [80, 60, 120, 0, 20, 0, 34]] },
  hera_rabia: { set: "olimpo", act(X) { const { t, lt } = X; P(C.HERA, mezcla({ x: 0, z: 20, ry: 0, cabY: 8 * Math.sin(t * 3) }, lt < 3 ? { bR: [-60 + 40 * Math.sin(t * 10), 40], bL: [-60 + 40 * Math.sin(t * 10 + 2), -40], cR: 80, cL: 80, salto: Math.abs(Math.sin(t * 10)) * 2 } : brazosCruz(1)), t, lt < 4 ? "enfado" : "malvado");
      P(C.ZEUS, mezcla(andar(lt, [120, -40], [220, -60], 3.5, 6), { cabY: -40 }), t, "sudor"); },
    cams: [cerca(C.HERA, 34, 0.2, 32), general(0, 0, 220, 60), contra(C.HERA, 1, 60)] },
  // ---------- juventud
  lino_lira: { set: "tebas", act(X) { const { t, lt } = X; const gl = 6.6;
      P(C.NINO, mezcla({ x: -20, z: 50, ry: 90, sentado: lt < 5.5 ? 1 : 0, bR: [-70, 20], cR: 60, bL: [-60, -10], cL: 70 }, lt > 5.5 ? mezcla(golpe(lt, gl), { sentado: 0 }) : {}, { cabY: 6 * Math.sin(t * 1.5) }), t, lt < 3.5 ? "dormido" : (lt < 5 ? "enfado" : "malvado")); enMano(C.NINO, LIRA);
      P(C.LINO, mezcla({ x: 30, z: 50, ry: -90 }, lt < 5 ? senala(lt, 3.6) : {}, lt > gl ? { lean: -50 * seg(lt, gl, gl + 0.3, eout), rz: 0 } : {}), t, lt < gl ? (lt > 3.5 ? "enfado" : "habla") : "espiral");
      if (X.una("lira")) part.add(X.t0 + gl, 24, 40, 50, 24, ["#f2c84a", "#ffffff"], 30, 0.8, 60, 1, true); },
    cams: [() => [5, 30, 140, 5, 22, 50, 36], cerca(C.NINO, 28, 0.4, 30), cerca(C.LINO, 28, -0.4, 30), () => [-60, 16, 90, 10, 26, 50, 42]] },
  lino_chiste: { set: "tebas", act(X) { const { t, lt } = X; P(C.LINO, { x: 30, z: 50, ry: -90, rz: -1.45 * seg(lt, 0, 0.4), y: 2 }, t, "espiral");
      P(C.NINO, mezcla({ x: -20, z: 50, ry: 90 }, encoge(lt, 1.2), { cabY: 20 * Math.sin(t * 2) }), t, lt < 2 ? "sorpresa" : "presumido"); enMano(C.NINO, LIRA); },
    cams: [() => [60, 26, 110, 5, 14, 50, 38], cerca(C.NINO, 26, 0.3, 28)] },
  quiron: { set: "campo", act(X) { const { t, lt } = X; quiron(lt < 3 ? lerp(-150, -60, seg(lt, 0, 3)) : -60, 10, 90, t, { v: lt < 3 ? 0.6 : 0, bR: lt > 3 ? [-90, 10] : [0, 0], cR: 0, expr: "habla" });
      const tira = 4.5 + ((lt - 4.5) % 1.6); P(C.NINO, mezcla({ x: 20, z: 20, ry: 160, bL: [-90, -10], cL: 0, bR: [-90, 20], cR: lt > 4.5 ? lerp(120, 0, seg(tira, 4.5, 4.6)) : 120 }, lt > 7.5 ? encoge(lt, 7.6) : {}), t, lt > 7.5 ? "presumido" : "enfado"); enMano(C.NINO, ARCO, "L");
      if (X.una("dianas")) for (const k of [0, 1, 2]) part.add(X.t0 + 5.0 + k * 1.6, [-120, 0, 120][k], 26, -116, 12, ["#d33a2f", "#e9dcc0", "#6b4424"], 18, 0.8); },
    cams: [general(-40, 0, 230, 50, -40), sigue(C.QUIRON.h, 50, 20, 60, 40, 30), () => [60, 20, 70, 0, 26, -80, 44], cerca(C.NINO, 26, 0.4, 30)] },
  tebas_familia: { set: "tebas", act(X) { const { t, lt } = X; P(H, mezcla({ x: 0, z: 60, ry: 0, bR: [-40, 30], cR: 60 }, { cabY: 10 * Math.sin(t) }), t, "risa"); P(C.DEYA, { x: 22, z: 60, ry: -20, bL: [-40, -30], cL: 60 }, t, "amor");
      [C.BEBE].forEach(c => P(c, { x: -14, z: 70, ry: 20, y: Math.abs(Math.sin(t * 6)) * 4, bR: [-150, 20], bL: [-150, -20], cR: 10, cL: 10 }, t, "risa")); },
    cams: [() => [10, 30, 150, 10, 24, 60, 34], cerca(H, 30, 0.3, 30)] },
  hera_locura: { set: "cielo_noche", act(X) { const { t, lt } = X; P(C.HERA, { x: -40, z: 0, ry: 30, y: 60 + 4 * Math.sin(t), bR: [-120, 30], cR: 20, bL: [-120, -30], cL: 20 }, t, "malvado");
      if (X.una("locura")) for (let k = 0; k < 5; k++) part.add(X.t0 + 2 + k * 0.5, 30, 50, 30, 20, ["#8a2ad8", "#3a0a5a", "#ff3a6a"], 30, 1, 20, 1.4, true);
      P(H, { x: 30, z: 30, ry: -20, cabY: 30 * Math.sin(t * 5), cabZ: 15 * Math.sin(t * 3), bR: [-100 + 50 * Math.sin(t * 8), 30], bL: [-100 + 50 * Math.sin(t * 7), -30], cR: 60, cL: 60, lean: 8 * Math.sin(t * 4) }, t, lt < 2 ? "susto" : "espiral"); },
    cams: [() => [-120, 70, 160, -20, 50, 0, 40], cerca(H, 30, 0.2, 32), contra(C.HERA, 1, 90)] },
  delfos: { set: "delfos", act(X) { const { t, lt } = X; P(H, mezcla(andar(lt, [-120, 120], [-20, 40], 0, 3), lt > 3 ? { lean: 25, cabX: 20, bR: [-30, 10], bL: [-30, -10] } : {}), t, lt > 3 ? "lloro" : "triste");
      const sib = { x: 20, z: 0, ry: -60, bR: [-120 + 20 * Math.sin(t * 2), 30], bL: [-120 + 20 * Math.sin(t * 2 + 1), -30], cR: 20, cL: 20 };
      P(C.ATENEA, sib, t, lt > 4 ? "espiral" : "cerrados"); C.ATENEA.extras.visible = false; },
    cams: [general(0, 0, 240, 70), () => [-80, 26, 120, 0, 30, 10, 38], cerca(H, 30, -0.3, 30), cerca(C.ATENEA, 30, 0.4, 32)] },
  euristeo_presenta: { set: "palacio", act(X) { const { t, lt } = X; P(C.EURI, mezcla({ x: 0, z: -140, ry: 0, y: 32, sentado: 1 }, lt > 2 && lt < 4 ? susto(lt, 2.2) : {}, lt > 5 ? { bL: [-60, -20], cL: 80, cabY: 20 * Math.sin(t) } : {}), t, lt < 2 ? "presumido" : (lt < 4 ? "susto" : "malvado"));
      if (lt > 4.6) { P(C.HERA, { x: -40, z: -150, ry: 30, y: 40 + 2 * Math.sin(t * 2), bR: [-40, 30], cR: 80 }, t, "amor"); }
      P(HL.root.visible ? H : H, mezcla({ x: 0, z: -20, ry: 180 }, lt > 7 ? encoge(lt, 7.2) : {}), t, lt > 7 ? "sudor" : "triste"); },
    cams: [() => [0, 30, 60, 0, 40, -140, 40], cerca(C.EURI, 30, 0.2, 30), () => [40, 8, -40, 0, 50, -140, 46], () => [0, 40, 60, 0, 30, -60, 38]] },
  // ---------- bucles abiertos (cliffhangers)
  bucle1: { set: "palacio", act(X) { const { t, lt } = X; P(C.EURI, { x: 0, z: -140, y: 32, sentado: 1, bR: [-60 + 20 * Math.sin(t * 6), 30], cR: 90, bL: [-60 + 20 * Math.sin(t * 6 + 1), -30], cL: 90, cabZ: 8 * Math.sin(t * 5) }, t, "malvado");
      P(H, { x: 0, z: -20, ry: 180, ...encoge(lt, 1.5) }, t, lt > 1.5 ? "sudor" : "sorpresa"); X.dato("Euristeo, rey de Tirinto y Micenas"); },
    cams: [() => [0, 22, -70, 0, 40, -140, 34], cerca(H, 30, 0.2, 30)] },
  bucle2: { set: "establos", act(X) { const { t, lt } = X; P(HL, mezcla(andar(lt, [-120, 80], [-40, 60], 0, 1.5), lt > 1.6 ? { bR: [-150, 70], bL: [-150, -70], cR: 120, cL: 120 } : {}), t, lt > 1.6 ? "enfado" : "sorpresa");
      if (X.una("moscas")) for (let k = 0; k < 6; k++) part.add(X.t0 + 0.5 + k * 0.6, -40, 30, 50, 8, ["#2a2a2a"], 14, 0.5, -10, 1.4); },
    cams: [() => [-60, 30, 160, -60, 26, 60, 36], cerca(HL, 30, 0.3, 30)] },
  bucle3: { set: "tracia", act(X) { const { t, lt } = X; quad("YEG1", -30, -20, 20, t, 0, { cabX: -20 }); quad("YEG2", 30, -20, -20, t, 0, { cabX: -20 }); quad("TORO", 0, -90, 0, t, 0); P(C.HERAD, { x: 90, z: 10, ry: -60, ...brazosCruz(1) }, t, "malvado"); },
    cams: [() => [0, 14, 90, 0, 22, -30, 44], cerca(C.HERAD, 30, 0.3, 30)] },
  bucle4: { set: "inframundo", act(X) { const { t, lt } = X; P(HL, mezcla(andar(lt, [0, 160], [0, 60], 0, X.dur)), t, "sudor"); quad("CERB", 0, -120, 0, t, 0, { cabX: -10 }); },
    cams: [() => [0, 40 + X_lt() * 4, 260 - X_lt() * 20, 0, 40, -60, 42]] },
  // ---------- Nemea
  nemea_flechas: { set: "nemea", act(X) { const { t, lt } = X; quad("LEON", 20, -40, -100, t, 0, { cabX: lt > 3 ? -20 : 0 });
      const tiro = (lt % 2.1); P(H, mezcla({ x: -90, z: 10, ry: 100, bL: [-90, -10], cL: 0, bR: [-90, 20], cR: lerp(120, 0, seg(tiro, 0.6, 0.7)) }, lt > 6 ? encoge(lt, 6.2) : {}), t, lt > 6 ? "sorpresa" : "enfado"); enMano(H, ARCO, "L");
      if (X.una("rebote")) for (let k = 0; k < 3; k++) part.add(X.t0 + 0.75 + k * 2.1, 14, 24, -40, 10, ["#cccccc", "#6b4424", "#ffffff"], 30, 0.7); },
    cams: [general(-30, -20, 220, 50), contra(H, 1, 70), () => [70, 16, 30, 20, 20, -40, 36], cerca(K.LEON ? H : H, 30, 0.3, 30)] },
  nemea_cueva: { set: "nemea", act(X) { const { t, lt } = X; const lu = lt > 3.5; const lx = lu ? 200 : lerp(40, 190, seg(lt, 1, 3.4));
      quad("LEON", lx, lu ? -150 : -60, 90, t, lu ? 0 : 0.8, lu ? { rz: Math.sin(t * 20) * 0.1 } : {}); K.LEON.g.visible = !lu || lt < 4;
      P(H, mezcla(lu ? { x: 200, z: -110, ry: 180, bR: [-90, 40], bL: [-90, -40], cR: 60 + 20 * Math.sin(t * 20), cL: 60 + 20 * Math.sin(t * 20 + 1), lean: 10 } : andar(lt, [-60, 0], [180, -90], 0.8, 3.4, { correr: 1 })), t, lu ? "enfado" : "grito");
      if (lu && X.una("polvo")) part.add(X.t0 + 4.2, 200, 20, -150, 40, ["#8a8780", "#6d6a64", "#d4a14a"], 30, 1.2, 40, 2); },
    cams: [general(60, -40, 240, 60), sigue(H, -60, 30, 70, 42), () => [200, 40, 0, 200, 20, -150, 40], cerca(H, 26, 0.3, 30)] },
  nemea_piel: { set: "nemea", act(X) { const { t, lt } = X; const ok = lt > 5.8; P(lt < 8 ? H : HL, mezcla({ x: 0, z: 20, ry: 0 }, lt < 5 ? { bR: [-60 + 30 * Math.sin(t * 12), 20], cR: 60, lean: 20, cabX: 20 } : (lt < 8 ? { bR: [-70 + 30 * Math.sin(t * 6), 20], cR: 50, lean: 15 } : arriba(lt, 8.2))), t, lt < 4 ? "sudor" : (lt < 5.5 ? "sorpresa" : (lt < 8 ? "presumido" : "risa")));
      if (lt < 8) quad("LEON", 0, -10, 90, t, 0, { rz: 1.5 }, -5); enMano(lt < 8 ? H : HL, ESPADA);
      if (X.una("ch")) part.add(X.t0 + 2.6, 0, 20, 5, 14, ["#ffffff", "#ffd040"], 30, 0.6, 60, 0.6, true); },
    cams: [() => [40, 30, 90, 0, 16, 0, 36], cerca(H, 28, 0.3, 30), () => [0, 24, 70, 0, 28, 20, 40]] },
  nemea_casco: { set: "nemea", act(X) { const { t, lt } = X; const a = X.lt * 0.4; P(HL, mezcla({ x: 0, z: 20, ry: 20 * Math.sin(t * 0.8) }, lt < 3 ? { bR: [-170, 20], cR: 10, bL: [-30, -40], cL: 80 } : brazosCruz(1), { cabY: 15 * Math.sin(t * 1.3) }), t, lt < 4 ? "presumido" : "risa"); },
    cams: [() => { const a = -0.8 + X_lt() * 0.3; return [Math.sin(a) * 80, 34, 20 + Math.cos(a) * 80, 0, 32, 20, 38]; }, cerca(HL, 26, 0.2, 30), contra(HL, -1, 60)] },
  nemea_vuelta: { set: "campo", act(X) { const { t, lt } = X; P(HL, mezcla(andar(lt, [-160, 40], [140, 40], 0, X.dur), { cabY: 15 * Math.sin(t * 2), bR: [-20 + 30 * Math.sin(t * 4), 30], lean: -6 }), t, "presumido");
      quietos2(X, [[-60, -20, 180], [40, -20, 180], [120, -30, 200]], "aplaude"); },
    cams: [sigue(HL, 70, 26, 90, 36), sigue(HL, -40, 10, 60, 44, 40), cerca(HL, 30, 0.4, 30)] },
  euristeo_miedo: { set: "palacio", act(X) { const { t, lt } = X; P(HL, mezcla(andar(lt, [0, 60], [0, -30], 0, 2)), t, "risa");
      P(C.EURI, mezcla({ x: 0, z: -140, y: 32, ry: 0, sentado: lt < 2.2 ? 1 : 0 }, lt > 2.2 ? mezcla(andar(lt, [0, -140], [-80, -150], 2.3, 3.4, { correr: 1 }), { y: 32, bR: [-150, 20], bL: [-150, -20] }) : {}, lt > 5 ? { ry: 160, x: -80, z: -150, y: 32, ...senala(lt, 5.2) } : {}), t, lt < 2.2 ? "presumido" : (lt < 5 ? "susto" : "grito"));
      if (lt > 6) { quad("LEON", 0, 40, 0, t, 0, { rz: 1.5 }, -5); P(HL, { x: 0, z: 60, ry: 180, ...encoge(lt, 6.4) }, t, "triste"); } },
    cams: [general(0, -40, 230, 70), () => [-20, 40, -20, -60, 36, -150, 38], () => [60, 30, 120, 0, 20, 40, 38]] },
  // ---------- Hidra
  hidra_llega: { set: "lerna", act(X) { const { t, lt } = X; hidra(t, lt < 3 ? 0 : 9, 0, -80, { nace: [0, 3] });
      P(HL, mezcla(andar(lt, [-120, 90], [-20, 50], 0, 3), lt > 5 ? { cabX: 10, bR: [-120, 30], cR: 100, lean: 10 } : {}), t, lt > 5 ? "sudor" : (lt > 3.2 ? "sorpresa" : "normal"));
      P(C.YOLAO, mezcla(andar(lt, [-160, 110], [-60, 70], 0.3, 3.3), lt > 5 ? { bR: [-120, 30], cR: 100 } : {}), t, lt > 5 ? "lloro" : "normal"); },
    cams: [general(-40, 20, 230, 50), () => [60, 20, 160, 0, 60, -80, 46], cerca(HL, 26, 0.4, 30), cerca(C.YOLAO, 26, -0.3, 30)] },
  hidra_corta: { set: "lerna", act(X) { const { t, lt } = X; X.dato("Hidra de Lerna: 9 cabezas (según Apolodoro)"); const cortes = [0.8, 2.2, 3.6], n = 9 + cortes.filter(c => lt > c + 0.4).length;
      hidra(t, n, 0, -60, { ataca: 1, nace: [9, cortes[0] + 0.4] }); P(HL, mezcla({ x: 0, z: 30, ry: 180 }, golpe(lt, cortes.find(c => lt < c + 0.9) || 9)), t, lt > 3.8 ? "espiral" : "enfado"); enMano(HL, ESPADA);
      for (const c of cortes) if (X.una("c" + c)) { part.add(X.t0 + c, 0, 50, -30, 26, ["#3f7a5a", "#2a5a3a", "#8ad08a"], 40); } },
    cams: [() => [70, 30, 120, 0, 50, -50, 44], cerca(HL, 26, 0.3, 30), picado(0, -20, 220, 100)] },
  hidra_yolao: { set: "lerna", act(X) { const { t, lt } = X; hidra(t, Math.max(3, 12 - Math.floor(lt / 0.8)), 0, -60, { ataca: 1 }); P(HL, mezcla({ x: -14, z: 30, ry: 180 }, golpe(lt, 0.6 + Math.floor(lt / 1.6) * 1.6)), t, "enfado"); enMano(HL, ESPADA);
      P(C.YOLAO, mezcla({ x: 26, z: 26, ry: 200 }, { bR: [-100 + 40 * Math.sin(t * 5), 20], cR: 30, lean: 6 }), t, "grito"); enMano(C.YOLAO, ANTOR); aLlama.scale.y = 1 + 0.3 * Math.sin(t * 20);
      if (X.una("fuego")) for (let k = 0; k < 6; k++) part.add(X.t0 + 0.8 + k * 1.1, 10, 50, -30, 16, ["#ff7a2a", "#ffb347", "#ffe080"], 25, 1, 20, 0.8, true); },
    cams: [() => [-60, 24, 110, 0, 40, -30, 44], cerca(C.YOLAO, 26, 0.3, 30), () => [80, 50, 100, 0, 50, -50, 40]] },
  hidra_roca: { set: "lerna", act(X) { const { t, lt } = X; const cae = 2.5; hidra(t, lt < cae ? 1 : 0, 0, -60, {}); ROCA.visible = true; ROCA.position.set(0, Math.max(0, 140 - Math.max(0, lt - 1.4) ** 2 * 160), -60);
      P(HL, mezcla({ x: 10, z: 20, ry: 180 }, lt < 1.4 ? hombros() : (lt > 4 ? brazosCruz(1) : {})), t, lt > 4 ? "presumido" : "enfado");
      if (X.una("roca")) part.add(X.t0 + cae, 0, 10, -60, 60, ["#8a8780", "#4f4a2c", "#3f7a5a"], 50, 1.4); },
    cams: [general(0, -20, 220, 60), cerca(HL, 26, 0.4, 30), () => [-80, 10, 60, 0, 30, -60, 44]] },
  cangrejo: { set: "lerna", act(X) { const { t, lt } = X; X.dato("Constelación de Cáncer"); const CG = K.CANG; CG.g.visible = lt < 4; CG.g.position.set(lerp(-100, 0, seg(lt, 0.3, 2.3)), 0, 40); CG.g.rotation.y = Math.PI / 2; CG.pinzas.forEach((p, i) => p.rotation.x = 0.4 * Math.sin(t * 12 + i));
      CG.g.scale.set(1, lt > 3.6 ? 0.15 : 1, 1);
      P(HL, mezcla({ x: 14, z: 40, ry: -90 }, lt > 2.4 && lt < 3.8 ? { pR: -60 * Math.sin(cl((lt - 3) / 0.6) * Math.PI), kR: 60 * Math.sin(cl((lt - 3) / 0.6) * Math.PI) } : {}, lt > 2.4 && lt < 3 ? { salto: 6 } : {}), t, lt < 2.6 ? "normal" : (lt < 3.6 ? "grito" : "presumido"));
      if (X.una("plas")) part.add(X.t0 + 3.6, 0, 6, 40, 30, ["#d0402a", "#ffffff"], 30, 1);
      if (lt > 5.5) { const c = lt - 5.5; part.add(0, 0, 0, 0, 0, []); } X.constelacion = lt > 6; },
    cams: [() => [0, 10, 110, 0, 10, 40, 38], cerca(HL, 26, 0.3, 30), () => [20, 14, 70, 0, 6, 40, 40]], alt: { from: 6.2, set: "cielo_noche", cams: [() => [0, 40, 200, 60, 420, -700, 48]] } },
  cancer_chiste: { set: "cielo_noche", act(X) { const { t, lt } = X; P(HL, { x: 0, z: 40, ry: 180, cabX: -30, ...encoge(lt, 2.2) }, t, "presumido"); },
    cams: [() => [40, 20, 120, 60, 300, -700, 48], cerca(HL, 30, 0.3, 32)] },
  // ---------- cierva y jabalí
  cierva: { set: "campo", act(X) { const { t, lt } = X; X.dato("Cierva de Cerinea: cuernos de oro"); quad("CIERVA", lerp(-40, 200, seg(lt, 0, X.dur, x => x)), 0, 90, t, 0.8); if (lt > 4.5) { P(C.ATENEA, { x: 40, z: -60, ry: 0, y: 40 + 3 * Math.sin(t), bR: [-90, 20], cR: 0, bL: [-30, -10], cL: 60 }, t, "enfado"); C.ATENEA.extras.visible = true; } },
    cams: [sigue(K.CIERVA, 0, 26, 110, 40, 16), () => [K.CIERVA.g.position.x + 30, 14, 40, K.CIERVA.g.position.x, 18, 0, 34], () => [0, 30, 160, 40, 40, -60, 40]] },
  cierva_anio: { set: "nieve", act(X) { const { t, lt } = X; const per = X.dur / 3, k = Math.floor(lt / per); const sets = ["nieve", "campo", "nieve"]; X.cambiaSet(sets[k]);
      quad("CIERVA", lerp(-60, 220, (lt % per) / per), 0, 90, t, 1); P(HL, mezcla(andar(lt % per, [-180, 10], [100, 10], 0, per, { correr: 1 }), { lean: 6 + k * 6 }), t, ["normal", "sudor", "espiral"][k]); },
    cams: [sigue(HL, 60, 24, 100, 40), sigue(HL, -40, 14, 60, 44, 30), sigue(HL, 80, 30, 120, 36)] },
  jabali: { set: "nieve", act(X) { const { t, lt } = X; const car = lt > 4.5; quad("JABALI", car ? 0 : lerp(80, -40, seg(lt, 0.5, 4)), car ? 30 : 0, car ? 0 : -90, t, car ? 0 : 0.7, car ? { rz: Math.PI } : {}, car ? 44 : 0);
      P(HL, mezcla(car ? mezcla({ x: 0, z: 30, ry: 0 }, hombros()) : { x: -60, z: 0, ry: 90, bR: [-60 + 40 * Math.sin(t * 9), 30], cR: 40 }), t, car ? "risa" : "grito");
      if (!car && X.una("nieve")) part.add(X.t0 + 4, -40, 10, 0, 40, ["#ffffff", "#e8f0f8"], 30, 1.2); },
    cams: [general(0, 0, 220, 50), cerca(HL, 30, 0.3, 30), contra(HL, 1, 70)] },
  tinaja: { set: "palacio", act(X) { const { t, lt } = X; const ent = 4.2; P(HL, mezcla(andar(lt, [0, 120], [0, -10], 0, 4.5), hombros()), t, "risa"); quad("JABALI", HL.root.position.x, HL.root.position.z, 0, t, 0, { rz: Math.PI }, 44);
      const sal = seg(lt, ent, ent + 0.6), dentro = lt > ent + 0.6; P(C.EURI, mezcla({ x: lerp(0, 70, sal), z: lerp(-140, -70, sal), y: dentro ? lerp(0, 2, seg(lt, ent + 0.6, ent + 0.9)) + muelle(lt, ent + 0.9, 3) : 32 * (1 - sal) + Math.sin(sal * Math.PI) * 30, ry: 0 }, susto(lt, ent), dentro && lt > 8 ? { y: 3 + 2 * Math.sin(t * 8), bR: [-150, 10], cR: 0 } : {}), t, lt < ent ? "presumido" : (lt > 8 ? "habla" : "susto")); },
    cams: [general(0, -40, 240, 70), cerca(HL, 30, 0.3, 30), () => [120, 30, -30, 70, 12, -70, 36], cerca(C.EURI, 26, 0.2, 30, -6)] },
  tinaja_chiste: { set: "palacio", act(X) { const { t, lt } = X; P(C.EURI, { x: 70, z: -70, y: 3 + 2 * Math.sin(t * 6), ry: -30, bR: [-150, 10], cR: 0 }, t, X.env(X.t) > 0.3 ? "habla" : "presumido");
      P(C.AMA1, { x: 20, z: -40, ry: 60, bR: [-30, 20], cR: 80, cabX: 20 }, t, "sudor"); C.AMA1.extras.visible = false; },
    cams: [() => [30, 20, -20, 70, 10, -70, 36], cerca(C.AMA1, 26, 0.3, 30)] },
  // ---------- establos y pájaros
  establos: { set: "establos", act(X) { const { t, lt } = X; P(HL, mezcla(andar(lt, [-160, 60], [-40, 40], 0, 2.5), lt > 3 ? { cabY: 30 * Math.sin(t * 1.2), cabX: 10 } : {}, lt > 6 ? { bR: [-60, 20], cR: 90 } : {}), t, lt > 3 ? (lt > 6 ? "sudor" : "sorpresa") : "normal");
      P(C.AUGIAS, mezcla({ x: 60, z: 40, ry: -60 }, gestoHabla(X)), t, X.env(X.t) > 0.35 ? "habla" : "malvado");
      if (X.una("moscas")) for (let k = 0; k < 6; k++) part.add(X.t0 + k * 1.5, (rnd(k) - 0.5) * 200, 10, -120, 8, ["#2a2a2a"], 12, 0.5, -10, 1.6); },
    cams: [general(0, -60, 260, 80), medio(HL, -1, 90), () => [40, 30, 120, 60, 26, 40, 38], general(-20, 20, 160, 40)] },
  rios: { set: "establos", act(X) { const { t, lt } = X; X.dato("Ríos Alfeo y Peneo"); const rompe = 2.6;
      P(HL, mezcla({ x: -170, z: -60, ry: -90 }, golpe(lt, rompe)), t, lt < rompe ? "enfado" : "risa");
      if (X.una("muro")) part.add(X.t0 + rompe, -184, 20, -100, 60, ["#9a6a3c", "#6b4424", "#7a5532"], 50, 1.4);
      const ag = seg(lt, rompe + 0.4, rompe + 3); X.rios(ag); },
    cams: [() => [-60, 40, 80, -170, 20, -80, 40], picado(0, -120, 300, 150, 48), () => [120, 30, 100, 0, 10, -120, 40]] },
  no_cuenta: { set: "palacio", act(X) { const { t, lt } = X; X.dato("10 trabajos → 12 trabajos"); P(C.EURI, mezcla({ x: 70, z: -70, y: 3, ry: 30 }, { bR: [-150 + 20 * Math.sin(t * 6), 10], cR: 30 }), t, X.env(X.t) > 0.3 ? "habla" : "malvado"); TIN.visible = false;
      P(HL, mezcla({ x: 0, z: 0, ry: 120 }, lt > 4 ? { bR: [-40, 30], cR: 80, bL: [-40, -30], cL: 80 } : {}, lt > 8 ? encoge(lt, 8.5) : {}), t, lt < 4 ? "sorpresa" : (lt < 8 ? "enfado" : "lloro"));
      P(C.YOLAO, { x: -30, z: 10, ry: 100, ...encoge(lt, 5) }, t, "triste"); },
    cams: [() => [40, 30, 40, 70, 10, -70, 34], cerca(HL, 30, 0.3, 30), () => [-20, 40, 120, 20, 20, -30, 38], cerca(C.EURI, 24, 0.2, 30, -6)] },
  pajaros: { set: "lago", act(X) { const { t, lt } = X; const suena = 4.6, flechas = 8.5; pajaros(t, lt < suena ? 0 : 12, 0, 120, -200, 160, flechas);
      P(C.ATENEA, { x: 60, z: 20, ry: -60, bR: [-90, 10], cR: 0 }, t, "presumido"); C.ATENEA.root.visible = lt < suena; C.ATENEA.extras.visible = true;
      P(HL, mezcla({ x: -20, z: 30, ry: 160 }, lt > suena && lt < flechas ? { bR: [-120, 40 + 30 * Math.sin(t * 20)], bL: [-120, -40 - 30 * Math.sin(t * 20)], cR: 60, cL: 60, salto: Math.abs(Math.sin(t * 10)) * 3 } : (lt > flechas ? { bL: [-110, -10], cL: 0, bR: [-110, 20], cR: lerp(120, 0, seg((lt - flechas) % 0.5, 0.3, 0.35)) } : {})), t, lt > suena && lt < flechas ? "risa" : "enfado");
      if (lt < flechas) { enMano(HL, CASTA); enMano(HL, CASTA2, "L"); } else enMano(HL, ARCO, "L"); },
    cams: [general(0, -40, 240, 60), () => [-80, 10, 80, 0, 120, -200, 50], cerca(HL, 26, 0.3, 30), () => [80, 20, 120, 0, 60, -200, 44]] },
  pajaros_chiste: { set: "lago", act(X) { const { t, lt } = X; P(HL, { x: -20, z: 30, ry: 180, bR: [-120, 40], bL: [-120, -40], cR: 60, cL: 60 }, t, "presumido"); enMano(HL, CASTA); enMano(HL, CASTA2, "L");
      quietos2(X, [[-90, -10, 140], [60, -10, 200]], "tapa"); },
    cams: [() => [0, 30, 120, -20, 28, 30, 36]] },
  // ---------- toro y yeguas
  toro: { set: "creta", act(X) { const { t, lt } = X; const k = lt < 5 ? 0 : (lt < 8 ? 1 : 2);
      if (k === 0) { quad("TORO", lerp(80, 0, seg(lt, 0, 2)), 0, -90, t, lt < 2 ? 0.8 : 0); P(HL, mezcla({ x: -30, z: 0, ry: 90 }, lt > 2 ? { bR: [-90, 30], bL: [-90, -30], cR: 30, cL: 30, lean: 15 } : {}), t, "enfado"); K.TORO.cabezas[0].rotation.x = lt > 2 ? 0.4 : 0; }
      else if (k === 1) { X.cambiaSet("palacio"); quad("TORO", lerp(0, 160, seg(lt, 6, 7.5)), 0, 90, t, lt > 6 ? 0.8 : 0); P(C.EURI, { x: -40, z: -20, ry: 90, bR: [-90, 10], cR: 0 }, t, "risa"); }
      else { X.cambiaSet("campo"); quad("TORO", lerp(-200, 200, seg(lt, 8, X.dur, x => x)), 0, 90, t, 0.5); quietos2(X, [[-60, -40, 200], [60, -40, 160]], "susto"); } },
    cams: [general(0, 0, 220, 50), cerca(HL, 30, 0.3, 30), () => [0, 30, 180, 40, 20, 0, 40], sigue(K.TORO, 0, 30, 160, 40, 20)] },
  yeguas: { set: "tracia", act(X) { const { t, lt } = X; const pelea = 4.5, cena = 8;
      quad("YEG1", -40, -40, 20, t, 0, { cabX: lt > cena ? 40 : -10 }); quad("YEG2", 40, -40, -20, t, 0, { cabX: lt > cena ? 40 : -10 });
      if (lt < cena) P(C.DIOM, mezcla({ x: 10, z: 30, ry: 180 }, lt < pelea ? gestoHabla(X) : { lean: -40 * seg(lt, pelea + 0.3, pelea + 0.6), salto: Math.sin(cl((lt - pelea - 0.3) / 0.6) * Math.PI) * 20 }), t, lt < pelea ? "malvado" : "espiral");
      if (lt > pelea + 0.6 && lt < cena) { C.DIOM.root.position.z = lerp(30, -30, seg(lt, pelea + 0.3, pelea + 0.9)); }
      P(HL, mezcla({ x: -20, z: 70, ry: 160 }, golpe(lt, pelea + 0.3), lt > cena + 1 ? { bR: [-60, 20], cR: 80 } : {}), t, lt < cena ? "enfado" : "presumido");
      if (X.una("pelea")) part.add(X.t0 + pelea + 0.35, 10, 30, 30, 30, ["#ffffff", "#ffd040"], 34, 0.8, 50, 0.8, true);
      if (lt > cena + 1.5) { K.YEG1.cabezas[0].rotation.x = 0.3; for (const y of [K.YEG1, K.YEG2]) y.g.rotation.z = 0.05 * Math.sin(t * 2); } },
    cams: [general(0, -10, 230, 60), cerca(C.DIOM, 30, -0.3, 30), contra(HL, 1, 70), () => [0, 24, 50, 0, 20, -40, 40]] },
  // ---------- amazonas, Gerión y columnas
  amazonas: { set: "amazonas", act(X) { const { t, lt } = X; P(HL, mezcla(andar(lt, [-140, 60], [-30, 30], 0, 2.5), lt > 4 ? gestoHabla(X, 1) : {}), t, lt > 2.5 ? "risa" : "normal");
      P(C.HIPO, mezcla({ x: 30, z: 20, ry: -70 }, lt > 6 ? { bR: [-90, 20], cR: 20 } : gestoHabla(X, 2)), t, lt > 5 ? "amor" : "normal"); },
    cams: [general(0, -20, 240, 60), cerca(C.HIPO, 30, 0.3, 30), cerca(HL, 30, -0.3, 30), () => [0, 30, 110, 0, 26, 25, 36]] },
  amazonas_hera: { set: "amazonas", act(X) { const { t, lt } = X; const ataque = 5.5;
      P(C.HERAD, mezcla({ x: -120, z: -20, ry: 70 }, gestoHabla(X, 3), lt > 3 ? senala(lt, 3) : {}), t, lt < 4 ? "malvado" : "risa"); C.HERAD.root.visible = lt < ataque + 1;
      P(C.AMA1, mezcla(lt > ataque ? andar(lt, [-60, -60], [-20, 10], ataque, ataque + 1.5, { correr: 1 }) : { x: -60, z: -60, ry: 40 }, lt > ataque ? { bR: [-150, 10], cR: 20 } : {}), t, lt > ataque ? "grito" : "sorpresa");
      P(C.AMA2, mezcla(lt > ataque ? andar(lt, [80, -60], [40, 10], ataque, ataque + 1.5, { correr: 1 }) : { x: 80, z: -60, ry: -40 }, lt > ataque ? { bR: [-150, 10], cR: 20 } : {}), t, lt > ataque ? "grito" : "sorpresa");
      P(HL, mezcla({ x: 0, z: 30, ry: 180 }, lt > ataque + 1 ? susto(lt, ataque + 1) : {}, lt > 9 ? encoge(lt, 9) : {}), t, lt < ataque + 1 ? "normal" : (lt < 9 ? "susto" : "lloro"));
      if (X.una("lio")) for (let k = 0; k < 5; k++) part.add(X.t0 + ataque + 1.5 + k * 0.4, (rnd(k) - 0.5) * 40, 20, 20, 20, ["#ffffff", "#c8c0b0", "#ffd040"], 34, 1); },
    cams: [cerca(C.HERAD, 30, 0.3, 30), general(0, -20, 240, 60), contra(HL, 1, 70), () => [0, 30, 120, 0, 26, 0, 40]] },
  columnas: { set: "gibraltar", act(X) { const { t, lt } = X; X.dato("Columnas de Hércules: escudo de España, «Plus Ultra»"); P(HL, mezcla(andar(lt, [-160, 120], [0, 80], 0, 3), lt > 5 && lt < 8 ? hombros() : {}, lt > 9 ? arriba(lt, 9) : {}), t, lt > 9 ? "risa" : (lt > 5 ? "sudor" : "normal"));
      if (lt > 5 && lt < 8) { ROCA.visible = true; ROCA.position.set(HL.root.position.x, 70, HL.root.position.z); ROCA.scale.set(0.6, 1.6, 0.6); } else ROCA.scale.set(1, 1, 1);
      if (X.una("col")) part.add(X.t0 + 8, 0, 10, 60, 40, ["#e8e2d4", "#c9c0ad", "#e3cf98"], 40, 1.2); },
    cams: [general(0, -40, 320, 80, 0, 60, 46), cerca(HL, 30, 0.3, 30), () => [0, 10, 260, 0, 140, -120, 50]] },
  gerion: { set: "gibraltar", act(X) { const { t, lt } = X; const k = lt < 5.5 ? 0 : 1;
      if (k === 0) { const G = C.ATLAS; P(G, { x: 120, z: 0, ry: -80, bR: [-100 + 30 * Math.sin(t * 3), 20], cR: 40 }, t, "enfado"); G.root.scale.setScalar(2.2); quad("PERRO", 60, 30, -90, t, 0.3);
        P(HL, mezcla({ x: -40, z: 40, ry: 90 }, golpe(lt, 3.2), lt > 4.2 ? brazosCruz(1) : {}), t, lt > 4 ? "presumido" : "enfado"); if (X.una("g")) part.add(X.t0 + 3.3, 60, 30, 30, 40, ["#5a4a3a", "#ffffff"], 40, 1); }
      else { C.ATLAS.root.scale.setScalar(2.8); X.cambiaSet("campo"); P(HL, mezcla(andar(lt, [-200, 60], [200, 60], 5.5, X.dur), { lean: 10 }), t, "sudor");
        ["BUEY"].forEach(b => quad(b, HL.root.position.x + 40, 30, 90, t, 0.4)); quad("TORO", HL.root.position.x + 80, 0, 90, t, 0.4); K.TORO.g.scale.setScalar(0.9); } },
    cams: [general(40, 0, 260, 80, 40, 50, 42), cerca(HL, 30, 0.3, 30), sigue(HL, 40, 30, 140, 40)] },
  // ---------- Atlas
  atlas: { set: "jardin", act(X) { const { t, lt } = X; X.dato("Atlas: el titán que sostiene el cielo"); X.cambiaSet(lt < 4 ? "jardin" : "atlas"); if (lt >= 4) { P(C.ATLAS, mezcla({ x: 0, z: -80, ry: 0 }, hombros(), { sq: 1 - 0.03 * Math.sin(t * 2) }), t, "sudor"); CIELOBOLA.visible = true; CIELOBOLA.position.set(0, 150, -80); CIELOBOLA.rotation.y = t * 0.2; CIELOBOLA.scale.setScalar(2.4); }
      else P(HL, mezcla(andar(lt, [-120, 80], [0, 40], 0, 3), { cabY: 30 * Math.sin(t) }), t, "sorpresa"); },
    cams: [general(0, -60, 240, 60), () => [60, 20, 140, 0, 120, -80, 50], contra(C.ATLAS, 1, 40), () => [0, 200, 140, 0, 160, -80, 40]] },
  atlas_trato: { set: "atlas", act(X) { const { t, lt } = X; const cambio = 4.0, vuelve = 7.5;
      const atlasLleva = lt < cambio, x0 = atlasLleva ? 0 : 0; CIELOBOLA.visible = true; CIELOBOLA.scale.setScalar(atlasLleva ? 2.4 : 1.4);
      if (atlasLleva) { P(C.ATLAS, mezcla({ x: 0, z: -80, ry: 0 }, hombros()), t, X.env(X.t) > 0.35 ? "habla" : "sudor"); CIELOBOLA.position.set(0, 150, -80); P(HL, mezcla({ x: 60, z: 0, ry: -30 }, gestoHabla(X)), t, X.env(X.t) > 0.35 ? "habla" : "risa"); }
      else { P(HL, mezcla({ x: 0, z: -40, ry: 0 }, hombros(), { sq: 0.94 }), t, lt > vuelve + 2 ? "sudor" : "normal"); CIELOBOLA.position.set(0, 78, -40);
        P(C.ATLAS, mezcla(andar(lt, [0, -120], [140, -60], cambio, vuelve - 0.5), lt > vuelve ? mezcla({ x: 100, z: 0, ry: -60 }, gestoHabla(X, 1)) : {}), t, lt > vuelve ? "malvado" : "risa"); if (lt > vuelve) { enMano(C.ATLAS, MANZ); MANZ.scale.setScalar(2); } } },
    cams: [() => [80, 30, 160, 0, 110, -80, 46], () => [60, 40, 130, 20, 50, -20, 40], () => [140, 60, 140, 40, 60, -40, 44], () => [-60, 120, 140, 0, 130, -80, 38]] },
  atlas_cojin: { set: "atlas", act(X) { const { t, lt } = X; const pasa = 5.0; CIELOBOLA.visible = true;
      if (lt < pasa) { P(HL, mezcla({ x: 0, z: -40, ry: 0 }, hombros()), t, X.env(X.t) > 0.35 ? "habla" : "presumido"); CIELOBOLA.scale.setScalar(1.4); CIELOBOLA.position.set(0, 78, -40); P(C.ATLAS, { x: 70, z: 0, ry: -60, ...encoge(lt, 2) }, t, "presumido"); enMano(C.ATLAS, MANZ); MANZ.scale.setScalar(2); }
      else { CIELOBOLA.scale.setScalar(2.4); CIELOBOLA.position.set(0, 150, -80); P(C.ATLAS, mezcla({ x: 0, z: -80, ry: 0 }, hombros()), t, lt > 9 ? "lloro" : "sorpresa");
        P(HL, mezcla(andar(lt, [20, 0], [220, 120], pasa + 1, X.dur), { bR: [-120 + 30 * Math.sin(t * 6), 30], cR: 40 }), t, "risa"); enMano(HL, MANZ); MANZ.scale.setScalar(1.2); COJIN.visible = lt > pasa + 1; COJIN.position.set(Math.min(HL.root.position.x, 60) - 10, 50, 0); } },
    cams: [() => [70, 40, 130, 0, 60, -40, 40], () => [0, 60, 200, 0, 80, -60, 44], () => [100, 60, 160, 0, 120, -80, 44], sigue(HL, 50, 30, 120, 40)] },
  // ---------- Cerbero
  inframundo: { set: "inframundo", act(X) { const { t, lt } = X; X.dato("Cerbero: guardián del Hades"); quad("CERB", 0, -80, 0, t, 0, { cabX: -10 + 6 * Math.sin(t * 3) }); P(HL, mezcla(andar(lt, [-140, 120], [-30, 60], 0, 3)), t, lt > 3 ? "sorpresa" : "normal");
      if (lt > 5) P(C.HADES, mezcla({ x: 220, z: -110, ry: -60, y: 20, sentado: 1 }, lt > 7.5 ? { bR: [-90, 20], cR: 0, bL: [-30, -20] } : gestoHabla(X)), t, lt > 7.5 ? "malvado" : "habla"); },
    cams: [general(0, -20, 260, 70), () => [-40, 10, 60, 0, 50, -80, 50], cerca(C.HADES, 34, 0.2, 32), cerca(HL, 30, 0.3, 30)] },
  hades: { set: "inframundo", act(X) { const { t, lt } = X; P(HL, mezcla(andar(lt, [-200, 40], [100, 40], 0, 6)), t, lt < 6 ? "sudor" : "normal");
      ALMAS.forEach((a, i) => { a.root.visible = true; pose(a, { x: -120 + i * 50, z: -40 - (i % 2) * 30, y: 6 + 4 * Math.sin(t * 2 + i), ry: 20 * Math.sin(t + i), bR: [-80, 20], bL: [-80, -20], cR: 20, cL: 20 }, t); cara(a, i % 2 ? "triste" : "lloro"); });
      if (lt > 6.5) P(C.HADES, mezcla({ x: 220, z: -110, ry: -60, y: 20, sentado: 1 }, brazosCruz(1)), t, lt > 10 ? "presumido" : "enfado"); },
    cams: [sigue(HL, 60, 30, 110, 40), () => [-80, 30, 80, -60, 30, -40, 40], cerca(C.HADES, 34, 0.2, 32), () => [100, 30, 120, 160, 30, -100, 40]] },
  cerbero: { set: "inframundo", act(X) { const { t, lt } = X; const agarra = 1.6;
      if (lt < agarra) { quad("CERB", 0, -60, 0, t, 0.4); P(HL, mezcla({ x: 0, z: 20, ry: 180 }, { bR: [-90, 30], bL: [-90, -30], cR: 20, cL: 20 }), t, "enfado"); }
      else { X.cambiaSet("campo"); quad("CERB", 0, 10, 90, t, 0.3, { cabX: 10 * Math.sin(t * 6) }, 0); K.CERB.g.position.y = 0; P(HL, mezcla(andar(lt, [-60, 40], [40, 40], agarra, X.dur), { bL: [-60, -20], cL: 30 }), t, "risa"); } },
    cams: [contra(HL, 1, 70), () => [20, 30, 160, 0, 30, 20, 40]] },
  cerbero_tinaja: { set: "palacio", act(X) { const { t, lt } = X; quad("CERB", 0, 20, 0, t, 0, { cabX: -20 }); P(HL, { x: -50, z: 30, ry: 30, bR: [-90, 20], cR: 30 }, t, "risa");
      P(C.EURI, { x: 70, z: -70, y: 3 + 3 * Math.sin(t * 10), ry: -30, bR: [-150 + 20 * Math.sin(t * 12), 10], cR: 20 }, t, lt > 3 ? "lloro" : "susto"); },
    cams: [general(0, -20, 240, 70), () => [110, 30, -30, 70, 10, -70, 34], cerca(C.EURI, 24, 0.2, 30, -6)] },
  // ---------- final
  resumen: { set: "olimpo", act(X) { const { t, lt } = X; const k = Math.min(3, Math.floor(lt / 2)), sets = ["nemea", "lerna", "establos", "palacio"]; X.cambiaSet(sets[k]);
      if (k === 0) { quad("LEON", 0, 0, 90, t, 0); P(HL, { x: -40, z: 10, ry: 90, ...arriba(lt, 0.2) }, t, "risa"); }
      if (k === 1) { hidra(t, 9, 0, -60, { ataca: 1 }); P(HL, { x: 0, z: 30, ry: 180, ...golpe(lt, 2.6) }, t, "enfado"); enMano(HL, ESPADA); }
      if (k === 2) { X.rios(1); P(HL, { x: -40, z: 40, ry: 20, ...brazosCruz(1) }, t, "presumido"); }
      if (k === 3) P(C.EURI, { x: 70, z: -70, y: 3, ry: 0, bR: [-150, 10], cR: 0 }, t, "habla"); },
    cams: [() => [60, 30, 120, -10, 26, 10, 40], () => [70, 30, 120, 0, 50, -50, 44], () => [0, 80, 200, 0, 10, -100, 44], () => [110, 30, -30, 70, 10, -70, 34]] },
  camisa: { set: "tebas", act(X) { const { t, lt } = X; const pone = 6.5;
      P(C.DEYA, mezcla({ x: 30, z: 40, ry: -90 }, lt < pone ? { bR: [-60, 20], bL: [-60, -20], cR: 70, cL: 70 } : (lt > 9 ? susto(lt, 9) : {})), t, lt < pone ? "amor" : (lt > 9 ? "susto" : "risa"));
      CAMISA.visible = lt < pone; CAMISA.position.set(20, 22, 40);
      P(HL, mezcla({ x: -20, z: 40, ry: 90 }, lt > pone ? { bR: [-100 + 50 * Math.sin(t * 14), 30], bL: [-100 + 50 * Math.sin(t * 13), -30], cR: 60, cL: 60, salto: Math.abs(Math.sin(t * 8)) * 3 } : {}), t, lt > pone + 2.5 ? "grito" : (lt > pone ? "sorpresa" : "risa"));
      if (lt > pone + 2.5 && X.una("veneno")) for (let k = 0; k < 6; k++) part.add(X.t0 + pone + 2.5 + k * 0.25, -20, 30, 40, 16, ["#6aff3a", "#3a8a1a", "#d0ff9a"], 24, 1, -20, 1.2, true); },
    cams: [() => [0, 30, 130, 0, 24, 40, 36], cerca(C.DEYA, 28, -0.3, 30), cerca(HL, 28, 0.3, 30)] },
  pira: { set: "pira", act(X) { const { t, lt } = X; const sube = 4.0; P(HL, mezcla(lt < 2 ? andar(lt, [-60, 40], [0, -40], 0, 2) : { x: 0, z: -60, y: 30, ry: 180 }, lt > 2 ? arriba(lt, 2.2) : {}), t, lt < sube ? "triste" : "risa");
      PIRA_FUEGO.visible = lt > 2.5; PIRA_FUEGO.position.set(0, 0, -60); PIRA_FUEGO.children.forEach((f, i) => { const s = 1 + 0.5 * Math.sin(t * 13 + i); f.scale.set(1, s, 1); }); FL.intensity = lt > 2.5 ? 8000 * (0.8 + 0.2 * Math.sin(t * 15)) : 0; FL.position.set(0, 40, -20);
      if (lt > sube) { HL.root.position.y = 30 + (lt - sube) * 60; X.cambiaSet(lt > sube + 1.5 ? "olimpo" : "pira"); if (lt > sube + 1.5) { HL.root.position.y = 0; P(HL, { x: 0, z: 20, ry: 0, ...arriba(lt, sube + 1.6) }, t, "risa"); P(C.ZEUS, { x: 40, z: 0, ry: -40, bR: [-60, 30], cR: 60 }, t, "risa"); }
        if (X.una("luz")) part.add(X.t0 + sube, 0, 60, -60, 50, ["#fff6c0", "#ffd040", "#ffffff"], 30, 1.2, -30, 2, true); } },
    cams: [general(0, -40, 240, 50), contra(HL, 1, 60), () => [60, 30, 120, 0, 30, 0, 40]] },
  hebe: { set: "olimpo", act(X) { const { t, lt } = X; const boda = 4;
      P(C.HERA, mezcla({ x: -40, z: 20, ry: 40 }, lt < boda ? gestoHabla(X) : { bR: [-60, 30], cR: 60 }), t, lt < 2 ? "enfado" : (lt < 8 ? "risa" : "malvado"));
      P(HL, mezcla({ x: 20, z: 20, ry: -20 }, lt > boda ? { bL: [-40, -30], cL: 60 } : {}), t, lt < boda ? "sorpresa" : (lt > 8 ? "sudor" : "amor"));
      if (lt > boda - 1) P(C.HEBE, mezcla(andar(lt, [140, 40], [44, 20], boda - 1, boda), { bR: [-40, 30], cR: 60 }), t, "amor");
      if (X.una("boda")) part.add(X.t0 + boda, 30, 50, 20, 40, ["#ff8ab0", "#ffffff", "#ffd040"], 30, 1, 20, 2, true); },
    cams: [() => [0, 30, 140, 0, 28, 20, 36], cerca(C.HERA, 30, 0.3, 30), cerca(HL, 30, -0.2, 30), () => [60, 40, 160, 20, 30, 20, 40]] },
  final_chiste: { set: "olimpo", act(X) { const { t, lt } = X; P(HL, mezcla({ x: 0, z: 30, ry: 0 }, lt < 4 ? arriba(lt, 0.3) : encoge(lt, 4.5)), t, lt < 4 ? "risa" : "lloro"); P(C.HERA, { x: -40, z: 0, ry: 30, ...brazosCruz(1) }, t, "malvado"); },
    cams: [cerca(HL, 34, 0.2, 32), () => [-20, 30, 130, -20, 26, 15, 38], cerca(C.HERA, 30, 0.3, 30)] },
  cierre: { set: "olimpo", act(X) { const { t, lt } = X; P(HL, mezcla({ x: 0, z: 40, ry: 0 }, lt > 2.5 && lt < 5 ? senala(lt, 2.6) : (lt > 5 ? arriba(lt, 5.2) : gestoHabla(X))), t, X.env(X.t) > 0.35 ? "habla" : "risa"); X.cta(lt); },
    cams: [() => [0, 34, 120, 0, 30, 40, 36]] },
};
let _lt = 0; export function setLt(v) { _lt = v; } function X_lt() { return _lt; }
// extras de reacción usados en algunas escenas
const _ex = []; let _exUsados = 0; export function resetExtras() { _exUsados = 0; _ex.forEach(e => e.root.visible = false); }
function quietos2(X, lista, accion) { lista.forEach(([x, z, ry], i) => { if (!_ex[_exUsados]) { const e = personaje({ seed: 600 + _exUsados * 7, piel: ["#f0c8a0", "#d39a6a", "#a8704a"][_exUsados % 3], pelo: ["#3a2414", "#1f1b17", "#c27a3a"][_exUsados % 3], ropa: ["#b5452f", "#3f6fb5", "#d9a630", "#5f9e3a"][_exUsados % 4], falda: 1, sandalia: "#5a3a1a" }); scene.add(e.root); _ex.push(e); }
  const e = _ex[_exUsados++], t = X.t, s = Math.sin(t * 12 + i); const p = { x, z, ry, seed: i };
  if (accion === "aplaude") Object.assign(p, { bR: [-80, 25 + 15 * s], bL: [-80, -25 - 15 * s], cR: 60, cL: 60 }); if (accion === "susto") Object.assign(p, { bR: [-150, 30], bL: [-150, -30], cR: 20, cL: 20, salto: Math.abs(s) * 3 });
  if (accion === "tapa") Object.assign(p, { bR: [-150, 70], bL: [-150, -70], cR: 120, cL: 120 }); P(e, p, t, accion === "aplaude" ? "risa" : (accion === "tapa" ? "enfado" : "susto")); }); }
