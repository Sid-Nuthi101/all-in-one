from datetime import datetime, timedelta

from agent_train import (
    MessageRecord,
    TrainingConfig,
    build_dataset,
    clean_messages,
    select_model_for_user,
    should_train,
    split_train_holdout,
    UserModelState,
)


def _msg(idx: int, text: str, ts: datetime) -> MessageRecord:
    return MessageRecord(message_id=str(idx), timestamp=ts, text=text)


def test_clean_messages_filters_and_redacts():
    now = datetime(2025, 1, 1, 12, 0, 0)
    messages = [
        _msg(1, "", now),
        _msg(2, "ok", now),
        _msg(3, "https://example.com", now),
        _msg(4, "👍👍", now),
        _msg(5, "Call me at 415-555-1111", now),
        _msg(6, "Email me at test@example.com", now),
        _msg(7, "Meet at 12 Main St", now),
        _msg(8, "Call me at 415-555-1111", now),
    ]

    config = TrainingConfig(short_message_threshold=3, redact_pii=True)
    cleaned = clean_messages(messages, config)

    assert len(cleaned) == 3
    assert cleaned[0].text == "Call me at [REDACTED_PHONE]"
    assert cleaned[1].text == "Email me at [REDACTED_EMAIL]"
    assert cleaned[2].text == "Meet at [REDACTED_ADDRESS]"


def test_build_dataset_split_and_hash():
    base_time = datetime(2025, 1, 1, 8, 0, 0)
    messages = [
        _msg(i, f"message {i}", base_time + timedelta(minutes=i))
        for i in range(10)
    ]

    config = TrainingConfig(holdout_ratio=0.1)
    train, holdout = split_train_holdout(messages, config.holdout_ratio)
    assert len(train) == 9
    assert len(holdout) == 1

    dataset = build_dataset(messages, config)
    assert len(dataset.train_lines) == 9
    assert dataset.dataset_hash

    first_line = dataset.train_lines[0]
    assert "\"role\": \"system\"" in first_line
    assert "\"role\": \"user\"" in first_line
    assert "\"role\": \"assistant\"" in first_line


def test_should_train_respects_weekly_and_delta():
    now = datetime(2025, 1, 8, 10, 0, 0)
    last = now - timedelta(days=8)

    assert should_train(now, last, 1000, 1200) is True
    assert should_train(now, last, 1000, 1100) is False
    assert should_train(now, now - timedelta(days=3), 1000, 2000) is False


def test_select_model_for_user():
    state_ready = UserModelState(
        user_id="u1",
        active_model_id="ft-model",
        model_status="ready",
    )
    state_none = UserModelState(user_id="u2")

    assert select_model_for_user(state_ready, "base-model") == "ft-model"
    assert select_model_for_user(state_none, "base-model") == "base-model"
