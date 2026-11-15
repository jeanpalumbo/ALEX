// Motor de bloques: texturas pixel propias, personajes con rig, criaturas, partículas, luces y cielos.
import * as THREE from "three";
export { THREE };
export const cl = (x, a = 0, b = 1) => Math.max(a, Math.min(b, x));
export const lerp = (a, b, x) => a + (b - a) * x;
export const sm = x => { x = cl(x); return x * x * (3 - 2 * x); };
export const eout = x => 1 - Math.pow(1 - cl(x), 3);
export const ein = x => Math.pow(cl(x), 3);
export const back = (x, s = 2) => { x = cl(x) - 1; return 1 + (s + 1) * x * x * x + s * x * x; };
export const seg = (t, a, b, e = sm) => e(cl((t - a) / (b - a)));
export const muelle = (t, t0, A, f = 14, d = 6) => t < t0 ? 0 : A * Math.sin((t - t0) * f) * Math.exp(-(t - t0) * d);
export const D = Math.PI / 180;
export function rnd(i) { const x = Math.sin(i * 127.1 + 311.7) * 43758.5453; return x - Math.floor(x); }
export function shade(hex, f) { const c = new THREE.Color(hex); c.multiplyScalar(f); return "#" + c.getHexString(); }
// ---------------- texturas
export function tex(w, h, fn, seed = 1) {
  const c = document.createElement("canvas"); c.width = w; c.height = h; const g = c.getContext("2d");
  const px = (x, y, col) => { g.fillStyle = col; g.fillRect(x, y, 1, 1); };
  fn(px, w, h, (x, y) => rnd(seed * 997 + x * 31 + y * 17), g);
  const t = new THREE.CanvasTexture(c); t.magFilter = THREE.NearestFilter; t.minFilter = THREE.NearestFilter; t.colorSpace = THREE.SRGBColorSpace; t.generateMipmaps = false; return t;
}
export const fill = (px, w, h, col, r, v = 0.08) => { for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) px(x, y, shade(col, 1 - v + 2 * v * r(x, y))); };
export const M = t => new THREE.MeshLambertMaterial({ map: t });
const _mc = {};
export function liso(col, v = 0.12, s = 16, seed = 0) { const k = col + v + s + seed; if (!_mc[k]) _mc[k] = M(tex(s, s, (px, w, h, r) => fill(px, w, h, col, r, v), seed + col.length * 7 + Math.floor(v * 100))); return _mc[k]; }
export const T = {
  hierbaTop: tex(16, 16, (px, w, h, r) => { fill(px, w, h, "#5f9e3a", r, 0.14); for (let k = 0; k < 18; k++) px(Math.floor(r(k, 1) * 16), Math.floor(r(1, k) * 16), "#7fbf4a"); }, 2),
  hierbaLado: tex(16, 16, (px, w, h, r) => { fill(px, w, h, "#7a5532", r, 0.14); for (let x = 0; x < 16; x++) { const d = 3 + Math.floor(r(x, 9) * 3); for (let y = 0; y < d; y++) px(x, y, shade("#5f9e3a", 0.9 + 0.2 * r(x, y))); } }, 3),
  nieveTop: tex(16, 16, (px, w, h, r) => fill(px, w, h, "#f2f6fa", r, 0.04), 13),
  nieveLado: tex(16, 16, (px, w, h, r) => { fill(px, w, h, "#7a5532", r, 0.14); for (let x = 0; x < 16; x++) { const d = 3 + Math.floor(r(x, 9) * 3); for (let y = 0; y < d; y++) px(x, y, "#f2f6fa"); } }, 14),
  marmol: tex(16, 16, (px, w, h, r) => { fill(px, w, h, "#e8e2d4", r, 0.05); for (let k = 0; k < 16; k++) px(k, Math.floor(8 + 4 * Math.sin(k * 0.7)), "#c9c0ad"); }, 5),
  columna: tex(16, 16, (px, w, h, r) => { for (let y = 0; y < 16; y++) for (let x = 0; x < 16; x++) px(x, y, shade(x % 4 === 0 ? "#cfc7b4" : "#ece6d8", 0.96 + 0.08 * r(x, y))); }, 6),
  oro: tex(16, 16, (px, w, h, r) => { fill(px, w, h, "#d9a630", r, 0.1); for (let x = 0; x < 16; x++) { px(x, 0, "#f3d26a"); px(x, 15, "#9a7020"); } }, 7),
  madera: tex(16, 16, (px, w, h, r) => { for (let y = 0; y < 16; y++) for (let x = 0; x < 16; x++) px(x, y, shade(y % 4 === 0 ? "#6b4424" : "#9a6a3c", 0.93 + 0.14 * r(x, y))); }, 8),
  piedra: tex(16, 16, (px, w, h, r) => { fill(px, w, h, "#8a8780", r, 0.15); for (let k = 0; k < 8; k++) px(Math.floor(r(k, 2) * 16), Math.floor(r(2, k) * 16), "#6d6a64"); }, 9),
  ladrillo: tex(16, 16, (px, w, h, r) => { for (let y = 0; y < 16; y++) for (let x = 0; x < 16; x++) { const m = y % 8 === 0 || (x + (Math.floor(y / 8) % 2) * 8) % 16 === 0; px(x, y, m ? "#4a4038" : shade("#8a7560", 0.92 + 0.16 * r(x, y))); } }, 10),
  tronco: tex(16, 16, (px, w, h, r) => { for (let y = 0; y < 16; y++) for (let x = 0; x < 16; x++) px(x, y, shade(x % 5 === 0 ? "#4a3220" : "#6b4a2c", 0.9 + 0.2 * r(x, y))); }, 34),
  hoja: tex(16, 16, (px, w, h, r) => { fill(px, 16, 16, "#3f7f2e", r, 0.22); for (let k = 0; k < 20; k++) px(Math.floor(r(k, 7) * 16), Math.floor(r(7, k) * 16), "#2c5e20"); }, 33),
  arena: tex(16, 16, (px, w, h, r) => fill(px, 16, 16, "#e3cf98", r, 0.08), 41),
  barro: tex(16, 16, (px, w, h, r) => { fill(px, 16, 16, "#4f4a2c", r, 0.15); for (let k = 0; k < 12; k++) px(Math.floor(r(k, 3) * 16), Math.floor(r(3, k) * 16), "#3a3a20"); }, 42),
  roca_infra: tex(16, 16, (px, w, h, r) => { fill(px, 16, 16, "#3a2a2a", r, 0.2); for (let k = 0; k < 6; k++) px(Math.floor(r(k, 5) * 16), Math.floor(r(5, k) * 16), "#7a2a1a"); }, 43),
  lava: tex(16, 16, (px, w, h, r) => { fill(px, 16, 16, "#ff6a1a", r, 0.2); for (let k = 0; k < 14; k++) px(Math.floor(r(k, 8) * 16), Math.floor(r(8, k) * 16), "#ffd040"); }, 44),
  agua: tex(16, 16, (px, w, h, r) => { fill(px, 16, 16, "#2f6fc0", r, 0.1); for (let k = 0; k < 10; k++) px(Math.floor(r(k, 6) * 16), Math.floor(r(6, k) * 16), "#5a9be0"); }, 45),
  pantano: tex(16, 16, (px, w, h, r) => { fill(px, 16, 16, "#3f5a3a", r, 0.12); for (let k = 0; k < 10; k++) px(Math.floor(r(k, 6) * 16), Math.floor(r(6, k) * 16), "#5a7a3a"); }, 46),
  tela: tex(16, 16, (px, w, h, r) => { fill(px, w, h, "#e9dcc0", r, 0.05); for (let x = 0; x < 16; x += 4) for (let y = 0; y < 16; y++) px(x, y, "#d4c4a2"); }, 11),
  paja: tex(16, 16, (px, w, h, r) => { for (let y = 0; y < 16; y++) for (let x = 0; x < 16; x++) px(x, y, shade((x + y) % 3 ? "#d9b85a" : "#b8963a", 0.9 + 0.2 * r(x, y))); }, 47),
  estiercol: tex(16, 16, (px, w, h, r) => { fill(px, 16, 16, "#5a4020", r, 0.2); for (let k = 0; k < 10; k++) px(Math.floor(r(k, 2) * 16), Math.floor(r(2, k) * 16), "#3a2a10"); }, 48),
};
export const MAT = {
  hierba: [M(T.hierbaLado), M(T.hierbaLado), M(T.hierbaTop), liso("#7a5532"), M(T.hierbaLado), M(T.hierbaLado)],
  nieve: [M(T.nieveLado), M(T.nieveLado), M(T.nieveTop), liso("#7a5532"), M(T.nieveLado), M(T.nieveLado)],
  marmol: M(T.marmol), columna: M(T.columna), oro: M(T.oro), madera: M(T.madera), piedra: M(T.piedra), ladrillo: M(T.ladrillo),
  tronco: M(T.tronco), hoja: M(T.hoja), arena: M(T.arena), barro: M(T.barro), rocaInfra: M(T.roca_infra), tela: M(T.tela), paja: M(T.paja), estiercol: M(T.estiercol),
  lava: new THREE.MeshBasicMaterial({ map: T.lava }), agua: new THREE.MeshLambertMaterial({ map: T.agua, transparent: true, opacity: 0.88 }),
  pantano: new THREE.MeshLambertMaterial({ map: T.pantano, transparent: true, opacity: 0.92 }),
  nube: new THREE.MeshLambertMaterial({ map: tex(8, 8, (px, w, h, r) => fill(px, w, h, "#ffffff", r, 0.03), 12), transparent: true, opacity: 0.95 }),
  brillo: c => new THREE.MeshBasicMaterial({ color: c }),
};
// ---------------- caras: 15 expresiones dibujadas pixel a pixel
export const EXPR = ["normal", "enfado", "risa", "cerrados", "grito", "susto", "triste", "sudor", "espiral", "sorpresa", "malvado", "lloro", "presumido", "dormido", "amor", "habla"];
function pintaCara(px, sp, r, e) {
  fill(px, 8, 8, sp.piel, r, 0.05);
  if (sp.melena) { for (let x = 0; x < 8; x++) { px(x, 0, sp.pelo); px(x, 1, sp.pelo); } for (let y = 2; y < 5; y++) { px(0, y, sp.pelo); px(7, y, sp.pelo); } }
  else if (sp.calvo) { px(0, 1, sp.pelo); px(7, 1, sp.pelo); }
  else for (let x = 0; x < 8; x++) { px(x, 0, sp.pelo); if (x < 2 || x > 5 || sp.flequillo) px(x, 1, sp.pelo); }
  if (sp.leon) { for (let x = 0; x < 8; x++) { px(x, 0, "#c48a2c"); px(x, 1, x % 3 ? "#d9a03c" : "#a66f22"); } px(1, 1, "#2a1a0a"); px(6, 1, "#2a1a0a"); px(0, 2, "#c48a2c"); px(7, 2, "#c48a2c"); }
  if (sp.casco) { for (let x = 0; x < 8; x++) { px(x, 0, sp.casco); px(x, 1, sp.casco); } px(0, 2, sp.casco); px(7, 2, sp.casco); }
  const pu = sp.ojos || "#3a2a1a", W = "#ffffff", osc = shade(sp.piel, 0.6), ceja = sp.ceja || shade(sp.pelo === "#e8e8e8" ? "#999999" : sp.pelo, 0.8);
  const ojos = (a, b, c, d) => { px(1, 4, a); px(2, 4, b); px(5, 4, c); px(6, 4, d); };
  switch (e) {
    case "cerrados": case "risa": case "dormido": case "presumido": ojos(osc, osc, osc, osc); if (e === "presumido") { px(1, 3, ceja); px(2, 3, ceja); } break;
    case "susto": case "sorpresa": ojos(W, pu, pu, W); px(1, 3, W); px(2, 3, W); px(5, 3, W); px(6, 3, W); px(1, 2, ceja); px(2, 2, ceja); px(5, 2, ceja); px(6, 2, ceja); break;
    case "espiral": ojos("#ffffff", "#7a3ab8", "#7a3ab8", "#ffffff"); px(1, 3, "#7a3ab8"); px(6, 3, "#7a3ab8"); px(2, 5, "#7a3ab8"); px(5, 5, "#7a3ab8"); break;
    case "amor": ojos(W, "#e0507a", "#e0507a", W); px(0, 5, "#f08aa0"); px(1, 5, "#f08aa0"); px(6, 5, "#f08aa0"); px(7, 5, "#f08aa0"); px(1, 3, osc); px(6, 3, osc); break;
    case "enfado": case "malvado": ojos(W, pu, pu, W); px(1, 3, ceja); px(2, 3, osc); px(5, 3, osc); px(6, 3, ceja); px(2, 2, ceja); px(5, 2, ceja); break;
    case "triste": case "lloro": ojos(W, pu, pu, W); px(2, 3, ceja); px(5, 3, ceja); px(1, 2, ceja); px(6, 2, ceja); if (e === "lloro") { px(1, 5, "#7ac8ff"); px(1, 6, "#7ac8ff"); px(6, 5, "#7ac8ff"); px(6, 6, "#7ac8ff"); } break;
    default: ojos(W, pu, pu, W); px(1, 3, shade(sp.piel, 0.82)); px(6, 3, shade(sp.piel, 0.82));
  }
  if (e === "sudor") { px(7, 2, "#7ac8ff"); px(7, 3, "#7ac8ff"); px(0, 3, "#7ac8ff"); }
  px(3, 5, shade(sp.piel, 0.85)); px(4, 5, shade(sp.piel, 0.85));
  if (sp.barba) { for (let x = 1; x < 7; x++) { px(x, 6, sp.barba); px(x, 7, sp.barba); } px(0, 5, sp.barba); px(7, 5, sp.barba); px(0, 6, sp.barba); px(7, 6, sp.barba); }
  if (sp.bigote) { px(2, 6, sp.bigote); px(3, 6, sp.bigote); px(4, 6, sp.bigote); px(5, 6, sp.bigote); }
  const mc = "#6b2a22", my = sp.barba || sp.bigote ? 7 : 6;
  switch (e) {
    case "risa": case "amor": px(2, my, mc); px(3, Math.min(7, my + 1), mc); px(4, Math.min(7, my + 1), mc); px(5, my, mc); px(3, my, "#fff"); px(4, my, "#fff"); break;
    case "grito": case "susto": case "habla": px(3, my, mc); px(4, my, mc); if (my < 7) { px(3, 7, mc); px(4, 7, mc); } if (e !== "habla") { px(2, my, mc); px(5, my, mc); } break;
    case "sorpresa": px(3, my, mc); px(4, my, mc); break;
    case "enfado": case "triste": case "lloro": px(2, 7, mc); px(3, my, mc); px(4, my, mc); px(5, 7, mc); break;
    case "malvado": case "presumido": px(3, my, mc); px(4, my, mc); px(5, my, mc); px(6, my - 1, mc); break;
    case "sudor": px(2, my, mc); px(3, my, mc); px(4, my, mc); px(5, my, mc); break;
    case "dormido": px(3, my, mc); break;
    case "espiral": px(2, my, mc); px(4, my, mc); px(3, Math.min(7, my + 1), mc); break;
    default: px(3, my, mc); px(4, my, mc);
  }
}
// ---------------- skin y personaje
export function skin(sp) {
  const S = sp.seed || 1;
  const caras = {};
  for (const e of EXPR) caras[e] = M(tex(8, 8, (px, w, h, r) => pintaCara(px, sp, r, e), S));
  const pc = sp.leon ? "#c48a2c" : sp.pelo;
  const pelo = M(tex(8, 8, (px, w, h, r) => { fill(px, 8, 8, sp.calvo ? sp.piel : pc, r, 0.12); if (sp.calvo) for (let x = 0; x < 8; x++) px(x, 7, sp.pelo); if (sp.casco) fill(px, 8, 8, sp.casco, r, 0.1); }, S + 1));
  const lado = (inv) => M(tex(8, 8, (px, w, h, r) => { fill(px, 8, 8, sp.piel, r, 0.05); for (let y = 0; y < 8; y++) for (let x = 0; x < 8; x++) { const xx = inv ? 7 - x : x; if ((!sp.calvo && (y < 2 || (xx > 4 && y < (sp.melena ? 8 : 5)))) || (sp.leon && (y < 3 || xx > 3)) || (sp.casco && y < 3)) px(x, y, shade(sp.casco || pc, 0.9 + 0.2 * r(x, y))); } if (sp.barba) for (let y = 5; y < 8; y++) for (let x = 0; x < 3; x++) px(inv ? 7 - x : x, y, sp.barba); px(inv ? 5 : 2, 4, shade(sp.piel, 0.8)); }, S + (inv ? 3 : 2)));
  const ropa = (w, h, fn, s) => M(tex(w, h, (px, W, H, r) => { fill(px, W, H, sp.ropa, r, 0.07); fn && fn(px, W, H, r); }, s));
  const torsoF = ropa(8, 12, (px, w, h, r) => {
    if (sp.desnudo) for (let y = 0; y < 7; y++) for (let x = 0; x < 8; x++) px(x, y, shade(sp.piel, 0.95 + 0.1 * r(x, y)));
    if (sp.cinto) for (let x = 0; x < 8; x++) px(x, 7, sp.cinto);
    if (sp.escote) { px(3, 0, sp.piel); px(4, 0, sp.piel); px(3, 1, sp.piel); px(4, 1, sp.piel); }
    if (sp.leon) { for (let x = 0; x < 8; x++) { px(x, 0, "#c48a2c"); px(x, 1, x % 2 ? "#d9a03c" : "#b07a26"); } px(0, 2, "#c48a2c"); px(7, 2, "#c48a2c"); px(3, 2, "#d9a03c"); px(4, 2, "#d9a03c"); }
    if (sp.ribete) for (let x = 0; x < 8; x++) px(x, 11, sp.ribete);
    if (sp.peto) for (let y = 1; y < 7; y++) for (let x = 1; x < 7; x++) px(x, y, shade(sp.peto, 0.9 + 0.2 * r(x, y)));
  }, S + 4);
  const torsoB = ropa(8, 12, (px, w, h, r) => { if (sp.leon) for (let y = 0; y < 10; y++) for (let x = 1; x < 7; x++) px(x, y, shade("#c48a2c", 0.85 + 0.25 * r(x, y))); if (sp.melena) for (let y = 0; y < 5; y++) for (let x = 1; x < 7; x++) px(x, y, sp.pelo); if (sp.cinto) for (let x = 0; x < 8; x++) px(x, 7, sp.cinto); if (sp.capa) for (let y = 0; y < 12; y++) for (let x = 0; x < 8; x++) px(x, y, shade(sp.capa, 0.9 + 0.2 * r(x, y))); }, S + 5);
  const torsoL = ropa(4, 12, (px, w, h, r) => { if (sp.cinto) for (let x = 0; x < 4; x++) px(x, 7, sp.cinto); }, S + 6);
  const brazoU = M(tex(4, 6, (px, w, h, r) => { fill(px, 4, 6, sp.mangas ? sp.ropa : sp.piel, r, 0.06); if (sp.brazalete) for (let x = 0; x < 4; x++) px(x, 4, sp.brazalete); }, S + 7));
  const brazoL = M(tex(4, 6, (px, w, h, r) => { fill(px, 4, 6, sp.mangasL ? sp.ropa : sp.piel, r, 0.06); if (sp.brazalete) for (let x = 0; x < 4; x++) px(x, 1, sp.brazalete); }, S + 8));
  const mano = M(tex(4, 4, (px, w, h, r) => fill(px, 4, 4, shade(sp.piel, 0.92), r, 0.05), S + 9));
  const piernaU = M(tex(4, 6, (px, w, h, r) => fill(px, 4, 6, sp.falda || sp.faldaLarga ? sp.ropa : (sp.pantalon || sp.piel), r, 0.07), S + 10));
  const piernaL = M(tex(4, 6, (px, w, h, r) => { fill(px, 4, 6, sp.faldaLarga ? sp.ropa : (sp.pantalon || sp.piel), r, 0.06); if (!sp.faldaLarga) for (let x = 0; x < 4; x++) { px(x, 5, sp.sandalia || "#6b4424"); px(x, 3, sp.sandalia || "#6b4424"); } }, S + 11));
  const pie = M(tex(4, 4, (px, w, h, r) => fill(px, 4, 4, sp.faldaLarga ? sp.ropa : (sp.sandalia || "#6b4424"), r, 0.08), S + 12));
  const mL = lado(false), mR = lado(true);
  return { caras, cabeza: e => [mR, mL, pelo, mano, caras[e] || caras.normal, pelo],
    torso: [M(tex(4, 12, () => {}, 0)), null, null, null, null, null].map((_, i) => [torsoL, torsoL, torsoL, torsoL, torsoF, torsoB][i]),
    brazoU, brazoL, mano, piernaU, piernaL, pie };
}
export function caja(w, h, d, mat, x = 0, y = 0, z = 0) { const m = new THREE.Mesh(new THREE.BoxGeometry(w, h, d), mat); m.position.set(x, y, z); m.castShadow = true; m.receiveShadow = true; return m; }
export function personaje(sp, escala = 1) {
  const S = skin(sp), root = new THREE.Group(), cad = new THREE.Group(); root.add(cad); cad.position.y = 12;
  const torso = new THREE.Group(); cad.add(torso); torso.add(caja(8, 12, 4, S.torso, 0, 6, 0));
  if (sp.faldaLarga) torso.add(caja(9, 7, 5, S.torso, 0, -3, 0));
  if (sp.capa) { const cp = caja(8.4, 13, 0.8, liso(sp.capa, 0.1, 8, 3), 0, 4.5, -2.6); cp.name = "capa"; torso.add(cp); }
  const cuello = new THREE.Group(); cuello.position.y = 12; torso.add(cuello);
  const cabeza = caja(8, 8, 8, S.cabeza("normal"), 0, 4, 0); cuello.add(cabeza);
  const extras = new THREE.Group(); cuello.add(extras);
  if (sp.leon) { const mel = liso("#c48a2c", 0.18, 8, 77); extras.add(caja(10, 4, 9.6, mel, 0, 8.4, -0.6)); extras.add(caja(2, 2, 2, mel, -3.6, 10.8, 1)); extras.add(caja(2, 2, 2, mel, 3.6, 10.8, 1)); extras.add(caja(9, 2, 1.2, liso("#ffffff", 0.05, 4), 0, 6.8, 4.4)); }
  if (sp.corona) { for (const [x, z] of [[-3, 3], [0, 3.4], [3, 3], [-3.4, 0], [3.4, 0], [-3, -3], [0, -3.4], [3, -3]]) extras.add(caja(1.6, 2.4, 1.6, MAT.oro, x, 9.2, z)); extras.add(caja(8.6, 1, 8.6, MAT.oro, 0, 8.2, 0)); }
  if (sp.melena) extras.add(caja(8.6, 9, 2, liso(sp.pelo, 0.12, 8, 78), 0, 3, -4.4));
  if (sp.cascoPenacho) { extras.add(caja(8.6, 4, 8.6, liso(sp.casco || "#a8afbd", 0.08, 8, 79), 0, 7.4, 0)); extras.add(caja(1.6, 5, 9, liso(sp.cascoPenacho, 0.1, 8, 80), 0, 10, 0)); }
  if (sp.laurel) for (const x of [-4.2, 4.2]) extras.add(caja(0.8, 1.2, 6, liso("#5f9e3a", 0.2, 4, 81), x, 6.8, 0));
  const mk = (lado) => { const sh = new THREE.Group(); sh.position.set(lado * 6, 10, 0); torso.add(sh); sh.add(caja(4, 6, 4, S.brazoU, 0, -3, 0));
    const el = new THREE.Group(); el.position.y = -6; sh.add(el); el.add(caja(3.9, 5, 3.9, S.brazoL, 0, -2.5, 0)); el.add(caja(4.1, 1.6, 4.1, S.mano, 0, -5.6, 0));
    const mano = new THREE.Group(); mano.position.y = -6.4; el.add(mano); return { sh, el, mano }; };
  const mkL = (lado) => { const hp = new THREE.Group(); hp.position.set(lado * 2, 0, 0); cad.add(hp); hp.add(caja(4, 6, 4, S.piernaU, 0, -3, 0));
    const kn = new THREE.Group(); kn.position.y = -6; hp.add(kn); kn.add(caja(3.9, 5, 3.9, S.piernaL, 0, -2.5, 0)); kn.add(caja(4.1, 1.2, 5, S.pie, 0, -5.4, 0.5)); return { hp, kn }; };
  const aR = mk(-1), aL = mk(1), lR = mkL(-1), lL = mkL(1);
  root.scale.setScalar(escala);
  return { root, cad, torso, cuello, cabeza, extras, aR, aL, lR, lL, S, sp, expr: "normal", escala };
}
export function cara(ch, e) { if (ch.expr !== e) { ch.cabeza.material = ch.S.cabeza(e); ch.expr = e; } }
// pose: {x,y,z,ry, lean, giro, ladeo, cabX, cabY, cabZ, bR:[x,z], bL, cR, cL, pR, pL, kR, kL, andar(fase), amp, salto, sq, sentado}
export function pose(ch, p, t) {
  const A = p.amp || 0, ph = p.andar || 0, run = p.correr ? 1.6 : 1;
  const sw = Math.sin(ph) * A, bob = Math.abs(Math.sin(ph)) * 1.2 * A * run;
  const resp = Math.sin(t * 2.4 + (p.seed || 0)) * 0.012;
  ch.root.position.set(p.x || 0, (p.y || 0) + (p.salto || 0) + bob, p.z || 0);
  ch.root.rotation.set(p.rx || 0, (p.ry || 0) * D, p.rz || 0);
  ch.cad.rotation.set(0, (p.giro || 0) * D, 0);
  ch.torso.rotation.set(((p.lean || 0) + sw * 3 * run + (p.correr ? 12 * A : 0)) * D, Math.sin(ph) * 6 * A * D, (p.ladeo || 0) * D);
  const sq = (p.sq || 1); ch.torso.scale.set(1 / Math.sqrt(sq), sq + resp, 1 / Math.sqrt(sq));
  ch.cuello.rotation.set((p.cabX || 0) * D, (p.cabY || 0) * D, (p.cabZ || 0) * D);
  const b = (arm, bx, bz, c, s) => { arm.sh.rotation.set((bx + s) * D, 0, bz * D); arm.el.rotation.set(-c * D, 0, 0); };
  b(ch.aR, (p.bR ? p.bR[0] : 0), (p.bR ? p.bR[1] : 0) - 4, p.cR ?? 8 + 6 * A, sw * 38 * run);
  b(ch.aL, (p.bL ? p.bL[0] : 0), (p.bL ? p.bL[1] : 0) + 4, p.cL ?? 8 + 6 * A, -sw * 38 * run);
  const l = (leg, a, k) => { leg.hp.rotation.set(a * D, 0, 0); leg.kn.rotation.set(k * D, 0, 0); };
  const sen = p.sentado ? 1 : 0;
  l(ch.lR, (p.pR || 0) - sw * 34 * run - 85 * sen, (p.kR || 0) + Math.max(0, Math.sin(ph + 1.4)) * 40 * A * run + 85 * sen);
  l(ch.lL, (p.pL || 0) + sw * 34 * run - 85 * sen, (p.kL || 0) + Math.max(0, Math.sin(ph + 1.4 + Math.PI)) * 40 * A * run + 85 * sen);
  if (sen) ch.root.position.y -= 6 * ch.escala;
}
// ---------------- criaturas genéricas
export function cuadrupedo(o) {   // {pelo, color, largo, alto, cabezas, melena, cuernos, astas, colmillos, cola, ojosRojos, escala}
  const g = new THREE.Group(), pel = liso(o.color, 0.12, 8, o.seed || 70), cuerpo = new THREE.Group(); cuerpo.position.y = o.patas || 10; g.add(cuerpo);
  const L = o.largo || 20, H = o.alto || 10, Wd = o.ancho || 11;
  cuerpo.add(caja(Wd, H, L, pel, 0, H / 2 - 2, 0));
  if (o.lomo) cuerpo.add(caja(Wd * 0.6, 3, L * 0.7, liso(o.lomo, 0.15, 8, 71), 0, H - 1, 0));
  const cabezas = [], n = o.cabezas || 1;
  for (let i = 0; i < n; i++) {
    const cg = new THREE.Group(), dx = n > 1 ? (i - (n - 1) / 2) * 9 : 0; cg.position.set(dx, H * 0.7, L / 2 + 1); cuerpo.add(cg);
    if (o.melena) cg.add(caja(16, 16, 6, liso(o.melena, 0.2, 8, 72), 0, 2, 0));
    const caraT = M(tex(8, 8, (px, w, h, r) => { fill(px, 8, 8, o.color, r, 0.08); const oj = o.ojosRojos ? "#ff2a1a" : "#222";
      px(1, 2, o.ojosRojos ? "#ff8a1a" : "#fff"); px(2, 2, oj); px(5, 2, oj); px(6, 2, o.ojosRojos ? "#ff8a1a" : "#fff"); px(3, 4, "#3a2010"); px(4, 4, "#3a2010");
      if (o.dientes) { px(2, 6, "#6b2a22"); px(3, 6, "#fff"); px(4, 6, "#fff"); px(5, 6, "#6b2a22"); } }, (o.seed || 70) + 5 + i));
    const cab = caja(9, 9, o.hocico ? 9 : 8, [pel, pel, pel, pel, caraT, pel], 0, 0, 5); cg.add(cab);
    if (o.hocico) cg.add(caja(5, 4, 4, liso(o.hocico, 0.08, 4, 73), 0, -2, 10.5));
    if (o.cuernos) for (const s of [-1, 1]) { cg.add(caja(2, 2, 2, liso(o.cuernos, 0.05, 4), s * 5.5, 4, 5)); cg.add(caja(2, 4, 2, liso(o.cuernos, 0.05, 4), s * 6.5, 6.5, 5)); }
    if (o.astas) for (const s of [-1, 1]) { const a = liso(o.astas, 0.1, 4); cg.add(caja(1.4, 8, 1.4, a, s * 3, 8, 4)); cg.add(caja(4, 1.4, 1.4, a, s * 5, 10, 4)); cg.add(caja(1.4, 4, 1.4, a, s * 6.4, 12, 4)); }
    if (o.colmillos) for (const s of [-1, 1]) cg.add(caja(1.2, 3, 1.2, liso("#fffbe8", 0.03, 4), s * 3, -2, 13));
    if (o.orejas) for (const s of [-1, 1]) cg.add(caja(2, 3, 1, pel, s * 3.5, 5.5, 3));
    cabezas.push(cg);
  }
  const patas = []; for (const [x, z] of [[-Wd / 2 + 2, L / 2 - 3], [Wd / 2 - 2, L / 2 - 3], [-Wd / 2 + 2, -L / 2 + 3], [Wd / 2 - 2, -L / 2 + 3]]) {
    const p = new THREE.Group(); p.position.set(x, -2, z); cuerpo.add(p); p.add(caja(3.6, o.patas || 10, 3.6, pel, 0, -(o.patas || 10) / 2, 0));
    if (o.pezunas) p.add(caja(3.8, 1.6, 3.8, liso(o.pezunas, 0.05, 4), 0, -(o.patas || 10) + 0.4, 0)); patas.push(p); }
  const cola = []; let prev = cuerpo; for (let k = 0; k < (o.cola || 5); k++) { const c = new THREE.Group(); c.position.set(0, k ? 0 : H - 4, k ? -2.6 : -L / 2); prev.add(c); c.add(caja(1.6, 1.6, 2.6, k === (o.cola || 5) - 1 && o.melena ? liso(o.melena, 0.2, 8) : pel, 0, 0, -1.3)); cola.push(c); prev = c; }
  g.scale.setScalar(o.escala || 1);
  return { g, cuerpo, cabezas, patas, cola, o };
}
export function animaCuadrupedo(c, t, v = 0, extra = {}) {    // v = velocidad del paso (0 quieto)
  const f = t * (6 + v * 10), A = v > 0 ? 35 : 4;
  c.patas.forEach((p, i) => p.rotation.x = A * D * Math.sin(f + (i % 2 ? Math.PI : 0) + (i > 1 ? 0.7 : 0)));
  c.cuerpo.position.y = (c.o.patas || 10) + (v > 0 ? Math.abs(Math.sin(f)) * 1.2 : 0.3 * Math.sin(t * 2));
  c.cabezas.forEach((h, i) => { h.rotation.x = ((extra.cabX || 0) + 5 * Math.sin(t * 2.2 + i * 1.3)) * D; h.rotation.y = ((extra.cabY || 0) + 8 * Math.sin(t * 1.4 + i * 2)) * D; });
  c.cola.forEach((q, i) => { q.rotation.y = 0.35 * Math.sin(t * 5 - i * 0.6); q.rotation.x = -0.12; });
}
export function serpienteCadena(c1, c2, n = 16, s0 = 3.2, seed = 61) {
  const g = new THREE.Group(), segs = [], mt = M(tex(4, 4, (px, w, h, r) => { fill(px, 4, 4, c1, r, 0.12); px(1, 1, c2); px(2, 2, c2); }, seed));
  for (let k = 0; k < n; k++) { const s = s0 - k * s0 * 0.035; const m = caja(s, s, s, mt); g.add(m); segs.push(m); }
  const cab = segs[0]; cab.scale.set(1.5, 1.2, 1.7);
  for (const x of [-1.1, 1.1]) cab.add(caja(0.8, 0.8, 0.4, MAT.brillo("#ffe14a"), x * s0 / 3.2, 0.7 * s0 / 3.2, 1.2 * s0 / 3.2));
  const lengua = caja(0.5, 0.3, 3, MAT.brillo("#d0302a"), 0, -0.3, 2.6); cab.add(lengua);
  return { g, segs, lengua };
}
// coloca una cadena siguiendo una curva f(u) -> [x,y,z] (u: 0 cabeza .. 1 cola)
export function colocaCadena(s, f) { const n = s.segs.length; for (let k = 0; k < n; k++) { const [x, y, z] = f(k / (n - 1)); s.segs[k].position.set(x, y, z); }
  const a = s.segs[0].position, b = s.segs[1].position; s.segs[0].lookAt(a.x * 2 - b.x, a.y * 2 - b.y, a.z * 2 - b.z); }
export function pajaro(color = "#5a5a6a") {
  const g = new THREE.Group(), m = liso(color, 0.15, 4, 90); g.add(caja(3, 3, 6, m)); g.add(caja(2.4, 2.4, 2.4, m, 0, 1, 3.6)); g.add(caja(0.8, 0.8, 2, liso("#d9a630", 0.05, 4), 0, 0.6, 5.4));
  const aL = new THREE.Group(), aR = new THREE.Group(); aL.position.x = 1.5; aR.position.x = -1.5; aL.add(caja(7, 0.6, 3.4, m, 3.5, 0, 0)); aR.add(caja(7, 0.6, 3.4, m, -3.5, 0, 0)); g.add(aL, aR);
  return { g, aL, aR };
}
// ---------------- partículas de bloques (pool)
export class Particulas {
  constructor(scene, n = 400) { this.p = []; this.ev = []; const g = new THREE.BoxGeometry(1.6, 1.6, 1.6);
    for (let k = 0; k < n; k++) { const m = new THREE.Mesh(g, new THREE.MeshLambertMaterial({ color: "#fff" })); m.visible = false; m.castShadow = true; scene.add(m); this.p.push(m); } }
  add(t0, x, y, z, n, cols, v = 40, sz = 1, grav = 90, dur = 1.6, brillo = false) { this.ev.push({ t0, x, y, z, n, cols, v, sz, grav, dur, brillo }); }
  clear() { this.ev = []; }
  update(t) { let k = 0;
    for (const e of this.ev) { const lt = t - e.t0;
      if (lt < 0 || lt > e.dur) { continue; }
      for (let i = 0; i < e.n && k < this.p.length; i++, k++) { const m = this.p[k], s = e.t0 * 13 + i;
        const vx = (rnd(s) - 0.5) * 2 * e.v, vz = (rnd(s + 1) - 0.5) * 2 * e.v, vy = (0.3 + rnd(s + 2)) * e.v;
        const y = e.y + vy * lt - e.grav * lt * lt;
        m.position.set(e.x + vx * lt, Math.max(0.8, y), e.z + vz * lt); m.rotation.set(lt * 9 + i, lt * 7, 0);
        m.material.color.set(e.cols[i % e.cols.length]); m.material.emissive && m.material.emissive.set(e.brillo ? e.cols[i % e.cols.length] : "#000");
        m.scale.setScalar(e.sz * (1 - cl((lt - e.dur * 0.7) / (e.dur * 0.3))) + 0.001); m.visible = true; } }
    for (; k < this.p.length; k++) this.p[k].visible = false; }
}
