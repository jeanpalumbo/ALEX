from unittest.mock import MagicMock, patch

from aicommerce.telegram_bridge import TelegramBridge


class FakeCEO:
    def __init__(self):
        self.messages = []

    def chat(self, text):
        self.messages.append(text)

        class Turn:
            content = f"CEO reply to: {text}"

        return Turn()


class FakeSystem:
    def __init__(self):
        self.ceo = FakeCEO()


def test_not_configured_without_token():
    bridge = TelegramBridge(FakeSystem(), token="", allowed_chat_id="")
    assert bridge.configured is False


def test_configured_with_token():
    bridge = TelegramBridge(FakeSystem(), token="123:abc", allowed_chat_id="")
    assert bridge.configured is True
    assert bridge.locked_down is False


def test_bootstrap_mode_tells_sender_their_chat_id_without_calling_ceo():
    system = FakeSystem()
    bridge = TelegramBridge(system, token="123:abc", allowed_chat_id="")

    update = {"update_id": 1, "message": {"chat": {"id": 555}, "text": "hello"}}
    with patch.object(bridge, "_send") as mock_send:
        bridge._handle_update(update)

    assert system.ceo.messages == []  # never reached the real CEO
    mock_send.assert_called_once()
    assert "555" in mock_send.call_args[0][1]


def test_locked_down_forwards_allowed_chat_to_ceo():
    system = FakeSystem()
    bridge = TelegramBridge(system, token="123:abc", allowed_chat_id="555")

    update = {"update_id": 1, "message": {"chat": {"id": 555}, "text": "hola CEO"}}
    with patch.object(bridge, "_send") as mock_send:
        bridge._handle_update(update)

    assert system.ceo.messages == ["hola CEO"]
    mock_send.assert_called_once_with("555", "CEO reply to: hola CEO")


def test_locked_down_ignores_messages_from_other_chats():
    system = FakeSystem()
    bridge = TelegramBridge(system, token="123:abc", allowed_chat_id="555")

    update = {"update_id": 1, "message": {"chat": {"id": 999}, "text": "im a stranger"}}
    with patch.object(bridge, "_send") as mock_send:
        bridge._handle_update(update)

    assert system.ceo.messages == []
    mock_send.assert_not_called()


def test_start_command_does_not_reach_ceo():
    system = FakeSystem()
    bridge = TelegramBridge(system, token="123:abc", allowed_chat_id="555")

    update = {"update_id": 1, "message": {"chat": {"id": 555}, "text": "/start"}}
    with patch.object(bridge, "_send") as mock_send:
        bridge._handle_update(update)

    assert system.ceo.messages == []
    mock_send.assert_called_once()


def test_update_without_text_is_ignored_safely():
    system = FakeSystem()
    bridge = TelegramBridge(system, token="123:abc", allowed_chat_id="555")
    update = {"update_id": 1, "message": {"chat": {"id": 555}, "sticker": {}}}
    bridge._handle_update(update)  # must not raise
    assert system.ceo.messages == []


def test_send_splits_long_messages():
    bridge = TelegramBridge(FakeSystem(), token="123:abc", allowed_chat_id="555")
    long_text = "x" * 9000

    fake_response = MagicMock()
    fake_response.raise_for_status.return_value = None
    with patch("aicommerce.telegram_bridge.requests.post", return_value=fake_response) as mock_post:
        bridge._send("555", long_text)

    assert mock_post.call_count == 3  # 9000 chars / 4000-char chunks


def test_get_updates_raises_on_api_error():
    bridge = TelegramBridge(FakeSystem(), token="123:abc", allowed_chat_id="555")

    fake_response = MagicMock()
    fake_response.raise_for_status.return_value = None
    fake_response.json.return_value = {"ok": False, "description": "bad token"}
    with patch("aicommerce.telegram_bridge.requests.get", return_value=fake_response):
        try:
            bridge._get_updates()
            assert False, "should have raised"
        except RuntimeError as exc:
            assert "bad token" in str(exc)


def test_start_without_token_is_a_noop():
    bridge = TelegramBridge(FakeSystem(), token="", allowed_chat_id="")
    bridge.start()  # must not raise, must not spawn a thread
    assert bridge._thread is None
