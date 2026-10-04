"""Tests for TaskBoard -- real, queryable task state (Jean's explicit,
repeated ask: the team must actually complete tasks, checkable by status,
not just narrative text in memory that happens to say 'done')."""
import pytest

from aicommerce.brain.tasks import InvalidTaskTransition, TaskBoard, TaskStatus


def test_create_task_starts_pending():
    board = TaskBoard()
    task = board.create(objective="validate product X", title="run demand research", owner="research")
    assert task.status == TaskStatus.PENDING
    assert task.owner == "research"


def test_update_status_persists():
    board = TaskBoard()
    task = board.create(objective="obj", title="t", owner="research")
    updated = board.update_status(task.id, TaskStatus.IN_PROGRESS)
    assert updated.status == TaskStatus.IN_PROGRESS
    fetched = board.get(task.id)
    assert fetched.status == TaskStatus.IN_PROGRESS


def test_cannot_move_a_done_task_to_another_status():
    board = TaskBoard()
    task = board.create(objective="obj", title="t", owner="research")
    board.update_status(task.id, TaskStatus.DONE)
    with pytest.raises(InvalidTaskTransition):
        board.update_status(task.id, TaskStatus.IN_PROGRESS)


def test_cannot_move_a_cancelled_task_to_another_status():
    board = TaskBoard()
    task = board.create(objective="obj", title="t", owner="research")
    board.update_status(task.id, TaskStatus.CANCELLED)
    with pytest.raises(InvalidTaskTransition):
        board.update_status(task.id, TaskStatus.DONE)


def test_update_status_unknown_task_raises_keyerror():
    board = TaskBoard()
    with pytest.raises(KeyError):
        board.update_status("not-a-real-id", TaskStatus.DONE)


def test_list_filters_by_objective_owner_and_status():
    board = TaskBoard()
    board.create(objective="obj-a", title="t1", owner="research")
    t2 = board.create(objective="obj-a", title="t2", owner="marketing")
    board.create(objective="obj-b", title="t3", owner="research")
    board.update_status(t2.id, TaskStatus.DONE)

    assert len(board.list(objective="obj-a")) == 2
    assert len(board.list(owner="research")) == 2
    assert len(board.list(status=TaskStatus.DONE)) == 1
    assert len(board.list(objective="obj-a", owner="marketing")) == 1


def test_summary_counts_real_rows_by_status():
    board = TaskBoard()
    t1 = board.create(objective="obj", title="t1", owner="research")
    board.create(objective="obj", title="t2", owner="marketing")
    board.update_status(t1.id, TaskStatus.DONE)

    summary = board.summary()
    assert summary["total"] == 2
    assert summary["by_status"]["done"] == 1
    assert summary["by_status"]["pending"] == 1


def test_persists_across_reconnect(tmp_path):
    db_path = tmp_path / "tasks.db"
    board = TaskBoard(db_path)
    task = board.create(objective="obj", title="t", owner="research")
    board.update_status(task.id, TaskStatus.IN_PROGRESS)
    board.close()

    board2 = TaskBoard(db_path)
    fetched = board2.get(task.id)
    assert fetched is not None
    assert fetched.status == TaskStatus.IN_PROGRESS
