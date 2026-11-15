// Reproductor: lee linea.json y pinta el fotograma t (acciones, cámaras, vida de fondo, efectos y rótulos).
import { THREE, cl, lerp, sm, eout, back, seg, D, rnd, M, MB, MAT, T, tex, fill, caja, personaje, pose, cara, hacerProp, texIcono, texPlanta } from "./motor.js";
import { construirSets } from "./sets.js";

const W = 1920, H = 1080;
const Q = new URLSearchParams(location.search); const PR = +(Q.get("pr") || 1), AA = Q.get("aa") !== "0";
const renderer = new THREE.WebGLRenderer({ antialias: AA, preserveDrawingBuffer: true });
renderer.setSize(W, H); renderer.setPixelRatio(PR); renderer.shadowMap.enabled = Q.get("sh") !== "0"; renderer.shadowMap.type = [THREE.BasicShadowMap, THREE.PCFShadowMap, THREE.PCFSoftShadowMap][+(Q.get("st") ?? 2)];
renderer.outputColorSpace = THREE.SRGBColorSpace; renderer.toneMapping = THREE.ACESFilmicToneMapping; renderer.toneMappingExposure = 1.05;
document.getElementById("lienzo").appendChild(renderer.domElement);
const scene = new THREE.Scene();
const cam = new THREE.PerspectiveCamera(40, W / H, 1, 6000);
const hemi = new THREE.HemisphereLight("#cfe6ff", "#6b5a3a", 1.1); scene.add(hemi);
const sol = new THREE.DirectionalLight("#fff1d8", 2.6); sol.castShadow = true; sol.shadow.mapSize.set(+(Q.get("sm") || 2048), +(Q.get("sm") || 2048));
Object.assign(sol.shadow.camera, { left: -220, right: 220, top: 220, bottom: -220, near: 1, far: 1200 }); sol.shadow.bias = -0.0006; sol.shadow.normalBias = 0.6;
scene.add(sol, sol.target);
const vela = new THREE.PointLight("#ffb050", 0, 320, 1.4); scene.add(vela);
const vela2 = new THREE.PointLight("#ffb050", 0, 260, 1.4); scene.add(vela2);
const rim = new THREE.DirectionalLight("#ffc070", 0); scene.add(rim); scene.add(rim.target);
const RIM = { dia: ["#ffe0a0", 1.5], tarde: ["#ffb050", 2.6], amanecer: ["#ffb890", 2.1], interior: ["#ffc070", 1.0], noche: ["#8aa8ff", 0.9], laberinto: ["#ff9a40", 1.1], tormenta: ["#c8d0ff", 0.6], mapa: ["#ffffff", 0] };
const cieloC = document.createElement("canvas"); cieloC.width = 2; cieloC.height = 256; const cieloT = new THREE.CanvasTexture(cieloC); cieloT.colorSpace = THREE.SRGBColorSpace;
let cieloK = "";
function cielo(a, b) { const k = a + b; if (k === cieloK) return; cieloK = k; const g = cieloC.getContext("2d"), gr = g.createLinearGradient(0, 0, 0, 256); gr.addColorStop(0, a); gr.addColorStop(1, b); g.fillStyle = gr; g.fillRect(0, 0, 2, 256); cieloT.needsUpdate = true; scene.background = cieloT; }
scene.fog = new THREE.Fog("#cfe6ff", 400, 1700);
// estrellas
const estrellas = (() => { const n = 900, p = new Float32Array(n * 3); for (let i = 0; i < n; i++) { const a = rnd(i) * Math.PI * 2, e = 0.08 + rnd(i + 9) * 1.3; p[i * 3] = Math.cos(a) * Math.cos(e) * 2500; p[i * 3 + 1] = Math.sin(e) * 2500; p[i * 3 + 2] = Math.sin(a) * Math.cos(e) * 2500; } const g = new THREE.BufferGeometry(); g.setAttribute("position", new THREE.BufferAttribute(p, 3)); const m = new THREE.Points(g, new THREE.PointsMaterial({ color: "#ffffff", size: 3, sizeAttenuation: false, fog: false })); m.visible = false; scene.add(m); return m; })();
const luna = caja(60, 60, 2, new THREE.MeshBasicMaterial({ color: "#f5f0d6", fog: false }), 0, 0, 0); luna.castShadow = false; luna.visible = false; scene.add(luna);

const { SETS, llamas, BARCO, BARCO2 } = construirSets(scene);

// ------------------------------------------------------------------ reparto
const SK = {
  teseo: [{ seed: 101, piel: "#e0a878", pelo: "#5a3418", ropa: "#2f6fb5", cinto: "#8a5a2a", ribete: "#e0b040", falda: 1, hombro: 1, brazalete: "#d9a630", sandalia: "#5a3a1a", capa: "#b8302a" }, 1],
  egeo: [{ seed: 111, piel: "#e8b88e", pelo: "#cfcfcf", barba: "#e8e8e8", ropa: "#6a3a8a", ribete: "#e0b040", cinto: "#e0b040", faldaLarga: 1, corona: 1, mangas: 1 }, 1],
  etra: [{ seed: 121, piel: "#f0c8a0", pelo: "#2a1a10", ropa: "#3f8f5a", ribete: "#e0b040", cinto: "#e0b040", faldaLarga: 1, melena: 1, escote: 1, diadema: 1 }, 1],
  medea: [{ seed: 131, piel: "#e6c2a8", pelo: "#141018", ropa: "#3a1a4a", ribete: "#b04ae0", cinto: "#b04ae0", faldaLarga: 1, melena: 1, melenaLarga: 14, ojos: "#7a2a9a", mangas: 1, mangasL: 1 }, 1],
  minos: [{ seed: 141, piel: "#c88a5a", pelo: "#1a120a", barba: "#1a120a", ropa: "#b0302a", ribete: "#e0b040", cinto: "#e0b040", faldaLarga: 1, corona: 1, brazalete: "#e0b040", capa: "#7a1a14" }, 1.05],
  ariadna: [{ seed: 151, piel: "#f2cfae", pelo: "#d0782a", ropa: "#e86a8a", ribete: "#f2ead8", cinto: "#e0b040", faldaLarga: 1, melena: 1, melenaLarga: 13, diadema: 1, ojos: "#2a6a3a", escote: 1 }, 0.95],
  dedalo: [{ seed: 161, piel: "#d8a880", pelo: "#e8e8e8", barba: "#e8e8e8", calvo: 1, ropa: "#7a5a3a", cinto: "#3a2a1a", faldaLarga: 1, mangas: 1 }, 0.95],
  pitia: [{ seed: 171, piel: "#e8c0a0", pelo: "#f0f0f0", ropa: "#e8e0d0", faldaLarga: 1, melena: 1, velo: "#f2ead8", ribete: "#d9a630" }, 1],
  perifetes: [{ seed: 181, piel: "#b07a50", pelo: "#2a1a0a", barba: "#2a1a0a", ropa: "#5a4a3a", falda: 1, cinto: "#3a2a1a", desnudo: 1, brazalete: "#8a6028" }, 1.1],
  sinis: [{ seed: 191, piel: "#c89a6a", pelo: "#a04a1a", barba: "#a04a1a", ropa: "#3a5a2a", falda: 1, cinto: "#6b4424", hombro: 1 }, 1],
  esciron: [{ seed: 201, piel: "#d0a070", pelo: "#111111", barba: "#111111", ropa: "#8a6a2a", falda: 1, cinto: "#3a2a1a", descalzo: 1 }, 1],
  procusto: [{ seed: 211, piel: "#a87048", pelo: "#0a0a0a", barba: "#222222", ropa: "#3a2a2a", falda: 1, cinto: "#8a1e18", desnudo: 1, brazalete: "#555" }, 1.15],
  viajero: [{ seed: 221, piel: "#e0b080", pelo: "#7a4a2a", ropa: "#b08a3a", falda: 1, cinto: "#6b4424", flequillo: 1 }, 1],
  dioniso: [{ seed: 231, piel: "#f0c8a0", pelo: "#3a1a3a", ropa: "#7a2a8a", ribete: "#5f9e3a", faldaLarga: 1, corona: 1, coronaCol: "#5f9e3a", hombro: 1 }, 1.05],
  aldeano1: [{ seed: 241, piel: "#d8a070", pelo: "#3a2414", ropa: "#c0582e", falda: 1, cinto: "#6b4424" }, 1],
  aldeano2: [{ seed: 251, piel: "#f0c8a0", pelo: "#6a3a1a", ropa: "#2f8a8a", faldaLarga: 1, melena: 1 }, 1],
  aldeano3: [{ seed: 261, piel: "#b8805a", pelo: "#111", barba: "#333", ropa: "#d9c08a", faldaLarga: 1 }, 1],
  joven1: [{ seed: 271, piel: "#e8b88e", pelo: "#2a1a0a", ropa: "#f2ead8", falda: 1, cinto: "#8a5a2a", flequillo: 1 }, 0.92],
  joven2: [{ seed: 281, piel: "#f0c8a0", pelo: "#c08a3a", ropa: "#d8d0c0", faldaLarga: 1, melena: 1 }, 0.9],
  joven3: [{ seed: 291, piel: "#c88a5a", pelo: "#111", ropa: "#e8e0d0", faldaLarga: 1, melena: 1, melenaLarga: 12 }, 0.9],
  joven4: [{ seed: 301, piel: "#d8a070", pelo: "#5a3418", ropa: "#ece4d4", falda: 1, cinto: "#6b4424" }, 0.92],
  soldado1: [{ seed: 311, piel: "#c88a5a", pelo: "#111", ropa: "#8a1e18", falda: 1, coraza: 1, casco: 1, cinto: "#3a2a1a" }, 1.05],
  soldado2: [{ seed: 321, piel: "#b07a50", pelo: "#111", ropa: "#8a1e18", falda: 1, coraza: 1, casco: 1, cinto: "#3a2a1a" }, 1.05],
  minotauro: [{ seed: 331, piel: "#5a3a24", pelo: "#3a2414", ropa: "#5a3a24", falda: 1, taparrabo: 1, toro: 1, ojos: "#ff2a1a", descalzo: 1, brazalete: "#8a6028" }, 1.45],
  bebe: [{ seed: 341, piel: "#f2c49a", pelo: "#5a3418", ropa: "#ffffff", falda: 1, flequillo: 1, descalzo: 1 }, 0.5],
};
const CAST = {};
for (const n in SK) { const ch = personaje(SK[n][0], SK[n][1]); ch.nombre = n; ch.root.visible = false; scene.add(ch.root); CAST[n] = ch; }
CAST.bebe.cabeza.scale.setScalar(1.45); CAST.bebe.cabeza.position.y = 5.5;
// extras de fondo (paseantes)
const EXTRAS = [];
for (let k = 0; k < 12; k++) { const ch = personaje({ seed: 900 + k * 7, piel: ["#e0b080", "#c88a5a", "#f0c8a0", "#b8805a", "#d8a070", "#e8b88e"][k % 6], pelo: ["#2a1a0a", "#5a3418", "#111", "#7a4a2a", "#c08a3a", "#333", "#3a2410"][k % 7], ropa: ["#c0582e", "#2f6fb5", "#d9c08a", "#3f8f5a", "#e8e0d0", "#7f5aa8", "#b03030", "#e0a030"][k % 8], falda: k % 2, faldaLarga: (k + 1) % 2, melena: k % 3 === 1, cinto: "#6b4424" }, 1); ch.root.visible = false; scene.add(ch.root); EXTRAS.push(ch); }
// accesorios por personaje (se crean al vuelo)
function prop(ch, n, lado = "R") { const k = n + lado; if (!ch.props[k]) { const p = hacerProp(n); (lado === "R" ? ch.aR : ch.aL).mano.add(p); ch.props[k] = p; } return ch.props[k]; }
function ocultaProps(ch) { for (const k in ch.props) ch.props[k].visible = false; }
// carro de dragones de Medea
const CARRO = (() => { const g = new THREE.Group(); g.add(caja(26, 6, 18, MAT.oro, 0, 3, 0)); g.add(caja(26, 10, 2, MAT.oro, 0, 8, -9)); for (const s of [-1, 1]) g.add(caja(4, 10, 4, MAT.oro, s * 13, 5, 2));
  const verde = M(tex(4, 4, (px, w, h, r) => fill(px, 4, 4, "#3f8a3a", r, 0.15), 801)); const alas = [];
  for (const s of [-1, 1]) { const d = new THREE.Group(); d.position.set(s * 16, 10, 34); d.add(caja(8, 8, 22, verde, 0, 0, 0)); d.add(caja(7, 7, 9, verde, 0, 5, 14)); d.add(caja(2, 2, 2, MB("#ffe14a"), -2.5, 7, 18.6)); d.add(caja(2, 2, 2, MB("#ffe14a"), 2.5, 7, 18.6));
    for (const w of [-1, 1]) { const a = new THREE.Group(); a.position.set(w * 4, 3, 0); a.add(caja(18, 1, 12, verde, w * 9, 0, 0)); d.add(a); alas.push([a, w]); } g.add(d); }
  g.visible = false; scene.add(g); return { g, alas }; })();

// ------------------------------------------------------------------ partículas y sprites
const PART = []; const pg = new THREE.BoxGeometry(1.6, 1.6, 1.6);
for (let k = 0; k < 360; k++) { const m = new THREE.Mesh(pg, new THREE.MeshLambertMaterial({ color: "#ffffff" })); m.visible = false; scene.add(m); PART.push(m); }
const SPR = []; for (let k = 0; k < 40; k++) { const m = new THREE.Mesh(new THREE.PlaneGeometry(1, 1), new THREE.MeshBasicMaterial({ transparent: true, alphaTest: 0.4, depthWrite: false, fog: false })); m.visible = false; scene.add(m); SPR.push(m); }
const HUMO = []; const hm = new THREE.MeshLambertMaterial({ color: "#d8d4cc", transparent: true, opacity: 0.8 });
for (let k = 0; k < 70; k++) { const m = new THREE.Mesh(new THREE.BoxGeometry(1, 1, 1), hm); m.visible = false; scene.add(m); HUMO.push(m); }
const AVES = []; for (let k = 0; k < 14; k++) { const g = new THREE.Group(), mb = new THREE.MeshLambertMaterial({ color: "#ffffff" }); g.add(caja(2.6, 2, 6, mb, 0, 0, 0)); const a1 = new THREE.Group(), a2 = new THREE.Group(); a1.add(caja(7, 0.6, 3.4, mb, 3.5, 0, 0)); a2.add(caja(7, 0.6, 3.4, mb, -3.5, 0, 0)); g.add(a1, a2); g.add(caja(1.4, 1.4, 2, MB("#f0a020"), 0, 0, 3.6)); g.visible = false; scene.add(g); AVES.push({ g, a1, a2, mb }); }
const HOJAS = []; for (let k = 0; k < 40; k++) { const m = caja(2, 0.3, 2, new THREE.MeshLambertMaterial({ color: ["#5f9e3a", "#8ab04a", "#d9a630", "#c0582e"][k % 4] })); m.castShadow = false; m.visible = false; scene.add(m); HOJAS.push(m); }
const LUCI = []; for (let k = 0; k < 40; k++) { const m = caja(1, 1, 1, MB("#fff27a")); m.castShadow = false; m.visible = false; scene.add(m); LUCI.push(m); }
const NUBES = []; for (let k = 0; k < 26; k++) { const g = new THREE.Group(); for (let j = 0; j < 4; j++) { const s = 30 + rnd(k * 9 + j) * 30; const b = caja(s * 1.6, s * 0.5, s, MAT.nube, j * 26 * (rnd(k + j) - 0.3), (j % 2) * 8, j * 14); b.castShadow = false; g.add(b); } g.visible = false; scene.add(g); NUBES.push(g); }
const DELF = []; for (let k = 0; k < 3; k++) { const g = new THREE.Group(), m = new THREE.MeshLambertMaterial({ color: "#7a9ab8" }); g.add(caja(4, 4, 14, m, 0, 0, 0)); g.add(caja(3, 2, 5, m, 0, -0.5, 9)); g.add(caja(1, 4, 3, m, 0, 3, -1)); g.add(caja(7, 1, 3, m, 0, 0, -8)); g.visible = false; scene.add(g); DELF.push(g); }
const FG = []; for (let k = 0; k < 4; k++) { const g = new THREE.Group(); const p1 = new THREE.Mesh(new THREE.PlaneGeometry(1, 1), texPlanta("hierba")); const p2 = p1.clone(); p2.rotation.y = 1.2; p1.rotation.y = -0.4; g.add(p1, p2); g.visible = false; scene.add(g); FG.push(g); }
const RAYOS = []; for (let k = 0; k < 6; k++) { const m = new THREE.Mesh(new THREE.PlaneGeometry(14, 400), new THREE.MeshBasicMaterial({ color: "#fff4c8", transparent: true, opacity: 0.18, depthWrite: false, side: THREE.DoubleSide, fog: false, blending: THREE.AdditiveBlending })); m.visible = false; scene.add(m); RAYOS.push(m); }
const CHARCO = caja(1, 0.4, 1, MB("#5ad040")); CHARCO.castShadow = false; CHARCO.visible = false; scene.add(CHARCO);
const COPA = hacerProp("copa"); COPA.visible = false; scene.add(COPA);

// ------------------------------------------------------------------ datos
const L = await (await fetch("linea.json")).json();
const PL = L.planos; window.DUR = L.dur;
let CAMOFF = {}; try { const r = await fetch("camfix.json"); if (r.ok) CAMOFF = await r.json(); } catch (e) {}
window.CAMOFF = CAMOFF;
const HOR = Object.keys(CAST);
// posición mundial de un actor del plano en el instante u (0..1 del segmento)
function spotDe(p) { return SETS[p.set].spots[p.spot]; }
function shipPos(p) { const s = SETS[p.set], sp = spotDe(p); const b = sp.barco || [0, -8, 0, 0]; return [s.ox + b[0], b[1], b[2], b[3] || 0]; }

// ------------------------------------------------------------------ acciones
function ang(dx, dz) { return Math.atan2(dx, dz) / D; }
function mover(a, u, vel = 1) { const to = a.to || [a.x, a.z]; const q = cl(u * 1.08 * vel); return { x: lerp(a.x, to[0], q), z: lerp(a.z, to[1], q), ry: (to[0] !== a.x || to[1] !== a.z) ? ang(to[0] - a.x, to[1] - a.z) : a.ry, mov: u < 0.93 }; }
function accion(a, lt, dur, t) {
  const u = cl(lt / dur), p = { x: a.x, z: a.z, ry: a.ry, seed: a.n.length, cabY: 6 * Math.sin(t * 0.9 + a.n.length) };
  const ah = (x) => x; let e = a.e;
  switch (a.acc) {
    case "quieto": p.bR = [4 * Math.sin(t * 1.3), 0]; p.bL = [-4 * Math.sin(t * 1.3), 0]; p.cabX = 3 * Math.sin(t * 0.7); break;
    case "hablar": p.bR = [-35 - 25 * Math.sin(lt * 4.2), -15]; p.cR = 50 + 25 * Math.sin(lt * 5.3); p.bL = [-10 - 15 * Math.max(0, Math.sin(lt * 3.1 + 1)), 8]; p.cL = 30; p.cabX = 4 * Math.sin(lt * 6.5); p.cabZ = 4 * Math.sin(lt * 2.1); p.ladeo = 2 * Math.sin(lt * 2); if (e === "normal" && Math.sin(lt * 17) > 0.2) e = "habla"; break;
    case "andar": case "correr": case "embestir": { const v = a.acc === "andar" ? 1 : 1.25; const m = mover(a, u, v); Object.assign(p, m); const d = Math.hypot(m.x - a.x, m.z - a.z); p.andar = d / (a.acc === "andar" ? 5.5 : 7.5); p.amp = m.mov ? (a.acc === "andar" ? 1 : 1.5) : 0; if (a.acc !== "andar") { p.lean = m.mov ? (a.acc === "embestir" ? 28 : 14) : 0; p.cabX = a.acc === "embestir" ? 25 : -6; }
      if (a.acc === "embestir") { p.bR = [-40, -30]; p.bL = [-40, 30]; } if (a.prop2 === "ovillo") { p.bL = [-28, 6]; p.cL = 45; } break; }
    case "agachado": { const m = mover(a, u, 0.85); Object.assign(p, m); const d = Math.hypot(m.x - a.x, m.z - a.z); p.andar = d / 4.5; p.amp = m.mov && a.to ? 0.7 : 0; p.lean = 26; p.pR = -28; p.pL = -28; p.kR = 44; p.kL = 44; p.cadY = -3.5; p.bR = [-60, -10]; p.cR = 60; p.bL = [-50, 10]; p.cL = 70; p.cabX = -18; p.cabY = 20 * Math.sin(t * 1.5); break; }
    case "senalar": p.bR = [-92 + 3 * Math.sin(t * 5), -6]; p.cR = 0; p.bL = [-20, 20]; p.cL = 90; p.lean = 6; p.cabX = -4; break;
    case "brazos": p.bR = [-30, 38]; p.bL = [-30, -38]; p.cR = 95; p.cL = 95; p.cabZ = 5 * Math.sin(t * 1.6); p.cabX = -5; p.pR = 6 * Math.max(0, Math.sin(t * 9)); break;
    case "celebrar": { const j = Math.abs(Math.sin(lt * 7)); p.bR = [-165 + 15 * Math.sin(lt * 14), -20]; p.bL = [-165 + 15 * Math.sin(lt * 14 + 1), 20]; p.cR = 10; p.cL = 10; p.salto = j * 5; p.cabX = -12; p.kR = 20 * j; p.kL = 20 * j; if (a.to) { const m = mover(a, u); p.x = m.x; p.z = m.z; } break; }
    case "levantar": { const b1 = seg(u, 0.05, 0.3), b2 = seg(u, 0.3, 0.5, x => back(x, 1.5)); p.lean = 35 * b1 * (1 - b2); p.kR = 50 * b1 * (1 - b2); p.kL = 50 * b1 * (1 - b2); p.pR = -30 * b1 * (1 - b2); p.pL = -30 * b1 * (1 - b2); p.cadY = -4 * b1 * (1 - b2);
      p.bR = [lerp(-60 * b1, -175, b2), -8]; p.bL = [lerp(-60 * b1, -175, b2), 8]; p.cR = 10; p.cL = 10; p.cabX = -12 * b2; p.salto = b2 * Math.abs(Math.sin(lt * 6)) * 1.5 * (u > 0.6 ? 1 : 0); break; }
    case "espada_alto": { const q = seg(u, 0.02, 0.18, x => back(x, 2)); p.bR = [-172 * q + 4 * Math.sin(t * 6), -8 * q]; p.cR = 6; p.bL = [-10, 30]; p.cL = 100; p.lean = -5 * q; p.cabX = -10 * q; p.pR = -10 * q; p.pL = 10 * q; break; }
    case "mostrar": p.bR = [-115 + 6 * Math.sin(t * 3), -12]; p.bL = [-115 + 6 * Math.sin(t * 3 + 1), 12]; p.cR = 25; p.cL = 25; p.cabX = -6; break;
    case "golpe": case "maza_golpe": case "patada": case "manotazo": {
      const k0 = a.acc === "maza_golpe" ? 0.45 : (a.acc === "manotazo" ? 0.25 : (a.acc === "patada" ? 0.42 : 0.35)), an = seg(u, k0 - 0.18, k0 - 0.03, x => x * x), hit = seg(u, k0 - 0.03, k0, x => x), rec = seg(u, k0 + 0.2, k0 + 0.4);
      if (a.acc === "golpe") { p.bR = [lerp(lerp(0, 40, an), -95, hit) * (1 - rec), lerp(lerp(0, 25, an), -10, hit) * (1 - rec)]; p.cR = lerp(lerp(10, 110, an), 0, hit) * (1 - rec) + 10; p.bL = [lerp(-30 * an, 20, hit), 20 * an]; p.cL = 70 * an; p.giro = lerp(lerp(0, 35, an), -25, hit) * (1 - rec); p.lean = lerp(lerp(0, -8, an), 14, hit) * (1 - rec); p.pR = lerp(0, 25, an) * (1 - hit); }
      else if (a.acc === "maza_golpe") { p.bR = [lerp(lerp(-30, -175, an), -50, hit), -10]; p.bL = [lerp(lerp(-30, -175, an), -50, hit), 10]; p.cR = 20; p.cL = 20; p.lean = lerp(lerp(0, -10, an), 22, hit) * (1 - rec * 0.5); }
      else if (a.acc === "patada") { p.pR = lerp(lerp(0, 30, an), -95, hit) * (1 - rec); p.kR = lerp(lerp(0, 60, an), 0, hit) * (1 - rec); p.lean = lerp(lerp(0, 6, an), -16, hit) * (1 - rec); p.bR = [-40 * hit, -40 * hit]; p.bL = [-40 * hit, 40 * hit]; if (a.n === "esciron" || a.ry === 180) { p.cadY = 0; } }
      else { p.bR = [-70, lerp(lerp(0, -30, an), 70, hit) * (1 - rec)]; p.cR = 10; p.lean = 8 * hit; p.giro = lerp(lerp(0, 25, an), -25, hit) * (1 - rec); }
      if (a.e2 && u > k0 + 0.1) e = a.e2; if (a.n === "teseo" && a.acc === "golpe" && u > 0.6) e = "guino";
      break; }
    case "espadazo": { const ph = lt * 2 * Math.PI / 0.62, s = Math.sin(ph); p.bR = [-110 + 70 * s, -10 - 20 * Math.cos(ph)]; p.cR = 20; p.bL = [-30, 30]; p.cL = 60; p.lean = 8 + 8 * s; p.giro = 20 * s; p.x = a.x + 3 * Math.sin(ph * 0.5); p.pR = -15; p.pL = 15; p.kL = 10; break; }
    case "pelear": { const ph = lt * 2 * Math.PI / 0.62 + 1.2, s = Math.sin(ph); p.bR = [-90 + 60 * s, -30]; p.bL = [-90 - 60 * s, 30]; p.cR = 30; p.cL = 30; p.lean = 10 + 6 * s; p.giro = -15 * s; p.cabX = 15; break; }
    case "caer": case "desmayo": case "caer_grande": { const k0 = a.acc === "desmayo" ? 0.45 : (a.acc === "caer_grande" ? 0.25 : 0.38), f = seg(u, k0, k0 + 0.18, x => x * x); const dir = a.acc === "caer_grande" ? 1 : -1;
      p.rotX = 88 * f * dir; p.y = 2 * f; p.bR = [-160 * f, -30]; p.bL = [-160 * f, 30]; p.cR = 10; p.cL = 10; if (u < k0) { p.ladeo = 10 * Math.sin(lt * 9) * (a.acc === "desmayo" ? 1 : 0.4); p.cabZ = 10 * Math.sin(lt * 7); p.lean = a.acc === "caer" ? -10 : 0; }
      if (a.acc === "caer") { p.x = a.x + 14 * f * Math.sin(a.ry * D + Math.PI) * -1; } if (a.acc === "desmayo") { p.rotX = 0; p.y = 0; p.cadY = -6 * f; p.lean = -20 * f; p.ladeo = 30 * f; } break; }
    case "tumbado": p.rotX = -90; p.y = a.y ?? 2; p.bR = [-10, -12 + 6 * Math.sin(t * 8)]; p.bL = [-10, 12 - 6 * Math.sin(t * 8)]; p.pR = 6 * Math.sin(t * 10); p.pL = -6 * Math.sin(t * 10); p.cabY = 20 * Math.sin(t * 3); break;
    case "dormir": p.rotX = -90; p.rotZ = 0; p.y = 2.5; p.bR = [-10, -6]; p.bL = [-10, 6]; p.cabY = 25; p.sq = 1 + 0.03 * Math.sin(t * 2); e = "cerrados"; break;
    case "sentado": p.y = a.y ?? 3.5; p.pR = -82; p.pL = -82; p.kR = 82; p.kL = 82; p.bR = [-40, -6]; p.bL = [-40, 6]; p.cR = 40; p.cL = 40; p.cabX = 3 * Math.sin(t * 0.8); break;
    case "susto": { const q = seg(u, 0.03, 0.15, x => back(x, 2.5)); p.bR = [-150 * q, -30 * q]; p.bL = [-150 * q, 30 * q]; p.cR = 20; p.cL = 20; p.lean = -12 * q; p.salto = 6 * Math.sin(seg(u, 0.02, 0.2) * Math.PI); p.x = a.x - 6 * q * Math.sin(a.ry * D); p.z = a.z - 6 * q * Math.cos(a.ry * D); p.ladeo = 3 * Math.sin(t * 30) * q; break; }
    case "pensar": p.bR = [-55, 22]; p.cR = 125; p.bL = [-40, -30]; p.cL = 90; p.cabZ = 10; p.cabX = -6 + 3 * Math.sin(t * 2); p.cabY = 15 * Math.sin(t * 0.8); break;
    case "llorar": p.bR = [-85, 28]; p.bL = [-85, -28]; p.cR = 130; p.cL = 130; p.cabX = 20; p.lean = 10; p.ladeo = 3 * Math.sin(t * 14); p.salto = 0.6 * Math.abs(Math.sin(t * 7)); break;
    case "saludar": p.bR = [-165, -28 + 25 * Math.sin(lt * 9)]; p.cR = 20; p.bL = [0, 6]; p.cabZ = 6 * Math.sin(lt * 3); break;
    case "mirar": p.bR = [-140, 28]; p.cR = 115; p.bL = [0, 6]; p.cabY = 25 * Math.sin(t * 0.7); p.cabX = -6; break;
    case "arrodillado": p.pR = -90; p.kR = 90; p.pL = 0; p.kL = 90; p.cadY = -6; p.y = 0; p.bR = [-95, 12]; p.bL = [-95, -12]; p.cR = 70; p.cL = 70; p.cabX = 10 + 6 * Math.sin(t * 2); break;
    case "empujar": p.lean = 30; p.bR = [-88, 0]; p.bL = [-88, 0]; p.cR = 15; p.cL = 15; p.andar = lt * 6; p.amp = 0.5; p.ladeo = 3 * Math.sin(lt * 12); break;
    case "abrazar": p.bR = [-85, 30]; p.bL = [-85, -30]; p.cR = 70; p.cL = 70; p.ladeo = 8 * Math.sin(lt * 4); p.salto = Math.abs(Math.sin(lt * 5)) * 1.5; break;
    case "encoger": { const s = Math.abs(Math.sin(lt * 2.2)); p.bR = [-20, -40 * s]; p.bL = [-20, 40 * s]; p.cR = 80; p.cL = 80; p.cabZ = 12 * s; p.sq = 1 + 0.04 * s; break; }
    case "facepalm": p.bR = [-110, 26]; p.cR = 145; p.cabX = 20; p.bL = [0, 5]; p.ladeo = 3 * Math.sin(t * 3); break;
    case "lanzado": { const to = a.to, f = cl(u * 1.2), h = a.h || 80, y2 = a.y2 || 0; p.x = lerp(a.x, to[0], f); p.z = lerp(a.z, to[1], f); p.y = h * 4 * f * (1 - f) + y2 * f * f; p.rotX = f * 720 * (to[1] < a.z ? -1 : 1); p.bR = [-160 + 40 * Math.sin(lt * 20), -40]; p.bL = [-160 + 40 * Math.sin(lt * 20 + 2), 40]; p.pR = 30 * Math.sin(lt * 18); p.pL = -30 * Math.sin(lt * 18); if (u > 0.85 && y2 < -50) p.y = -400; break; }
    case "bailar": { const s = Math.sin(lt * 7); p.bR = [-90 - 70 * s, -20]; p.bL = [-90 + 70 * s, 20]; p.cR = 40; p.cL = 40; p.ladeo = 12 * s; p.giro = 20 * s; p.salto = Math.abs(Math.sin(lt * 7)) * 3; p.kR = 25 * Math.max(0, s); p.kL = 25 * Math.max(0, -s); break; }
    case "verter": p.bR = [-80, -8]; p.cR = 20; p.bL = [-120 + 10 * Math.sin(t * 4), 20]; p.cL = 40; p.cabX = 18; p.lean = 8; break;
    case "ofrecer": { const q = seg(u, 0.05, 0.3); p.bR = [-75 * q, -4]; p.cR = 15; p.lean = 5 * q; p.cabX = 4; break; }
    case "sacar_espada": { const q = seg(u, 0.15, 0.4, x => back(x, 1.6)); p.bR = [lerp(10, -120, q), lerp(25, -10, q)]; p.cR = lerp(60, 10, q); p.giro = lerp(-20, 10, q); p.cabX = -6 * q; break; }
    case "magia": p.bR = [-95 + 10 * Math.sin(lt * 11), -20]; p.bL = [-95 + 10 * Math.sin(lt * 11 + 1.5), 20]; p.cR = 20; p.cL = 20; p.lean = 5; p.cabX = -5; p.ladeo = 4 * Math.sin(lt * 3); break;
    case "susurrar": p.bR = [-115, 38]; p.cR = 120; p.lean = 16; p.cabZ = -10; p.cabX = 8; p.bL = [-10, 10]; if (Math.sin(lt * 15) > 0.3) e = "malvado"; break;
    case "triste": p.cabX = 22; p.bR = [2, 2]; p.bL = [2, -2]; p.lean = 6; p.ladeo = 2 * Math.sin(t * 0.8); if (a.to) { const m = mover(a, u); Object.assign(p, m); p.andar = Math.hypot(m.x - a.x, m.z - a.z) / 5; p.amp = m.mov ? 0.7 : 0; } break;
    case "lanza": p.bR = [-30, -2]; p.cR = 80; p.cabY = 15 * Math.sin(t * 0.6); break;
    case "plano": p.bR = [-60, 12]; p.bL = [-60, -12]; p.cR = 60; p.cL = 60; p.cabX = 18 + 6 * Math.sin(lt * 5); break;
    case "perdido": { const r = 16, a0 = lt * 1.6; p.x = a.x + Math.cos(a0) * r; p.z = a.z + Math.sin(a0) * r; p.ry = ang(-Math.sin(a0), Math.cos(a0)); p.andar = lt * 5; p.amp = 0.8; p.bR = [-160, 30]; p.cR = 120; p.cabZ = 10 * Math.sin(lt * 4); break; }
    case "pulgar": p.bR = [-78, -6]; p.cR = 85; p.salto = Math.abs(Math.sin(lt * 4)) * 1.2; p.bL = [0, 6]; p.cabZ = 6; break;
    case "musculos": { const q = 0.8 + 0.2 * Math.sin(lt * 6); p.bR = [-10, -85 * q]; p.bL = [-10, 85 * q]; p.cR = 110; p.cL = 110; p.sq = 1.04; p.cabX = -8; p.lean = -4; break; }
    case "acunar": p.bR = [-60, 22]; p.bL = [-60, -22]; p.cR = 75; p.cL = 75; p.ladeo = 8 * Math.sin(lt * 2.5); p.cabX = 18; break;
    case "bebe": p.lean = -30; p.pR = -70; p.pL = -70; p.kR = 30 * Math.sin(lt * 9); p.kL = 30 * Math.sin(lt * 9 + 1); p.bR = [-120 + 30 * Math.sin(lt * 8), -20]; p.bL = [-120 + 30 * Math.sin(lt * 8 + 2), 20]; p.y = a.y ?? 14; break;
    case "mano_pecho": p.bR = [-45, 34]; p.cR = 100; p.bL = [-150, 20]; p.cL = 10; p.cabX = -8; p.cabZ = 6; break;
    case "suspiro": { const s = Math.sin(lt * 2.4); p.bR = [-70, 30]; p.bL = [-70, -30]; p.cR = 115; p.cL = 115; p.ladeo = 10 * s; p.cabZ = 12 * s; p.salto = Math.abs(Math.sin(lt * 4.8)) * 1.2; break; }
    case "estirar": { const s = Math.max(0, Math.sin(lt * 6)); p.lean = -18 - 8 * s; p.bR = [-80, 8]; p.bL = [-80, -8]; p.cR = 10; p.cL = 10; p.pR = -20; p.kR = 10; p.x = a.x + 3 * s; break; }
    case "respirar": { const s = Math.sin(lt * 3.2); p.sq = 1 + 0.05 * s; p.cabX = 18 + 6 * s; p.bR = [-10, -18 - 6 * s]; p.bL = [-10, 18 + 6 * s]; p.cR = 30; p.cL = 30; p.lean = 12; p.salto = 0; break; }
    case "rugir": { const q = seg(u, 0.05, 0.25, x => back(x, 2)); p.cabX = -35 * q; p.bR = [-130 * q, -45 * q]; p.bL = [-130 * q, 45 * q]; p.cR = 50; p.cL = 50; p.lean = -12 * q; p.ladeo = 3 * Math.sin(t * 35) * q; e = "enfado"; break; }
    case "esquivar": { const q = seg(u, 0.45, 0.62, eout); p.x = a.x + 38 * q; p.salto = 14 * Math.sin(q * Math.PI); p.rotZ = -40 * Math.sin(q * Math.PI); p.bR = [-120 * q, -30]; p.bL = [-60, 40]; p.cR = 30; if (u < 0.45) { p.bR = [-60, -10]; p.cR = 40; } break; }
    case "sacudir": { const s = Math.sin(lt * 9); p.ladeo = 18 * s; p.giro = 15 * Math.sin(lt * 4.5); p.bR = [-120 + 30 * s, -40]; p.bL = [-120 - 30 * s, 40]; p.cabX = 20; p.cabZ = -10 * s; break; }
    case "montar": break;  // se resuelve después (sobre el minotauro)
    case "caer_acantilado": { const q = seg(u, 0.08, 0.35), f = seg(u, 0.35, 0.8, x => x * x); p.x = a.x + 22 * q + 30 * f; p.andar = q * 4; p.amp = q < 1 ? 0.8 : 0; p.y = (a.y2 ?? -170) * f; p.rotX = 60 * f; p.bR = [-160 * f, -40]; p.bL = [-160 * f, 40]; if (u < 0.35) { p.cabX = 15; } if (u > 0.82) p.y = (a.y2 ?? -170) > -50 ? -60 : -400; break; }
    case "aparecer": { const q = seg(u, 0.0, 0.2, x => back(x, 2)); p.sc = Math.max(0.001, q); p.bR = [-60 - 20 * Math.sin(lt * 4), -30]; p.cR = 40; p.bL = [-150, 20]; p.salto = 6 * (1 - q); break; }
    case "volar_carro": { const f = seg(u, 0.15, 1.0, x => x * x); p.x = lerp(a.x, a.to[0], f); p.z = lerp(a.z, a.to[1], f); p.y = (a.h || 200) * f + 7; p.ry = ang(a.to[0] - a.x, a.to[1] - a.z); p.bR = [-150, -30]; p.cR = 10; p.bL = [-40, 10]; p.cabX = -10; p.pR = -10; p.pL = 10; break; }
    default: break;
  }
  // ---- vida: entrada andando / paso / giro, y balanceo de peso (nada estático)
  if (a.ent || a.gira) {
    const lw = lt - (a.ent_d || 0);
    if (a.ent) { const dx = a.x - a.ent[0], dz = a.z - a.ent[1], L = Math.hypot(dx, dz), Tw = Math.max(0.45, L / 26); const q = cl(lw / Tw);
      if (q < 1) { p.x = lerp(a.ent[0], a.x, q); p.z = lerp(a.ent[1], a.z, q); p.ry = ang(dx, dz); p.andar = L * q / 5.5; p.amp = 1; p.bR = undefined; p.bL = undefined; p.cR = undefined; p.cL = undefined; p.lean = 4; p.rotX = 0; p.y = undefined; p.pR = 0; p.pL = 0; p.kR = 0; p.kL = 0; p.cadY = 0; }
      else { const r = cl((lw - Tw) / 0.3, 0, 1), a0 = ang(dx, dz); let dr = ((p.ry - a0) % 360 + 540) % 360 - 180; p.ry = a0 + dr * eout(r); p.x = a.x; p.z = a.z; } }
    if (a.gira) { const q = cl(lw / 0.55); p.ry = (p.ry || 0) + a.gira * (1 - eout(q)); if (q < 1) { p.andar = q * 3; p.amp = 0.6; p.salto = (p.salto || 0) + 1.5 * Math.sin(q * Math.PI); } }
  }
  if (["quieto", "hablar", "brazos", "pensar", "lanza", "mirar", "plano", "mano_pecho", "senalar"].includes(a.acc)) { const s = a.n.length * 1.7; p.ladeo = (p.ladeo || 0) + 3 * Math.sin(t * 1.3 + s); p.giro = (p.giro || 0) + 6 * Math.sin(t * 0.9 + s); p.salto = (p.salto || 0) + 0.5 * Math.max(0, Math.sin(t * 2.6 + s)); }
  if (a.prop === "espada" && !["espada_alto", "espadazo", "sacar_espada", "mostrar", "montar", "caer"].includes(a.acc) && !p.bR) { p.bR = [-25, -6]; p.cR = 50; }
  return { p, e };
}

// ------------------------------------------------------------------ luces
const LUZ = {
  dia: { c: ["#5fa8e8", "#d8ecff"], f: ["#d2e6f6", 450, 2000], h: ["#cfe6ff", 1.1], s: ["#fff1d8", 2.6], x: 1.05 },
  tarde: { c: ["#e8743a", "#ffd9a0"], f: ["#ffd0a0", 450, 2000], h: ["#ffd0a0", 0.95], s: ["#ffb070", 2.6], x: 1.05 },
  amanecer: { c: ["#7a7ad0", "#ffb59a"], f: ["#f0b8a8", 450, 1900], h: ["#d8c0e8", 0.9], s: ["#ffc0a0", 2.0], x: 1.08 },
  noche: { c: ["#070c22", "#1e2a50"], f: ["#121a36", 300, 1500], h: ["#6a7fb8", 0.45], s: ["#9ab0ff", 0.8], x: 1.25, noche: 1 },
  tormenta: { c: ["#3a4250", "#7a8290"], f: ["#5a6270", 300, 1500], h: ["#a0a8b8", 0.75], s: ["#c8d0e0", 1.0], x: 1.05 },
  interior: { c: ["#5fa8e8", "#d8ecff"], f: ["#d2e6f6", 500, 2200], h: ["#ffe2c0", 1.0], s: ["#fff1d8", 1.8], x: 1.1, velas: 1 },
  laberinto: { c: ["#0a0e1c", "#1c2234"], f: ["#101422", 140, 650], h: ["#7a8ac0", 0.62], s: ["#8a98d0", 0.7], x: 1.25, velas: 1, noche: 1 },
  mapa: { c: ["#9ad0f0", "#e8f6ff"], f: ["#e8f6ff", 2500, 6000], h: ["#ffffff", 1.25], s: ["#fff6e0", 2.2], x: 1.0 },
};
function luces(nm, t, foco, set) {
  const L0 = LUZ[nm] || LUZ.dia; cielo(L0.c[0], L0.c[1]); scene.fog.color.set(L0.f[0]); scene.fog.near = L0.f[1]; scene.fog.far = L0.f[2];
  hemi.color.set(L0.h[0]); hemi.intensity = L0.h[1]; sol.color.set(L0.s[0]); sol.intensity = L0.s[1]; renderer.toneMappingExposure = L0.x;
  const sx = nm === "tarde" ? -220 : (nm === "amanecer" ? 240 : 140);
  sol.position.set(foco.x + sx, 300, foco.z + 200); sol.target.position.set(foco.x, 0, foco.z);
  estrellas.visible = !!L0.noche; luna.visible = nm === "noche"; if (luna.visible) { luna.position.set(cam.position.x - 600, 700, cam.position.z - 1500); luna.lookAt(cam.position); }
  if (nm === "tormenta") { const f = Math.floor(t * 3); if (rnd(f * 7.7) > 0.86 && (t * 3 - f) < 0.12) { hemi.intensity = 2.6; renderer.toneMappingExposure = 1.6; } }
  const fl = 1 + 0.08 * Math.sin(t * 17) + 0.05 * Math.sin(t * 29);
  vela.intensity = L0.velas ? (nm === "laberinto" ? 650 : 1500) * fl : (nm === "noche" ? 1300 * fl : 0);
  vela.position.copy(foco).lerp(cam.position, 0.55); vela.position.y += 32;
  if (set === "naxos" && SETS.naxos.vida.fogata) { const f = SETS.naxos.vida.fogata; vela.position.set(f[0], f[1] + 10, f[2]); vela.intensity = 2200 * fl; }
}

// ------------------------------------------------------------------ cámara
const v3 = (x, y, z) => new THREE.Vector3(x, y, z);
function look(p, tgt, fov) { cam.position.copy(p); cam.fov = fov; cam.updateProjectionMatrix(); cam.lookAt(tgt); cam.updateMatrixWorld(true); }
function camara(spec, ctx, lt, d, t, shake) {
  const [tipo, foco, angS] = (spec + "::").split(":"); const an = (+angS || 0) + (CAMOFF[ctx.idx] || 0), u = cl(lt / d);
  let F, ry = 0, alto = 28, actor = null;
  const sp = ctx.sp;
  if (foco.includes(",")) { const [a, b] = foco.split(",").map(n => ctx.pos[n]).filter(Boolean); if (a && b) { F = a.p.clone().add(b.p).multiplyScalar(0.5); const dx = b.p.x - a.p.x, dz = b.p.z - a.p.z; ry = ang(-dz, dx); if (Math.cos(ry * D) < 0) ry += 180; alto = Math.max(a.alto, b.alto); } }
  if (!F && ctx.pos[foco]) { actor = ctx.pos[foco]; F = actor.p.clone(); ry = actor.ry; alto = actor.alto; }
  if (!F && foco === "barco") { F = BARCO.g.position.clone().add(v3(0, 6, 0)); alto = 64; }
  if (!F && foco === "espada_teseo" && ctx.pos.teseo) { F = ctx.pos.teseo.mano.clone(); alto = 0; }
  if (!F && foco === "vela_blanca" && ctx.pos.egeo) { F = ctx.pos.egeo.mano.clone(); alto = 0; }
  if (!F && foco === "ovillo") { const o = Object.values(ctx.pos).find(q => q.ovillo); if (o) { F = o.ovillo.clone(); alto = 0; } }
  if (!F && sp.pts[foco]) { const q = sp.pts[foco]; F = v3(q[0], q[1], q[2]); alto = 0; }
  if (!F) { const prim = Object.values(ctx.pos)[0]; if (prim && foco !== "spot") { F = prim.p.clone(); ry = prim.ry; alto = prim.alto; actor = prim; } else { F = v3(sp.x, sp.y, sp.z); alto = 20; } }
  const base = (actor || foco.includes(",")) && ["primer", "medio", "contra", "hombro", "dos", "orbita"].includes(tipo) ? ry : 0;
  const yaw = (base + an) * D, fx = Math.sin(yaw), fz = Math.cos(yaw), rxv = Math.cos(yaw), rzv = -Math.sin(yaw);
  const tgt = F.clone(), pos = F.clone(); let fov = 40; const drift = Math.sin(t * 0.35) * 0.5;
  switch (tipo) {
    case "primer": { const dd = 40 * (1 - 0.1 * u) * (alto > 30 ? alto / 28 : 1); tgt.y += alto * 1.03; pos.set(F.x + fx * dd + rxv * drift * 4, F.y + alto * 1.06 + 1, F.z + fz * dd + rzv * drift * 4); fov = 34; break; }
    case "medio": { const dd = 72 * (alto > 30 ? alto / 28 : 1); tgt.y += alto * 0.72; pos.set(F.x + fx * dd + rxv * (u - 0.5) * 14, F.y + alto * 0.95, F.z + fz * dd + rzv * (u - 0.5) * 14); fov = 38; break; }
    case "contra": { const dd = 50 * (alto > 30 ? alto / 28 : 1); tgt.y += alto * 1.1; pos.set(F.x + fx * dd + rxv * (u - 0.5) * 10, F.y + 4, F.z + fz * dd + rzv * (u - 0.5) * 10); fov = 50; break; }
    case "general": { const dd = 112; tgt.y += 18; pos.set(F.x + fx * dd + rxv * (u - 0.5) * 46, F.y + 40 - 8 * u, F.z + fz * dd + rzv * (u - 0.5) * 40); fov = 40; break; }
    case "paisaje": { const a2 = yaw + (u - 0.5) * 0.32, dd = 200 - 20 * u; tgt.y += 24; pos.set(F.x + Math.sin(a2) * dd, F.y + 64, F.z + Math.cos(a2) * dd); fov = 46; break; }
    case "picado": { const dd = 60; tgt.y += 4; pos.set(F.x + fx * dd + rxv * (u - 0.5) * 16, F.y + 115 - 10 * u, F.z + fz * dd + rzv * (u - 0.5) * 16); fov = 46; break; }
    case "cenital": { tgt.y = F.y; pos.set(F.x + Math.sin(u * 0.4) * 30, F.y + 720 - 80 * u, F.z + 260); fov = 50; break; }
    case "travel": { const dd = 96; tgt.y += alto * 0.7; pos.set(F.x + 18 + Math.sin(an * D) * 0, F.y + 26, F.z + dd); fov = 38; break; }
    case "orbita": { const a2 = yaw + u * 0.9 - 0.45, dd = 74 * (alto > 30 ? alto / 28 : 1); tgt.y += alto * 0.8; pos.set(F.x + Math.sin(a2) * dd, F.y + alto * 1.1, F.z + Math.cos(a2) * dd); fov = 40; break; }
    case "hombro": { const by = (ry + 180 + 18) * D, dd = 32; pos.set(F.x + Math.sin(by) * dd, F.y + alto * 1.25, F.z + Math.cos(by) * dd); tgt.set(F.x + Math.sin(ry * D) * 260, F.y + alto * 0.5, F.z + Math.cos(ry * D) * 260); fov = 42; break; }
    case "dos": { const dd = 96; tgt.y += alto * 0.75; pos.set(F.x + fx * dd + rxv * (u - 0.5) * 12, F.y + alto, F.z + fz * dd + rzv * (u - 0.5) * 12); fov = 38; break; }
  }
  if (ctx.sp.caja) { const c = ctx.sp.caja; pos.x = cl(pos.x, ctx.sp.x + c[0], ctx.sp.x + c[1]); pos.z = cl(pos.z, ctx.sp.z + c[2], ctx.sp.z + c[3]); }
  if (ctx.zoom) fov *= ctx.zoom;
  if (shake) { pos.x += shake * (rnd(Math.floor(t * 60)) - 0.5); pos.y += shake * (rnd(Math.floor(t * 60) + 3) - 0.5); }
  look(pos, tgt, fov); window.__ult = { tgt: tgt.clone(), pos: pos.clone(), foco, tipo, F: F.clone() };
  return { tipo, F };
}

// ------------------------------------------------------------------ efectos (partículas, sprites)
const FXC = { polvo: ["#9a7a50", "#7a5532", "#c2a070"], golpe: ["#ffffff", "#ffe14a", "#ffb347"], bloques: ["#5a3a24", "#8a6450", "#d8dde4", "#ffe14a"], muro: ["#55524c", "#4a6a2a", "#2a2824"],
  salpicar_mar: ["#bfe6ff", "#5aa6e0", "#ffffff"], hojas: ["#2a5a32", "#5f9e3a", "#6b4a2c"], veneno: ["#5ad040", "#2a8a20", "#a0f080"], chispas_moradas: ["#c9a0ff", "#8a5ad8", "#ffffff"], chispas_doradas: ["#ffe14a", "#fff4c8", "#f0b020"], brillo: ["#ffffff", "#fff4c8"], vapor: ["#ffffff", "#e0e0e0"] };
function particulas(t, evs) {
  let k = 0;
  for (const e of evs) { const lt = t - e.t; const dur = e.dur || 1.6; if (lt < 0 || lt > dur) continue;
    for (let i = 0; i < e.n && k < PART.length; i++, k++) { const m = PART[k], s = e.t * 13 + i;
      let x, y, z; const vx = (rnd(s) - 0.5) * 2 * e.v, vz = (rnd(s + 1) - 0.5) * 2 * e.v, vy = (0.4 + rnd(s + 2)) * e.v;
      if (e.tipo === "sube") { x = e.x + (rnd(s) - 0.5) * 20 + Math.sin(lt * 3 + i) * 3; z = e.z + (rnd(s + 1) - 0.5) * 20; y = e.y + lt * (12 + rnd(s + 2) * 20); }
      else if (e.tipo === "chorro") { x = e.x + vx * 0.15 * lt; z = e.z + 10 * lt + vz * 0.1 * lt; y = e.y + 5 * lt - 40 * lt * lt; }
      else { x = e.x + vx * lt; z = e.z + vz * lt; y = Math.max(e.y0 ?? -1000, e.y + vy * lt - 90 * lt * lt); }
      m.position.set(x, y, z); m.rotation.set(lt * 9 + i, lt * 7, 0); m.material.color.set(e.cols[i % e.cols.length]); m.scale.setScalar(e.sz * (1 - cl((lt - dur * 0.7) / (dur * 0.3))) + 0.001); m.visible = true; } }
  for (; k < PART.length; k++) PART[k].visible = false;
}
function sprites(t, evs) {
  let k = 0;
  for (const e of evs) { const lt = t - e.t, dur = e.dur || 1.8; if (lt < 0 || lt > dur) continue;
    for (let i = 0; i < e.n && k < SPR.length; i++, k++) { const m = SPR[k], s = e.t * 7 + i; m.material.map = texIcono(e.ico); m.material.needsUpdate = m.userData.ico !== e.ico; m.userData.ico = e.ico;
      let x, y, z, sc = e.sz;
      if (e.ico === "estrella") { const a = lt * 6 + i * 2.1; x = e.x + Math.cos(a) * 9; z = e.z + Math.sin(a) * 9; y = e.y + 2 * Math.sin(a * 2); sc *= 0.7; }
      else if (e.ico === "zzz") { x = e.x + 4 + lt * 4 + i * 4; y = e.y + lt * 8 + i * 6; z = e.z; sc *= 0.8 + 0.2 * Math.sin(lt * 4); }
      else { x = e.x + (rnd(s) - 0.5) * 30; z = e.z + (rnd(s + 1) - 0.5) * 20; y = e.y + lt * (10 + rnd(s + 2) * 12) + (rnd(s + 3) - 0.5) * 10; sc *= (0.6 + 0.4 * rnd(s)) * Math.min(1, lt * 5) * (1 - cl((lt - dur * 0.75) / (dur * 0.25))); }
      m.position.set(x, y, z); m.quaternion.copy(cam.quaternion); m.scale.setScalar(Math.max(0.001, sc)); m.visible = true; } }
  for (; k < SPR.length; k++) SPR[k].visible = false;
}

// ------------------------------------------------------------------ vida de fondo
function vida(t, set, sp, nm, ctx) {
  const S = SETS[set], V = Object.assign({}, S.vida, sp.vida || {}), F = v3(sp.x, sp.y, sp.z);
  const noche = nm === "noche" || nm === "laberinto";
  // agua
  for (const a of S.aguas) { a.offset.x = t * (sp.navega ? 0.05 : 0.012); a.offset.y = t * (sp.navega ? 0.012 : 0.006) + 0.004 * Math.sin(t * 0.8); }
  if (V.fuente) V.fuente.position.y = 9 + 0.4 * Math.sin(t * 4);
  // llamas
  llamas.forEach((f, i) => { f.scale.set(1 + 0.1 * Math.sin(t * 13 + i), 1 + 0.3 * Math.sin(t * 19 + i * 1.7), 1 + 0.1 * Math.cos(t * 11 + i)); });
  S.g.traverse(o => { if (o.name === "rueda") o.rotation.z = t * 0.8; });
  // aves
  const tipo = noche && V.pajaros !== "murcielago" ? null : V.pajaros;
  AVES.forEach((b, i) => { if (!tipo || (tipo === "murcielago" && i > 7)) { b.g.visible = false; return; }
    const R = (tipo === "murcielago" ? 60 : 180) + rnd(i) * (tipo === "murcielago" ? 80 : 260), w = (0.25 + rnd(i + 5) * 0.2) * (i % 2 ? 1 : -1) * (tipo === "murcielago" ? 2.2 : 1), a = t * w + i * 2.4;
    const cx = F.x + (rnd(i + 2) - 0.5) * 300, cz = F.z - 120 + (rnd(i + 3) - 0.5) * 300, hy = (tipo === "murcielago" ? 70 : 130) + rnd(i + 4) * 90 + 10 * Math.sin(t * 1.3 + i);
    b.g.position.set(cx + Math.cos(a) * R, F.y + hy, cz + Math.sin(a) * R); b.g.rotation.y = -a + (w > 0 ? 0 : Math.PI); b.g.rotation.z = 0.25 * Math.sign(w);
    const fl = Math.sin(t * (tipo === "murcielago" ? 26 : 13) + i) * 0.8; b.a1.rotation.z = fl; b.a2.rotation.z = -fl;
    b.mb.color.set(tipo === "gaviota" ? "#ffffff" : (tipo === "murcielago" ? "#1a1418" : "#3a3030")); b.g.scale.setScalar(tipo === "murcielago" ? 0.8 : 1.2); b.g.visible = true; });
  // nubes
  NUBES.forEach((n, i) => { if (set === "laberinto" || set === "mapa") { n.visible = false; return; } const span = 3600, x = ((rnd(i) * span + t * (8 + rnd(i + 1) * 6)) % span) - span / 2; n.position.set(F.x + x, F.y + 300 + rnd(i + 2) * 200, F.z - 1800 + rnd(i + 3) * 3000); n.visible = !(nm === "interior"); });
  // humo de chimeneas
  const em = (V.humo || []).concat(ctx.fxHumo ? [ctx.fxHumo] : []); let k = 0;
  em.forEach((e, j) => { for (let i = 0; i < (V.humoDenso ? 14 : 9) && k < HUMO.length; i++, k++) { const per = 4.5, f = ((t / per + i / 9 + j * 0.37) % 1); const m = HUMO[k]; m.position.set(e[0] + f * 22 + Math.sin(f * 6 + i) * 4, e[1] + f * 90, e[2] + Math.cos(f * 5 + i) * 3); m.scale.setScalar(3 + f * 14); m.visible = true; } });
  hm.color.set(noche ? "#5a5866" : "#d8d4cc");
  for (; k < HUMO.length; k++) HUMO[k].visible = false;
  // hojas cayendo
  HOJAS.forEach((h, i) => { if (!V.hojas || nm === "interior") { h.visible = false; return; } const per = 6 + rnd(i) * 4, f = ((t / per + rnd(i + 1)) % 1); h.position.set(ctx.foco.x + (rnd(i + 2) - 0.5) * 220 + Math.sin(f * 9 + i) * 10, ctx.foco.y + 110 - f * 120, ctx.foco.z + (rnd(i + 3) - 0.5) * 160); h.rotation.set(f * 12 + i, f * 7, f * 5); h.visible = true; });
  // luciérnagas / polvo flotando en el laberinto
  const oro = !noche && !V.polvo && ["dia", "tarde", "amanecer"].includes(nm) && set !== "mapa";
  if (oro) { const fw = v3(0, 0, -1).applyQuaternion(cam.quaternion), rt = v3(1, 0, 0).applyQuaternion(cam.quaternion);
    LUCI.forEach((l, i) => { const dd = 20 + rnd(i) * 90, a = t * 0.25 + i * 1.3; const P = cam.position.clone().addScaledVector(fw, dd).addScaledVector(rt, (rnd(i + 1) - 0.5) * dd * 1.1 + Math.sin(a) * 3); P.y += (rnd(i + 2) - 0.5) * dd * 0.6 + Math.sin(a * 1.4) * 2 + ((t * 1.5 + i * 3) % 12) - 6; l.position.copy(P); l.material.color.set(nm === "dia" ? "#fff0b0" : "#ffc860"); l.scale.setScalar((0.18 + 0.2 * rnd(i + 3)) * (0.6 + 0.4 * Math.sin(t * 2 + i)) * (dd / 40)); l.visible = true; }); }
  else LUCI.forEach((l, i) => { const on = (V.luciernagas && noche) || (V.polvo); if (!on) { l.visible = false; return; } const a = t * 0.3 + i; l.position.set(ctx.foco.x + (rnd(i) - 0.5) * 240 + Math.sin(a) * 8, ctx.foco.y + 6 + rnd(i + 1) * 60 + Math.sin(a * 1.3) * 5, ctx.foco.z + (rnd(i + 2) - 0.5) * 200); l.material.color.set(V.polvo ? "#c8c0a8" : "#fff27a"); l.scale.setScalar(V.polvo ? 0.5 : (0.6 + 0.6 * Math.max(0, Math.sin(t * 3 + i * 2)))); l.visible = true; });
  // delfines
  DELF.forEach((d, i) => { if (!V.delfines) { d.visible = false; return; } const per = 5 + i, f = ((t + i * 1.7) % per) / per; if (f > 0.35) { d.visible = false; return; } const q = f / 0.35; d.position.set(F.x - 120 + i * 90 + q * 60, -8 + Math.sin(q * Math.PI) * 26, F.z - 160 - i * 60); d.rotation.x = -Math.cos(q * Math.PI) * 0.9; d.rotation.y = Math.PI / 2; d.visible = true; });
  // paseantes
  const paths = (V.aldeanos && V.aldeanosOn !== 0 && nm !== "interior") ? V.aldeanos : [];
  EXTRAS.forEach((ch, i) => { const pth = paths[i % Math.max(1, paths.length)]; if (!paths.length || i >= paths.length * 3) { ch.root.visible = false; return; }
    const len = Math.hypot(pth[2] - pth[0], pth[3] - pth[1]), per = len / 14 * 2, f = ((t / per + i * 0.43) % 1), ida = f < 0.5, q = ida ? f * 2 : 2 - f * 2;
    const x = lerp(pth[0], pth[2], q), z = lerp(pth[1], pth[3], q) + (Math.floor(i / paths.length) * 22 - 11) * (i >= paths.length ? 1 : 0); const ry = ang((pth[2] - pth[0]) * (ida ? 1 : -1), (pth[3] - pth[1]) * (ida ? 1 : -1));
    pose(ch, { x, z, ry, andar: q * len / 5.5, amp: 1, seed: i }, t); cara(ch, Math.sin(t * 0.5 + i) > 0.6 ? "risa" : "normal"); ch.root.visible = true; });
}

// ------------------------------------------------------------------ rótulos (DOM)
const $ = id => document.getElementById(id);
function rotulos(t, p, ctx) {
  // título
  const ti = $("titulo"); if (p.ov === "titulo") { const lt = t - p.s0; ti.style.display = "flex"; const q = back(cl(lt / 0.45), 2.2); ti.style.transform = `scale(${0.3 + 0.7 * q}) rotate(${(1 - q) * -8}deg)`; ti.style.opacity = cl(lt / 0.2) * (1 - cl((lt - (p.s1 - p.s0) + 0.35) / 0.35)); $("sub").style.opacity = cl((lt - 0.8) / 0.4); } else ti.style.display = "none";
  // capítulo
  const c = L.caps.find(c => t >= c.t && t < c.t + 3.4), ca = $("cap");
  if (c) { const lt = t - c.t, ent = eout(cl(lt / 0.35)), sal = cl((lt - 3.0) / 0.4); ca.style.display = "block"; ca.style.transform = `translateX(${(-1 + ent) * 700 - sal * 700}px)`; $("capn").textContent = "CAPÍTULO " + c.n; $("capt").textContent = c.tit; } else ca.style.display = "none";
  // spoiler
  const so = $("spoiler"); if (p.ov === "spoiler") { const lt = t - p.s0, q = back(cl((lt - 0.25) / 0.25), 3); so.style.display = "block"; so.style.transform = `translate(-50%,-50%) rotate(-12deg) scale(${2.2 - 1.2 * q})`; so.style.opacity = cl((lt - 0.25) / 0.1); } else so.style.display = "none";
  // suscríbete
  const su = $("suscribete"); if (p.ov === "suscribete") { const lt = t - p.s0, d = p.s1 - p.s0, q = back(cl((lt - d * 0.12) / 0.4), 2); su.style.display = "flex"; su.style.transform = `translateX(-50%) scale(${Math.max(0.01, q)})`; const cl2 = Math.floor((lt - d * 0.12 - 1.2) / 0.6); $("campana").style.transform = `rotate(${lt > d * 0.12 + 0.6 ? 18 * Math.sin(lt * 14) : 0}deg)`; $("boton").classList.toggle("pulsado", lt > d * 0.12 + 1.2 && lt < d * 0.12 + 1.6); $("prox").style.opacity = cl((lt - d * 0.45) / 0.4); } else su.style.display = "none";
  // etiquetas del mapa
  const et = $("etiquetas"); et.innerHTML = "";
  if (p.set === "mapa") { const sp = spotDe(p), lt = t - p.s0; const labs = [["ATENAS", "atenas"], ["CRETA", "creta"], ["NAXOS", "naxos"]]; if (p.mapa === "egeo") labs.push(["MAR EGEO", "egeo"]);
    labs.forEach(([txt, k], i) => { const q = sp.pts[k]; const v = v3(q[0], q[1], q[2]).project(cam); if (v.z > 1) return; const d = document.createElement("div"); d.className = "etq" + (k === "egeo" ? " grande" : ""); d.textContent = txt; const s = k === "egeo" ? back(cl((lt - 0.6) / 0.5), 2) : back(cl((lt - i * 0.25) / 0.35), 2); d.style.left = ((v.x + 1) / 2 * W) + "px"; d.style.top = ((1 - v.y) / 2 * H) + "px"; d.style.transform = `translate(-50%,-50%) scale(${s})`; et.appendChild(d); }); }
}

// ------------------------------------------------------------------ precálculo de efectos con posición
function chestPos(a, sp, u = 0) { const to = a.to || [a.x, a.z]; const q = cl(u); return v3(sp.x + lerp(a.x, to[0], q), sp.y + 20 * (SK[a.n] ? SK[a.n][1] : 1), sp.z + lerp(a.z, to[1], q)); }
const PEV = [], SEV = [], SHAKES = [], FLASH = [];
const vistos = new Set();
for (const p of PL) { if (p.sub) continue; const sp = spotDe(p), d = p.s1 - p.s0;
  for (const [nm, ta] of p.fxa) { const key = nm + ta.toFixed(2); if (vistos.has(key)) continue; vistos.add(key); const u = (ta - p.s0) / d;
    const acts = p.act; const a0 = acts[0], a1 = acts[1];
    let P = a0 ? chestPos(a0, sp, u) : v3(sp.x, sp.y + 20, sp.z);
    if (a0 && a1 && (nm === "golpe")) P = chestPos(a0, sp, u).add(chestPos(a1, sp, u)).multiplyScalar(0.5);
    const lanz = acts.find(a => a.acc === "lanzado" || a.acc === "caer_acantilado");
    if (nm === "salpicar_mar" && lanz) { const to = lanz.acc === "lanzado" ? lanz.to : [lanz.x + 52, lanz.z]; P = v3(sp.x + to[0], (lanz.y2 ?? -170) + sp.y - 4, sp.z + to[1]); }
    if (nm === "muro" && sp.pts.muro) { const q = sp.pts.muro; P = v3(q[0], q[1], q[2]); }
    if (nm === "polvo" && a0) P.y = sp.y + 2;
    if (nm === "vapor" && a0) { const q = chestPos(a0, sp, u); const sc = SK[a0.n] ? SK[a0.n][1] : 1; P = v3(q.x + Math.sin(a0.ry * D) * 9 * sc, sp.y + 33 * sc, q.z + Math.cos(a0.ry * D) * 9 * sc); }
    if ((nm === "veneno" || nm === "veneno_suelo" || nm === "copa_vuela") && sp.pts.copa) { /* posición junto a la mano */ P = chestPos(a0, sp, u); P.y += 4; }
    const T0 = { t: ta, x: P.x, y: P.y, z: P.z };
    switch (nm) {
      case "polvo": PEV.push({ ...T0, n: 40, cols: FXC.polvo, v: 30, sz: 1.4, y0: sp.y + 0.8 }); break;
      case "golpe": PEV.push({ ...T0, n: 26, cols: FXC.golpe, v: 40, sz: 1, dur: 0.8 }); SHAKES.push([ta, 0.3, 3]); break;
      case "bloques": PEV.push({ ...T0, n: 70, cols: FXC.bloques, v: 55, sz: 1.6, y0: sp.y + 0.8 }); break;
      case "muro": PEV.push({ ...T0, n: 60, cols: FXC.muro, v: 45, sz: 2.2, y0: sp.y + 0.8 }); break;
      case "salpicar_mar": PEV.push({ ...T0, n: 60, cols: FXC.salpicar_mar, v: 40, sz: 1.6 }); break;
      case "hojas": PEV.push({ ...T0, y: sp.y + 90, n: 50, cols: FXC.hojas, v: 40, sz: 1.4, dur: 2.2 }); break;
      case "veneno": PEV.push({ ...T0, n: 20, cols: FXC.veneno, v: 6, sz: 0.8, tipo: "chorro", dur: 1.2 }); break;
      case "chispas_moradas": PEV.push({ ...T0, n: 50, cols: FXC.chispas_moradas, v: 10, sz: 0.8, tipo: "sube", dur: 2.4 }); break;
      case "chispas_doradas": PEV.push({ ...T0, n: 60, cols: FXC.chispas_doradas, v: 10, sz: 0.8, tipo: "sube", dur: 2.6 }); break;
      case "brillo": PEV.push({ ...T0, n: 16, cols: FXC.brillo, v: 14, sz: 0.7, dur: 0.9 }); break;
      case "vapor": PEV.push({ ...T0, n: 18, cols: FXC.vapor, v: 7, sz: 1.1, dur: 0.9, y0: -999 }); break;
      case "corazones": SEV.push({ ...T0, y: T0.y + 14, n: 8, ico: "corazon", sz: 8, dur: 2.2 }); break;
      case "estrellas": SEV.push({ ...T0, y: T0.y + 18, n: 4, ico: "estrella", sz: 6, dur: 1.8 }); break;
      case "zzz": SEV.push({ ...T0, y: T0.y + 4, n: 2, ico: "zzz", sz: 9, dur: (p.s1 - ta) }); break;
      case "temblor": SHAKES.push([ta, 0.45, 5]); break;
      case "flash": FLASH.push([ta, 0.25]); SHAKES.push([ta, 0.5, 6]); break;
      case "trueno": FLASH.push([ta, 0.18]); break;
      case "zoom": break;
    }
  } }

// ------------------------------------------------------------------ pintar(t)
const tmp = new THREE.Vector3();
function pintar(t) {
  let i = PL.findIndex(q => t >= q.t0 && t < q.t1); if (i < 0) i = PL.length - 1;
  const p = PL[i], S = SETS[p.set], sp = spotDe(p);
  const lt = t - p.s0, d = p.s1 - p.s0, tAcc = p.congelar ? p.s0 + 0.35 : t, ltA = tAcc - p.s0;
  for (const n in SETS) SETS[n].g.visible = n === p.set;
  // objetos del set
  S.g.traverse(o => { if (o.name === "mesa") o.visible = p.spot === "banquete"; if (o.name === "roca") o.visible = !(p.ocultar || []).includes("roca"); if (o.name === "espada_suelo" || o.name === "sandalias") o.visible = (p.mostrar || []).includes("espada_suelo"); });
  if (S.pinos) { const dob = p.pinos === "doblados" ? 1 : (p.pinos === "soltar" ? 1 - seg(lt / d, 0.15, 0.3, eout) + muelleP(lt - d * 0.3) : 0); S.pinos[0].rotation.z = -1.0 * dob; S.pinos[1].rotation.z = 1.0 * dob; }
  if (S.tortuga) { const sa = Math.max(0, Math.sin(t * 1.1)); S.tortuga.cab.position.z = 40 + 6 * sa; S.tortuga.cab.rotation.x = -0.2 * sa; S.tortuga.g.position.y = -150 + Math.sin(t * 1.5) * 1.5; }
  if (S.puertaLab) { const fxp = p.fxa.find(f => f[0] === "puerta"); const cerr = fxp ? seg(t, fxp[1], fxp[1] + 0.6, eout) : 0; S.puertaLab.position.x = S.ox + 1500 + 44 * (1 - cerr); }
  if (S.ruta) { const vis = (p.mapa === "ruta" || p.mapa === "egeo") ? cl((lt - 0.3) / (d - 0.8)) : 0; S.ruta.forEach((m, k) => m.visible = k / S.ruta.length < vis); const bm = S.barcoMapa; bm.g.visible = p.mapa === "ruta" || p.mapa === "egeo"; if (bm.g.visible) { const [P0, P1, P2] = S.rutaPts, u = vis, a = u < 0.5 ? u * 2 : 1, b = u < 0.5 ? 0 : (u - 0.5) * 2; const x = u < 0.5 ? lerp(P0[0], P1[0], a) : lerp(P1[0], P2[0], b), z = u < 0.5 ? lerp(P0[1], P1[1], a) : lerp(P1[1], P2[1], b); bm.g.position.set(S.ox + x, -2, z); bm.g.rotation.y = u < 0.5 ? Math.atan2(P1[1] - P0[1], -(P1[0] - P0[0])) * 0 + -Math.atan2(P1[1] - P0[1], P1[0] - P0[0]) : -Math.atan2(P2[1] - P1[1], P2[0] - P1[0]); bm.velaM.material = MAT.telaNegra; } }
  // barcos
  BARCO.g.visible = false; BARCO2.g.visible = false;
  if (p.barco || sp.barco) { const [bx, by, bz, br] = shipPos(p); let mx = 0; if (p.barco_mueve) mx = -seg(lt / d, 0.35, 1, x => x * x) * 300; BARCO.g.position.set(bx + mx, by + 1.2 * Math.sin(t * 1.4), bz); BARCO.g.rotation.set(0, br, 0.03 * Math.sin(t * 1.1)); BARCO.g.visible = !!(p.barco || sp.navega || p.set === "naxos" && p.barco); BARCO.velaM.material = p.barco === "blancas" ? MAT.tela : MAT.telaNegra; BARCO.vela.scale.z = 1 + 0.15 * Math.sin(t * 2); BARCO.vela.position.z = 2 + 3 * Math.sin(t * 2); }
  if (p.barco_lejos && sp.barcoLejos) { const b = sp.barcoLejos; const q = cl(lt / d); BARCO.g.position.set(S.ox + b[0] - 200 * q, b[1] + Math.sin(t * 1.4), b[2]); BARCO.g.rotation.set(0, Math.PI, 0.03 * Math.sin(t)); BARCO.g.visible = true; BARCO.velaM.material = MAT.telaNegra; }
  // actores
  for (const n of HOR) { CAST[n].root.visible = false; ocultaProps(CAST[n]); CAST[n].ico.visible = false; }
  CARRO.g.visible = false;
  const ctx = { sp, pos: {}, foco: v3(sp.x, sp.y, sp.z), idx: i };
  let montar = null;
  for (const a of p.act) { const ch = CAST[a.n]; if (!ch) continue;
    const { p: q, e } = accion(a, ltA, d, tAcc);
    // coordenadas del spot / cubierta del barco
    let ox = sp.x, oy = sp.y, oz = sp.z, rot = 0;
    if (a.y === "cubierta") { const [bx, by, bz, br] = [BARCO.g.position.x, BARCO.g.position.y, BARCO.g.position.z, BARCO.g.rotation.y]; ox = bx; oy = by + 13; oz = bz; q.z = cl(q.z, -14, 14); rot = br; q.x *= 0.8; }
    const lx = q.x, lz = q.z; q.x = ox + lx * Math.cos(rot) + lz * Math.sin(rot); q.z = oz - lx * Math.sin(rot) + lz * Math.cos(rot); q.y = oy + (typeof q.y === "number" ? q.y : (typeof a.y === "number" && !["sentado", "tumbado", "bebe"].includes(a.acc) ? a.y : 0)); q.ry = (q.ry || 0) + rot / D;
    pose(ch, q, tAcc); if (q.sc) ch.root.scale.setScalar(SK[a.n][1] * q.sc); else ch.root.scale.setScalar(SK[a.n][1]);
    if (a.sc) ch.root.scale.set(SK[a.n][1] * a.sc[0], SK[a.n][1] * a.sc[1], SK[a.n][1] * a.sc[2]);
    // parpadeo
    let ex = e; if (["normal", "enfado", "triste", "sorpresa", "sudor", "aburrido", "malvado"].includes(ex) && ((tAcc + a.n.length * 0.7) % 3.3) < 0.11) ex = "cerrados";
    cara(ch, ex); ch.root.visible = true;
    if (a.prop) { const pr = prop(ch, a.prop === "espada_cinto" ? "espada_cinto" : a.prop); pr.visible = true; if (a.prop === "espada_cinto") { ch.aR.mano.remove(pr); ch.torso.add(pr); pr.position.set(-4.6, 5, 1); pr.rotation.set(0, 0, 0.3); } else if (a.prop === "roca") { pr.position.set(6, -2, 0); } else if (["espada", "maza"].includes(a.prop)) pr.rotation.set(-Math.PI / 2, 0, 0); else if (a.prop === "antorcha") pr.rotation.set(Math.PI / 2, 0, 0); }
    if (a.acc === "lanza") { const pr = prop(ch, "lanza"); pr.visible = true; pr.rotation.x = Math.PI / 2; }
    if (a.prop2) { const pr = prop(ch, a.prop2, "L"); pr.visible = true; }
    if (a.ico && a.ico !== "corona") { ch.ico.material.map = texIcono(a.ico === "?" ? "?" : "!"); ch.ico.material.needsUpdate = true; ch.ico.visible = ltA > 0.15 && ltA < 2.6; ch.ico.position.y = 46 + 2 * Math.sin(tAcc * 6); ch.ico.quaternion.copy(cam.quaternion); ch.ico.scale.setScalar(back(cl((ltA - 0.15) / 0.25), 2.5) + 0.001); }
    if (a.ico === "corona" && !ch.sp.corona) { if (!ch.props.corona) { const cg = new THREE.Group(); for (const [x, z] of [[-3, 3], [0, 3.4], [3, 3], [-3.4, 0], [3.4, 0], [-3, -3], [0, -3.4], [3, -3]]) cg.add(caja(1.6, 2.4, 1.6, MAT.oro, x, 9.2, z)); cg.add(caja(8.6, 1, 8.6, MAT.oro, 0, 8.2, 0)); ch.cuello.add(cg); ch.props.corona = cg; } ch.props.corona.visible = true; }
    if (a.acc === "volar_carro") { CARRO.g.visible = true; CARRO.g.position.set(q.x, q.y - 7, q.z); CARRO.g.rotation.y = q.ry * D; CARRO.alas.forEach(([al, w], k) => al.rotation.z = w * 0.6 * Math.sin(tAcc * 12 + k)); }
    ch.root.updateMatrixWorld(true);
    const alto = 28 * SK[a.n][1] * (a.sc ? a.sc[1] : 1) * ((a.acc === "sentado" || a.acc === "arrodillado") ? 0.82 : 1) * (a.n === "bebe" ? 1.6 : 1);
    const info = { p: v3(ch.root.position.x, q.y - (["sentado", "tumbado", "dormir", "lanzado", "caer_acantilado", "volar_carro"].includes(a.acc) ? 0 : 0), ch.root.position.z), ry: q.ry, alto: ["tumbado", "dormir"].includes(a.acc) ? 6 : alto, mano: ch.aR.mano.getWorldPosition(new THREE.Vector3()) };
    if (a.acc === "lanzado" || a.acc === "caer_acantilado" || a.acc === "volar_carro") info.p.y = Math.max(q.y, -150);
    if (a.prop2 === "ovillo" || a.prop === "ovillo") info.ovillo = (a.prop2 === "ovillo" ? ch.aL : ch.aR).mano.getWorldPosition(new THREE.Vector3());
    ctx.pos[a.n] = info; if (Object.keys(ctx.pos).length === 1) ctx.foco.copy(info.p);
    if (a.acc === "montar") montar = a;
    // hilo rojo
    if (a.hilo && S.hilo) { const ini = v3(S.ox - 660, 2, 0), fin = ch.aL.mano.getWorldPosition(new THREE.Vector3()); const mid = ini.clone().add(fin).multiplyScalar(0.5); S.hilo.position.copy(mid); S.hilo.scale.set(ini.distanceTo(fin), 1, 1); S.hilo.lookAt(fin); S.hilo.rotateY(Math.PI / 2); S.hilo.visible = true; }
  }
  if (S.hilo && !p.act.some(a => a.hilo)) S.hilo.visible = false;
  if (montar && ctx.pos.minotauro) { const mi = CAST.minotauro, te = CAST.teseo, mp = ctx.pos.minotauro.p; pose(te, { x: mp.x, y: mp.y + 30, z: mp.z - 8, ry: 0, pR: -70, pL: -70, kR: 60, kL: 60, bR: [-150 + 40 * Math.sin(tAcc * 9), -20], cR: 20, bL: [-80, 10], cL: 30, lean: 10, ladeo: mi.torso.rotation.z / D * 0.8 }, tAcc); te.root.visible = true; ctx.pos.teseo = { p: v3(mp.x, mp.y + 30, mp.z - 8), ry: 0, alto: 28, mano: te.aR.mano.getWorldPosition(new THREE.Vector3()) }; }
  // efectos derivados de acciones
  ctx.zoom = 1; const zf = p.fxa.find(f => f[0] === "zoom"); if (zf) ctx.zoom = 1 - 0.25 * seg(t, zf[1], zf[1] + 0.18, eout);
  ctx.fxHumo = p.fxa.some(f => f[0] === "humo_tripode") && sp.pts.tripode ? sp.pts.tripode : null;
  // copa que vuela / charco de veneno
  COPA.visible = false; CHARCO.visible = false;
  const cv = p.fxa.find(f => f[0] === "copa_vuela"); if (cv && ctx.pos.egeo) { const lq = t - cv[1]; if (lq > 0 && lq < 1.2) { const m = ctx.pos.egeo.mano; COPA.position.set(m.x - 30 * lq, m.y + 30 * lq - 60 * lq * lq, m.z + 20 * lq); COPA.rotation.set(lq * 12, lq * 5, 0); COPA.visible = COPA.position.y > 1; } }
  const vs = p.fxa.find(f => f[0] === "veneno_suelo") || (PL[i].tx && PL[i].tx.startsWith("Le tiró") ? null : null); if (vs) { const q = seg(t, vs[1], vs[1] + 1.2, eout); CHARCO.visible = q > 0; const c = ctx.pos.egeo ? ctx.pos.egeo.p : ctx.foco; CHARCO.position.set(c.x - 24, 0.3, c.z + 14); CHARCO.scale.set(4 + 30 * q, 1, 3 + 22 * q); }
  // rayos de luz
  const ry = p.fxa.find(f => f[0] === "rayos"); RAYOS.forEach((r, k) => { r.visible = !!ry; if (ry) { const c = ctx.foco; r.position.set(c.x + (k - 2.5) * 22, c.y + 150, c.z - 30 + (k % 2) * 20); r.rotation.set(0, 0.3 * k, 0.18 - 0.06 * k); r.material.opacity = 0.12 + 0.06 * Math.sin(t * 2 + k); } });
  // cámara
  let shake = 0; for (const [ts, du, am] of SHAKES) { const q = t - ts; if (q > 0 && q < du) shake = Math.max(shake, am * (1 - q / du)); }
  if (p.cam1.startsWith("contra") && p.act.some(a => a.acc === "embestir")) shake = Math.max(shake, 1.5);
  const nm = p.luz || sp.luz || S.luz;
  const cr = camara(p.cam1, ctx, t - p.t0, p.t1 - p.t0, t, shake);
  ctx.foco = cr.F;
  luces(nm, t, cr.F, p.set);
  // antorcha en mano: luz
  const ant = p.act.find(a => a.prop === "antorcha"); if (ant && ctx.pos[ant.n]) { const m = ctx.pos[ant.n].mano; vela2.position.set(m.x, m.y + 12, m.z); vela2.intensity = 1500 * (1 + 0.1 * Math.sin(t * 21)); CAST[ant.n].props.antorchaR?.traverse(o => { if (o.name === "llama") o.scale.y = 1 + 0.3 * Math.sin(t * 19); }); } else vela2.intensity = 0;
  { const R = RIM[nm] || RIM.dia, F = cr.F, dv = F.clone().sub(cam.position); dv.y = 0; dv.normalize(); rim.color.set(R[0]); rim.intensity = R[1]; rim.position.set(F.x + dv.x * 300, F.y + 150, F.z + dv.z * 300); rim.target.position.copy(F); rim.target.updateMatrixWorld(); }
  vida(t, p.set, sp, nm, ctx);
  particulas(t, PEV); sprites(t, SEV);
  // primer plano (capa delantera)
  const ext = !["interior", "mapa"].includes(nm) && p.set !== "mapa" && !["cenital", "paisaje", "picado"].includes(cr.tipo) && cam.position.y < sp.y + 70 && p.set !== "mar";
  FG.forEach((g, k) => { g.visible = ext && k < 2; if (!g.visible) return; const lado = k ? 1 : -1, dd = 22, hh = Math.tan(cam.fov * D / 2) * dd, ww = hh * W / H;
    const tp = p.set === "laberinto" ? (k ? "helecho" : "hueso") : (p.set === "naxos" ? "arbusto" : (["camino", "delfos", "atenas"].includes(p.set) ? (k ? "seca" : "arbusto") : (k ? "helecho" : "hierba")));
    g.children.forEach(c => { c.material = texPlanta(tp); });
    tmp.set(lado * ww * 0.88, -hh * 0.9, -dd); g.position.copy(cam.localToWorld(tmp.clone())); g.quaternion.copy(cam.quaternion); g.scale.setScalar(hh * 0.5 * (1 + 0.04 * Math.sin(t * 1.7 + k))); });
  // destello
  let fl = 0; for (const [ts, du] of FLASH) { const q = t - ts; if (q > 0 && q < du) fl = Math.max(fl, 1 - q / du); }
  $("flash").style.opacity = fl;
  rotulos(t, p, ctx);
  if (!window.NORENDER) renderer.render(scene, cam);
}
function muelleP(x) { return x < 0 ? 0 : 0.25 * Math.sin(x * 14) * Math.exp(-x * 5); }
window.pintar = pintar; window.PL = PL; window.__cam = (x, y, z, a, b2, c) => { cam.position.set(x, y, z); cam.lookAt(a, b2, c); renderer.render(scene, cam); }; window.__dbg = () => ({ etq: document.getElementById("etiquetas").innerHTML.slice(0, 300), cam: cam.position.toArray().map(Math.round), fov: cam.fov, egeo: CAST.egeo.root.position.toArray().map(Math.round), vis: CAST.egeo.root.visible, sc: CAST.egeo.root.scale.x });
const rc = new THREE.Raycaster();
window.__tapado = (i) => { const p = PL[i], S = SETS[p.set], U = window.__ult, fo = U.foco.split(","); const objs = [];
  S.g.traverse(o => { if ((o.isMesh || o.isInstancedMesh) && !o.userData.planta && o.visible !== false && !(o.material && o.material.transparent)) objs.push(o); });
  for (const n of HOR) if (CAST[n].root.visible && !fo.includes(n)) objs.push(CAST[n].root);
  if (BARCO.g.visible && U.foco !== "barco") objs.push(BARCO.g);
  const mats = new Map(); for (const o of objs) o.traverse(q => { if (q.material && !Array.isArray(q.material) && !mats.has(q.material)) mats.set(q.material, q.material.side); });
  for (const m of mats.keys()) m.side = THREE.DoubleSide;
  const dir = U.pos.clone().sub(U.tgt), L0 = dir.length(); dir.normalize(); rc.set(U.tgt, dir); rc.far = L0 + 3;
  const esActor = !!CAST[fo[0]]; let hs = [];
  const rgt = v3(1, 0, 0).applyQuaternion(cam.quaternion), up = v3(0, 1, 0).applyQuaternion(cam.quaternion);
  for (const off of [[0, 0], [9, 0], [-9, 0], [0, 6]]) { const P = U.pos.clone().addScaledVector(rgt, off[0]).addScaledVector(up, off[1]); const dv = P.clone().sub(U.tgt), Lp = dv.length(); dv.normalize(); rc.set(U.tgt, dv); rc.far = Lp + 3;
    hs = hs.concat(rc.intersectObjects(objs, true).filter(h => h.distance > (esActor ? 3 : Math.min(14, L0 * 0.3)) && h.distance > Lp * 0.5 && h.object.visible && !h.object.userData.planta)); if (off[0] === 0 && off[1] === 0) hs = hs.concat([]); }
  for (const [m, sd] of mats) m.side = sd;
  // ¿hay algún objeto en la línea o a < 6 de la cámara?
  return hs.length ? Math.round(hs[0].distance) : 0; };
window.__buscaCam = (i) => { const p = PL[i]; window.NORENDER = 1; const offs = [0, 35, -35, 70, -70, 110, -110, 150, -150, 180]; let best = 0, bestMal = 1e9;
  for (const o of offs) { CAMOFF[i] = o; let mal = 0; for (const u of [0.05, 0.35, 0.65, 0.95]) { pintar(p.t0 + u * (p.t1 - p.t0) - 0.001 + 0.002); if (window.__tapado(i)) mal++; } if (mal < bestMal) { bestMal = mal; best = o; } if (!mal) break; }
  CAMOFF[i] = best; window.NORENDER = 0; return [best, bestMal]; };
window.__T = { CAST, SETS, scene, pose, cara, cam, renderer, prop, ocultaProps, THREE, hemi, sol, rim, EXTRAS, BARCO, BARCO2, CARRO, LUCI, PART, SPR, HUMO, NUBES, AVES, FG, estrellas, luna };
pintar(0); window.LISTO = 1;
