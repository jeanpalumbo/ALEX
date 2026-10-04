import { useEffect, useRef } from 'react'
import type { OfficeAgent } from './types'
import { OFFICE_LAYOUT, OfficeWorld, TILE_SIZE as T, parseLayout, type Dir } from './world'
import { OUT, characterSprite, drawBubble, drawMonitor, drawUnknown, renderStaticMap, shadowSprite, type Look } from './pixelart'

const map = parseLayout(OFFICE_LAYOUT)
const SCALE = 3
const FONT = '"Press Start 2P", ui-monospace, monospace'

// Acento fijo por agente (no por posicion), segun el diseno: el color no es
// el unico medio para distinguirlos; ademas cada uno tiene nombre y rol.
const LOOKS: Record<string, Look> = {
  ceo: { hair: '#2b2018', skin: '#f1c9a5', shirt: '#3d6fb5', pants: '#2f3a5c' },
  research: { hair: '#a0432b', skin: '#f1c9a5', shirt: '#f2a63a' },
  store_ops: { hair: '#1d1d1d', skin: '#b9825a', shirt: '#4ea05e' },
  engineering_lead: { hair: '#141018', skin: '#c58c64', shirt: '#9a5bc0' },
  finance: { hair: '#5a3a22', skin: '#e8b890', shirt: '#d8453d' },
  marketing: { hair: '#d9a441', skin: '#f5d2b3', shirt: '#3fb0ae' },
  design: { hair: '#2a1b12', skin: '#d9a679', shirt: '#e0709a' },
  rnd: { hair: '#0f0f14', skin: '#a8744f', shirt: '#6f77d8' },
}
const FALLBACKS: Look[] = [
  { hair: '#6b3b8a', skin: '#f1c9a5', shirt: '#d96f8a' },
  { hair: '#1b2b3a', skin: '#c58c64', shirt: '#e0b030' },
]
const OWNER: Look = { hair: '#3a2a22', skin: '#f1c9a5', shirt: '#2b2d4a', pants: '#2b2d4a', cap: true }
const lookFor = (id: string, i: number): Look => LOOKS[id] ?? (FALLBACKS[i % FALLBACKS.length] as Look)

const KEYS: Record<string, Dir> = {
  ArrowUp: 'up', w: 'up', ArrowDown: 'down', s: 'down', ArrowLeft: 'left', a: 'left', ArrowRight: 'right', d: 'right',
}

interface Dialog { name: string; text: string; shown: number }

function wrap(text: string, n: number): string[] {
  const lines: string[] = []
  let cur = ''
  for (const word of text.split(' ')) {
    if ((cur + ' ' + word).trim().length > n) { lines.push(cur); cur = word } else cur = (cur + ' ' + word).trim()
  }
  if (cur) lines.push(cur)
  return lines
}

interface Props {
  agents: OfficeAgent[]
  selectedId: string | null
  /** Sin conexion: se muestra el ultimo estado conocido marcado con "?", nunca como "inactivo". */
  stale: boolean
  onSelect: (agentId: string) => void
}

function say(a: OfficeAgent, stale: boolean): string {
  if (stale) return 'Sin conexion con el backend: este es el ultimo estado conocido, puede estar desactualizado.'
  return a.status === 'working' ? `Trabajando en: ${a.task?.title ?? '(sin detalle)'}` : 'Sin tarea activa.'
}

export function OfficeScene({ agents, selectedId, stale, onSelect }: Props) {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const worldRef = useRef<OfficeWorld | null>(null)
  const agentsRef = useRef<OfficeAgent[]>(agents)
  const selectedRef = useRef<string | null>(selectedId)
  const staleRef = useRef(stale)
  const onSelectRef = useRef(onSelect)
  const dialogRef = useRef<Dialog | null>(null)
  const heldRef = useRef<Dir[]>([])
  useEffect(() => {
    agentsRef.current = agents
    selectedRef.current = selectedId
    staleRef.current = stale
    onSelectRef.current = onSelect
  })

  // El mundo se recrea solo si cambia el conjunto de agentes. Los agentes no
  // se pasean: la oficina representa estado, no una cronologia inventada.
  const idsKey = agents.map((a) => a.agent_id).join('|')
  useEffect(() => {
    const seeds = agentsRef.current.map((a) => ({
      id: a.agent_id, name: a.display_name, role: a.role, status: a.status, task: a.task?.title ?? null,
    }))
    worldRef.current = seeds.length ? new OfficeWorld(map, seeds, { wander: false }) : null
  }, [idsKey])

  useEffect(() => {
    const w = worldRef.current
    if (!w) return
    for (const a of agents) {
      const cur = w.agents.find((x) => x.id === a.agent_id)
      const task = a.task?.title ?? null
      if (cur && (cur.status !== a.status || cur.task !== task)) w.setStatus(a.agent_id, a.status, task)
    }
  }, [agents])

  useEffect(() => {
    const canvas = canvasRef.current
    const ctx = canvas?.getContext('2d')
    if (!canvas || !ctx) return
    canvas.width = map.width * T * SCALE
    canvas.height = map.height * T * SCALE
    const stat = renderStaticMap(map.rows)
    let raf = 0
    let last = performance.now()

    const openDialog = (id: string) => {
      const a = agentsRef.current.find((x) => x.agent_id === id)
      if (!a) return
      onSelectRef.current(id)
      dialogRef.current = { name: `${a.display_name} - ${a.role}`, text: say(a, staleRef.current), shown: 0 }
    }
    const interact = () => {
      const d = dialogRef.current
      if (d && d.shown < d.text.length) d.shown = d.text.length
      else if (d) dialogRef.current = null
      else {
        const f = worldRef.current?.facingAgent()
        if (f) openDialog(f.id)
      }
    }

    const frame = (now: number) => {
      const dt = Math.min(now - last, 100)
      last = now
      const w = worldRef.current
      const dialog = dialogRef.current
      if (w) {
        const held = heldRef.current
        if (!dialog && held.length) w.movePlayer(held[held.length - 1] as Dir)
        w.update(dt)
      }
      if (dialog) dialog.shown += dt / 30

      ctx.imageSmoothingEnabled = false
      ctx.setTransform(SCALE, 0, 0, SCALE, 0, 0)
      ctx.drawImage(stat, 0, 0)
      if (w) {
        for (const a of w.agents) {
          const on = !staleRef.current && a.status === 'working'
          drawMonitor(ctx, a.seat.x, a.seat.y - 1, on, now)
        }
        const actors = [...w.agents.map((a, i) => ({ a, m: a.mover, look: lookFor(a.id, i) })), { a: null, m: w.player, look: OWNER }]
        actors.sort((l, r) => w.renderPos(l.m).y - w.renderPos(r.m).y)
        for (const { a, m, look } of actors) {
          const pos = w.renderPos(m)
          const X = Math.round(pos.x * T)
          const Y = Math.round(pos.y * T) - 2
          const moving = !!m.from
          const bob = moving && m.progress > 0.25 && m.progress < 0.75 ? 1 : 0
          ctx.drawImage(shadowSprite(), X, Y + 2)
          ctx.drawImage(characterSprite(look, m.dir, moving ? 1 : 0), X, Y - bob)
          if (a && w.isSeated(a)) {
            if (staleRef.current) drawUnknown(ctx, pos.x, pos.y - 0.1)
            else if (a.status === 'working') drawBubble(ctx, pos.x, pos.y - 0.1, now)
          }
          if (a && a.id === selectedRef.current) {
            ctx.strokeStyle = '#ffd24a'
            ctx.lineWidth = 1
            ctx.strokeRect(X + 1.5, Y + 0.5, 13, 16)
          }
        }
        ctx.setTransform(1, 0, 0, 1, 0, 0)
        ctx.font = `bold 15px ${FONT}`
        ctx.textAlign = 'center'
        for (const a of w.agents) {
          const label = (a.name.split(' ')[0] ?? a.name).slice(0, 10)
          const cx = (a.seat.x * T + T / 2) * SCALE
          const cy = (a.seat.y * T + T) * SCALE + 20
          const tw = label.length * 15 + 12
          ctx.fillStyle = OUT
          ctx.fillRect(cx - tw / 2, cy - 17, tw, 24)
          ctx.fillStyle = '#fffaf0'
          ctx.fillRect(cx - tw / 2 + 3, cy - 14, tw - 6, 18)
          ctx.fillStyle = OUT
          ctx.fillText(label, cx, cy)
        }
        ctx.textAlign = 'left'
      }

      ctx.setTransform(1, 0, 0, 1, 0, 0)
      if (dialog) {
        const h = 210
        const y = canvas.height - h - 16
        const x0 = 16
        const wd = canvas.width - 32
        ctx.fillStyle = OUT
        ctx.fillRect(x0, y, wd, h)
        ctx.fillStyle = '#ffffff'
        ctx.fillRect(x0 + 6, y + 6, wd - 12, h - 12)
        ctx.fillStyle = OUT
        ctx.fillRect(x0 + 12, y + 12, wd - 24, 3)
        ctx.fillRect(x0 + 12, y + h - 15, wd - 24, 3)
        ctx.fillStyle = '#ffffff'
        ctx.fillRect(x0 + 12, y + 15, wd - 24, h - 30)
        ctx.fillStyle = OUT
        ctx.font = `bold 20px ${FONT}`
        ctx.fillText(dialog.name.toUpperCase(), x0 + 30, y + 56)
        ctx.font = `18px ${FONT}`
        wrap(dialog.text.slice(0, Math.floor(dialog.shown)), 48).forEach((l, i) => ctx.fillText(l, x0 + 30, y + 98 + i * 32))
        if (dialog.shown >= dialog.text.length && Math.floor(now / 400) % 2) {
          ctx.fillRect(x0 + wd - 54, y + h - 46, 14, 3)
          ctx.fillRect(x0 + wd - 51, y + h - 43, 8, 3)
          ctx.fillRect(x0 + wd - 48, y + h - 40, 2, 3)
        }
      }
      raf = requestAnimationFrame(frame)
    }
    raf = requestAnimationFrame(frame)

    const onKeyDown = (e: KeyboardEvent) => {
      const dir = KEYS[e.key]
      if (dir) {
        e.preventDefault()
        if (!heldRef.current.includes(dir)) heldRef.current.push(dir)
      } else if (['z', 'Z', 'Enter', ' '].includes(e.key)) {
        e.preventDefault()
        interact()
      }
    }
    const onKeyUp = (e: KeyboardEvent) => {
      const dir = KEYS[e.key]
      if (dir) heldRef.current = heldRef.current.filter((d) => d !== dir)
    }
    const onClick = (e: MouseEvent) => {
      const w = worldRef.current
      if (!w) return
      const r = canvas.getBoundingClientRect()
      const tx = Math.floor(((e.clientX - r.left) / r.width) * map.width)
      const ty = Math.floor(((e.clientY - r.top) / r.height) * map.height)
      const a = w.agentAt(tx, ty) ?? w.agentAt(tx, ty + 1)
      if (a) openDialog(a.id)
    }
    const onBlur = () => { heldRef.current = [] }
    canvas.addEventListener('keydown', onKeyDown)
    canvas.addEventListener('keyup', onKeyUp)
    canvas.addEventListener('blur', onBlur)
    canvas.addEventListener('click', onClick)
    return () => {
      cancelAnimationFrame(raf)
      canvas.removeEventListener('keydown', onKeyDown)
      canvas.removeEventListener('keyup', onKeyUp)
      canvas.removeEventListener('blur', onBlur)
      canvas.removeEventListener('click', onClick)
    }
  }, [])

  return (
    <canvas
      ref={canvasRef}
      tabIndex={0}
      className="office-canvas"
      aria-label="Oficina de agentes. Flechas o WASD para mover a tu personaje, Z o Enter para ver la tarea del agente que tienes delante. La lista de abajo contiene la misma informacion."
    />
  )
}
