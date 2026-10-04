import { useCallback, useEffect, useRef, useState } from 'react'
import './App.css'
import { fetchOfficeSnapshot, OfficeApiError } from './api'
import { OfficeScene } from './OfficeScene'
import type { OfficeAgent } from './types'

type ConnectionState = 'connecting' | 'connected' | 'error'

// MVP vertical slice: REST polling every 5s. Real-time WebSocket sync
// (reconnect/backoff, event dedupe) is phase 3 of the design doc and is
// NOT implemented yet -- documented here rather than silently skipped.
const POLL_INTERVAL_MS = 5000

function timeAgo(iso: string | null): string {
  if (!iso) return ''
  const seconds = Math.max(0, Math.floor((Date.now() - new Date(iso).getTime()) / 1000))
  if (seconds < 60) return `hace ${seconds}s`
  const minutes = Math.floor(seconds / 60)
  if (minutes < 60) return `hace ${minutes}min`
  return `hace ${Math.floor(minutes / 60)}h`
}

export default function App() {
  const [agents, setAgents] = useState<OfficeAgent[]>([])
  const [selectedId, setSelectedId] = useState<string | null>(null)
  const [connection, setConnection] = useState<ConnectionState>('connecting')
  const [lastSyncedAt, setLastSyncedAt] = useState<string | null>(null)
  const [errorMessage, setErrorMessage] = useState<string | null>(null)
  const pollRef = useRef<number | null>(null)

  const refresh = useCallback(async () => {
    try {
      const snapshot = await fetchOfficeSnapshot()
      setAgents(snapshot.agents)
      setConnection('connected')
      setLastSyncedAt(snapshot.server_time)
      setErrorMessage(null)
    } catch (err) {
      setConnection('error')
      setErrorMessage(err instanceof OfficeApiError ? err.message : 'no se pudo conectar con el backend')
    }
  }, [])

  useEffect(() => {
    refresh()
    pollRef.current = window.setInterval(refresh, POLL_INTERVAL_MS)
    return () => {
      if (pollRef.current) window.clearInterval(pollRef.current)
    }
  }, [refresh])

  const handleSelect = useCallback((agentId: string) => {
    setSelectedId(agentId)
  }, [])

  const selected = agents.find((a) => a.agent_id === selectedId) ?? null
  const workingCount = agents.filter((a) => a.status === 'working').length

  return (
    <div className="office-app">
      <header className="office-topbar">
        <h1>Oficina de agentes</h1>
        <span className={`conn-badge conn-${connection}`} role="status">
          {connection === 'connected' && `${agents.length} agentes · ${workingCount} trabajando`}
          {connection === 'connecting' && 'Conectando…'}
          {connection === 'error' && `Sin conexión — ${errorMessage}`}
        </span>
      </header>

      <main className="office-main">
        <section className="office-scene-wrap">
          <OfficeScene agents={agents} selectedId={selectedId} onSelect={handleSelect} />
          <ul className="office-roster" aria-label="Lista de agentes (accesible por teclado)">
            {agents.map((a) => (
              <li key={a.agent_id}>
                <button
                  type="button"
                  aria-pressed={a.agent_id === selectedId}
                  onClick={() => handleSelect(a.agent_id)}
                >
                  <span className={`status-dot status-${a.status}`} aria-hidden="true" />
                  {a.display_name} — {a.status === 'working' ? 'Trabajando' : 'Inactivo'}
                </button>
              </li>
            ))}
          </ul>
        </section>

        <aside className="office-panel" aria-label="Detalle del agente seleccionado">
          {selected ? (
            <>
              <h2>{selected.display_name}</h2>
              <p className="role">{selected.role}</p>
              <p>
                <strong>Estado:</strong>{' '}
                <span className={`status-dot status-${selected.status}`} aria-hidden="true" />
                {selected.status === 'working' ? 'Trabajando' : 'Inactivo'}
              </p>
              <p>
                <strong>Tarea actual:</strong>{' '}
                <span className="selectable-text">{selected.task ? selected.task.title : 'Sin tarea activa'}</span>
              </p>
              {selected.updated_at && (
                <p className="updated-at">Actualizado {timeAgo(selected.updated_at)}</p>
              )}
            </>
          ) : (
            <p>Selecciona un agente para ver su detalle.</p>
          )}
          {lastSyncedAt && <p className="sync-note">Última sincronización: {timeAgo(lastSyncedAt)}</p>}
        </aside>
      </main>
    </div>
  )
}
