"""
Unit test suite for backend.core.config.

Tests configuration defaults, environment variable overrides, computed properties,
path normalization, and directory initialization.
"""

from __future__ import annotations

import os
from pathlib import Path
import pytest

from backend.core.config import (
    AppConfig,
    Settings,
    get_config,
    get_settings,
    get_test_settings,
)


def test_default_settings(tmp_path: Path) -> None:
    settings = get_test_settings(
        project_root=tmp_path,
        cache_dir=tmp_path / "cache",
        output_dir=tmp_path / "outputs",
        temp_dir=tmp_path / "tmp",
    )
    assert settings.ue5_http_port == 30010
    assert settings.ue5_ws_port == 30020
    assert settings.mcp_server_port == 8000
    assert settings.fast_test_mode is False
    assert settings.ue5_mock_mode is True
    assert settings.cache_dir.is_dir()
    assert settings.output_dir.is_dir()
    assert settings.temp_dir.is_dir()


def test_computed_properties() -> None:
    settings = Settings(
        ue5_host="192.168.1.100",
        ue5_http_port=30010,
        ue5_ws_port=30020,
        comfyui_host="10.0.0.5",
        comfyui_port=8188,
    )
    assert settings.ue5_http_url == "http://192.168.1.100:30010"
    assert settings.ue5_ws_url == "ws://192.168.1.100:30020/remote/protocol"
    assert settings.comfyui_url == "http://10.0.0.5:8188"


def test_environment_variable_overrides(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("IANIMATION_FAST_TEST_MODE", "true")
    monkeypatch.setenv("IANIMATION_UE5_HTTP_PORT", "30999")
    monkeypatch.setenv("IANIMATION_ENV", "test")
    monkeypatch.setenv("FAL_KEY", "test-fal-key-1234")
    monkeypatch.setenv("TRIPO_API_KEY", "test-tripo-key-5678")

    # Clear lru_cache on get_settings
    get_settings.cache_clear()

    settings = get_settings()
    assert settings.fast_test_mode is True
    assert settings.ue5_http_port == 30999
    assert settings.env == "test"
    assert settings.fal_key == "test-fal-key-1234"
    assert settings.tripo_api_key == "test-tripo-key-5678"

    # Reset cache afterwards
    get_settings.cache_clear()


def test_app_config_alias() -> None:
    assert AppConfig is Settings
    assert get_config is get_settings


def test_get_test_settings_isolation(tmp_path: Path) -> None:
    s1 = get_test_settings(fast_test_mode=True, mcp_server_port=9001)
    s2 = get_test_settings(fast_test_mode=False, mcp_server_port=9002)

    assert s1.fast_test_mode is True
    assert s1.mcp_server_port == 9001

    assert s2.fast_test_mode is False
    assert s2.mcp_server_port == 9002


def test_log_level_case_insensitivity(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify that lowercase and mixed-case log levels are normalized to uppercase."""
    test_cases = [
        ("debug", "DEBUG"),
        ("info", "INFO"),
        ("warning", "WARNING"),
        ("error", "ERROR"),
        ("critical", "CRITICAL"),
        ("DeBuG", "DEBUG"),
    ]
    for raw_level, expected_level in test_cases:
        monkeypatch.setenv("IANIMATION_LOG_LEVEL", raw_level)
        get_settings.cache_clear()
        settings = get_settings()
        assert settings.log_level == expected_level

    get_settings.cache_clear()


def test_port_range_validation_ue5_http(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify UE5 HTTP port enforces 1..65535."""
    from pydantic import ValidationError

    for invalid_port in ["-1", "0", "65536", "99999"]:
        monkeypatch.setenv("IANIMATION_UE5_HTTP_PORT", invalid_port)
        get_settings.cache_clear()
        with pytest.raises(ValidationError):
            get_settings()

    get_settings.cache_clear()


def test_port_range_validation_ue5_ws(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify UE5 WebSocket port enforces 1..65535."""
    from pydantic import ValidationError

    for invalid_port in ["-1", "0", "65536", "99999"]:
        monkeypatch.setenv("IANIMATION_UE5_WS_PORT", invalid_port)
        get_settings.cache_clear()
        with pytest.raises(ValidationError):
            get_settings()

    get_settings.cache_clear()
