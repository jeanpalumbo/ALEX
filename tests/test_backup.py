import pytest

from aicommerce import backup


def test_backup_copies_known_db_files(tmp_path):
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    (data_dir / "brain.db").write_text("brain-content")
    (data_dir / "events.db").write_text("events-content")
    # scheduler.db intentionally missing — must not be an error

    dest = backup.backup_data_dir(data_dir)

    assert (dest / "brain.db").read_text() == "brain-content"
    assert (dest / "events.db").read_text() == "events-content"
    assert not (dest / "scheduler.db").exists()


def test_backup_with_nothing_to_back_up_raises():
    import tempfile
    from pathlib import Path

    with tempfile.TemporaryDirectory() as d:
        with pytest.raises(FileNotFoundError):
            backup.backup_data_dir(Path(d))


def test_restore_overwrites_current_files(tmp_path):
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    (data_dir / "brain.db").write_text("original")

    dest = backup.backup_data_dir(data_dir)

    (data_dir / "brain.db").write_text("corrupted-or-changed")

    restored = backup.restore_data_dir(dest, data_dir)

    assert restored == ["brain.db"]
    assert (data_dir / "brain.db").read_text() == "original"


def test_restore_from_missing_backup_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        backup.restore_data_dir(tmp_path / "does-not-exist", tmp_path / "data")


def test_list_backups_returns_them_sorted(tmp_path):
    import time

    data_dir = tmp_path / "data"
    data_dir.mkdir()
    (data_dir / "brain.db").write_text("v1")
    b1 = backup.backup_data_dir(data_dir)
    time.sleep(0.01)
    (data_dir / "brain.db").write_text("v2")
    b2 = backup.backup_data_dir(data_dir)

    backups = backup.list_backups(data_dir)
    assert [b.name for b in backups] == sorted([b1.name, b2.name])
