"""
Universal Runtime Rendering Validator (UAF-81.75).
Normative validator for camera systems, render graphs, materials, shaders,
culling invariants, and GPU resource lifetimes.
"""

from __future__ import annotations
from typing import List, Dict, Set, Optional

from ..models.definition import (
    RenderCamera,
    RenderLight,
    RenderMesh,
    RenderMaterial,
    RenderableEntity,
    RenderGraph,
    GPUResource,
    RenderWorld,
)


class RenderValidationIssue(str):
    """A string-compatible validation issue with structured error attributes."""

    error_code: str
    message: str
    severity: str

    def __new__(cls, error_code: str, message: str = "", severity: str = "ERROR"):
        full = f"{severity}: [{error_code}] {message}" if message else error_code
        instance = super().__new__(cls, full)
        instance.error_code = error_code
        instance.message = message or error_code
        instance.severity = severity
        return instance


class UniversalRuntimeRenderingValidator:
    """Normative validation of runtime rendering world entities, passes and constraints."""

    def validate_camera(self, camera: RenderCamera) -> List[RenderValidationIssue]:
        errors: List[RenderValidationIssue] = []
        if camera.near_clip <= 0.0:
            errors.append(RenderValidationIssue("INVALID_CAMERA", f"near_clip must be > 0 ({camera.near_clip})."))
        if camera.far_clip <= camera.near_clip:
            errors.append(RenderValidationIssue("INVALID_CAMERA", f"far_clip ({camera.far_clip}) must be > near_clip ({camera.near_clip})."))
        if not (0.0 < camera.fov < 180.0):
            errors.append(RenderValidationIssue("INVALID_CAMERA", f"fov ({camera.fov}) must be in (0, 180)."))
        return errors

    def validate_mesh(self, mesh: RenderMesh) -> List[RenderValidationIssue]:
        errors: List[RenderValidationIssue] = []
        if mesh.lod_count < 1:
            errors.append(RenderValidationIssue("INVALID_MESH", "lod_count must be at least 1."))
        if mesh.bounds_min[0] > mesh.bounds_max[0] or mesh.bounds_min[1] > mesh.bounds_max[1] or mesh.bounds_min[2] > mesh.bounds_max[2]:
            errors.append(RenderValidationIssue("INVALID_MESH", "Inverted bounding box extents."))
        return errors

    def validate_material(self, material: RenderMaterial) -> List[RenderValidationIssue]:
        errors: List[RenderValidationIssue] = []
        if not material.shader_id or not material.shader_id.strip():
            errors.append(RenderValidationIssue("EMPTY_SHADER_ID", "INVALID_MATERIAL: shader_id cannot be empty."))
        for tkey, tval in material.textures.items():
            if not tval or not tval.strip():
                errors.append(RenderValidationIssue("EMPTY_TEXTURE_PATH", f"INVALID_MATERIAL: Texture path for '{tkey}' cannot be empty."))
        return errors

    def validate_renderable(self, renderable: RenderableEntity, world: Optional[RenderWorld] = None) -> List[RenderValidationIssue]:
        errors: List[RenderValidationIssue] = []
        for mid in renderable.material_ids:
            if not mid or not mid.strip():
                errors.append(RenderValidationIssue("EMPTY_MATERIAL_BINDING", "material_ids cannot contain empty string."))
        if world:
            if renderable.mesh_id and renderable.mesh_id not in world.meshes:
                errors.append(RenderValidationIssue("MISSING_MESH", f"Mesh '{renderable.mesh_id}' not found in RenderWorld."))
            for mid in renderable.material_ids:
                if mid and mid not in world.materials:
                    errors.append(RenderValidationIssue("MISSING_MATERIAL", f"Material '{mid}' not found in RenderWorld."))
        return errors

    def validate_gpu_resource(self, resource: GPUResource) -> List[RenderValidationIssue]:
        errors: List[RenderValidationIssue] = []
        if resource.size_bytes <= 0:
            errors.append(RenderValidationIssue("INVALID_GPU_RESOURCE_SIZE", f"size_bytes must be > 0 ({resource.size_bytes})."))
        return errors

    def validate_render_graph(self, graph: RenderGraph) -> List[RenderValidationIssue]:
        errors: List[RenderValidationIssue] = []
        passes = graph.passes
        visited: Dict[str, int] = {}

        def visit(node: str, path: List[str]):
            if visited.get(node) == 0:
                errors.append(RenderValidationIssue("NO_RENDER_GRAPH_CYCLE", f"Cycle detected: {' -> '.join(path + [node])}"))
                return
            if visited.get(node) == 1:
                return

            visited[node] = 0
            p = passes.get(node)
            if p:
                for dep in p.dependencies:
                    if dep in passes:
                        visit(dep, path + [node])
                    else:
                        errors.append(RenderValidationIssue("MISSING_PASS_DEPENDENCY", f"Dependency '{dep}' not in render graph."))
            visited[node] = 1

        for pid in sorted(passes.keys()):
            if pid not in visited:
                visit(pid, [])

        return errors

    def validate_world(self, world: RenderWorld) -> List[RenderValidationIssue]:
        errors: List[RenderValidationIssue] = []
        for cam in world.cameras.values():
            errors.extend(self.validate_camera(cam))
        for m in world.meshes.values():
            errors.extend(self.validate_mesh(m))
        for mat in world.materials.values():
            errors.extend(self.validate_material(mat))
        for r in world.renderables.values():
            errors.extend(self.validate_renderable(r, world))
        for res in world.gpu_resources.values():
            errors.extend(self.validate_gpu_resource(res))
        errors.extend(self.validate_render_graph(world.render_graph))
        return errors
