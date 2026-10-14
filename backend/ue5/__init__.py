"""
Unreal Engine 5 Bridge Package for IANIMATION.

Provides REST and WebSocket clients for the Unreal Engine Remote Control API,
procedural CineCamera choreography, Lumen lighting configuration, PBR material
assignment, Movie Render Queue (MRQ) scheduling, and an offline high-fidelity mock server.
"""

from backend.ue5.client import (
    AsyncUE5RemoteClient,
    AsyncUE5RestClient,
    AsyncUE5WebSocketClient,
    UE5RemoteClient,
    UE5RestClient,
    UE5WebSocketClient,
)
from backend.ue5.camera import CineCameraChoreographer, generate_camera_track
from backend.ue5.lighting import (
    LightActorConfig,
    LightingRig,
    LumenLightingSetup,
    setup_lumen_lighting,
)
from backend.ue5.materials import (
    MaterialManager,
    PBRMaterialInstance,
    create_pbr_material,
)
from backend.ue5.mock_server import UE5MockServer, UE5MockState
from backend.ue5.mrq import MRQManager, render_sequence
from backend.ue5.companion import (
    UE5Companion,
    UE5DiagnosticReport,
    UE5PluginStatus,
    UE5SceneBootstrapConfig,
    UE5BootstrapResult,
    generate_default_engine_ini_snippet,
)

__all__ = [
    "AsyncUE5RemoteClient",
    "AsyncUE5RestClient",
    "AsyncUE5WebSocketClient",
    "UE5RemoteClient",
    "UE5RestClient",
    "UE5WebSocketClient",
    "CineCameraChoreographer",
    "generate_camera_track",
    "LightActorConfig",
    "LightingRig",
    "LumenLightingSetup",
    "setup_lumen_lighting",
    "MaterialManager",
    "PBRMaterialInstance",
    "create_pbr_material",
    "UE5MockServer",
    "UE5MockState",
    "MRQManager",
    "render_sequence",
    "UE5Companion",
    "UE5DiagnosticReport",
    "UE5PluginStatus",
    "UE5SceneBootstrapConfig",
    "UE5BootstrapResult",
    "generate_default_engine_ini_snippet",
]

