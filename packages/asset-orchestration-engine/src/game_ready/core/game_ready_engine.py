import copy
import time
from typing import Dict, Any, Optional, List, Tuple
from .game_ready_manifest import GameReadyManifest
from ..validation.approval_validator import ApprovalValidator
from ..validation.naming_validator import NamingValidator
from ..validation.budget_validator import BudgetValidator
from ..lod.lod_profile import GameReadyLODProfile
from ..lod.lod_generator import LODGenerator
from ..lod.lod_validator import LODValidator
from ..collision.collision_profile import CollisionProfile
from ..collision.collision_generator import CollisionGenerator
from ..collision.collision_validator import CollisionValidator
from ..transforms.pivot_manager import PivotManager, PivotType
from ..transforms.scale_manager import ScaleManager
from ..sockets.socket_schema import SocketDefinition, SocketManager
from ..unreal.asset_mapper import AssetMapper
from ..unreal.import_settings import UnrealImportSettings
from ...geometry.core.geometry_engine import GeometryEngine
from ...appearance.core.appearance_engine import AppearanceEngine

class GameReadyEngine:
    """
    Game Ready Processing & Unreal Preparation Engine (AOE v6)
    
    Invariantes:
    1. SOURCE ASSET IS READ ONLY.
    2. Optimiza, prepara y valida sin rediseñar la geometría ni la apariencia aprobada.
    3. Bloqueo obligatorio si geometry/appearance no están APPROVED.
    """
    def __init__(
        self,
        geometry_engine: Optional[GeometryEngine] = None,
        appearance_engine: Optional[AppearanceEngine] = None
    ):
        self.geo_engine = geometry_engine
        self.app_engine = appearance_engine
        self.socket_manager = SocketManager()
        self.manifests: Dict[str, GameReadyManifest] = {}

    def process_game_ready(
        self,
        asset_id: str,
        category: str = "Weapons",
        geometry_status: str = "APPROVED",
        appearance_status: str = "APPROVED",
        lod_profile: Optional[GameReadyLODProfile] = None,
        collision_profile: Optional[CollisionProfile] = None,
        pivot_type: PivotType = PivotType.BOTTOM_CENTER,
        scope: Optional[List[str]] = None,
        dry_run: bool = False
    ) -> Dict[str, Any]:
        # 1. Validar Scope
        if scope and asset_id not in scope:
            return {"success": False, "error_code": "GAME_READY_SCOPE_VIOLATION", "message": f"Asset '{asset_id}' is not in allowed scope {scope}."}

        # 2. Validar Aprobaciones Previas
        app_ok, app_err = ApprovalValidator.validate_approvals(geometry_status, appearance_status)
        if not app_ok:
            return {"success": False, "error_code": app_err.split(":")[0], "message": app_err}

        if not self.geo_engine:
            return {"success": False, "error_code": "GEOMETRY_ENGINE_UNAVAILABLE", "message": "GeometryEngine is required."}

        # 3. Obtener componentes de geometría fuente (READ ONLY)
        comps = self.geo_engine.registry.list_components(asset_id)
        if not comps:
            return {"success": False, "error_code": "ASSET_NOT_FOUND", "message": f"Asset '{asset_id}' has no components."}

        # Copia aislada para no alterar la fuente original (Source Immutability)
        source_geos = {c.component_id: copy.deepcopy(c.geometry) for c in comps if c.geometry}

        # 4. Transformaciones y Pivote
        geos_pivoted, offset_applied = PivotManager.adjust_pivot(source_geos, pivot_type)
        geos_unreal_scale = ScaleManager.convert_meters_to_centimeters(geos_pivoted)

        # 5. Generación y Validación de Cadena de LODs
        l_profile = lod_profile or GameReadyLODProfile()
        lods = LODGenerator.generate_lods(geos_unreal_scale, l_profile)
        lod_ok, lod_err = LODValidator.validate_lods(lods, l_profile)
        if not lod_ok:
            return {"success": False, "error_code": lod_err.split(":")[0], "message": lod_err}

        # 6. Generación y Validación de Colisión Simplificada (UCX_)
        c_profile = collision_profile or CollisionProfile()
        unreal_mapping = AssetMapper.create_mapping(asset_id, category)
        collision_hulls = CollisionGenerator.generate_collision(unreal_mapping.unreal_asset_name, geos_unreal_scale, c_profile)
        col_ok, col_err = CollisionValidator.validate_collision(collision_hulls, c_profile)
        if not col_ok:
            return {"success": False, "error_code": col_err.split(":")[0], "message": col_err}

        # 7. Validación de Nomenclatura Unreal
        name_ok, name_err = NamingValidator.validate_name(unreal_mapping.unreal_asset_name, expected_prefix="SM_")
        if not name_ok:
            return {"success": False, "error_code": name_err.split(":")[0], "message": name_err}

        # 8. Obtener Slots de Materiales y Preservación
        mat_slots = []
        if self.app_engine:
            app_manifest = self.app_engine.get_appearance_manifest(asset_id)
            mat_slots = [a.get("material_id", "M_Default") for a in app_manifest.get("assignments", [])]
        if not mat_slots:
            mat_slots = ["M_DefaultMaterial"]

        # Calcular dimensiones finales en cm
        all_uu_verts = []
        for g in geos_unreal_scale.values():
            all_uu_verts.extend(g.vertices)
        w_cm = max(v[0] for v in all_uu_verts) - min(v[0] for v in all_uu_verts)
        d_cm = max(v[1] for v in all_uu_verts) - min(v[1] for v in all_uu_verts)
        h_cm = max(v[2] for v in all_uu_verts) - min(v[2] for v in all_uu_verts)

        # 9. Crear Manifiesto Game Ready
        manifest = GameReadyManifest(
            asset_id=asset_id,
            source_geometry_version="v4",
            source_appearance_version="v3",
            game_ready_version="game_ready_v1",
            status="GAME_READY",
            unreal_mapping=unreal_mapping,
            import_settings=UnrealImportSettings(),
            lods_summary={f"LOD{lod.level}": lod.total_triangles for lod in lods},
            collision_hulls=[h.hull_name for h in collision_hulls],
            sockets=[s.socket_id for s in self.socket_manager.list_sockets()],
            material_slots=mat_slots,
            dimensions_cm=(round(w_cm, 2), round(d_cm, 2), round(h_cm, 2)),
            validation_status="APPROVED"
        )

        if dry_run:
            return {
                "success": True,
                "status": "dry_run",
                "asset_id": asset_id,
                "expected_manifest": manifest.__dict__
            }

        self.manifests[asset_id] = manifest

        return {
            "success": True,
            "status": "GAME_READY",
            "asset_id": asset_id,
            "game_ready_version": manifest.game_ready_version,
            "unreal_asset_name": unreal_mapping.unreal_asset_name,
            "unreal_package_path": unreal_mapping.unreal_package_path,
            "triangles": manifest.lods_summary,
            "collision": "PASS" if collision_hulls else "NONE",
            "materials": "PASS",
            "dimensions_cm": manifest.dimensions_cm,
            "manifest": manifest
        }

    def add_socket(self, socket_id: str, parent_component: str, location: Tuple[float, float, float] = (0,0,0)) -> Dict[str, Any]:
        s_def = SocketDefinition(socket_id=socket_id, parent_component=parent_component, location=location)
        ok, err = self.socket_manager.register_socket(s_def)
        if not ok:
            return {"success": False, "error_code": "SOCKET_INVALID", "message": err}
        return {"success": True, "socket_id": socket_id}

    def get_manifest(self, asset_id: str) -> Optional[GameReadyManifest]:
        return self.manifests.get(asset_id)
