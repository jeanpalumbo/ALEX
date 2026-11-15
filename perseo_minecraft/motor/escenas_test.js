import { personaje, pose, cara } from "./motor.js";
import { scene } from "./mundo.js";
const P0 = personaje({ seed: 5, piel: "#d39a6a", pelo: "#5a3414", ropa: "#3f6fb5", cinto: "#c48a2c", falda: 1 }, 1.1); scene.add(P0.root);
const L = ["cueva_gorgonas","isla_gorgonas","torre","torre_interior","mar_tormenta","playa_serifos","banquete","templo_atenea","cueva_greas","vuelo_nubes","desierto_atlas","acantilado_etiopia","estadio"];
let i = 0; const B = {};
export const E = new Proxy({}, { get: (o, k) => { if (!B[k]) { const s = L[i++ % L.length]; B[k] = { set: s, act(X) { pose(P0, { x: 0, z: 30, andar: X.t * 4, amp: 1 }, X.t); cara(P0, "habla"); }, cams: [() => [0, 50, 230, 0, 30, -40, 42]] }; } return B[k]; } });
export function ocultaTodo() {} export function resetExtras() {} export function setLt() {}
