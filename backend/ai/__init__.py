"""
Generative AI Subsystems Package for IANIMATION.

Modular, plug-and-play AI adapters for audio analysis, image-to-3d generation,
auto-rigging, motion capture extraction, rotoscopy, and neural rendering.
"""

from backend.ai.base import BaseAIProvider, ProviderRegistry, provider_registry
from backend.ai.async_engine import AsyncTaskSupervisor, CancellationToken
from backend.ai.audio import AudioAnalyzer, AudioSeparator, analyze_audio, separate_stems
from backend.ai.image_to_3d import (
    FalAIProvider,
    ImageTo3DProvider,
    ProceduralGLBProvider,
    TripoProvider,
    generate_procedural_glb,
)
from backend.ai.auto_rig import AutoRigger, auto_rig
from backend.ai.mocap import (
    MocapExtractor,
    extract_mocap,
    generate_dance_loop,
    remove_background,
    rotoscope_video,
)
from backend.ai.neural import ComfyUIClient, NeuralEnhancer, enhance_video
from backend.ai.advanced_kinematics import (
    BipedalWalkCycleParams,
    CollisionCapsule,
    IKChainSpec,
    JointLimit,
    KinematicRigResult,
    generate_bipedal_walk_cycle,
    get_standard_collision_hulls,
    get_standard_joint_limits,
    resolve_capsule_interpenetration,
    solve_two_bone_ik,
)

__all__ = [
    "BaseAIProvider",
    "ProviderRegistry",
    "provider_registry",
    "AsyncTaskSupervisor",
    "CancellationToken",
    "AudioAnalyzer",
    "AudioSeparator",
    "analyze_audio",
    "separate_stems",
    "ImageTo3DProvider",
    "FalAIProvider",
    "TripoProvider",
    "ProceduralGLBProvider",
    "generate_procedural_glb",
    "AutoRigger",
    "auto_rig",
    "MocapExtractor",
    "extract_mocap",
    "generate_dance_loop",
    "remove_background",
    "rotoscope_video",
    "ComfyUIClient",
    "NeuralEnhancer",
    "enhance_video",
    "BipedalWalkCycleParams",
    "CollisionCapsule",
    "IKChainSpec",
    "JointLimit",
    "KinematicRigResult",
    "generate_bipedal_walk_cycle",
    "get_standard_collision_hulls",
    "get_standard_joint_limits",
    "resolve_capsule_interpenetration",
    "solve_two_bone_ik",
]
