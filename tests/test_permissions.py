import pytest

from aicommerce.control_plane.permissions import PermissionDeniedError, PermissionManager, Role


def test_deny_by_default_for_unknown_agent():
    pm = PermissionManager()
    assert pm.can_act("nobody", "publish_content") is False
    with pytest.raises(PermissionDeniedError):
        pm.require_action("nobody", "publish_content")


def test_role_grants_action_and_tool():
    pm = PermissionManager()
    pm.define_role(Role(name="content", allowed_actions=frozenset({"publish_content"}), allowed_tools=frozenset({"cms"})))
    pm.assign_role("content_agent", "content")

    assert pm.can_act("content_agent", "publish_content") is True
    assert pm.can_use_tool("content_agent", "cms") is True
    assert pm.can_act("content_agent", "delete_customer") is False


def test_require_tool_raises_when_missing():
    pm = PermissionManager()
    pm.define_role(Role(name="content", allowed_actions=frozenset({"publish_content"})))
    pm.assign_role("content_agent", "content")

    with pytest.raises(PermissionDeniedError):
        pm.require_tool("content_agent", "cms")


def test_agent_can_have_multiple_roles():
    pm = PermissionManager()
    pm.define_role(Role(name="content", allowed_actions=frozenset({"publish_content"})))
    pm.define_role(Role(name="seo", allowed_actions=frozenset({"edit_metadata"})))
    pm.assign_role("agent", "content")
    pm.assign_role("agent", "seo")

    pm.require_action("agent", "publish_content")
    pm.require_action("agent", "edit_metadata")
