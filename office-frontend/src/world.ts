export type Dir = "up" | "down" | "left" | "right";
export type AgentStatus = "idle" | "working" | "blocked";

export interface Point {
  x: number;
  y: number;
}

export class OfficeMapError extends Error {}
export class OfficeWorldError extends Error {}

export const TILE_SIZE = 16;

/**
 * Leyenda: # pared, W ventana, M pizarra, B estanteria, d escritorio, P planta,
 * T mesa, . suelo, r alfombra, s silla (puesto), X puerta. Se pisan . r s X.
 */
const DESK_XS = [3, 8, 13, 18, 23]
const WIDTH = 28

function buildLayout(): readonly string[] {
  const blank = '#' + '.'.repeat(WIDTH - 2) + '#'
  const wall = '#'.repeat(WIDTH)
  const put = (row: string, x: number, str: string) => row.slice(0, x) + str + row.slice(x + str.length)
  const rows: string[] = Array.from({ length: 15 }, () => blank)
  rows[0] = put(put(put(put(wall, 5, 'WW'), 12, 'MM'), 17, 'WW'), 23, 'WW')
  rows[1] = put(put(blank, 1, 'BB'), WIDTH - 3, 'BB')
  for (const [deskY, seatY] of [[3, 4], [8, 9]] as const) {
    let desk = blank
    let seat = blank
    for (const x of DESK_XS) {
      desk = put(desk, x, 'dd')
      seat = put(seat, x, 's')
    }
    rows[deskY] = desk
    rows[seatY] = seat
  }
  rows[6] = put(put(blank, 1, 'P'), WIDTH - 2, 'P')
  rows[10] = put(blank, 10, 'rrrrrr')
  rows[11] = put(blank, 10, 'rTTTTr')
  rows[12] = put(blank, 10, 'rTTTTr')
  rows[13] = put(put(put(blank, 1, 'P'), WIDTH - 2, 'P'), 10, 'rrrrrr')
  rows[14] = put(wall, 7, 'XX')
  return rows
}

export const OFFICE_LAYOUT: readonly string[] = buildLayout()


const WALKABLE = new Set([".", "s", "X", "r"]);
const DELTAS: Record<Dir, Point> = {
  up: { x: 0, y: -1 },
  down: { x: 0, y: 1 },
  left: { x: -1, y: 0 },
  right: { x: 1, y: 0 },
};

export interface TileMap {
  width: number;
  height: number;
  rows: readonly string[];
}

export function parseLayout(rows: readonly string[]): TileMap {
  const first = rows[0];
  if (!first) throw new OfficeMapError("El mapa no tiene filas.");
  rows.forEach((row, y) => {
    if (row.length !== first.length) {
      throw new OfficeMapError(`La fila ${y} mide ${row.length}, se esperaba ${first.length}.`);
    }
  });
  return { width: first.length, height: rows.length, rows };
}

export function tileAt(map: TileMap, x: number, y: number): string | undefined {
  return map.rows[y]?.[x];
}

export function isWalkable(map: TileMap, x: number, y: number): boolean {
  const tile = tileAt(map, x, y);
  return tile !== undefined && WALKABLE.has(tile);
}

export function findSeats(map: TileMap): Point[] {
  const seats: Point[] = [];
  map.rows.forEach((row, y) => {
    [...row].forEach((tile, x) => {
      if (tile === "s") seats.push({ x, y });
    });
  });
  return seats;
}

const key = (p: Point): string => `${p.x},${p.y}`;

/** BFS en 4 direcciones. Devuelve los pasos sin incluir el origen; [] si no hay ruta. */
export function findPath(
  map: TileMap,
  from: Point,
  to: Point,
  isBlocked: (p: Point) => boolean = () => false,
): Point[] {
  if (from.x === to.x && from.y === to.y) return [];
  if (!isWalkable(map, to.x, to.y) || isBlocked(to)) return [];
  const prev = new Map<string, Point | null>([[key(from), null]]);
  const queue: Point[] = [from];
  for (let head = 0; head < queue.length; head++) {
    const cur = queue[head] as Point;
    for (const d of Object.values(DELTAS)) {
      const next = { x: cur.x + d.x, y: cur.y + d.y };
      if (prev.has(key(next)) || !isWalkable(map, next.x, next.y) || isBlocked(next)) continue;
      prev.set(key(next), cur);
      if (next.x === to.x && next.y === to.y) {
        const path: Point[] = [];
        for (let p: Point | null = next; p && key(p) !== key(from); p = prev.get(key(p)) ?? null) path.unshift(p);
        return path;
      }
      queue.push(next);
    }
  }
  return [];
}

export interface AgentSeed {
  id: string;
  name: string;
  role: string;
  status: AgentStatus;
  task: string | null;
}

export interface Mover {
  x: number;
  y: number;
  dir: Dir;
  from: Point | null;
  progress: number;
  walkFrame: number;
}

export interface OfficeAgent extends AgentSeed {
  seat: Point;
  mover: Mover;
  path: Point[];
  waitMs: number;
}

export interface WorldOptions {
  rng?: () => number;
  stepMs?: number;
  wander?: boolean;
}

const newMover = (p: Point, dir: Dir): Mover => ({ x: p.x, y: p.y, dir, from: null, progress: 0, walkFrame: 0 });

export class OfficeWorld {
  readonly map: TileMap;
  readonly agents: OfficeAgent[];
  readonly player: Mover;
  private readonly rng: () => number;
  private readonly stepMs: number;
  private readonly wander: boolean;
  private readonly wanderTiles: Point[];

  constructor(map: TileMap, seeds: readonly AgentSeed[], options: WorldOptions = {}) {
    const seats = findSeats(map);
    if (seeds.length > seats.length) {
      throw new OfficeWorldError(`Hay ${seeds.length} agentes y solo ${seats.length} puestos.`);
    }
    this.map = map;
    this.rng = options.rng ?? Math.random;
    this.stepMs = options.stepMs ?? 260;
    this.wander = options.wander ?? false;
    this.wanderTiles = [];
    map.rows.forEach((row, y) => [...row].forEach((t, x) => (t === "." || t === "r") && this.wanderTiles.push({ x, y })));
    this.agents = seeds.map((seed, i) => {
      const seat = seats[i] as Point;
      return { ...seed, seat, mover: newMover(seat, "up"), path: [], waitMs: this.rollWait() };
    });
    this.player = newMover({ x: 8, y: 13 }, "up");
  }

  setStatus(id: string, status: AgentStatus, task: string | null): void {
    const agent = this.agents.find((a) => a.id === id);
    if (!agent) throw new OfficeWorldError(`Agente desconocido: ${id}`);
    agent.status = status;
    agent.task = task;
    agent.path = [];
    agent.waitMs = this.rollWait();
  }

  agentAt(x: number, y: number): OfficeAgent | undefined {
    return this.agents.find((a) => this.occupies(a.mover, x, y));
  }

  /** Agente en el tile que mira el jugador, si lo hay. */
  facingAgent(): OfficeAgent | undefined {
    const d = DELTAS[this.player.dir];
    return this.agentAt(this.player.x + d.x, this.player.y + d.y);
  }

  movePlayer(dir: Dir): boolean {
    const p = this.player;
    if (p.from) return false;
    p.dir = dir;
    const d = DELTAS[dir];
    const target = { x: p.x + d.x, y: p.y + d.y };
    if (!isWalkable(this.map, target.x, target.y) || this.isOccupied(target, p)) return false;
    this.startStep(p, target);
    return true;
  }

  update(dtMs: number): void {
    this.advance(this.player, dtMs);
    for (const agent of this.agents) {
      this.advance(agent.mover, dtMs);
      if (agent.mover.from) continue;
      this.think(agent, dtMs);
    }
  }

  /** Posicion en tiles (fraccional) para dibujar. */
  renderPos(m: Mover): Point {
    if (!m.from) return { x: m.x, y: m.y };
    return { x: m.from.x + (m.x - m.from.x) * m.progress, y: m.from.y + (m.y - m.from.y) * m.progress };
  }

  isSeated(agent: OfficeAgent): boolean {
    return !agent.mover.from && agent.mover.x === agent.seat.x && agent.mover.y === agent.seat.y;
  }

  private think(agent: OfficeAgent, dtMs: number): void {
    const m = agent.mover;
    if (agent.status === "working") {
      if (this.isSeated(agent)) {
        m.dir = "up";
        return;
      }
      if (agent.path.length === 0) {
        agent.path = findPath(this.map, m, agent.seat, (p) => this.isOccupied(p, m));
      }
    } else if (!this.wander) {
      return;
    } else if (agent.path.length === 0) {
      agent.waitMs -= dtMs;
      if (agent.waitMs > 0) return;
      agent.waitMs = this.rollWait();
      const target = this.wanderTiles[Math.floor(this.rng() * this.wanderTiles.length)];
      if (target) agent.path = findPath(this.map, m, target, (p) => this.isOccupied(p, m));
    }
    const next = agent.path[0];
    if (!next) return;
    if (this.isOccupied(next, m)) {
      agent.path = [];
      return;
    }
    agent.path.shift();
    this.startStep(m, next);
  }

  private startStep(m: Mover, target: Point): void {
    m.from = { x: m.x, y: m.y };
    m.dir = target.x > m.x ? "right" : target.x < m.x ? "left" : target.y > m.y ? "down" : "up";
    m.x = target.x;
    m.y = target.y;
    m.progress = 0;
    m.walkFrame = 1 - m.walkFrame;
  }

  private advance(m: Mover, dtMs: number): void {
    if (!m.from) return;
    m.progress += dtMs / this.stepMs;
    if (m.progress >= 1) {
      m.from = null;
      m.progress = 0;
    }
  }

  private occupies(m: Mover, x: number, y: number): boolean {
    return (m.x === x && m.y === y) || (m.from?.x === x && m.from?.y === y);
  }

  private isOccupied(p: Point, self: Mover): boolean {
    if (this.player !== self && this.occupies(this.player, p.x, p.y)) return true;
    return this.agents.some((a) => a.mover !== self && this.occupies(a.mover, p.x, p.y));
  }

  private rollWait(): number {
    return 800 + this.rng() * 2800;
  }
}
