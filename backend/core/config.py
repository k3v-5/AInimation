"""
Central application configuration and environment variable resolver for IANIMATION.

Adheres strictly to Pydantic v2 BaseSettings, SOLID principles, and the Zero-Any policy.
"""

from __future__ import annotations

from functools import lru_cache
import os
from pathlib import Path
from typing import Literal, Optional, Union

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

AppEnvironment = Literal["development", "production", "test"]
LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
McpTransport = Literal["sse", "stdio", "stream"]

ConfigOverrideValue = Union[str, int, float, bool, Path, None]


class Settings(BaseSettings):
    """
    Central configuration class for IANIMATION application.

    Loads configuration from environment variables (prefixed with IANIMATION_),
    standard service environment variables (e.g. FAL_KEY), or local .env files.
    """

    model_config = SettingsConfigDict(
        env_prefix="IANIMATION_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # -------------------------------------------------------------------------
    # Application & Execution Flags
    # -------------------------------------------------------------------------
    app_name: str = Field(
        default="IANIMATION 3D AI Orchestrator",
        description="Name of the desktop application orchestrator.",
    )
    env: AppEnvironment = Field(
        default="development",
        description="Runtime environment mode (development, production, test).",
    )
    fast_test_mode: bool = Field(
        default=False,
        description=(
            "When True, enables synthetic mock fallbacks for AI inference and UE5 calls, "
            "allowing ultra-fast offline test execution without GPU/Cloud dependencies."
        ),
    )
    log_level: LogLevel = Field(
        default="INFO",
        description="Root logging verbosity level.",
    )
    debug: bool = Field(
        default=False,
        description="Enable verbose debug assertions and telemetry details.",
    )

    # -------------------------------------------------------------------------
    # File System Paths
    # -------------------------------------------------------------------------
    project_root: Path = Field(
        default_factory=lambda: Path.cwd(),
        description="Root directory of the project.",
    )
    cache_dir: Path = Field(
        default_factory=lambda: Path.cwd() / ".cache",
        description="Directory for Content-Addressable Storage (CAS) asset cache.",
    )
    output_dir: Path = Field(
        default_factory=lambda: Path.cwd() / "outputs",
        description="Directory for final exported renders, audio stems, and 3D files.",
    )
    temp_dir: Path = Field(
        default_factory=lambda: Path.cwd() / ".tmp",
        description="Directory for temporary scratch files during processing.",
    )

    # -------------------------------------------------------------------------
    # Unreal Engine 5 Bridge & Mock Settings
    # -------------------------------------------------------------------------
    ue5_host: str = Field(
        default="127.0.0.1",
        description="Host address for Unreal Engine 5 Remote Control API.",
    )
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
    ue5_mock_mode: bool = Field(
        default=True,
        description="If True, connect to internal UE5 Mock Server instead of requiring live UE5.",
    )
    ue5_timeout_seconds: float = Field(
        default=30.0,
        description="Timeout in seconds for UE5 Remote Control RPC calls.",
    )

    # -------------------------------------------------------------------------
    # FastMCP Server Settings
    # -------------------------------------------------------------------------
    mcp_server_name: str = Field(
        default="ianimation-mcp",
        description="Identifiable name of the FastMCP server instance.",
    )
    mcp_server_host: str = Field(
        default="127.0.0.1",
        description="Host on which FastMCP server binds.",
    )
    mcp_server_port: int = Field(
        default=8000,
        ge=1,
        le=65535,
        description="Port for FastMCP SSE server or HTTP endpoint.",
    )
    mcp_transport: McpTransport = Field(
        default="sse",
        description="Communication transport protocol for MCP client-server communication.",
    )

    # -------------------------------------------------------------------------
    # Telemetry & Event Streaming Settings
    # -------------------------------------------------------------------------
    telemetry_ws_port: int = Field(
        default=8001,
        ge=1,
        le=65535,
        description="WebSocket broadcast port for real-time progress and telemetry events.",
    )
    telemetry_history_size: int = Field(
        default=1000,
        description="Maximum number of historical telemetry events preserved in memory.",
    )

    # -------------------------------------------------------------------------
    # Cloud API Keys & External Services (Optional / Fallback)
    # -------------------------------------------------------------------------
    fal_key: Optional[str] = Field(
        default=None,
        description="API key for Fal.ai Cloud Generative 3D & Image services.",
    )
    tripo_api_key: Optional[str] = Field(
        default=None,
        description="API key for Tripo AI 3D Mesh generation platform.",
    )
    replicate_api_token: Optional[str] = Field(
        default=None,
        description="API token for Replicate models (Demucs, 3D, Mocap).",
    )
    comfyui_host: str = Field(
        default="127.0.0.1",
        description="Host address for local or headless ComfyUI server.",
    )
    comfyui_port: int = Field(
        default=8188,
        ge=1,
        le=65535,
        description="Port for local ComfyUI REST/WebSocket endpoint.",
    )

    # -------------------------------------------------------------------------
    # CAS Asset Cache Policies
    # -------------------------------------------------------------------------
    cache_enabled: bool = Field(
        default=True,
        description="Global toggle for Content-Addressable Storage (CAS) caching.",
    )
    cache_ttl_seconds: int = Field(
        default=86400 * 7,  # 7 days
        description="Default Time-To-Live in seconds for cached assets (0 = indefinite).",
    )
    cache_max_size_bytes: int = Field(
        default=10 * 1024 * 1024 * 1024,  # 10 GiB
        description="Maximum cache storage quota in bytes before LRU eviction triggers.",
    )

    # -------------------------------------------------------------------------
    # Validators
    # -------------------------------------------------------------------------
    @field_validator("log_level", mode="before")
    @classmethod
    def normalize_log_level(cls, v: object) -> object:
        """Convert log level string to uppercase for case-insensitive validation."""
        if isinstance(v, str):
            return v.upper()
        return v

    @field_validator("cache_dir", "output_dir", "temp_dir", "project_root", mode="after")
    @classmethod
    def resolve_and_normalize_path(cls, v: Path) -> Path:
        """Resolve paths to absolute normalized paths."""
        return v.resolve()

    # -------------------------------------------------------------------------
    # Computed Properties
    # -------------------------------------------------------------------------
    @property
    def ue5_http_url(self) -> str:
        """Construct the full base HTTP URL for UE5 Remote Control."""
        return f"http://{self.ue5_host}:{self.ue5_http_port}"

    @property
    def ue5_ws_url(self) -> str:
        """Construct the full base WebSocket URL for UE5 Remote Control."""
        return f"ws://{self.ue5_host}:{self.ue5_ws_port}/remote/protocol"

    @property
    def comfyui_url(self) -> str:
        """Construct the full base HTTP URL for ComfyUI."""
        return f"http://{self.comfyui_host}:{self.comfyui_port}"

    # -------------------------------------------------------------------------
    # Directory Bootstrap Helper
    # -------------------------------------------------------------------------
    def ensure_directories(self) -> None:
        """Create configured directory paths on disk if they do not exist."""
        for path in (self.cache_dir, self.output_dir, self.temp_dir):
            path.mkdir(parents=True, exist_ok=True)


# Contract aliases for cross-module compatibility
AppConfig = Settings


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """
    Retrieve cached application settings singleton instance.

    Reads external cloud keys from standard un-prefixed env vars if IANIMATION_ prefix was not set.
    """
    settings = Settings()

    # Fallback to standard cloud environment variable names if not provided via prefix
    if not settings.fal_key:
        settings.fal_key = os.getenv("FAL_KEY")
    if not settings.tripo_api_key:
        settings.tripo_api_key = os.getenv("TRIPO_API_KEY")
    if not settings.replicate_api_token:
        settings.replicate_api_token = os.getenv("REPLICATE_API_TOKEN")

    settings.ensure_directories()
    return settings


# Contract alias for get_settings
get_config = get_settings


def get_test_settings(**overrides: ConfigOverrideValue) -> Settings:
    """
    Construct an isolated Settings instance for test execution.

    Does not use the global lru_cache, allowing fine-grained test overrides.
    """
    settings = Settings(**overrides)
    settings.ensure_directories()
    return settings
