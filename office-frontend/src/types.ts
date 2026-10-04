// Mirrors the real contract served by GET /api/office/agents
// (aicommerce/webapp/office.py). Nothing here is invented -- status/task
// are derived strictly from the real TaskBoard on the backend.
export type AgentStatus = 'working' | 'idle'

export interface AgentTask {
  id: string
  title: string
}

export interface OfficeAgent {
  agent_id: string
  display_name: string
  role: string
  status: AgentStatus
  task: AgentTask | null
  updated_at: string | null
}

export interface OfficeSnapshot {
  server_time: string
  agents: OfficeAgent[]
}
