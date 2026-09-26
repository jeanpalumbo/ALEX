from aicommerce.control_plane.events import EventBus


def test_events_survive_a_new_bus_instance_against_the_same_db(tmp_path):
    db_path = tmp_path / "events.db"

    bus1 = EventBus(db_path=db_path)
    bus1.publish("order.created", {"order_id": 1})
    bus1.publish("order.created", {"order_id": 2})

    bus2 = EventBus(db_path=db_path)  # simulates a restart
    events = bus2.history("order.created")

    assert [e.payload["order_id"] for e in events] == [1, 2]
    bus1.close()
    bus2.close()


def test_query_persisted_is_paginated(tmp_path):
    bus = EventBus(db_path=tmp_path / "events.db")
    for i in range(5):
        bus.publish("tick", {"i": i})

    page1 = bus.query_persisted("tick", limit=2, offset=0)
    page2 = bus.query_persisted("tick", limit=2, offset=2)

    assert [e.payload["i"] for e in page1] == [4, 3]
    assert [e.payload["i"] for e in page2] == [2, 1]
    bus.close()


def test_in_memory_only_bus_still_works_without_db_path():
    bus = EventBus()
    bus.publish("x", {"a": 1})
    assert len(bus.history("x")) == 1
