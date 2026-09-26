"""RBAC / scopes — per-agent tool and action permissions (least privilege)."""
from __future__ import annotations

from dataclasses import dataclass, field


class PermissionDeniedError(RuntimeError):
    pass


@dataclass
class Role:
    name: str
    allowed_actions: frozenset[str] = field(default_factory=frozenset)
    allowed_tools: frozenset[str] = field(default_factory=frozenset)


class PermissionManager:
    """Least-privilege enforcement: an agent may only act within its assigned role(s).

    Deny-by-default: an agent with no role, or a role missing the requested
    action/tool, is denied.
    """

    def __init__(self) -> None:
        self._roles: dict[str, Role] = {}
        self._agent_roles: dict[str, set[str]] = {}

    def define_role(self, role: Role) -> None:
        self._roles[role.name] = role

    def assign_role(self, agent_name: str, role_name: str) -> None:
        if role_name not in self._roles:
            raise ValueError(f"unknown role '{role_name}'")
        self._agent_roles.setdefault(agent_name, set()).add(role_name)

    def _roles_for(self, agent_name: str) -> list[Role]:
        return [self._roles[r] for r in self._agent_roles.get(agent_name, set())]

    def can_act(self, agent_name: str, action: str) -> bool:
        return any(action in r.allowed_actions for r in self._roles_for(agent_name))

    def can_use_tool(self, agent_name: str, tool: str) -> bool:
        return any(tool in r.allowed_tools for r in self._roles_for(agent_name))

    def require_action(self, agent_name: str, action: str) -> None:
        if not self.can_act(agent_name, action):
            raise PermissionDeniedError(
                f"agent '{agent_name}' is not permitted to perform action '{action}'"
            )

    def require_tool(self, agent_name: str, tool: str) -> None:
        if not self.can_use_tool(agent_name, tool):
            raise PermissionDeniedError(
                f"agent '{agent_name}' is not permitted to use tool '{tool}'"
            )
