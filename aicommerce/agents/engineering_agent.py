"""EngineeringAgent — real coding/engineering capability (master plan Fase 11).

Scope agreed with Jean: the agent can read, edit, test and commit freely
inside a sandbox branch. It can NEVER touch `master`/`main` directly, and
`merge_to_master` is registered as a `high_risk_action` on its AgentSpec —
enforced at the Orchestrator level (`aicommerce/ceo/orchestrator.py`), not
just by prompt instruction — so it always stops at human approval no matter
what risk/reversible a caller claims. This is Fase 12/13's "self-editing
controlado" and "protección de autoridad" made concrete: the agent can do
whatever it wants in its own branch; reaching `master` always needs Jean.

Runs against THIS repo's own working tree (there is no separate sandbox
checkout yet) — editing/committing on a branch is safe with the server
running (Python doesn't hot-reload `.py` files), but this agent refuses to
operate while `master`/`main` is checked out, and never pushes to any
remote (no push capability is implemented at all).
"""
from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Optional

from aicommerce import config
from aicommerce.agents.base import Agent, AgentResult

PROTECTED_BRANCHES = {"master", "main"}
_GIT_TIMEOUT_SECONDS = 60
_TEST_TIMEOUT_SECONDS = 300


class EngineeringAgent(Agent):
    name = "engineering"

    READ_ACTIONS = {"read_file", "list_files", "git_status", "git_diff", "run_tests", "current_branch"}
    WRITE_ACTIONS = {"create_branch", "write_file", "commit"}
    # merge_to_master is deliberately its own set -- registered as
    # high_risk_actions on the AgentSpec, never bundled with the others.
    MERGE_ACTIONS = {"merge_to_master"}

    def __init__(self, repo_root: Optional[Path] = None) -> None:
        self.repo_root = Path(repo_root or config.ROOT_DIR).resolve()

    # ------------------------------------------------------------------
    def execute(self, task: dict) -> AgentResult:
        action = task.get("action")
        params = task.get("params", {})
        handler = getattr(self, f"_do_{action}", None)
        if handler is None:
            return AgentResult(success=False, error=f"unknown engineering action '{action}'")
        try:
            output = handler(**params)
            return AgentResult(
                success=True, output=output, evidence=f"engineering action '{action}' completed"
            )
        except EngineeringGuardError as exc:
            return AgentResult(success=False, error=str(exc))
        except subprocess.TimeoutExpired as exc:
            return AgentResult(success=False, error=f"command timed out: {exc}")
        except Exception as exc:  # noqa: BLE001 — surface as a failed result, not a crash
            return AgentResult(success=False, error=f"unexpected error: {exc}")

    # ------------------------------------------------------------------
    # Safety helpers
    # ------------------------------------------------------------------
    def _resolve_within_repo(self, relative_path: str) -> Path:
        candidate = (self.repo_root / relative_path).resolve()
        if self.repo_root not in candidate.parents and candidate != self.repo_root:
            raise EngineeringGuardError(f"path '{relative_path}' escapes the repo root — refused")
        return candidate

    def _run_git(self, *args: str) -> str:
        result = subprocess.run(
            ["git", *args],
            cwd=self.repo_root,
            capture_output=True,
            text=True,
            timeout=_GIT_TIMEOUT_SECONDS,
        )
        if result.returncode != 0:
            raise EngineeringGuardError(f"git {' '.join(args)} failed: {result.stderr.strip()}")
        return result.stdout

    def _current_branch(self) -> str:
        return self._run_git("rev-parse", "--abbrev-ref", "HEAD").strip()

    def _require_not_on_protected_branch(self) -> None:
        branch = self._current_branch()
        if branch in PROTECTED_BRANCHES:
            raise EngineeringGuardError(
                f"currently on protected branch '{branch}' — create/checkout a sandbox branch "
                f"first (create_branch), never write directly on {sorted(PROTECTED_BRANCHES)}"
            )

    # ------------------------------------------------------------------
    # Reads
    # ------------------------------------------------------------------
    def _do_current_branch(self) -> str:
        return self._current_branch()

    def _do_read_file(self, path: str) -> str:
        full = self._resolve_within_repo(path)
        if not full.is_file():
            raise EngineeringGuardError(f"not a file: {path}")
        return full.read_text(encoding="utf-8", errors="replace")

    def _do_list_files(self, pattern: str = "**/*.py") -> list[str]:
        return sorted(
            str(p.relative_to(self.repo_root)).replace("\\", "/")
            for p in self.repo_root.glob(pattern)
            if p.is_file() and ".git" not in p.parts
        )

    def _do_git_status(self) -> str:
        return self._run_git("status", "--short")

    def _do_git_diff(self, against: str = "master") -> str:
        return self._run_git("diff", against)

    def _do_run_tests(self) -> dict:
        result = subprocess.run(
            ["python", "-m", "pytest", "-q"],
            cwd=self.repo_root,
            capture_output=True,
            text=True,
            timeout=_TEST_TIMEOUT_SECONDS,
        )
        return {
            "passed": result.returncode == 0,
            "returncode": result.returncode,
            "output_tail": "\n".join(result.stdout.strip().splitlines()[-30:]),
        }

    # ------------------------------------------------------------------
    # Writes — sandbox branch only
    # ------------------------------------------------------------------
    def _do_create_branch(self, name: str) -> str:
        if name in PROTECTED_BRANCHES:
            raise EngineeringGuardError(f"refusing to create/checkout a protected branch name: {name}")
        existing = self._run_git("branch", "--list", name).strip()
        if existing:
            self._run_git("checkout", name)
            return f"checked out existing branch '{name}'"
        self._run_git("checkout", "-b", name)
        return f"created and checked out new branch '{name}'"

    def _do_write_file(self, path: str, content: str) -> str:
        self._require_not_on_protected_branch()
        full = self._resolve_within_repo(path)
        full.parent.mkdir(parents=True, exist_ok=True)
        full.write_text(content, encoding="utf-8")
        return f"wrote {len(content)} chars to {path}"

    def _do_commit(self, message: str) -> str:
        self._require_not_on_protected_branch()
        self._run_git("add", "-A")
        status = self._run_git("status", "--short")
        if not status.strip():
            return "nothing to commit"
        return self._run_git("commit", "-m", message)

    # ------------------------------------------------------------------
    # Merge — always high-risk, only ever reached via approved Orchestrator flow
    # ------------------------------------------------------------------
    def _do_merge_to_master(self, branch: str) -> str:
        if branch in PROTECTED_BRANCHES:
            raise EngineeringGuardError("refusing to merge a protected branch into itself")
        self._run_git("checkout", "master")
        return self._run_git("merge", "--no-ff", branch, "-m", f"Merge {branch} into master (CEO-approved)")


class EngineeringGuardError(RuntimeError):
    pass
