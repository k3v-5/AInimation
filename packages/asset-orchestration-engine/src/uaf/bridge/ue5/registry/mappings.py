"""Naming conventions and deterministic Unreal Engine package path resolvers."""

from __future__ import annotations
import re
from typing import Optional


class PathSecurityError(Exception):
    """Raised when an asset or package path violates safety invariants."""
    pass


PREFIX_MAP = {
    "StaticMesh": "SM",
    "SkeletalMesh": "SK",
    "Material": "M",
    "MaterialInstance": "MI",
    "Texture": "TX",
    "Texture2D": "TX",
    "NiagaraSystem": "NS",
    "NiagaraEmitter": "NE",
    "Audio": "A",
    "SoundWave": "A",
    "Level": "L",
    "AnimationSequence": "AN",
    "ControlRig": "CR",
    "Actor": "BP",
}


def sanitize_name(name: str) -> str:
    """Replaces spaces and invalid Unreal identifier characters with underscores."""
    sanitized = re.sub(r"[^a-zA-Z0-9_]", "_", name)
    # Collapse consecutive underscores
    sanitized = re.sub(r"_+", "_", sanitized)
    return sanitized.strip("_")


def generate_asset_name(
    asset_type: str,
    semantic_name: str,
    stable_id: str = "",
    variant: str = "",
    lod: str = "",
) -> str:
    """Generates standard Unreal naming e.g. SM_Rock_7A92_LOD0."""
    prefix = PREFIX_MAP.get(asset_type, "UAF")
    safe_sem = sanitize_name(semantic_name) or "Asset"

    parts = [prefix, safe_sem]
    if stable_id:
        short_id = sanitize_name(stable_id)[:6].upper()
        if short_id:
            parts.append(short_id)
    if variant:
        parts.append(sanitize_name(variant))
    if lod:
        parts.append(sanitize_name(lod))
    return "_".join(parts)


def resolve_package_path(
    asset_type: str,
    asset_name: str,
    custom_subfolder: str = "",
    game_prefix: str = "/Game",
) -> str:
    """Computes standard Unreal package paths e.g. /Game/Environment/Rocks/SM_Rock_01."""
    folder_map = {
        "StaticMesh": "Meshes",
        "SkeletalMesh": "Characters",
        "Material": "Materials",
        "MaterialInstance": "Materials",
        "Texture": "Textures",
        "Texture2D": "Textures",
        "NiagaraSystem": "VFX",
        "NiagaraEmitter": "VFX",
        "Audio": "Audio",
        "SoundWave": "Audio",
        "Level": "Maps",
        "AnimationSequence": "Animations",
        "ControlRig": "Rigs",
        "Actor": "Blueprints",
    }
    sub = custom_subfolder or folder_map.get(asset_type, "Assets")
    return f"{game_prefix}/{sub}/{asset_name}"
