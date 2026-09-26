from aicommerce.control_plane.events import EventBus


def test_subscriber_receives_published_event():
    bus = EventBus()
    received = []
    bus.subscribe("order.created", received.append)

    event = bus.publish("order.created", {"order_id": 123})

    assert len(received) == 1
    assert received[0] is event
    assert received[0].payload == {"order_id": 123}


def test_subscriber_only_receives_its_event_type():
    bus = EventBus()
    order_events = []
    inventory_events = []
    bus.subscribe("order.created", order_events.append)
    bus.subscribe("inventory.low", inventory_events.append)

    bus.publish("order.created", {})

    assert len(order_events) == 1
    assert len(inventory_events) == 0


def test_history_filters_by_type():
    bus = EventBus()
    bus.publish("order.created", {})
    bus.publish("inventory.low", {})
    bus.publish("order.created", {})

    assert len(bus.history("order.created")) == 2
    assert len(bus.history()) == 3


def test_multiple_subscribers_all_receive_event():
    bus = EventBus()
    calls = []
    bus.subscribe("agent.failed", lambda e: calls.append("first"))
    bus.subscribe("agent.failed", lambda e: calls.append("second"))

    bus.publish("agent.failed", {})

    assert calls == ["first", "second"]
