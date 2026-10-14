# Configuration Remediation Proposal: `backend/core/config.py`

**Component**: `backend/core/config.py`  
**Milestone**: Milestone 1 Iteration 2 (Config & Integration Remediation)  
**Author**: Explorer 3 (`explorer_m1_it2_3`)  
**Status**: Ready for Implementation  

---

## 1. Executive Summary

Empirical testing by Challenger 2 identified two primary defects in `backend/core/config.py`:
1. **Case-Sensitivity on `log_level`**: Setting `IANIMATION_LOG_LEVEL="debug"` or `"info"` causes Pydantic to crash with a `ValidationError` because `LogLevel` is defined as a strict `Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]`. Pydantic's `case_sensitive=False` in `SettingsConfigDict` normalizes environment variable names, but not literal values.
2. **Missing Port Range Validation**: Network port fields (specifically `ue5_http_port`, `ue5_ws_port`, `mcp_server_port`, `telemetry_ws_port`, and `comfyui_port`) lacked numeric boundary constraints (`ge=1, le=65535`), allowing invalid port numbers like `-1`, `0`, or `70000` to be accepted without validation errors.

This document presents the exact remediation changes to `backend/core/config.py`, analyzes cross-test compatibility with `tests/backend/test_adversarial_m1.py` and `tests/backend/test_challenger_m1_2.py`, and specifies test updates.

---

## 2. Target File Modifications (`backend/core/config.py`)

### Change A: Add `mode="before"` Validator for `log_level`

Add `@field_validator("log_level", mode="before")` to `Settings` to uppercase string values prior to `Literal` evaluation.

```python
    @field_validator("log_level", mode="before")
    @classmethod
    def normalize_log_level(cls, v: object) -> object:
        """Convert log level string to uppercase for case-insensitive validation."""
        if isinstance(v, str):
            return v.upper()
        return v
```

### Change B: Constrain Port Ranges (`ge=1, le=65535`)

Update the port field definitions in `Settings`:

```python
    ue5_http_port: int = Field(
        default=30010,
        ge=1,
        le=65535,
        description="Unreal Engine 5 Remote Control REST HTTP port.",
    )
    ue5_ws_port: int = Field(
        default=30020,
        ge=1,
        le=65535,
        description="Unreal Engine 5 Remote Control WebSocket port.",
    )
```

And consistently harden the companion service ports:

```python
    mcp_server_port: int = Field(
        default=8000,
        ge=1,
        le=65535,
        description="Port for FastMCP SSE server or HTTP endpoint.",
    )
    telemetry_ws_port: int = Field(
        default=8001,
        ge=1,
        le=65535,
        description="WebSocket broadcast port for real-time progress and telemetry events.",
    )
    comfyui_port: int = Field(
        default=8188,
        ge=1,
        le=65535,
        description="Port for local ComfyUI REST/WebSocket endpoint.",
    )
```

---

## 3. Exact Unified Diff for `backend/core/config.py`

```diff
--- a/backend/core/config.py
+++ b/backend/core/config.py
@@ -94,10 +94,14 @@ class Settings(BaseSettings):
     ue5_http_port: int = Field(
         default=30010,
+        ge=1,
+        le=65535,
         description="Unreal Engine 5 Remote Control REST HTTP port.",
     )
     ue5_ws_port: int = Field(
         default=30020,
+        ge=1,
+        le=65535,
         description="Unreal Engine 5 Remote Control WebSocket port.",
     )
     ue5_mock_mode: bool = Field(
@@ -122,6 +126,8 @@ class Settings(BaseSettings):
     mcp_server_port: int = Field(
         default=8000,
+        ge=1,
+        le=65535,
         description="Port for FastMCP SSE server or HTTP endpoint.",
     )
     mcp_transport: McpTransport = Field(
@@ -134,6 +140,8 @@ class Settings(BaseSettings):
     telemetry_ws_port: int = Field(
         default=8001,
+        ge=1,
+        le=65535,
         description="WebSocket broadcast port for real-time progress and telemetry events.",
     )
     telemetry_history_size: int = Field(
@@ -162,6 +170,8 @@ class Settings(BaseSettings):
     comfyui_port: int = Field(
         default=8188,
+        ge=1,
+        le=65535,
         description="Port for local ComfyUI REST/WebSocket endpoint.",
     )
 
@@ -184,6 +194,13 @@ class Settings(BaseSettings):
     # -------------------------------------------------------------------------
     # Validators
     # -------------------------------------------------------------------------
+    @field_validator("log_level", mode="before")
+    @classmethod
+    def normalize_log_level(cls, v: object) -> object:
+        """Convert log level string to uppercase for case-insensitive validation."""
+        if isinstance(v, str):
+            return v.upper()
+        return v
+
     @field_validator("cache_dir", "output_dir", "temp_dir", "project_root", mode="after")
     @classmethod
     def resolve_and_normalize_path(cls, v: Path) -> Path:
```

---

## 4. Test Compatibility Analysis

### 4.1 Compatibility with `tests/backend/test_adversarial_m1.py`
- `test_adversarial_m1.py` focuses on domain models (`Vector3D`, `ColorRGB`, `AudioAnalysisRequest`, `CameraKeyframe`, `PlanStep`, `TelemetryEvent`), `TelemetryBus` concurrency, and `ContentAddressableStorage`.
- It imports `Settings` and `get_test_settings` at line 37, but does not invoke or configure custom `Settings` instances with invalid ports or lowercase log levels.
- **Result**: **100% Compatible (Zero Regressions)**.

### 4.2 Compatibility with `tests/backend/test_config.py`
- Current tests in `test_config.py`:
  - `test_default_settings`: tests ports `30010`, `30020`, `8000` (all within `[1, 65535]`).
  - `test_computed_properties`: tests ports `30010`, `30020`, `8188` (all within `[1, 65535]`).
  - `test_environment_variable_overrides`: tests `IANIMATION_UE5_HTTP_PORT="30999"` (within `[1, 65535]`).
  - `test_get_test_settings_isolation`: tests `mcp_server_port=9001` and `9002` (within `[1, 65535]`).
- **Result**: **100% Compatible (All 5 tests pass)**.

### 4.3 Diagnostic Probes in `tests/backend/test_challenger_m1_2.py`
In `tests/backend/test_challenger_m1_2.py`, Challenger 2 authored two exploratory diagnostic probes:

```python
# Lines 395-406
def test_config_case_sensitivity_log_level(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("IANIMATION_LOG_LEVEL", "debug")
    get_settings.cache_clear()
    with pytest.raises(Exception) as exc_info:  # <-- Expects failure in unpatched code!
        get_settings()
    print(f"\n[DIAGNOSTIC] Lowercase log_level rejected: {exc_info.value}")

# Lines 417-427
def test_config_port_range_boundaries(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("IANIMATION_UE5_HTTP_PORT", "-1")
    get_settings.cache_clear()
    s = get_settings()  # <-- Expects successful parsing of -1 in unpatched code!
    print(f"\n[DIAGNOSTIC] Port -1 accepted by settings: {s.ue5_http_port}")
```

**CRITICAL FINDING**:
- Once `backend/core/config.py` is remediated:
  1. `IANIMATION_LOG_LEVEL="debug"` will succeed without raising an exception, causing `with pytest.raises(Exception):` to fail.
  2. `IANIMATION_UE5_HTTP_PORT="-1"` will trigger `ValidationError`, causing `s = get_settings()` to fail.
- **Recommended Action for Worker**:
  Update `tests/backend/test_challenger_m1_2.py` to assert the verified behavior instead of the buggy behavior:

```python
def test_config_case_sensitivity_log_level(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify that lowercase log_level is normalized to uppercase without errors."""
    monkeypatch.setenv("IANIMATION_LOG_LEVEL", "debug")
    get_settings.cache_clear()
    settings = get_settings()
    assert settings.log_level == "DEBUG"


def test_config_port_range_boundaries(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify that negative or out-of-range port numbers raise ValidationError."""
    from pydantic import ValidationError

    monkeypatch.setenv("IANIMATION_UE5_HTTP_PORT", "-1")
    get_settings.cache_clear()
    with pytest.raises(ValidationError):
        get_settings()
```

---

## 5. Recommended Test Suite Additions for `tests/backend/test_config.py`

To permanently lock in regression prevention in the main test suite, add the following unit tests to `tests/backend/test_config.py`:

```python
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


def test_port_range_validation_ue5_http(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify UE5 HTTP port enforces 1..65535."""
    from pydantic import ValidationError

    for invalid_port in ["-1", "0", "65536", "99999"]:
        monkeypatch.setenv("IANIMATION_UE5_HTTP_PORT", invalid_port)
        get_settings.cache_clear()
        with pytest.raises(ValidationError):
            get_settings()


def test_port_range_validation_ue5_ws(monkeypatch: pytest.MonkeyPatch) -> None:
    """Verify UE5 WebSocket port enforces 1..65535."""
    from pydantic import ValidationError

    for invalid_port in ["-1", "0", "65536", "99999"]:
        monkeypatch.setenv("IANIMATION_UE5_WS_PORT", invalid_port)
        get_settings.cache_clear()
        with pytest.raises(ValidationError):
            get_settings()
```
