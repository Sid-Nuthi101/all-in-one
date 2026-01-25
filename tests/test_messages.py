import sys
import types
from types import SimpleNamespace

import pytest

foundation = types.ModuleType("Foundation")
foundation.NSData = object
foundation.NSKeyedUnarchiver = object
sys.modules.setdefault("Foundation", foundation)

import messages
from messages import MessageBridge


def test_escape_applescript_string():
    value = 'He said "hi" \\ ok'
    escaped = MessageBridge._escape_applescript_string(value)
    assert escaped == 'He said \\"hi\\" \\\\ ok'


def test_send_imessage_to_chat_escapes(monkeypatch):
    bridge = MessageBridge.__new__(MessageBridge)
    recorded = {}

    def fake_run(args, check=False):
        recorded["args"] = args
        recorded["check"] = check
        return SimpleNamespace(returncode=0)

    monkeypatch.setattr(messages.subprocess, "run", fake_run)

    bridge.send_imessage_to_chat('iMessage;+;+"test"', 'hi "there" \\ ok')

    assert recorded["check"] is True
    assert recorded["args"][0] == "osascript"
    script = recorded["args"][2]
    assert 'id is "iMessage;+;+\\\"test\\\""' in script
    assert 'send "hi \\"there\\" \\\\ ok"' in script


def test_send_message_to_chat_uses_direct_imessage_for_one_participant(monkeypatch):
    bridge = MessageBridge.__new__(MessageBridge)
    sent = {}

    def fake_send_imessage(recipient, text):
        sent["recipient"] = recipient
        sent["text"] = text

    monkeypatch.setattr(bridge, "send_imessage", fake_send_imessage)

    chat = {"participant_handles": ["+15551234567"], "chat_identifier": "iMessage;+;+15551234567"}
    bridge.send_message_to_chat(chat, "hello")

    assert sent == {"recipient": "+15551234567", "text": "hello"}


def test_send_message_to_chat_uses_chat_identifier_for_group(monkeypatch):
    bridge = MessageBridge.__new__(MessageBridge)
    sent = {}

    def fake_send_imessage_to_chat(chat_identifier, text):
        sent["chat_identifier"] = chat_identifier
        sent["text"] = text

    monkeypatch.setattr(bridge, "send_imessage_to_chat", fake_send_imessage_to_chat)

    chat = {
        "participant_handles": ["+15551234567", "+15557654321"],
        "chat_identifier": "iMessage;+;+15551234567,+15557654321",
    }
    bridge.send_message_to_chat(chat, "group hello")

    assert sent == {
        "chat_identifier": "iMessage;+;+15551234567,+15557654321",
        "text": "group hello",
    }


def test_send_message_to_chat_requires_chat_identifier_for_group():
    bridge = MessageBridge.__new__(MessageBridge)
    chat = {"participant_handles": ["+15551234567", "+15557654321"]}

    with pytest.raises(ValueError, match="Missing chat_identifier"):
        bridge.send_message_to_chat(chat, "group hello")
