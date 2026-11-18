"""
Universal Asset Processing Engine & Fabricator.
Complies with UAF-81.71 specification.
"""

import copy
import hashlib
import json
import math
from pathlib import Path
import re
import time
from typing import Any, Callable, Dict, List, Optional, Set, Tuple

from uaf.universal_processing.models.definition import (
    ResourceType,
    TextureFormat,
    ColorSpace,
    ResizeFilter,
    MipFilter,
    IndexFormat,
    DecimationStrategy,
    AudioFormat,
    ShaderStage,
    ShaderTarget,
    PlatformVariant,
    QualityLevel,
    ProcessingStatus,
    normalize_processing_path,
    ProcessingProfile,
    TextureProcessingProfile,
    MeshProcessingProfile,
    AudioProcessingProfile,
    MaterialProcessingProfile,
    ShaderProcessingProfile,
    DerivedResource,
    LODLevel,
    LODChain,
    ShaderReflectionData,
    ShaderVariant,
    OptimizationPass,
    BuildArtifact,
    BuildManifest,
    ProcessingTelemetry,
    ProcessingStateSnapshot,
    ProcessingDiagnosticBundle,
)


class UniversalProcessingFabricator:
    """Core fabricator coordinating all asset processing products and derived resource generation."""

    def __init__(self, cache_limit_mb: int = 2048):
        self.cache_limit_mb = cache_limit_mb
        self.profiles: Dict[str, ProcessingProfile] = {}
        self.derived_resources: Dict[str, DerivedResource] = {}
        self.artifacts: Dict[str, BuildArtifact] = {}
        self.optimization_passes: Dict[str, OptimizationPass] = {}
        self.shader_sources: Dict[str, str] = {}
        self.cache: Dict[str, DerivedResource] = {}
        self.telemetry = ProcessingTelemetry()
        self._register_default_passes()

    def _register_default_passes(self) -> None:
        self.register_optimization_pass(OptimizationPass(
            pass_id="vertex_cache_optimizer",
            version="1.0.0",
            supported_types=[ResourceType.MESH],
            settings={"algorithm": "tipsify", "cache_size": 32}
        ))
        self.register_optimization_pass(OptimizationPass(
            pass_id="texture_crunch",
            version="1.0.0",
            supported_types=[ResourceType.TEXTURE],
            settings={"level": 5}
        ))

    # --------------------------------------------------------------------------
    # Profiles & Registries
    # --------------------------------------------------------------------------

    def register_profile(self, profile: ProcessingProfile) -> None:
        self.profiles[profile.profile_id] = profile

    def get_profile(self, profile_id: str) -> Optional[ProcessingProfile]:
        return self.profiles.get(profile_id)

    def register_optimization_pass(self, opt_pass: OptimizationPass) -> None:
        self.optimization_passes[opt_pass.pass_id] = opt_pass

    def register_shader_source(self, shader_id: str, source_code: str) -> None:
        self.shader_sources[shader_id] = source_code

    # --------------------------------------------------------------------------
    # Caching & Deterministic Fingerprints
    # --------------------------------------------------------------------------

    def compute_cache_key(
        self,
        source_id: str,
        profile_hash: str,
        platform: PlatformVariant,
        quality: QualityLevel,
        extra_fingerprint: str = ""
    ) -> str:
        payload = f"{source_id}:{profile_hash}:{platform.value}:{quality.value}:{extra_fingerprint}"
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    # --------------------------------------------------------------------------
    # 1. Texture Processing
    # --------------------------------------------------------------------------

    def generate_mipmaps(self, width: int, height: int, min_dim: int = 1) -> List[Tuple[int, int]]:
        """Generates deterministic mipmap levels from (width, height) down to min_dim."""
        if width <= 0 or height <= 0:
            raise ValueError("INVALID_DIMENSIONS: Width and height must be positive integers.")
        mips: List[Tuple[int, int]] = []
        w, h = width, height
        while True:
            mips.append((w, h))
            if w <= min_dim and h <= min_dim:
                break
            w = max(min_dim, w // 2)
            h = max(min_dim, h // 2)
        return mips

    def pack_channels(
        self,
        channels: Dict[str, Tuple[str, str]],
        target_dim: Tuple[int, int] = (256, 256)
    ) -> bytes:
        """Simulates packing separate texture channels into a single RGBA byte array."""
        for c in ["R", "G", "B", "A"]:
            if c in channels:
                src_id, ch = channels[c]
                if ch not in ["R", "G", "B", "A"]:
                    raise ValueError(f"INVALID_CHANNEL: Invalid source channel '{ch}'.")
        sorted_keys = sorted(channels.keys())
        packed_payload = f"PACKED:{target_dim[0]}x{target_dim[1]}:" + ",".join(
            f"{k}={channels[k][0]}:{channels[k][1]}" for k in sorted_keys
        )
        return packed_payload.encode("utf-8")

    def process_texture(
        self,
        source_id: str,
        raw_data: bytes,
        profile: TextureProcessingProfile,
        platform: PlatformVariant = PlatformVariant.DEFAULT,
        quality: QualityLevel = QualityLevel.HIGH,
        original_width: int = 1024,
        original_height: int = 1024
    ) -> DerivedResource:
        """Processes texture: validates, resizes, generates mipmaps, compresses."""
        # Validation
        if len(raw_data) == 0:
            self.telemetry.failure_count += 1
            raise ValueError("EMPTY_TEXTURE_DATA: Texture data buffer is empty.")
        if original_width <= 0 or original_height <= 0:
            self.telemetry.failure_count += 1
            raise ValueError("INVALID_DIMENSIONS: Texture dimensions must be positive.")
        if len(raw_data) > 256 * 1024 * 1024:
            self.telemetry.failure_count += 1
            raise ValueError("TEXTURE_BOMB_EXCEEDED: Raw texture data exceeds maximum safety limit.")

        cache_key = self.compute_cache_key(source_id, profile.compute_hash(), platform, quality)
        if cache_key in self.cache:
            self.telemetry.cache_hits += 1
            return self.cache[cache_key]

        self.telemetry.cache_misses += 1

        # Resize calculations
        target_w = min(original_width, profile.max_width)
        target_h = min(original_height, profile.max_height)

        # Mipmap calculation
        mip_levels = self.generate_mipmaps(target_w, target_h) if profile.generate_mipmaps else [(target_w, target_h)]

        # Payload simulation
        meta = {
            "width": target_w,
            "height": target_h,
            "mip_count": len(mip_levels),
            "format": profile.target_format.value,
            "color_space": profile.color_space.value,
            "is_normal_map": profile.is_normal_map,
            "compression_quality": profile.compression_quality,
        }
        derived_id = f"tex_derived_{source_id}_{platform.value}_{quality.value}"
        payload_str = f"{derived_id}:{json.dumps(meta, sort_keys=True)}"
        out_hash = hashlib.sha256(payload_str.encode("utf-8")).hexdigest()

        resource = DerivedResource(
            derived_resource_id=derived_id,
            source_asset_id=source_id,
            resource_type=ResourceType.TEXTURE,
            processor_id="UniversalTextureProcessor",
            processor_version="1.0.0",
            profile_id=profile.profile_id,
            fingerprint=cache_key,
            output_hash=out_hash,
            platform=platform,
            quality=quality,
            data=payload_str.encode("utf-8"),
            metadata=meta,
        )
        self.derived_resources[derived_id] = resource
        self.cache[cache_key] = resource
        self.telemetry.processed_count += 1
        self.telemetry.total_output_bytes += len(resource.data)
        return resource

    # --------------------------------------------------------------------------
    # 2. Mesh Processing
    # --------------------------------------------------------------------------

    def validate_mesh_topology(
        self,
        vertices: List[List[float]],
        indices: List[int]
    ) -> Tuple[bool, List[str]]:
        errors = []
        if len(vertices) == 0:
            errors.append("EMPTY_VERTICES: Vertex buffer is empty.")
        if len(indices) == 0 or len(indices) % 3 != 0:
            errors.append("INVALID_INDICES_COUNT: Index count must be a non-zero multiple of 3.")
        num_v = len(vertices)
        for idx in indices:
            if idx < 0 or idx >= num_v:
                errors.append(f"INDEX_OUT_OF_BOUNDS: Index {idx} out of range [0, {num_v - 1}].")
                break
        return len(errors) == 0, errors

    def cleanup_mesh(
        self,
        vertices: List[List[float]],
        indices: List[int]
    ) -> Tuple[List[List[float]], List[int], int]:
        """Removes degenerate triangles (where two or more indices are identical)."""
        clean_indices = []
        degenerate_count = 0
        for i in range(0, len(indices), 3):
            i0, i1, i2 = indices[i], indices[i+1], indices[i+2]
            if i0 == i1 or i1 == i2 or i0 == i2:
                degenerate_count += 1
            else:
                clean_indices.extend([i0, i1, i2])
        return vertices, clean_indices, degenerate_count

    def generate_lod_chain(
        self,
        mesh_id: str,
        vertices: List[List[float]],
        indices: List[int],
        profile: MeshProcessingProfile
    ) -> LODChain:
        chain = LODChain(chain_id=f"lod_chain_{mesh_id}", source_mesh_id=mesh_id)
        # LOD0 is base
        base_tri_count = len(indices) // 3
        h0 = hashlib.sha256(f"LOD0:{mesh_id}:{len(vertices)}:{base_tri_count}".encode("utf-8")).hexdigest()
        chain.levels.append(LODLevel(
            level=0,
            triangle_ratio=1.0,
            screen_size=1.0,
            vertex_count=len(vertices),
            triangle_count=base_tri_count,
            output_hash=h0
        ))

        # Additional LODs
        for lod_spec in profile.lod_levels:
            lvl = lod_spec.get("level", len(chain.levels))
            ratio = lod_spec.get("ratio", max(0.1, 1.0 - lvl * 0.25))
            screen = lod_spec.get("screen_size", max(0.05, 1.0 - lvl * 0.3))
            tri_count = max(1, int(base_tri_count * ratio))
            vert_count = max(3, int(len(vertices) * ratio))
            hl = hashlib.sha256(f"LOD{lvl}:{mesh_id}:{vert_count}:{tri_count}".encode("utf-8")).hexdigest()
            chain.levels.append(LODLevel(
                level=lvl,
                triangle_ratio=ratio,
                screen_size=screen,
                vertex_count=vert_count,
                triangle_count=tri_count,
                output_hash=hl
            ))
        return chain

    def process_mesh(
        self,
        source_id: str,
        vertices: List[List[float]],
        indices: List[int],
        profile: MeshProcessingProfile,
        platform: PlatformVariant = PlatformVariant.DEFAULT,
        quality: QualityLevel = QualityLevel.HIGH
    ) -> Tuple[DerivedResource, LODChain]:
        ok, errs = self.validate_mesh_topology(vertices, indices)
        if not ok:
            self.telemetry.failure_count += 1
            raise ValueError(f"MESH_VALIDATION_FAILED: {errs[0]}")

        cache_key = self.compute_cache_key(source_id, profile.compute_hash(), platform, quality)
        if cache_key in self.cache:
            self.telemetry.cache_hits += 1
            res = self.cache[cache_key]
            lod_chain = self.generate_lod_chain(source_id, vertices, indices, profile)
            return res, lod_chain

        self.telemetry.cache_misses += 1

        v_clean, idx_clean, deg_removed = self.cleanup_mesh(vertices, indices) if profile.remove_degenerates else (vertices, indices, 0)
        lod_chain = self.generate_lod_chain(source_id, v_clean, idx_clean, profile)

        meta = {
            "vertex_count": len(v_clean),
            "triangle_count": len(idx_clean) // 3,
            "degenerates_removed": deg_removed,
            "lod_count": len(lod_chain.levels),
            "normals_generated": profile.generate_normals,
            "tangents_generated": profile.generate_tangents,
            "index_format": profile.index_format.value,
        }
        derived_id = f"mesh_derived_{source_id}_{platform.value}_{quality.value}"
        payload_str = f"{derived_id}:{json.dumps(meta, sort_keys=True)}"
        out_hash = hashlib.sha256(payload_str.encode("utf-8")).hexdigest()

        resource = DerivedResource(
            derived_resource_id=derived_id,
            source_asset_id=source_id,
            resource_type=ResourceType.MESH,
            processor_id="UniversalMeshProcessor",
            processor_version="1.0.0",
            profile_id=profile.profile_id,
            fingerprint=cache_key,
            output_hash=out_hash,
            platform=platform,
            quality=quality,
            data=payload_str.encode("utf-8"),
            metadata=meta,
        )
        self.derived_resources[derived_id] = resource
        self.cache[cache_key] = resource
        self.telemetry.processed_count += 1
        return resource, lod_chain

    # --------------------------------------------------------------------------
    # 3. Audio Processing
    # --------------------------------------------------------------------------

    def process_audio(
        self,
        source_id: str,
        audio_data: bytes,
        profile: AudioProcessingProfile,
        platform: PlatformVariant = PlatformVariant.DEFAULT,
        quality: QualityLevel = QualityLevel.HIGH,
        original_sample_rate: int = 44100,
        original_channels: int = 2
    ) -> DerivedResource:
        if len(audio_data) == 0:
            self.telemetry.failure_count += 1
            raise ValueError("EMPTY_AUDIO_DATA: Audio payload is empty.")

        cache_key = self.compute_cache_key(source_id, profile.compute_hash(), platform, quality)
        if cache_key in self.cache:
            self.telemetry.cache_hits += 1
            return self.cache[cache_key]

        self.telemetry.cache_misses += 1

        meta = {
            "source_sample_rate": original_sample_rate,
            "target_sample_rate": profile.target_sample_rate,
            "channels": profile.target_channels,
            "bit_depth": profile.bit_depth,
            "normalized_db": profile.target_db if profile.normalize_loudness else 0.0,
            "codec": profile.codec.value,
            "loop_preserved": profile.preserve_loop_metadata,
        }
        derived_id = f"audio_derived_{source_id}_{platform.value}_{quality.value}"
        payload_str = f"{derived_id}:{json.dumps(meta, sort_keys=True)}"
        out_hash = hashlib.sha256(payload_str.encode("utf-8")).hexdigest()

        resource = DerivedResource(
            derived_resource_id=derived_id,
            source_asset_id=source_id,
            resource_type=ResourceType.AUDIO,
            processor_id="UniversalAudioProcessor",
            processor_version="1.0.0",
            profile_id=profile.profile_id,
            fingerprint=cache_key,
            output_hash=out_hash,
            platform=platform,
            quality=quality,
            data=payload_str.encode("utf-8"),
            metadata=meta,
        )
        self.derived_resources[derived_id] = resource
        self.cache[cache_key] = resource
        self.telemetry.processed_count += 1
        return resource

    # --------------------------------------------------------------------------
    # 4. Material Compilation
    # --------------------------------------------------------------------------

    def compile_material(
        self,
        source_id: str,
        profile: MaterialProcessingProfile,
        platform: PlatformVariant = PlatformVariant.DEFAULT,
        quality: QualityLevel = QualityLevel.HIGH
    ) -> DerivedResource:
        cache_key = self.compute_cache_key(source_id, profile.compute_hash(), platform, quality)
        if cache_key in self.cache:
            self.telemetry.cache_hits += 1
            return self.cache[cache_key]

        self.telemetry.cache_misses += 1

        meta = {
            "shader_reference": profile.shader_reference,
            "parameter_count": len(profile.parameter_overrides),
            "texture_slot_count": len(profile.texture_slots),
            "variant_defines": profile.variant_defines,
        }
        derived_id = f"mat_derived_{source_id}_{platform.value}_{quality.value}"
        payload_str = f"{derived_id}:{json.dumps(meta, sort_keys=True)}"
        out_hash = hashlib.sha256(payload_str.encode("utf-8")).hexdigest()

        resource = DerivedResource(
            derived_resource_id=derived_id,
            source_asset_id=source_id,
            resource_type=ResourceType.MATERIAL,
            processor_id="UniversalMaterialCompiler",
            processor_version="1.0.0",
            profile_id=profile.profile_id,
            fingerprint=cache_key,
            output_hash=out_hash,
            platform=platform,
            quality=quality,
            data=payload_str.encode("utf-8"),
            metadata=meta,
        )
        self.derived_resources[derived_id] = resource
        self.cache[cache_key] = resource
        self.telemetry.processed_count += 1
        return resource

    # --------------------------------------------------------------------------
    # 5. Shader Preprocessing & Compilation
    # --------------------------------------------------------------------------

    def preprocess_shader(
        self,
        source_code: str,
        defines: Dict[str, str],
        include_map: Optional[Dict[str, str]] = None,
        included_stack: Optional[Set[str]] = None
    ) -> str:
        """Preprocesses shader source resolving #include statements and detecting cycles."""
        include_map = include_map or {}
        included_stack = included_stack or set()

        processed_lines = []
        for line in source_code.splitlines():
            inc_match = re.match(r'^\s*#include\s+["<]([^">]+)[">]', line)
            if inc_match:
                inc_file = inc_match.group(1).strip()
                if inc_file in included_stack:
                    raise ValueError(f"INCLUDE_CYCLE_DETECTED: Recursive include cycle for '{inc_file}'.")
                if inc_file not in include_map:
                    raise ValueError(f"INCLUDE_NOT_FOUND: Included shader file '{inc_file}' not found.")
                included_stack.add(inc_file)
                expanded = self.preprocess_shader(include_map[inc_file], defines, include_map, included_stack)
                included_stack.remove(inc_file)
                processed_lines.append(expanded)
            else:
                # Apply defines substitution
                for d_k, d_v in defines.items():
                    line = re.sub(rf'\b{d_k}\b', str(d_v), line)
                processed_lines.append(line)

        return "\n".join(processed_lines)

    def extract_shader_reflection(self, source_code: str) -> ShaderReflectionData:
        refl = ShaderReflectionData()
        # Split by semicolons or lines to handle multiple statements
        statements = [s.strip() for line in source_code.splitlines() for s in line.split(";") if s.strip()]
        for stmt in statements:
            if stmt.startswith("uniform"):
                parts = stmt.split()
                if len(parts) >= 3:
                    refl.uniforms.append({"type": parts[1], "name": parts[2]})
            elif stmt.startswith("Texture2D"):
                parts = stmt.split()
                if len(parts) >= 2:
                    refl.samplers.append({"type": "Texture2D", "name": parts[1]})
        return refl

    def compile_shader(
        self,
        source_id: str,
        source_code: str,
        profile: ShaderProcessingProfile,
        include_map: Optional[Dict[str, str]] = None,
        platform: PlatformVariant = PlatformVariant.DEFAULT,
        quality: QualityLevel = QualityLevel.HIGH
    ) -> Tuple[DerivedResource, List[ShaderVariant]]:
        if not source_code.strip():
            self.telemetry.failure_count += 1
            raise ValueError("EMPTY_SHADER_SOURCE: Shader source is empty.")

        preprocessed = self.preprocess_shader(source_code, profile.defines, include_map)
        reflection = self.extract_shader_reflection(preprocessed)

        cache_key = self.compute_cache_key(source_id, profile.compute_hash(), platform, quality, extra_fingerprint=preprocessed)
        if cache_key in self.cache:
            self.telemetry.cache_hits += 1
            res = self.cache[cache_key]
            v = ShaderVariant(
                variant_id=f"var_{source_id}_default",
                defines=profile.defines,
                bytecode_hash=res.output_hash,
                reflection=reflection
            )
            return res, [v]

        self.telemetry.cache_misses += 1

        # Compile variants
        variants: List[ShaderVariant] = []
        variant_limit = profile.max_variants
        v0_hash = hashlib.sha256(f"BYTECODE:{source_id}:{preprocessed}:{platform.value}".encode("utf-8")).hexdigest()
        v0 = ShaderVariant(
            variant_id=f"var_{source_id}_0",
            defines=profile.defines,
            bytecode_hash=v0_hash,
            reflection=reflection
        )
        variants.append(v0)

        derived_id = f"shader_derived_{source_id}_{platform.value}_{quality.value}"
        meta = {
            "stage": profile.target_stage.value,
            "target_profile": profile.target_profile.value,
            "entry_point": profile.entry_point,
            "variant_count": len(variants),
            "uniform_count": len(reflection.uniforms),
            "sampler_count": len(reflection.samplers),
        }
        resource = DerivedResource(
            derived_resource_id=derived_id,
            source_asset_id=source_id,
            resource_type=ResourceType.SHADER,
            processor_id="UniversalShaderCompiler",
            processor_version="1.0.0",
            profile_id=profile.profile_id,
            fingerprint=cache_key,
            output_hash=v0_hash,
            platform=platform,
            quality=quality,
            data=v0_hash.encode("utf-8"),
            metadata=meta,
        )
        self.derived_resources[derived_id] = resource
        self.cache[cache_key] = resource
        self.telemetry.processed_count += 1
        return resource, variants

    # --------------------------------------------------------------------------
    # 6. Optimization Passes
    # --------------------------------------------------------------------------

    def run_optimization_passes(
        self,
        resource: DerivedResource,
        pass_ids: List[str]
    ) -> DerivedResource:
        current_res = resource
        for pid in pass_ids:
            if pid not in self.optimization_passes:
                raise ValueError(f"PASS_NOT_FOUND: Optimization pass '{pid}' is not registered.")
            op = self.optimization_passes[pid]
            if current_res.resource_type not in op.supported_types:
                raise ValueError(f"PASS_INCOMPATIBLE: Pass '{pid}' does not support resource type '{current_res.resource_type.value}'.")
            
            # Apply pass mutation deterministically
            new_hash = hashlib.sha256(f"{current_res.output_hash}:{pid}".encode("utf-8")).hexdigest()
            current_res = DerivedResource(
                derived_resource_id=current_res.derived_resource_id,
                source_asset_id=current_res.source_asset_id,
                resource_type=current_res.resource_type,
                processor_id=current_res.processor_id,
                processor_version=current_res.processor_version,
                profile_id=current_res.profile_id,
                fingerprint=current_res.fingerprint,
                output_hash=new_hash,
                platform=current_res.platform,
                quality=current_res.quality,
                data=current_res.data,
                metadata={**current_res.metadata, "last_optimization_pass": pid},
            )
        return current_res

    # --------------------------------------------------------------------------
    # 7. Build Artifacts & Packaging
    # --------------------------------------------------------------------------

    def create_build_artifact(
        self,
        derived_resource: DerivedResource,
        output_path: str
    ) -> BuildArtifact:
        norm_path = normalize_processing_path(output_path)
        art_id = f"art_{derived_resource.derived_resource_id}"
        art = BuildArtifact(
            artifact_id=art_id,
            source_id=derived_resource.source_asset_id,
            derived_resource_id=derived_resource.derived_resource_id,
            platform=derived_resource.platform,
            quality=derived_resource.quality,
            output_path=norm_path,
            content_hash=derived_resource.output_hash,
            size_bytes=len(derived_resource.data),
            metadata=derived_resource.metadata,
        )
        self.artifacts[art_id] = art
        return art

    def generate_build_manifest(self, artifacts: List[BuildArtifact]) -> BuildManifest:
        man_id = f"manifest_{int(time.time() * 1000)}"
        return BuildManifest(manifest_id=man_id, artifacts=artifacts)

    # --------------------------------------------------------------------------
    # 8. Housekeeping & Garbage Collection
    # --------------------------------------------------------------------------

    def detect_orphans(self, valid_source_ids: Set[str]) -> List[str]:
        return [
            rid for rid, res in self.derived_resources.items()
            if res.source_asset_id not in valid_source_ids
        ]

    def garbage_collect(self, valid_source_ids: Set[str]) -> int:
        orphans = self.detect_orphans(valid_source_ids)
        for rid in orphans:
            res = self.derived_resources.pop(rid)
            self.cache.pop(res.fingerprint, None)
        return len(orphans)

    # --------------------------------------------------------------------------
    # 9. Diagnostics & Snapshots
    # --------------------------------------------------------------------------

    def take_snapshot(self) -> ProcessingStateSnapshot:
        snap_id = f"snap_proc_{int(time.time() * 1000)}"
        res_dict = {rid: res.to_dict() for rid, res in self.derived_resources.items()}
        art_dict = {aid: vars(art) for aid, art in self.artifacts.items()}
        return ProcessingStateSnapshot(
            snapshot_id=snap_id,
            timestamp=time.time(),
            resources=res_dict,
            artifacts=art_dict
        )

    def generate_diagnostic_bundle(self) -> ProcessingDiagnosticBundle:
        b_id = f"bundle_proc_{int(time.time() * 1000)}"
        snap = self.take_snapshot()
        return ProcessingDiagnosticBundle(
            bundle_id=b_id,
            timestamp=time.time(),
            snapshot=snap,
            telemetry=self.telemetry
        )
