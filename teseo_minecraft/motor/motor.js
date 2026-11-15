// Núcleo del motor estilo bloques: utilidades, texturas, personajes con 15 caras, accesorios, vóxeles instanciados, partículas.
import * as THREE from "three";
export { THREE };
export const cl = (x, a = 0, b = 1) => Math.max(a, Math.min(b, x));
export const lerp = (a, b, x) => a + (b - a) * x;
export const sm = x => { x = cl(x); return x * x * (3 - 2 * x); };
export const eout = x => 1 - Math.pow(1 - cl(x), 3);
export const back = (x, s = 2) => { x = cl(x) - 1; return 1 + (s + 1) * x * x * x + s * x * x; };
export const seg = (t, a, b, e = sm) => e(cl((t - a) / (b - a)));
export const D = Math.PI / 180;
export function rnd(i) { const x = Math.sin(i * 127.1 + 311.7) * 43758.5453; return x - Math.floor(x); }
export function shade(hex, f) { const c = new THREE.Color(hex); c.multiplyScalar(f); return "#" + c.getHexString(); }

// ------------------------------------------------------------------ texturas pixel
export function tex(w, h, fn, seed = 1) {
  const c = document.createElement("canvas"); c.width = w; c.height = h; const g = c.getContext("2d");
  const px = (x, y, col) => { g.fillStyle = col; g.fillRect(x, y, 1, 1); };
  fn(px, w, h, (x, y) => rnd(seed * 997 + x * 31 + y * 17), g);
  const t = new THREE.CanvasTexture(c); t.magFilter = THREE.NearestFilter; t.minFilter = THREE.NearestFilter; t.colorSpace = THREE.SRGBColorSpace; t.generateMipmaps = false; return t;
}
export const fill = (px, w, h, col, r, v = 0.08) => { for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) px(x, y, shade(col, 1 - v + 2 * v * r(x, y))); };
export const M = t => new THREE.MeshLambertMaterial({ map: t });
export const MB = c => new THREE.MeshBasicMaterial({ color: c });
const ladr = (base, junta, sd, alto = 4) => tex(16, 16, (px, w, h, r) => { for (let y = 0; y < 16; y++) for (let x = 0; x < 16; x++) { const fila = Math.floor(y / alto), m = y % alto === 0 || (x + (fila % 2) * 8) % 16 === 0; px(x, y, m ? junta : shade(base, 0.9 + 0.2 * r(x, y))); } }, sd);
const salpic = (base, v, extra, sd) => tex(16, 16, (px, w, h, r) => { fill(px, 16, 16, base, r, v); if (extra) for (let k = 0; k < extra[1]; k++) px(Math.floor(r(k, 2) * 16), Math.floor(r(2, k) * 16), extra[0]); }, sd);
export const T = {
  hierbaTop: tex(16, 16, (px, w, h, r) => { fill(px, w, h, "#5f9e3a", r, 0.14); for (let k = 0; k < 18; k++) px(Math.floor(r(k, 1) * 16), Math.floor(r(1, k) * 16), "#7fbf4a"); }, 2),
  hierbaLado: tex(16, 16, (px, w, h, r) => { fill(px, w, h, "#7a5532", r, 0.14); for (let x = 0; x < 16; x++) { const d = 3 + Math.floor(r(x, 9) * 3); for (let y = 0; y < d; y++) px(x, y, shade("#5f9e3a", 0.9 + 0.2 * r(x, y))); } }, 3),
  hierbaSecaTop: salpic("#a8a046", 0.14, ["#c2b25a", 20], 13),
  tierra: salpic("#7a5532", 0.16, ["#5e4026", 10], 4),
  camino: salpic("#b08a5a", 0.12, ["#8a6a40", 14], 14),
  marmol: tex(16, 16, (px, w, h, r) => { fill(px, w, h, "#e8e2d4", r, 0.05); for (let k = 0; k < 16; k++) px(k, Math.floor(8 + 4 * Math.sin(k * 0.7)), "#c9c0ad"); }, 5),
  columna: tex(16, 16, (px, w, h, r) => { for (let y = 0; y < 16; y++) for (let x = 0; x < 16; x++) px(x, y, shade(x % 4 === 0 ? "#cfc7b4" : "#ece6d8", 0.96 + 0.08 * r(x, y))); }, 6),
  oro: tex(16, 16, (px, w, h, r) => { fill(px, w, h, "#d9a630", r, 0.1); for (let x = 0; x < 16; x++) { px(x, 0, "#f3d26a"); px(x, 15, "#9a7020"); } }, 7),
  madera: tex(16, 16, (px, w, h, r) => { for (let y = 0; y < 16; y++) for (let x = 0; x < 16; x++) px(x, y, shade(y % 4 === 0 ? "#6b4424" : "#9a6a3c", 0.93 + 0.14 * r(x, y))); }, 8),
  maderaOsc: tex(16, 16, (px, w, h, r) => { for (let y = 0; y < 16; y++) for (let x = 0; x < 16; x++) px(x, y, shade(y % 4 === 0 ? "#3a2412" : "#5a3a1e", 0.93 + 0.14 * r(x, y))); }, 15),
  piedra: salpic("#8a8780", 0.15, ["#6d6a64", 8], 9),
  piedraOsc: ladr("#55524c", "#2a2824", 16, 8),
  musgo: tex(16, 16, (px, w, h, r) => { for (let y = 0; y < 16; y++) for (let x = 0; x < 16; x++) { const m = y % 8 === 0 || (x + (Math.floor(y / 8) % 2) * 8) % 16 === 0; px(x, y, m ? "#2a2824" : (r(x, y) < 0.45 ? shade("#4a6a2a", 0.8 + 0.3 * r(y, x)) : shade("#55524c", 0.9 + 0.2 * r(x, y)))); } }, 17),
  roca: salpic("#7d7a72", 0.2, ["#5f5c55", 26], 18),
  arena: salpic("#e6d39a", 0.08, ["#d4bd80", 18], 19),
  arenaMojada: salpic("#bfa870", 0.08, ["#a8925c", 14], 20),
  cal: salpic("#f2efe6", 0.04, ["#e2ddd0", 8], 21),
  teja: tex(16, 16, (px, w, h, r) => { for (let y = 0; y < 16; y++) for (let x = 0; x < 16; x++) px(x, y, shade(y % 4 === 3 ? "#8a3a20" : ((x + (Math.floor(y / 4) % 2) * 4) % 8 === 0 ? "#9a4426" : "#c0582e"), 0.93 + 0.14 * r(x, y))); }, 22),
  rojo: tex(16, 16, (px, w, h, r) => { for (let y = 0; y < 16; y++) for (let x = 0; x < 16; x++) px(x, y, shade(x % 8 === 0 ? "#8a1e18" : "#b8302a", 0.94 + 0.12 * r(x, y))); }, 23),
  negro: salpic("#22201e", 0.1, null, 24),
  ocre: salpic("#d9b46a", 0.06, ["#c49a50", 10], 25),
  friso: tex(16, 16, (px, w, h, r) => { fill(px, w, h, "#d9b46a", r, 0.05); for (let x = 0; x < 16; x++) { px(x, 4, "#b8302a"); px(x, 5, "#b8302a"); px(x, 11, "#2f5f9f"); px(x, 12, "#2f5f9f"); if (x % 4 < 2) px(x, 8, "#22201e"); } }, 26),
  tela: tex(16, 16, (px, w, h, r) => { fill(px, w, h, "#f2ead8", r, 0.04); for (let x = 0; x < 16; x += 5) for (let y = 0; y < 16; y++) px(x, y, "#ddd2b8"); }, 11),
  telaNegra: tex(16, 16, (px, w, h, r) => { fill(px, w, h, "#1e1c22", r, 0.08); for (let x = 0; x < 16; x += 5) for (let y = 0; y < 16; y++) px(x, y, "#121016"); }, 27),
  hoja: tex(16, 16, (px, w, hh, r) => { fill(px, 16, 16, "#3f7f2e", r, 0.22); for (let k = 0; k < 20; k++) px(Math.floor(r(k, 7) * 16), Math.floor(r(7, k) * 16), "#2c5e20"); }, 33),
  olivo: tex(16, 16, (px, w, hh, r) => { fill(px, 16, 16, "#7a8a4a", r, 0.2); for (let k = 0; k < 24; k++) px(Math.floor(r(k, 7) * 16), Math.floor(r(7, k) * 16), "#a8b06a"); }, 35),
  pino: tex(16, 16, (px, w, hh, r) => { fill(px, 16, 16, "#2a5a32", r, 0.2); for (let k = 0; k < 20; k++) px(Math.floor(r(k, 9) * 16), Math.floor(r(9, k) * 16), "#1c4024"); }, 36),
  palma: tex(16, 16, (px, w, hh, r) => { fill(px, 16, 16, "#4a9a3a", r, 0.2); for (let y = 0; y < 16; y += 3) for (let x = 0; x < 16; x++) px(x, y, "#357a2a"); }, 37),
  tronco: tex(16, 16, (px, w, hh, r) => { for (let y = 0; y < 16; y++) for (let x = 0; x < 16; x++) px(x, y, shade(x % 5 === 0 ? "#4a3220" : "#6b4a2c", 0.9 + 0.2 * r(x, y))); }, 34),
  nieve: salpic("#f4f6fa", 0.04, null, 38),
  nube: tex(8, 8, (px, w, h, r) => fill(px, w, h, "#ffffff", r, 0.03), 12),
  agua: tex(16, 16, (px, w, h, r) => { fill(px, w, h, "#2f7fc0", r, 0.06); for (let k = 0; k < 14; k++) { const x = Math.floor(r(k, 3) * 14), y = Math.floor(r(3, k) * 16); px(x, y, "#5aa6e0"); px(x + 1, y, "#5aa6e0"); } }, 39),
  aguaOsc: tex(16, 16, (px, w, h, r) => { fill(px, w, h, "#1f5a96", r, 0.06); for (let k = 0; k < 10; k++) { const x = Math.floor(r(k, 3) * 14), y = Math.floor(r(3, k) * 16); px(x, y, "#3f7fc0"); px(x + 1, y, "#3f7fc0"); } }, 40),
  alfombra: tex(16, 16, (px, w, h, r) => { fill(px, 16, 16, "#8a2f2f", r, 0.08); for (let i = 0; i < 16; i++) { px(i, 0, "#d9a630"); px(i, 15, "#d9a630"); px(0, i, "#d9a630"); px(15, i, "#d9a630"); } }, 81),
  hueso: salpic("#e8e2cc", 0.06, null, 41),
  bronce: salpic("#b0813a", 0.12, ["#8a6028", 10], 42),
  paja: tex(16, 16, (px, w, h, r) => { for (let y = 0; y < 16; y++) for (let x = 0; x < 16; x++) px(x, y, shade((x + y) % 3 === 0 ? "#b8963e" : "#d8b858", 0.9 + 0.2 * r(x, y))); }, 43),
};
export const MAT = {};
for (const k in T) MAT[k] = M(T[k]);
MAT.hierba = [M(T.hierbaLado), M(T.hierbaLado), M(T.hierbaTop), M(T.tierra), M(T.hierbaLado), M(T.hierbaLado)];
MAT.hierbaSeca = [M(T.hierbaLado), M(T.hierbaLado), M(T.hierbaSecaTop), M(T.tierra), M(T.hierbaLado), M(T.hierbaLado)];
MAT.nube = new THREE.MeshLambertMaterial({ map: T.nube, transparent: true, opacity: 0.95, fog: true });
MAT.fuego = MB("#ffb347"); MAT.fuego2 = MB("#ff7a2a"); MAT.brasa = MB("#ffdd66");
MAT.vidrio = MB("#1b2a55");

// ------------------------------------------------------------------ vóxeles instanciados
export class Vox {
  constructor(grupo) { this.g = grupo; this.b = new Map(); }
  add(mk, x, y, z, s = 16, sy, sz) { const k = mk + "|" + s + "|" + (sy || s) + "|" + (sz || s); if (!this.b.has(k)) this.b.set(k, []); this.b.get(k).push([x, y, z]); }
  // cubo apoyado en y (y = base)
  cubo(mk, x, y, z, s = 16) { this.add(mk, x, y + s / 2, z, s); }
  hacer(sombra = true) {
    const m = new THREE.Matrix4();
    for (const [k, l] of this.b) { const [mk, s, sy, sz] = k.split("|"); const im = new THREE.InstancedMesh(new THREE.BoxGeometry(+s, +sy, +sz), MAT[mk], l.length);
      l.forEach((p, i) => { m.makeTranslation(p[0], p[1], p[2]); im.setMatrixAt(i, m); }); im.castShadow = sombra; im.receiveShadow = true; im.frustumCulled = false; im.computeBoundingSphere(); this.g.add(im); }
    this.b.clear();
  }
}
// plantas en cruz instanciadas
const PLANTAS = {};
export function texPlanta(tipo) {
  if (PLANTAS[tipo]) return PLANTAS[tipo];
  const f = {
    hierba: (px, w, h, r) => { for (let x = 0; x < 8; x++) { const top = 2 + Math.floor(r(x, 1) * 5); for (let y = top; y < 8; y++) px(x, y, shade("#5f9e3a", 0.85 + 0.3 * r(x, y))); } },
    seca: (px, w, h, r) => { for (let x = 0; x < 8; x++) { const top = 2 + Math.floor(r(x, 1) * 5); for (let y = top; y < 8; y++) px(x, y, shade("#b8a24a", 0.85 + 0.3 * r(x, y))); } },
    helecho: (px, w, h, r) => { for (let y = 1; y < 8; y++) { const a = Math.floor((8 - y) / 2); for (let x = 3 - a; x <= 4 + a; x++) if ((x + y) % 2 === 0 || x === 3 || x === 4) px(x, y, shade("#3f8a3a", 0.8 + 0.3 * r(x, y))); } },
    roja: (px, w, h, r) => { for (let y = 3; y < 8; y++) px(4, y, "#3f7f2e"); px(3, 5, "#3f7f2e"); px(4, 1, "#d33a2f"); px(3, 2, "#d33a2f"); px(5, 2, "#d33a2f"); px(4, 3, "#d33a2f"); px(4, 2, "#ffe04a"); },
    amarilla: (px, w, h, r) => { for (let y = 3; y < 8; y++) px(4, y, "#3f7f2e"); px(5, 5, "#3f7f2e"); px(4, 1, "#f2c84a"); px(3, 2, "#f2c84a"); px(5, 2, "#f2c84a"); px(4, 3, "#f2c84a"); px(4, 2, "#a0602a"); },
    morada: (px, w, h, r) => { for (let y = 3; y < 8; y++) px(4, y, "#3f7f2e"); px(3, 6, "#3f7f2e"); px(4, 1, "#7f5aa8"); px(3, 2, "#7f5aa8"); px(5, 2, "#7f5aa8"); px(4, 3, "#7f5aa8"); px(4, 2, "#fff"); },
    arbusto: (px, w, h, r) => { for (let y = 2; y < 8; y++) for (let x = 0; x < 8; x++) if (Math.hypot(x - 3.5, y - 5) < 3.6 && r(x, y) > 0.15) px(x, y, shade("#4f7a2e", 0.75 + 0.4 * r(x, y))); },
    juncos: (px, w, h, r) => { for (let x = 0; x < 8; x += 2) { const top = Math.floor(r(x, 4) * 3); for (let y = top; y < 8; y++) px(x, y, shade("#6a8a3a", 0.8 + 0.3 * r(x, y))); px(x, top, "#6a4a2a"); } },
    hueso: (px, w, h, r) => { for (let x = 1; x < 7; x++) px(x, 6, "#e8e2cc"); px(0, 5, "#e8e2cc"); px(0, 7, "#e8e2cc"); px(7, 5, "#e8e2cc"); px(7, 7, "#e8e2cc"); px(2, 3, "#e8e2cc"); px(3, 2, "#e8e2cc"); px(4, 3, "#e8e2cc"); px(3, 4, "#e8e2cc"); px(3, 3, "#222"); },
  }[tipo];
  return PLANTAS[tipo] = new THREE.MeshLambertMaterial({ map: tex(8, 8, f, 88 + tipo.length), transparent: true, alphaTest: 0.5, side: THREE.DoubleSide });
}
export class Plantas {
  constructor(grupo) { this.g = grupo; this.b = {}; }
  add(tipo, x, y, z, s = 10) { (this.b[tipo] ||= []).push([x, y, z, s]); }
  hacer() {
    const m = new THREE.Matrix4(), q = new THREE.Quaternion(), e = new THREE.Euler(), v = new THREE.Vector3(), sc = new THREE.Vector3();
    for (const tipo in this.b) { const l = this.b[tipo], mat = texPlanta(tipo);
      for (const rot of [0.78, -0.78]) { const im = new THREE.InstancedMesh(new THREE.PlaneGeometry(1, 1), mat, l.length);
        l.forEach((p, i) => { e.set(0, rot + (rnd(i * 3.1) - 0.5) * 0.3, 0); q.setFromEuler(e); v.set(p[0], p[1] + p[3] / 2, p[2]); sc.set(p[3], p[3], 1); m.compose(v, q, sc); im.setMatrixAt(i, m); });
        im.frustumCulled = false; this.g.add(im); } }
  }
}

// ------------------------------------------------------------------ caras (8x8) — 15 expresiones
export const EXPR = ["normal", "enfado", "risa", "cerrados", "grito", "susto", "triste", "sorpresa", "sudor", "enamorado", "mareado", "malvado", "aburrido", "llanto", "guino", "habla"];
function pintaCara(px, sp, expr, r) {
  fill(px, 8, 8, sp.piel, r, 0.05);
  if (sp.melena) { for (let x = 0; x < 8; x++) { px(x, 0, sp.pelo); px(x, 1, sp.pelo); } for (const y of [2, 3, 4]) { px(0, y, sp.pelo); px(7, y, sp.pelo); } }
  else if (!sp.calvo) for (let x = 0; x < 8; x++) { px(x, 0, sp.pelo); if (x < 2 || x > 5 || sp.flequillo) px(x, 1, sp.pelo); }
  else { px(0, 1, sp.pelo); px(7, 1, sp.pelo); px(0, 2, sp.pelo); px(7, 2, sp.pelo); }
  if (sp.casco) for (let x = 0; x < 8; x++) { px(x, 0, "#b0813a"); px(x, 1, "#b0813a"); if (x < 1 || x > 6) { px(x, 2, "#b0813a"); px(x, 3, "#b0813a"); } }
  const W = "#ffffff", P = sp.ojos || "#3a2a1a", piel6 = shade(sp.piel, 0.6), piel8 = shade(sp.piel, 0.82), ceja = sp.ceja || shade(sp.pelo, 0.8);
  const ojos = (l, rr) => { px(1, 4, l[0]); px(2, 4, l[1]); px(5, 4, rr[0]); px(6, 4, rr[1]); };
  // ojos
  switch (expr) {
    case "cerrados": case "risa": ojos([piel6, piel6], [piel6, piel6]); break;
    case "guino": ojos([W, P], [piel6, piel6]); break;
    case "mareado": px(1, 4, P); px(2, 3, P); px(2, 5, P); px(5, 3, P); px(6, 4, P); px(5, 5, P); break;
    case "enamorado": for (const o of [1, 5]) { px(o, 3, "#e0304a"); px(o + 1, 3, "#e0304a"); px(o, 4, "#e0304a"); px(o + 1, 4, "#e0304a"); } px(1, 5, "#e0304a"); px(6, 5, "#e0304a"); break;
    case "sorpresa": case "susto": px(1, 3, W); px(2, 3, W); px(1, 4, W); px(2, 4, P); px(5, 3, W); px(6, 3, W); px(5, 4, P); px(6, 4, W); break;
    case "aburrido": ojos([piel8, P], [P, piel8]); px(1, 3, piel6); px(2, 3, piel6); px(5, 3, piel6); px(6, 3, piel6); break;
    case "malvado": ojos([W, P], [P, W]); px(1, 3, ceja); px(2, 3, sp.piel); px(6, 3, ceja); px(5, 3, sp.piel); px(2, 2, ceja); px(5, 2, ceja); break;
    default: ojos([W, P], [P, W]);
  }
  if (expr === "enfado") { px(1, 3, ceja); px(2, 3, piel6); px(6, 3, ceja); px(5, 3, piel6); px(2, 2, ceja); px(5, 2, ceja); }
  if (expr === "triste" || expr === "llanto") { px(1, 2, ceja); px(2, 3, ceja); px(6, 2, ceja); px(5, 3, ceja); }
  if (sp.toro) return;
  px(3, 5, shade(sp.piel, 0.85)); px(4, 5, shade(sp.piel, 0.85));
  if (sp.barba) { for (let x = 1; x < 7; x++) { px(x, 6, sp.barba); px(x, 7, sp.barba); } px(0, 5, sp.barba); px(7, 5, sp.barba); px(0, 6, sp.barba); px(7, 6, sp.barba); }
  const mc = "#6b2a22", dien = "#ffffff";
  switch (expr) {
    case "risa": case "enamorado": px(2, 6, mc); px(3, 7, mc); px(4, 7, mc); px(5, 6, mc); px(3, 6, dien); px(4, 6, dien); break;
    case "guino": px(3, 6, mc); px(4, 6, mc); px(5, 6, mc); px(5, 5, mc); break;
    case "grito": case "susto": case "habla": px(3, 6, mc); px(4, 6, mc); px(3, 7, mc); px(4, 7, mc); if (expr !== "habla") { px(2, 6, mc); px(5, 6, mc); } break;
    case "sorpresa": px(3, 6, mc); px(4, 6, mc); px(3, 7, mc); px(4, 7, mc); break;
    case "enfado": px(2, 7, mc); px(3, 6, mc); px(4, 6, mc); px(5, 7, mc); break;
    case "triste": case "llanto": px(2, 7, mc); px(3, 6, mc); px(4, 6, mc); px(5, 7, mc); break;
    case "malvado": px(2, 6, mc); px(3, 6, mc); px(4, 6, mc); px(5, 5, mc); px(3, 7, dien); break;
    case "mareado": px(2, 6, mc); px(3, 7, mc); px(4, 6, mc); px(5, 7, mc); break;
    case "aburrido": px(3, 6, mc); px(4, 6, mc); px(5, 6, mc); break;
    case "sudor": px(2, 6, mc); px(3, 6, mc); px(4, 6, mc); px(5, 6, mc); px(3, 6, dien); px(4, 6, dien); break;
    default: px(3, 6, mc); px(4, 6, mc);
  }
  if (expr === "sudor") { px(7, 2, "#7ac8ff"); px(7, 3, "#bfe6ff"); }
  if (expr === "llanto") { px(1, 5, "#7ac8ff"); px(1, 6, "#7ac8ff"); px(6, 5, "#7ac8ff"); px(6, 6, "#7ac8ff"); px(1, 7, "#bfe6ff"); px(6, 7, "#bfe6ff"); }
  if (expr === "enfado" || expr === "grito") { px(0, 5, shade(sp.piel, 0.92)); }
  if (expr === "enamorado" || expr === "risa") { px(0, 5, "#e88a8a"); px(7, 5, "#e88a8a"); }
}

// ------------------------------------------------------------------ personajes
export function caja(w, h, d, mat, x = 0, y = 0, z = 0) { const m = new THREE.Mesh(new THREE.BoxGeometry(w, h, d), mat); m.position.set(x, y, z); m.castShadow = true; m.receiveShadow = true; return m; }
function skin(sp) {
  const caras = {};
  for (const e of EXPR) caras[e] = M(tex(8, 8, (px, w, h, r) => pintaCara(px, sp, e, r), sp.seed));
  const P = sp.leon ? "#c48a2c" : sp.pelo;
  const pelo = tex(8, 8, (px, w, h, r) => { fill(px, 8, 8, sp.calvo ? sp.piel : P, r, 0.12); if (sp.casco) fill(px, 8, 8, "#b0813a", r, 0.12); }, sp.seed + 1);
  const ladoT = (izq) => tex(8, 8, (px, w, h, r) => { fill(px, 8, 8, sp.piel, r, 0.05); for (let y = 0; y < 8; y++) for (let x = 0; x < 8; x++) { const xx = izq ? x : 7 - x; if ((!sp.calvo && (y < 2 || (xx > 4 && y < (sp.melena ? 8 : 5)))) || (sp.calvo && xx > 5 && y > 1 && y < 5)) px(x, y, shade(P, 0.9 + 0.2 * r(x, y))); if (sp.casco && y < 4) px(x, y, "#b0813a"); } if (sp.barba) for (let y = 5; y < 8; y++) for (let x = 0; x < 3; x++) px(izq ? x : 7 - x, y, sp.barba); px(izq ? 2 : 5, 4, shade(sp.piel, 0.8)); }, sp.seed + (izq ? 2 : 3));
  const nuca = tex(8, 8, (px, w, h, r) => { fill(px, 8, 8, sp.calvo ? sp.piel : P, r, 0.12); if (sp.calvo) for (let x = 0; x < 8; x++) { px(x, 4, sp.pelo); px(x, 5, sp.pelo); } if (sp.casco) for (let y = 0; y < 5; y++) for (let x = 0; x < 8; x++) px(x, y, "#b0813a"); }, sp.seed + 13);
  const ropa = (w, h, fn, s) => tex(w, h, (px, W, H, r) => { fill(px, W, H, sp.ropa, r, 0.07); fn && fn(px, W, H, r); }, s);
  const torsoF = ropa(8, 12, (px, w, h, r) => {
    if (sp.desnudo) for (let y = 0; y < 7; y++) for (let x = 0; x < 8; x++) px(x, y, shade(sp.piel, 0.95 + 0.1 * r(x, y)));
    if (sp.hombro) for (let y = 0; y < 7; y++) for (let x = 0; x < 3; x++) px(x, y, shade(sp.piel, 0.95 + 0.1 * r(x, y)));
    if (sp.escote) { px(3, 0, sp.piel); px(4, 0, sp.piel); px(3, 1, sp.piel); px(4, 1, sp.piel); }
    if (sp.coraza) for (let y = 0; y < 7; y++) for (let x = 0; x < 8; x++) px(x, y, shade("#b0813a", 0.85 + 0.25 * r(x, y) + (x === 3 || x === 4 ? 0.1 : 0)));
    if (sp.cinto) for (let x = 0; x < 8; x++) px(x, 7, sp.cinto);
    if (sp.ribete) for (let x = 0; x < 8; x++) px(x, 11, sp.ribete);
    if (sp.taparrabo) { for (let y = 8; y < 12; y++) for (let x = 0; x < 8; x++) px(x, y, shade("#6a4a2a", 0.9 + 0.2 * r(x, y))); for (let y = 0; y < 8; y++) for (let x = 0; x < 8; x++) px(x, y, shade(sp.piel, 0.9 + 0.15 * r(x, y) - (y === 3 && (x === 2 || x === 5) ? 0.15 : 0))); }
  }, sp.seed + 4);
  const torsoB = ropa(8, 12, (px, w, h, r) => { if (sp.melena) for (let y = 0; y < 5; y++) for (let x = 1; x < 7; x++) px(x, y, sp.pelo); if (sp.capa) for (let y = 0; y < 12; y++) for (let x = 0; x < 8; x++) px(x, y, shade(sp.capa, 0.9 + 0.15 * r(x, y))); if (sp.cinto) for (let x = 0; x < 8; x++) px(x, 7, sp.cinto); if (sp.taparrabo) fill(px, 8, 8, sp.piel, r, 0.08); }, sp.seed + 5);
  const torsoL = ropa(4, 12, (px, w, h, r) => { if (sp.cinto) for (let x = 0; x < 4; x++) px(x, 7, sp.cinto); if (sp.taparrabo) for (let y = 0; y < 8; y++) for (let x = 0; x < 4; x++) px(x, y, shade(sp.piel, 0.92 + 0.1 * r(x, y))); }, sp.seed + 6);
  const brazoU = tex(4, 6, (px, w, h, r) => { fill(px, 4, 6, sp.mangas ? sp.ropa : sp.piel, r, 0.06); if (sp.brazalete) for (let x = 0; x < 4; x++) px(x, 4, sp.brazalete); }, sp.seed + 7);
  const brazoL = tex(4, 6, (px, w, h, r) => { fill(px, 4, 6, sp.mangasL ? sp.ropa : sp.piel, r, 0.06); if (sp.brazalete) for (let x = 0; x < 4; x++) px(x, 1, sp.brazalete); }, sp.seed + 8);
  const mano = tex(4, 4, (px, w, h, r) => fill(px, 4, 4, shade(sp.piel, 0.92), r, 0.05), sp.seed + 9);
  const piernaU = tex(4, 6, (px, w, h, r) => fill(px, 4, 6, sp.falda ? sp.ropa : (sp.pantalon || sp.piel), r, 0.07), sp.seed + 10);
  const piernaL = tex(4, 6, (px, w, h, r) => { fill(px, 4, 6, sp.faldaLarga ? sp.ropa : (sp.pantalon || sp.piel), r, 0.06); if (!sp.faldaLarga && !sp.descalzo) { for (let x = 0; x < 4; x++) { px(x, 5, sp.sandalia || "#6b4424"); px(x, 3, sp.sandalia || "#6b4424"); } } }, sp.seed + 11);
  const pie = tex(4, 4, (px, w, h, r) => fill(px, 4, 4, sp.descalzo ? sp.piel : (sp.faldaLarga ? sp.ropa : (sp.sandalia || "#6b4424")), r, 0.08), sp.seed + 12);
  const mP = M(pelo), mL = M(ladoT(true)), mR = M(ladoT(false)), mN = M(nuca), mPie = M(pie);
  const cabezas = {}; for (const e of EXPR) cabezas[e] = [mR, mL, mP, M(mano), caras[e], mN];
  return { caras, cabeza: e => cabezas[e] || cabezas.normal, torso: [M(torsoL), M(torsoL), M(torsoL), M(torsoL), M(torsoF), M(torsoB)],
    brazoU: M(brazoU), brazoL: M(brazoL), mano: M(mano), piernaU: M(piernaU), piernaL: M(piernaL), pie: mPie };
}
export function personaje(sp, escala = 1) {
  const S = skin(sp), root = new THREE.Group(), cad = new THREE.Group(); root.add(cad); cad.position.y = 12;
  const torso = new THREE.Group(); cad.add(torso);
  torso.add(caja(8, 12, 4, S.torso, 0, 6, 0));
  if (sp.faldaLarga) torso.add(caja(9, 7, 5, S.torso, 0, -3, 0));
  const cuello = new THREE.Group(); cuello.position.y = 12; torso.add(cuello);
  let cabeza;
  if (sp.toro) {   // cabeza de toro: cráneo + hocico con la cara + cuernos + aro
    const pelT = M(tex(8, 8, (px, w, h, r) => fill(px, 8, 8, "#4a2c18", r, 0.15), 401));
    const g = new THREE.Group(); g.position.y = 4; cuello.add(g);
    cabeza = caja(9, 9, 8, S.cabeza("normal"), 0, 0.5, -0.5); g.add(cabeza);
    const hocico = caja(7, 5, 4, [pelT, pelT, pelT, pelT, M(tex(8, 6, (px, w, h, r) => { fill(px, 8, 6, "#8a6450", r, 0.08); px(2, 2, "#2a1a10"); px(5, 2, "#2a1a10"); px(1, 4, "#5a2a1a"); px(6, 4, "#5a2a1a"); for (let x = 2; x < 6; x++) px(x, 4, "#3a1a10"); }, 402)), pelT], 0, -2, 5); g.add(hocico);
    const aro = caja(3, 2.4, 0.8, MAT.oro, 0, -4.4, 7.2); g.add(aro);
    const cuerno = new THREE.MeshLambertMaterial({ map: T.hueso });
    for (const s of [-1, 1]) { g.add(caja(4, 2.2, 2.2, cuerno, s * 6, 3.6, 0)); g.add(caja(2.2, 4, 2.2, cuerno, s * 8, 6, 0)); g.add(caja(1.6, 2.6, 1.6, cuerno, s * 8, 9, 0.4)); g.add(caja(2, 3, 1.2, pelT, s * 5.8, 1.6, -1)); }
  } else { cabeza = caja(8, 8, 8, S.cabeza("normal"), 0, 4, 0); cuello.add(cabeza); }
  if (sp.corona) { const om = sp.coronaCol ? M(tex(4, 4, (px, w, h, r) => fill(px, 4, 4, sp.coronaCol, r, 0.15), 403)) : MAT.oro; const cg = new THREE.Group(); for (const [x, z] of [[-3, 3], [0, 3.4], [3, 3], [-3.4, 0], [3.4, 0], [-3, -3], [0, -3.4], [3, -3]]) cg.add(caja(1.6, 2.4, 1.6, om, x, 9.2, z)); cg.add(caja(8.6, 1, 8.6, om, 0, 8.2, 0)); cuello.add(cg); }
  if (sp.diadema) cuello.add(caja(8.4, 1, 8.4, MAT.oro, 0, 6.6, 0));
  if (sp.melena) cuello.add(caja(8.6, sp.melenaLarga || 9, 2, M(tex(8, 8, (px, w, h, r) => fill(px, 8, 8, sp.pelo, r, 0.12), 78 + sp.seed)), 0, 4 - ((sp.melenaLarga || 9) - 9) / 2, -4.4));
  if (sp.casco) { cuello.add(caja(1.6, 4, 9, M(tex(4, 4, (px, w, h, r) => fill(px, 4, 4, "#b8302a", r, 0.15), 404)), 0, 9.6, -0.5)); }
  if (sp.velo) cuello.add(caja(9, 9, 9, new THREE.MeshLambertMaterial({ color: sp.velo, transparent: true, opacity: 0.55 }), 0, 4.5, -0.6));
  const mk = (lado) => {
    const sh = new THREE.Group(); sh.position.set(lado * 6, 10, 0); torso.add(sh);
    sh.add(caja(4, 6, 4, S.brazoU, 0, -3, 0));
    const el = new THREE.Group(); el.position.y = -6; sh.add(el);
    el.add(caja(3.9, 5, 3.9, S.brazoL, 0, -2.5, 0)); el.add(caja(4.1, 1.6, 4.1, S.mano, 0, -5.6, 0));
    const mano = new THREE.Group(); mano.position.set(0, -6, 0.5); el.add(mano);
    return { sh, el, mano };
  };
  const mkL = (lado) => {
    const hp = new THREE.Group(); hp.position.set(lado * 2, 0, 0); cad.add(hp);
    hp.add(caja(4, 6, 4, S.piernaU, 0, -3, 0));
    const kn = new THREE.Group(); kn.position.y = -6; hp.add(kn);
    kn.add(caja(3.9, 5, 3.9, S.piernaL, 0, -2.5, 0)); kn.add(caja(4.1, 1.2, 5, S.pie, 0, -5.4, 0.5));
    return { hp, kn };
  };
  const aR = mk(-1), aL = mk(1), lR = mkL(-1), lL = mkL(1);
  if (sp.capa) { const capa = caja(8, 16, 0.8, M(tex(4, 8, (px, w, h, r) => fill(px, 4, 8, sp.capa, r, 0.1), 405)), 0, 2, -2.6); torso.add(capa); }
  // icono sobre la cabeza
  const ico = new THREE.Mesh(new THREE.PlaneGeometry(9, 9), new THREE.MeshBasicMaterial({ transparent: true, alphaTest: 0.4, depthWrite: false, fog: false })); ico.position.y = 50; ico.visible = false; root.add(ico);
  root.scale.setScalar(escala);
  return { root, cad, torso, cuello, cabeza, aR, aL, lR, lL, S, expr: "", ico, sp, escala, props: {} };
}
export function cara(ch, e) { if (ch.expr !== e) { ch.cabeza.material = ch.S.cabeza(e); ch.expr = e; } }
// pose genérica: {x,y,z,ry, rotX, rotZ, lean, giro, ladeo, cabX, cabY, cabZ, bR:[x,z], bL, cR, cL, pR, pL, kR, kL, andar, amp, salto, sq}
export function pose(ch, p, t) {
  const A = p.amp || 0, ph = p.andar || 0;
  const sw = Math.sin(ph) * Math.min(A, 1.4), bob = Math.abs(Math.sin(ph)) * 1.2 * A;
  const resp = Math.sin(t * 2.4 + (p.seed || 0)) * 0.012;
  ch.root.position.set(p.x || 0, (p.y || 0) + (p.salto || 0) + bob, p.z || 0);
  ch.root.rotation.set((p.rotX || 0) * D, (p.ry || 0) * D, (p.rotZ || 0) * D, "YXZ");
  ch.cad.rotation.set(0, (p.giro || 0) * D, 0);
  ch.cad.position.y = 12 + (p.cadY || 0);
  ch.torso.rotation.set(((p.lean || 0) + sw * 3) * D, Math.sin(ph) * 6 * A * D, (p.ladeo || 0) * D);
  ch.torso.scale.set(1, 1 + resp + ((p.sq || 1) - 1), 1);
  ch.cuello.rotation.set((p.cabX || 0) * D, (p.cabY || 0) * D, (p.cabZ || 0) * D);
  const b = (arm, bx, bz, c, s) => { arm.sh.rotation.set((bx + s) * D, 0, bz * D); arm.el.rotation.set(-c * D, 0, 0); };
  b(ch.aR, (p.bR ? p.bR[0] : 0), (p.bR ? p.bR[1] : 0) - 4, p.cR ?? 8 + 6 * A, sw * 38);
  b(ch.aL, (p.bL ? p.bL[0] : 0), (p.bL ? p.bL[1] : 0) + 4, p.cL ?? 8 + 6 * A, -sw * 38);
  const l = (leg, a, k) => { leg.hp.rotation.set(a * D, 0, 0); leg.kn.rotation.set(k * D, 0, 0); };
  l(ch.lR, (p.pR || 0) - sw * 34, (p.kR || 0) + Math.max(0, Math.sin(ph + 1.4)) * 40 * A);
  l(ch.lL, (p.pL || 0) + sw * 34, (p.kL || 0) + Math.max(0, Math.sin(ph + 1.4 + Math.PI)) * 40 * A);
}

// ------------------------------------------------------------------ accesorios (se cuelgan de la mano)
export function hacerProp(n) {
  const g = new THREE.Group();
  const hoja = new THREE.MeshLambertMaterial({ color: "#d8dde4", emissive: "#202428" });
  switch (n) {
    case "espada": g.add(caja(1.4, 3.6, 1.4, MAT.maderaOsc, 0, 0, 0)); g.add(caja(6, 1.2, 1.6, MAT.oro, 0, -2.2, 0)); g.add(caja(1.8, 15, 0.8, hoja, 0, -10, 0)); g.add(caja(1, 1.4, 0.8, hoja, 0, -18, 0)); g.rotation.x = -Math.PI / 2 * 0.0; g.userData.apunta = 1; break;
    case "maza": g.add(caja(1.6, 16, 1.6, MAT.maderaOsc, 0, -4, 0)); g.add(caja(5, 6, 5, MAT.bronce, 0, -13, 0)); for (const [x, z] of [[3, 0], [-3, 0], [0, 3], [0, -3]]) g.add(caja(1.4, 1.4, 1.4, MAT.bronce, x, -13, z)); g.userData.apunta = 1; break;
    case "copa": g.add(caja(4, 3, 4, MAT.oro, 0, 1.5, 1.2)); g.add(caja(1.2, 2, 1.2, MAT.oro, 0, -0.5, 1.2)); g.add(caja(3, 0.6, 3, MAT.oro, 0, -1.6, 1.2)); g.add(caja(3.2, 0.4, 3.2, MB("#5a1030"), 0, 3, 1.2)); break;
    case "ovillo": { const m = M(tex(4, 4, (px, w, h, r) => { fill(px, 4, 4, "#c0202a", r, 0.15); px(0, 1, "#ff5a5a"); px(2, 3, "#ff5a5a"); }, 501)); g.add(caja(4, 4, 4, m, 0, -0.5, 1.5)); g.add(caja(4.4, 1, 1, m, 0, 0.4, 1.5)); break; }
    case "antorcha": { g.add(caja(1.4, 12, 1.4, MAT.madera, 0, 1, 0)); const f = caja(2.6, 3.4, 2.6, MAT.fuego, 0, 8.4, 0); f.name = "llama"; g.add(f); const f2 = caja(1.6, 2, 1.6, MAT.brasa, 0, 9.6, 0); f2.name = "llama2"; g.add(f2); g.userData.luz = 1; break; }
    case "tela": g.add(caja(8, 10, 0.5, MAT.tela, 0, -4, 2)); break;
    case "plano": g.add(caja(10, 0.4, 7, M(tex(16, 12, (px, w, h, r) => { fill(px, 16, 12, "#3a6ab0", r, 0.05); for (let k = 0; k < 16; k++) { px(k, 2, "#cfe0ff"); px(k, 9, "#cfe0ff"); } for (let y = 2; y < 10; y++) { px(2, y, "#cfe0ff"); px(13, y, "#cfe0ff"); px(7, y, y % 3 ? "#cfe0ff" : "#3a6ab0"); } }, 502)), 0, 0, 3)); break;
    case "lanza": g.add(caja(1.2, 40, 1.2, MAT.maderaOsc, 0, 8, 0)); g.add(caja(2.4, 5, 1, MAT.bronce, 0, 30, 0)); break;
    case "roca": g.add(caja(30, 18, 22, MAT.roca, 0, 9, 0)); g.add(caja(20, 6, 16, MAT.roca, 3, 20, 0)); break;
    case "espada_cinto": g.add(caja(1.2, 12, 0.8, hoja, 0, -6, 0)); g.add(caja(4, 1, 1.2, MAT.oro, 0, 0, 0)); g.add(caja(1.2, 3, 1.2, MAT.maderaOsc, 0, 2, 0)); break;
  }
  g.traverse(o => { if (o.isMesh) o.castShadow = true; });
  return g;
}

// ------------------------------------------------------------------ iconos (sprites pixel)
const ICO = {};
export function texIcono(n) {
  if (ICO[n]) return ICO[n];
  const f = {
    "!": (px) => { for (let y = 1; y < 10; y++) for (let x = 5; x < 9; x++) px(x, y, "#ffd23a"); for (let y = 12; y < 15; y++) for (let x = 5; x < 9; x++) px(x, y, "#ffd23a"); for (let y = 0; y < 16; y++) { px(4, y, y > 10 && y < 12 ? "rgba(0,0,0,0)" : "#3a2a00"); } },
    "?": (px) => { const m = ["0111110", "1100011", "0000011", "0000110", "0001100", "0001100", "0000000", "0001100", "0001100"]; m.forEach((row, y) => [...row].forEach((c, x) => { if (c === "1") { px(x * 2 + 1, y * 2 - 1 + 1, "#ffffff"); px(x * 2 + 2, y * 2 + 1, "#ffffff"); px(x * 2 + 1, y * 2 + 1, "#ffffff"); px(x * 2 + 2, y * 2, "#ffffff"); } })); },
    corazon: (px) => { const m = ["0110110", "1111111", "1111111", "0111110", "0011100", "0001000"]; m.forEach((row, y) => [...row].forEach((c, x) => { if (c === "1") { px(x * 2 + 1, y * 2 + 2, "#ff3a5a"); px(x * 2 + 2, y * 2 + 2, "#ff3a5a"); px(x * 2 + 1, y * 2 + 3, "#e0203a"); px(x * 2 + 2, y * 2 + 3, "#e0203a"); } })); px(4, 4, "#ffb0c0"); },
    estrella: (px) => { const m = ["0001000", "0011100", "1111111", "0111110", "0110110", "1100011"]; m.forEach((row, y) => [...row].forEach((c, x) => { if (c === "1") { px(x * 2 + 1, y * 2 + 2, "#ffe24a"); px(x * 2 + 2, y * 2 + 2, "#ffe24a"); px(x * 2 + 1, y * 2 + 3, "#f0b020"); px(x * 2 + 2, y * 2 + 3, "#f0b020"); } })); },
    zzz: (px) => { for (const [ox, oy, s] of [[1, 9, 5], [7, 3, 4]]) { for (let x = 0; x < s; x++) { px(ox + x, oy, "#cfe6ff"); px(ox + x, oy + s - 1, "#cfe6ff"); px(ox + s - 1 - x, oy + x, "#cfe6ff"); } } },
  }[n];
  return ICO[n] = tex(16, 16, f, 600);
}
