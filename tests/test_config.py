"""Configuration must load with sane, safe defaults and no .env present."""

from config import allowed_telegram_ids, settings


def test_settings_load_with_defaults():
    assert settings.MODEL
    assert settings.NINEROUTER_BASE_URL.startswith("http")
    assert settings.WEB_PORT > 0
    assert settings.MAX_STEPS > 0


def test_dangerous_features_are_off_by_default():
    # These must never default to on — they unlock shell execution and file writes.
    assert settings.ENABLE_SHELL is False
    assert settings.ENABLE_FILE_WRITE is False
    assert settings.REQUIRE_CONFIRMATION is True


def test_allowed_telegram_ids_parsing(monkeypatch):
    monkeypatch.setattr(settings, "ALLOWED_TELEGRAM_IDS", "")
    assert allowed_telegram_ids() == set()

    monkeypatch.setattr(settings, "ALLOWED_TELEGRAM_IDS", "111, 222 ,333")
    assert allowed_telegram_ids() == {111, 222, 333}
