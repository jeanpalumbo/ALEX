"""Tests for the office real-data adapter -- status/task must come strictly
from TaskBoard, never invented."""
from aicommerce.bootstrap import System
from aicommerce.brain.tasks import TaskStatus
from aicommerce.webapp.office import get_office_agents


def test_office_agents_default_to_idle_with_no_task(tmp_path, monkeypatch):
    from aicommerce import config

    monkeypatch.setattr(config, "BRAIN_DB_PATH", tmp_path / "brain.db")
    monkeypatch.setattr(config, "DATA_DIR", tmp_path)

    system = System()
    agents = get_office_agents(system)

    agent_ids = {a["agent_id"] for a in agents}
    assert agent_ids == {"ceo", "research", "store_ops", "engineering_lead", "finance", "marketing", "design", "rnd"}
    for a in agents:
        assert a["status"] == "idle"
        assert a["task"] is None


def test_office_agent_shows_working_with_real_in_progress_task(tmp_path, monkeypatch):
    from aicommerce import config

    monkeypatch.setattr(config, "BRAIN_DB_PATH", tmp_path / "brain.db")
    monkeypatch.setattr(config, "DATA_DIR", tmp_path)

    system = System()
    task = system.tasks.create(objective="validate product X", title="run demand research", owner="research")
    system.tasks.update_status(task.id, TaskStatus.IN_PROGRESS)

    agents = get_office_agents(system)
    research = next(a for a in agents if a["agent_id"] == "research")
    assert research["status"] == "working"
    assert research["task"]["title"] == "run demand research"
    assert research["updated_at"] is not None

    others = [a for a in agents if a["agent_id"] != "research"]
    assert all(a["status"] == "idle" for a in others)


def test_office_agent_display_names_are_real_persona_identities(tmp_path, monkeypatch):
    from aicommerce import config

    monkeypatch.setattr(config, "BRAIN_DB_PATH", tmp_path / "brain.db")
    monkeypatch.setattr(config, "DATA_DIR", tmp_path)

    system = System()
    agents = get_office_agents(system)
    names = {a["agent_id"]: a["display_name"] for a in agents}

    assert names["ceo"] == "Alex Rivera"
    assert names["research"] == "Elena Voss"
    assert names["rnd"] == "Noor Kaelin"


def test_done_task_does_not_show_as_working(tmp_path, monkeypatch):
    from aicommerce import config

    monkeypatch.setattr(config, "BRAIN_DB_PATH", tmp_path / "brain.db")
    monkeypatch.setattr(config, "DATA_DIR", tmp_path)

    system = System()
    task = system.tasks.create(objective="obj", title="t", owner="marketing")
    system.tasks.update_status(task.id, TaskStatus.DONE)

    agents = get_office_agents(system)
    marketing = next(a for a in agents if a["agent_id"] == "marketing")
    assert marketing["status"] == "idle"
