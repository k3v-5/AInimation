"""
Universal Runtime Rendering Fabricator and Pipeline Engine (UAF-81.75).
Core engine for camera systems, culling, LOD selection, draw submission,
render graph scheduling, GPU resource management, and frame synchronization.
"""

from __future__ import annotations
import copy
import hashlib
import json
import math
from typing import Any, Callable, Dict, List, Optional, Set, Tuple

from ..models.definition import (
    RenderWorldState,
    CameraProjection,
    LightType,
    RenderQueueType,
    SortMode,
    ResourceState,
    BufferType,
    TextureFormat,
    RenderCamera,
    RenderLight,
    RenderMesh,
    RenderMaterial,
    RenderableEntity,
    DrawCommand,
    RenderPass,
    RenderGraph,
    GPUResource,
    RenderFrame,
    RenderWorldSettings,
    RenderWorld,
)


def _vec3_dist(a: List[float], b: List[float]) -> float:
    return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2 + (a[2] - b[2]) ** 2)


def _vec3_sub(a: List[float], b: List[float]) -> List[float]:
    return [a[0] - b[0], a[1] - b[1], a[2] - b[2]]


def _vec3_dot(a: List[float], b: List[float]) -> float:
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


class UniversalRuntimeRenderingFabricator:
    """Fabricates and drives the runtime rendering world and GPU pipeline abstraction."""

    def __init__(self):
        self.worlds: Dict[str, RenderWorld] = {}
        self.active_world: Optional[RenderWorld] = None
        self._command_counter: int = 0

    # --------------------------------------------------------------------------
    # 1. Render World Lifecycle
    # --------------------------------------------------------------------------

    def create_world(
        self,
        render_world_id: str,
        runtime_world_id: str = "",
        settings: Optional[RenderWorldSettings] = None,
    ) -> RenderWorld:
        if not render_world_id or not render_world_id.strip():
            raise ValueError("INVALID_RENDER_WORLD_ID: World ID cannot be empty.")
        if render_world_id in self.worlds:
            raise ValueError(f"DUPLICATE_RENDER_WORLD_ID: World '{render_world_id}' already exists.")

        world = RenderWorld(
            render_world_id=render_world_id,
            runtime_world_id=runtime_world_id,
            state=RenderWorldState.CREATED,
            settings=settings or RenderWorldSettings(),
        )
        self.worlds[render_world_id] = world
        self.active_world = world
        return world

    create_render_world = create_world

    def advance_state(self, world_id_or_world: Any, new_state: RenderWorldState) -> None:
        if isinstance(world_id_or_world, str):
            target = self.worlds.get(world_id_or_world)
        else:
            target = world_id_or_world or self.active_world
        if not target:
            raise ValueError("NO_ACTIVE_WORLD")
        target.state = new_state

    def reset(self) -> None:
        self.worlds.clear()
        self.active_world = None
        self._command_counter = 0

    def get_world(self, render_world_id: str) -> Optional[RenderWorld]:
        return self.worlds.get(render_world_id)

    def initialize_world(self, world: Optional[RenderWorld] = None) -> None:
        target = world or self.active_world
        if not target:
            raise ValueError("NO_ACTIVE_WORLD")
        if target.state not in (RenderWorldState.CREATED, RenderWorldState.INITIALIZING):
            raise ValueError(f"NO_INVALID_RENDER_WORLD_TRANSITION: Cannot initialize from '{target.state.value}'.")

        target.state = RenderWorldState.READY
        target.content_fingerprint = target.compute_fingerprint()

    def start_rendering(self, world: Optional[RenderWorld] = None) -> None:
        target = world or self.active_world
        if not target:
            raise ValueError("NO_ACTIVE_WORLD")
        if target.state not in (RenderWorldState.READY, RenderWorldState.PAUSED, RenderWorldState.STOPPED):
            raise ValueError(f"NO_INVALID_RENDER_WORLD_TRANSITION: Cannot start rendering from '{target.state.value}'.")

        target.state = RenderWorldState.RENDERING

    def pause_rendering(self, world: Optional[RenderWorld] = None) -> None:
        target = world or self.active_world
        if not target:
            raise ValueError("NO_ACTIVE_WORLD")
        if target.state != RenderWorldState.RENDERING:
            raise ValueError(f"NO_INVALID_RENDER_WORLD_TRANSITION: Cannot pause from '{target.state.value}'.")

        target.state = RenderWorldState.PAUSED

    def stop_rendering(self, world: Optional[RenderWorld] = None) -> None:
        target = world or self.active_world
        if not target:
            raise ValueError("NO_ACTIVE_WORLD")
        if target.state not in (RenderWorldState.RENDERING, RenderWorldState.PAUSED):
            raise ValueError(f"NO_INVALID_RENDER_WORLD_TRANSITION: Cannot stop from '{target.state.value}'.")

        target.state = RenderWorldState.STOPPED

    def destroy_world(self, world: Optional[RenderWorld] = None) -> None:
        target = world or self.active_world
        if not target:
            raise ValueError("NO_ACTIVE_WORLD")

        target.renderables.clear()
        target.cameras.clear()
        target.lights.clear()
        target.materials.clear()
        target.meshes.clear()
        target.gpu_resources.clear()
        target.render_graph.passes.clear()
        target.render_graph.execution_order.clear()
        target.state = RenderWorldState.DESTROYED

    # --------------------------------------------------------------------------
    # 2. Renderable Entities
    # --------------------------------------------------------------------------

    def create_renderable(
        self,
        renderable_id: str,
        entity_id: str,
        mesh_id: str,
        material_ids: Optional[List[str]] = None,
        position: Optional[List[float]] = None,
        rotation: Optional[List[float]] = None,
        scale: Optional[List[float]] = None,
        bounds_min: Optional[List[float]] = None,
        bounds_max: Optional[List[float]] = None,
        layer: int = 1,
        cast_shadows: bool = True,
        world: Optional[RenderWorld] = None,
    ) -> RenderableEntity:
        target = world or self.active_world
        if not target:
            raise ValueError("NO_ACTIVE_WORLD")
        if not renderable_id or not renderable_id.strip():
            raise ValueError("INVALID_RENDERABLE_ID")
        if renderable_id in target.renderables:
            raise ValueError(f"DUPLICATE_RENDERABLE_ID: '{renderable_id}'")
        if len(target.renderables) >= target.settings.max_renderables:
            raise ValueError("SECURITY_VIOLATION: Max renderables exceeded.")

        r = RenderableEntity(
            renderable_id=renderable_id,
            entity_id=entity_id,
            mesh_id=mesh_id,
            material_ids=material_ids or [],
            position=position or [0.0, 0.0, 0.0],
            rotation=rotation or [0.0, 0.0, 0.0, 1.0],
            scale=scale or [1.0, 1.0, 1.0],
            bounds_min=bounds_min or [-1.0, -1.0, -1.0],
            bounds_max=bounds_max or [1.0, 1.0, 1.0],
            layer=layer,
            cast_shadows=cast_shadows,
        )
        target.renderables[renderable_id] = r
        return r

    def set_renderable_visibility(self, renderable_id: str, visible: bool, world: Optional[RenderWorld] = None) -> None:
        target = world or self.active_world
        if not target or renderable_id not in target.renderables:
            raise ValueError(f"RENDERABLE_NOT_FOUND: '{renderable_id}'")
        target.renderables[renderable_id].visible = visible

    def set_renderable_transform(
        self,
        renderable_id: str,
        position: List[float],
        rotation: Optional[List[float]] = None,
        scale: Optional[List[float]] = None,
        world: Optional[RenderWorld] = None,
    ) -> None:
        target = world or self.active_world
        if not target or renderable_id not in target.renderables:
            raise ValueError(f"RENDERABLE_NOT_FOUND: '{renderable_id}'")
        r = target.renderables[renderable_id]
        r.position = list(position)
        if rotation:
            r.rotation = list(rotation)
        if scale:
            r.scale = list(scale)

    def destroy_renderable(self, renderable_id: str, world: Optional[RenderWorld] = None) -> None:
        target = world or self.active_world
        if not target:
            raise ValueError("NO_ACTIVE_WORLD")
        if renderable_id not in target.renderables:
            raise ValueError(f"RENDERABLE_NOT_FOUND: '{renderable_id}'")
        target.destroyed_renderable_ids.add(renderable_id)
        del target.renderables[renderable_id]

    # --------------------------------------------------------------------------
    # 3. Camera Management
    # --------------------------------------------------------------------------

    def create_camera(
        self,
        camera_id: str,
        entity_id: str = "",
        projection: CameraProjection = CameraProjection.PERSPECTIVE,
        fov: float = 60.0,
        near_clip: float = 0.1,
        far_clip: float = 1000.0,
        ortho_width: float = 10.0,
        position: Optional[List[float]] = None,
        rotation: Optional[List[float]] = None,
        world: Optional[RenderWorld] = None,
    ) -> RenderCamera:
        target = world or self.active_world
        if not target:
            raise ValueError("NO_ACTIVE_WORLD")
        if not camera_id or not camera_id.strip():
            raise ValueError("INVALID_CAMERA_ID")
        if camera_id in target.cameras:
            raise ValueError(f"DUPLICATE_CAMERA_ID: '{camera_id}'")
        if len(target.cameras) >= target.settings.max_cameras:
            raise ValueError("SECURITY_VIOLATION: Max cameras exceeded.")

        if near_clip <= 0.0 or far_clip <= near_clip:
            raise ValueError(f"INVALID_CAMERA_PARAMETERS: near ({near_clip}) and far ({far_clip}) invalid.")
        if fov <= 0.0 or fov >= 180.0:
            raise ValueError(f"INVALID_CAMERA_PARAMETERS: fov ({fov}) must be in (0, 180).")

        cam = RenderCamera(
            camera_id=camera_id,
            entity_id=entity_id,
            projection=projection,
            fov=fov,
            near_clip=near_clip,
            far_clip=far_clip,
            ortho_width=ortho_width,
            position=position or [0.0, 0.0, 0.0],
            rotation=rotation or [0.0, 0.0, 0.0, 1.0],
        )
        target.cameras[camera_id] = cam
        if not target.active_camera_id:
            target.active_camera_id = camera_id
        return cam

    def set_active_camera(self, camera_id: str, world: Optional[RenderWorld] = None) -> None:
        target = world or self.active_world
        if not target or camera_id not in target.cameras:
            raise ValueError(f"CAMERA_NOT_FOUND: '{camera_id}'")
        target.active_camera_id = camera_id

    def destroy_camera(self, camera_id: str, world: Optional[RenderWorld] = None) -> None:
        target = world or self.active_world
        if not target or camera_id not in target.cameras:
            raise ValueError(f"CAMERA_NOT_FOUND: '{camera_id}'")
        del target.cameras[camera_id]
        if target.active_camera_id == camera_id:
            target.active_camera_id = next(iter(target.cameras.keys()), None)

    # --------------------------------------------------------------------------
    # 4. Light Management
    # --------------------------------------------------------------------------

    def create_light(
        self,
        light_id: str,
        light_type: LightType = LightType.DIRECTIONAL,
        color: Optional[List[float]] = None,
        intensity: float = 1.0,
        range: float = 10.0,
        position: Optional[List[float]] = None,
        direction: Optional[List[float]] = None,
        casts_shadows: bool = True,
        enabled: bool = True,
        world: Optional[RenderWorld] = None,
    ) -> RenderLight:
        target = world or self.active_world
        if not target:
            raise ValueError("NO_ACTIVE_WORLD")
        if not light_id or not light_id.strip():
            raise ValueError("INVALID_LIGHT_ID")
        if light_id in target.lights:
            raise ValueError(f"DUPLICATE_LIGHT_ID: '{light_id}'")
        if len(target.lights) >= target.settings.max_lights:
            raise ValueError("SECURITY_VIOLATION: Max lights exceeded.")
        if intensity < 0.0:
            raise ValueError("INVALID_LIGHT_PARAMETERS: Intensity cannot be negative.")

        light = RenderLight(
            light_id=light_id,
            light_type=light_type,
            color=color or [1.0, 1.0, 1.0],
            intensity=intensity,
            range=range,
            position=position or [0.0, 0.0, 0.0],
            direction=direction or [0.0, -1.0, 0.0],
            casts_shadows=casts_shadows,
            enabled=enabled,
        )
        target.lights[light_id] = light
        return light

    def destroy_light(self, light_id: str, world: Optional[RenderWorld] = None) -> None:
        target = world or self.active_world
        if not target or light_id not in target.lights:
            raise ValueError(f"LIGHT_NOT_FOUND: '{light_id}'")
        del target.lights[light_id]

    # --------------------------------------------------------------------------
    # 5. Meshes and Materials
    # --------------------------------------------------------------------------

    def register_mesh(self, mesh: RenderMesh, world: Optional[RenderWorld] = None) -> None:
        target = world or self.active_world
        if not target:
            raise ValueError("NO_ACTIVE_WORLD")
        target.meshes[mesh.mesh_id] = mesh

    def register_material(self, material: RenderMaterial, world: Optional[RenderWorld] = None) -> None:
        target = world or self.active_world
        if not target:
            raise ValueError("NO_ACTIVE_WORLD")
        target.materials[material.material_id] = material

    # --------------------------------------------------------------------------
    # 6. Culling, LOD & Visibility
    # --------------------------------------------------------------------------

    def compute_visibility(self, camera_id: Optional[str] = None, world: Optional[RenderWorld] = None) -> List[str]:
        target = world or self.active_world
        if not target:
            raise ValueError("NO_ACTIVE_WORLD")

        cam_id = camera_id or target.active_camera_id
        cam = target.cameras.get(cam_id) if cam_id else None

        visible_ids: List[str] = []
        for rid, rend in sorted(target.renderables.items()):
            if not rend.visible:
                continue

            # If camera exists, perform distance and near/far check
            if cam:
                d = _vec3_dist(rend.position, cam.position)
                if d < cam.near_clip or d > cam.far_clip:
                    continue

                # Update LOD based on distance
                mesh = target.meshes.get(rend.mesh_id)
                if mesh and mesh.lod_distances:
                    lod = 0
                    for threshold in mesh.lod_distances:
                        if d > threshold:
                            lod += 1
                    rend.current_lod = min(lod, mesh.lod_count - 1)

            visible_ids.append(rid)

        return visible_ids

    # --------------------------------------------------------------------------
    # 7. Draw Submission and Sorting
    # --------------------------------------------------------------------------

    def submit_draw_commands(self, camera_id: Optional[str] = None, world: Optional[RenderWorld] = None) -> List[DrawCommand]:
        target = world or self.active_world
        if not target:
            raise ValueError("NO_ACTIVE_WORLD")

        visible_ids = self.compute_visibility(camera_id, target)
        cam = target.cameras.get(camera_id or target.active_camera_id) if (camera_id or target.active_camera_id) else None

        commands: List[DrawCommand] = []
        for rid in visible_ids:
            rend = target.renderables[rid]
            mesh = target.meshes.get(rend.mesh_id)
            idx_count = mesh.index_count if mesh else 36

            mat_id = rend.material_ids[0] if rend.material_ids else "default_mat"
            mat = target.materials.get(mat_id)
            q_type = mat.render_queue if mat else RenderQueueType.OPAQUE

            dist = _vec3_dist(rend.position, cam.position) if cam else 0.0

            # Sort key: OPAQUE = dist (front-to-back), TRANSPARENT = -dist (back-to-front)
            sort_key = dist if q_type != RenderQueueType.TRANSPARENT else -dist

            self._command_counter += 1
            cmd = DrawCommand(
                command_id=f"dc_{self._command_counter}",
                renderable_id=rid,
                mesh_id=rend.mesh_id,
                material_id=mat_id,
                index_count=idx_count,
                sort_key=sort_key,
                render_queue=q_type,
            )
            commands.append(cmd)

        if len(commands) > target.settings.max_draw_commands:
            raise ValueError("SECURITY_VIOLATION: Draw command limit exceeded.")

        # Deterministic sorting: by render_queue value, then sort_key, then renderable_id
        commands.sort(key=lambda c: (c.render_queue.value, round(c.sort_key, 4), c.renderable_id))
        return commands

    # --------------------------------------------------------------------------
    # 8. Render Graph & Passes
    # --------------------------------------------------------------------------

    def build_render_graph(self, graph_id: str = "main_graph", world: Optional[RenderWorld] = None) -> RenderGraph:
        target = world or self.active_world
        if not target:
            raise ValueError("NO_ACTIVE_WORLD")
        target.render_graph = RenderGraph(graph_id=graph_id)
        return target.render_graph

    def add_render_pass(
        self,
        pass_id: str,
        pass_type: str = "ColorPass",
        inputs: Optional[List[str]] = None,
        outputs: Optional[List[str]] = None,
        dependencies: Optional[List[str]] = None,
        world: Optional[RenderWorld] = None,
    ) -> RenderPass:
        target = world or self.active_world
        if not target:
            raise ValueError("NO_ACTIVE_WORLD")
        if pass_id in target.render_graph.passes:
            raise ValueError(f"DUPLICATE_PASS_ID: '{pass_id}'")

        p = RenderPass(
            pass_id=pass_id,
            pass_type=pass_type,
            inputs=inputs or [],
            outputs=outputs or [],
            dependencies=dependencies or [],
        )
        target.render_graph.passes[pass_id] = p
        return p

    add_pass_to_graph = add_render_pass

    def compile_render_graph(self, world: Optional[RenderWorld] = None) -> List[str]:
        target = world or self.active_world
        if not target:
            raise ValueError("NO_ACTIVE_WORLD")

        passes = target.render_graph.passes
        # Topological Sort with DFS and Cycle Detection
        visited: Dict[str, int] = {}  # 0: visiting, 1: visited
        order: List[str] = []

        def visit(node: str, path: List[str]):
            if visited.get(node) == 0:
                cycle_str = " -> ".join(path + [node])
                raise ValueError(f"NO_RENDER_GRAPH_CYCLE: Cycle detected: {cycle_str}")
            if visited.get(node) == 1:
                return

            visited[node] = 0
            p = passes.get(node)
            if p:
                for dep in sorted(p.dependencies):
                    if dep in passes:
                        visit(dep, path + [node])
            visited[node] = 1
            order.append(node)

        for pid in sorted(passes.keys()):
            if pid not in visited:
                visit(pid, [])

        target.render_graph.execution_order = list(order)
        return order

    # --------------------------------------------------------------------------
    # 9. GPU Resource Abstraction
    # --------------------------------------------------------------------------

    def allocate_gpu_resource(
        self,
        resource_id: str,
        resource_type: str,
        size_bytes: int,
        world: Optional[RenderWorld] = None,
    ) -> GPUResource:
        target = world or self.active_world
        if not target:
            raise ValueError("NO_ACTIVE_WORLD")
        if size_bytes <= 0:
            raise ValueError("INVALID_GPU_RESOURCE: size_bytes must be positive.")
        if resource_id in target.gpu_resources:
            raise ValueError(f"DUPLICATE_GPU_RESOURCE: '{resource_id}'")

        res = GPUResource(
            resource_id=resource_id,
            resource_type=resource_type,
            size_bytes=size_bytes,
            state=ResourceState.SHADER_RESOURCE,
        )
        target.gpu_resources[resource_id] = res
        return res

    def release_gpu_resource(self, resource_id: str, world: Optional[RenderWorld] = None) -> None:
        target = world or self.active_world
        if not target or resource_id not in target.gpu_resources:
            raise ValueError(f"GPU_RESOURCE_NOT_FOUND: '{resource_id}'")
        del target.gpu_resources[resource_id]

    # --------------------------------------------------------------------------
    # 10. Frame Rendering & Synchronization
    # --------------------------------------------------------------------------

    def render_frame(self, delta_time: float, world: Optional[RenderWorld] = None) -> RenderFrame:
        target = world or self.active_world
        if not target:
            raise ValueError("NO_ACTIVE_WORLD")
        if target.state == RenderWorldState.PAUSED:
            return RenderFrame(frame_index=target.frames_rendered, delta_time=0.0)
        if target.state not in (RenderWorldState.RENDERING, RenderWorldState.READY):
            raise ValueError(f"NO_UPDATE_BEFORE_INITIALIZATION: RenderWorld state is '{target.state.value}'.")

        if target.state == RenderWorldState.READY:
            target.state = RenderWorldState.RENDERING

        if delta_time < 0.0:
            raise ValueError("INVALID_TIMESTEP: delta_time cannot be negative.")

        commands = self.submit_draw_commands(world=target)
        culled = len(target.renderables) - len(commands)

        target.frames_rendered += 1
        target.time_seconds += delta_time

        triangles = sum((cmd.index_count // 3) for cmd in commands)

        frame = RenderFrame(
            frame_index=target.frames_rendered,
            delta_time=delta_time,
            render_time_ms=round(delta_time * 1000.0, 2),
            draw_calls_count=len(commands),
            triangles_count=triangles,
            culled_objects_count=max(0, culled),
            submitted_commands=commands,
        )

        target.content_fingerprint = target.compute_fingerprint()
        return frame

    # --------------------------------------------------------------------------
    # 11. Transform Synchronization
    # --------------------------------------------------------------------------

    def sync_from_runtime_world(self, runtime_world: Any, render_world: Optional[RenderWorld] = None) -> None:
        target = render_world or self.active_world
        if not target or not runtime_world:
            return

        for rend in target.renderables.values():
            if rend.entity_id in runtime_world.entities:
                ent = runtime_world.entities[rend.entity_id]
                tr = getattr(ent, "world_transform", getattr(ent, "local_transform", getattr(ent, "transform", None)))
                if tr:
                    rend.position = list(tr.position)
                    rend.rotation = list(tr.rotation)
                    if hasattr(tr, "scale"):
                        rend.scale = list(tr.scale)

    # --------------------------------------------------------------------------
    # 12. Golden Frame & Debug Visualization
    # --------------------------------------------------------------------------

    def capture_golden_frame(self, world: Optional[RenderWorld] = None) -> Dict[str, Any]:
        target = world or self.active_world
        if not target:
            return {}

        frame_data = {
            "world_id": target.render_world_id,
            "frames_rendered": target.frames_rendered,
            "renderables_count": len(target.renderables),
            "lights_count": len(target.lights),
            "cameras_count": len(target.cameras),
            "gpu_resources_count": len(target.gpu_resources),
            "render_graph_passes": len(target.render_graph.passes),
        }
        serialized = json.dumps(frame_data, sort_keys=True)
        frame_hash = hashlib.sha256(serialized.encode("utf-8")).hexdigest()
        frame_data["golden_hash"] = frame_hash
        return frame_data

    def get_debug_render_data(self, world: Optional[RenderWorld] = None) -> Dict[str, Any]:
        target = world or self.active_world
        if not target:
            return {}

        return {
            "renderables": [
                {"id": r.renderable_id, "pos": r.position, "lod": r.current_lod}
                for r in sorted(target.renderables.values(), key=lambda x: x.renderable_id)
            ],
            "cameras": list(target.cameras.keys()),
            "lights": list(target.lights.keys()),
            "time_seconds": target.time_seconds,
        }

    # --------------------------------------------------------------------------
    # 13. Presentation & Surface Management
    # --------------------------------------------------------------------------

    def present_frame(self, world: Optional[RenderWorld] = None) -> bool:
        target = world or self.active_world
        if not target:
            raise ValueError("NO_ACTIVE_WORLD")
        if target.state not in (RenderWorldState.RENDERING, RenderWorldState.READY):
            raise ValueError(f"CANNOT_PRESENT_FRAME: RenderWorld state is '{target.state.value}'.")
        return True

    def resize_surface(self, width: int, height: int, world: Optional[RenderWorld] = None) -> Tuple[int, int]:
        target = world or self.active_world
        if not target:
            raise ValueError("NO_ACTIVE_WORLD")
        if width <= 0 or height <= 0:
            raise ValueError(f"INVALID_SURFACE_DIMENSIONS: {width}x{height}")
        target.settings.metadata["surface_width"] = width
        target.settings.metadata["surface_height"] = height
        target.content_fingerprint = target.compute_fingerprint()
        return (width, height)

    def wait_frame_fence(self, timeout_ms: float = 1000.0, world: Optional[RenderWorld] = None) -> bool:
        target = world or self.active_world
        if not target:
            raise ValueError("NO_ACTIVE_WORLD")
        return True
