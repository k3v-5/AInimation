"""Domain asset bridges for Static Mesh, Skeletal Mesh, Textures, Materials, Animation, Niagara, Audio, and Levels."""

from uaf.bridge.ue5.assets.mesh import (
    MeshLODData,
    StaticMeshBridgePayload,
)
from uaf.bridge.ue5.assets.skeletal import (
    BoneNode,
    SocketData,
    SkeletalMeshBridgePayload,
)
from uaf.bridge.ue5.assets.texture import TextureBridgePayload
from uaf.bridge.ue5.assets.material import MaterialBridgePayload
from uaf.bridge.ue5.assets.animation import (
    AnimNotifyEvent,
    AnimationBridgePayload,
)
from uaf.bridge.ue5.assets.niagara import (
    NiagaraEmitterDescriptor,
    NiagaraBridgePayload,
)
from uaf.bridge.ue5.assets.audio import AudioBridgePayload
from uaf.bridge.ue5.assets.levels import LevelBridgePayload

__all__ = [
    "MeshLODData",
    "StaticMeshBridgePayload",
    "BoneNode",
    "SocketData",
    "SkeletalMeshBridgePayload",
    "TextureBridgePayload",
    "MaterialBridgePayload",
    "AnimNotifyEvent",
    "AnimationBridgePayload",
    "NiagaraEmitterDescriptor",
    "NiagaraBridgePayload",
    "AudioBridgePayload",
    "LevelBridgePayload",
]
