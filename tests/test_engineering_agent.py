"""Tests run against a throwaway git repo in tmp_path -- never against the
real ai-commerce-os checkout. Requires a real `git` binary (same as the
agent itself; there is no mocked git layer, this is testing the real thing)."""
import subprocess

import pytest

from aicommerce.agents.engineering_agent import EngineeringAgent


def make_repo(tmp_path) -> EngineeringAgent:
    subprocess.run(["git", "init", "-b", "master"], cwd=tmp_path, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=tmp_path, check=True)
    (tmp_path / "README.md").write_text("hello\n")
    subprocess.run(["git", "add", "-A"], cwd=tmp_path, check=True)
    subprocess.run(["git", "commit", "-m", "initial"], cwd=tmp_path, check=True, capture_output=True)
    return EngineeringAgent(repo_root=tmp_path)


def test_current_branch_reports_master(tmp_path):
    agent = make_repo(tmp_path)
    result = agent.execute({"action": "current_branch", "params": {}})
    assert result.success is True
    assert result.output == "master"


def test_write_file_refused_on_master(tmp_path):
    agent = make_repo(tmp_path)
    result = agent.execute({"action": "write_file", "params": {"path": "x.txt", "content": "hi"}})
    assert result.success is False
    assert "protected branch" in result.error


def test_commit_refused_on_master(tmp_path):
    agent = make_repo(tmp_path)
    result = agent.execute({"action": "commit", "params": {"message": "sneaky"}})
    assert result.success is False
    assert "protected branch" in result.error


def test_create_branch_write_and_commit_on_sandbox_branch(tmp_path):
    agent = make_repo(tmp_path)
    r1 = agent.execute({"action": "create_branch", "params": {"name": "ceo-sandbox/task-1"}})
    assert r1.success is True

    r2 = agent.execute({"action": "write_file", "params": {"path": "feature.py", "content": "x = 1\n"}})
    assert r2.success is True
    assert (tmp_path / "feature.py").read_text() == "x = 1\n"

    r3 = agent.execute({"action": "commit", "params": {"message": "add feature"}})
    assert r3.success is True
    assert "add feature" in r3.output

    r4 = agent.execute({"action": "current_branch", "params": {}})
    assert r4.output == "ceo-sandbox/task-1"


def test_create_branch_refuses_protected_names(tmp_path):
    agent = make_repo(tmp_path)
    result = agent.execute({"action": "create_branch", "params": {"name": "master"}})
    assert result.success is False
    assert "protected" in result.error


def test_read_file_and_list_files(tmp_path):
    agent = make_repo(tmp_path)
    result = agent.execute({"action": "read_file", "params": {"path": "README.md"}})
    assert result.success is True
    assert result.output == "hello\n"

    listing = agent.execute({"action": "list_files", "params": {"pattern": "*.md"}})
    assert "README.md" in listing.output


def test_read_file_refuses_path_escaping_repo_root(tmp_path):
    agent = make_repo(tmp_path)
    result = agent.execute({"action": "read_file", "params": {"path": "../../etc/passwd"}})
    assert result.success is False
    assert "escapes the repo root" in result.error


def test_git_status_and_diff_reflect_real_changes(tmp_path):
    agent = make_repo(tmp_path)
    agent.execute({"action": "create_branch", "params": {"name": "ceo-sandbox/diff-test"}})
    agent.execute({"action": "write_file", "params": {"path": "new.py", "content": "y = 2\n"}})

    status = agent.execute({"action": "git_status", "params": {}})
    assert "new.py" in status.output

    agent.execute({"action": "commit", "params": {"message": "add new.py"}})
    diff = agent.execute({"action": "git_diff", "params": {"against": "master"}})
    assert "new.py" in diff.output
    assert "y = 2" in diff.output


def test_merge_to_master_actually_merges_when_called_directly(tmp_path):
    """The agent itself will perform the merge if asked -- the approval gate
    lives in the Orchestrator (tested separately), not in this agent. This
    proves the merge mechanics work when it IS reached."""
    agent = make_repo(tmp_path)
    agent.execute({"action": "create_branch", "params": {"name": "ceo-sandbox/merge-test"}})
    agent.execute({"action": "write_file", "params": {"path": "merged.py", "content": "z = 3\n"}})
    agent.execute({"action": "commit", "params": {"message": "add merged.py"}})

    result = agent.execute({"action": "merge_to_master", "params": {"branch": "ceo-sandbox/merge-test"}})
    assert result.success is True

    current = agent.execute({"action": "current_branch", "params": {}})
    assert current.output == "master"
    assert (tmp_path / "merged.py").exists()


def test_run_tests_action_executes_pytest_in_the_target_repo(tmp_path):
    (tmp_path / "test_sample.py").write_text("def test_ok():\n    assert 1 == 1\n")
    subprocess.run(["git", "init", "-b", "master"], cwd=tmp_path, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.email", "t@example.com"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.name", "T"], cwd=tmp_path, check=True)
    subprocess.run(["git", "add", "-A"], cwd=tmp_path, check=True)
    subprocess.run(["git", "commit", "-m", "init"], cwd=tmp_path, check=True, capture_output=True)

    agent = EngineeringAgent(repo_root=tmp_path)
    result = agent.execute({"action": "run_tests", "params": {}})
    assert result.success is True
    assert result.output["passed"] is True
