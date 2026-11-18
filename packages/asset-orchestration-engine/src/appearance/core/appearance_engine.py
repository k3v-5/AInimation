import copy
import time
from typing import Dict, Any, Optional, List, Tuple
from ..materials.material_schema import MaterialDefinition, PBRParameters, ShaderType
from ..materials.material_instance import MaterialInstance
from ..materials.material_registry import MaterialRegistry
from ..textures.texture_schema import TextureMetadata, TextureUsage, ColorSpace
from ..textures.texture_registry import TextureRegistry
from ..textures.color_space_validator import ColorSpaceValidator
from ..uv.uv_schema import UVSet, UVMethod
from ..uv.uv_projection import UVProjection
from ..uv.uv_validator import UVValidator
from ..assignment.material_assignment import MaterialAssignmentManager
from ..appearance_qa.appearance_validator import AppearanceValidator
from ..appearance_qa.appearance_diff import AppearanceDiff
from .appearance_context import AppearanceContext
from ...geometry.core.geometry_engine import GeometryEngine

class AppearanceEngine:
    """
    Appearance Engine (AOE v5)
    
    Invariantes:
    1. GEOMETRY != MATERIAL != UV != TEXTURE
    2. Las operaciones de apariencia nunca alteran geometría (GEOMETRY_LOCK).
    3. Failure Isolation: Si falla un material/textura/UV, solo se revierte su propio subsistema.
    """
    def __init__(self, geometry_engine: Optional[GeometryEngine] = None):
        self.geo_engine = geometry_engine
        self.materials = MaterialRegistry()
        self.textures = TextureRegistry()
        self.assignments = MaterialAssignmentManager()
        self.uv_sets: Dict[str, UVSet] = {} # comp_id -> UVSet
        self.context = AppearanceContext()

    def enforce_geometry_lock(self):
        """Si la geometría está bloqueada, cualquier mutación de mallas está prohibida."""
        if self.context.geometry_locked:
            return True
        return False

    def create_material(
        self,
        material_id: str,
        name: str,
        shader_type: str = "PBR",
        parameters: Optional[Dict[str, Any]] = None,
        textures: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        if self.materials.get_material(material_id):
            return {"success": False, "error_code": "MATERIAL_ALREADY_EXISTS", "message": f"Material '{material_id}' already exists."}

        pbr_params = PBRParameters()
        if parameters:
            for k, v in parameters.items():
                if hasattr(pbr_params, k):
                    setattr(pbr_params, k, v)

        val_ok, val_err = pbr_params.validate()
        if not val_ok:
            return {"success": False, "error_code": "INVALID_MATERIAL_PARAMETER", "message": val_err}

        mat = MaterialDefinition(
            material_id=material_id,
            name=name,
            shader_type=ShaderType(shader_type),
            parameters=pbr_params,
            textures=textures or {},
            version=1
        )
        self.materials.register_material(mat)
        self.context.metrics.material_count += 1

        return {
            "success": True,
            "material_id": material_id,
            "version": 1,
            "parameters": pbr_params.__dict__
        }

    def assign_material(self, component_id: str, material_id: str, slot_name: str = "default_slot") -> Dict[str, Any]:
        base_mat = self.materials.get_material(material_id)
        if not base_mat:
            return {"success": False, "error_code": "MATERIAL_NOT_FOUND", "message": f"Material '{material_id}' not found."}

        # Registrar asignación de slot
        self.assignments.assign_material(component_id, material_id, slot_name=slot_name)

        # Crear instancia de material aislada para el componente
        inst = MaterialInstance(
            instance_id=f"{material_id}_{component_id}_inst",
            base_material_id=material_id,
            component_id=component_id
        )
        self.materials.register_instance(inst)

        return {
            "success": True,
            "component_id": component_id,
            "material_id": material_id,
            "instance_id": inst.instance_id,
            "slot_name": slot_name
        }

    def modify_material(
        self,
        target_id: str, # Puede ser material_id o component_id
        changes: Dict[str, Any],
        scope: Optional[List[str]] = None,
        dry_run: bool = False
    ) -> Dict[str, Any]:
        # 1. Scope Check
        if scope and target_id not in scope:
            return {"success": False, "error_code": "SCOPE_VIOLATION", "message": f"Target '{target_id}' outside allowed scope {scope}."}

        # 2. Buscar si es una instancia de componente o material base
        inst = self.materials.get_instance_for_component(target_id)
        base_mat = self.materials.get_material(target_id)

        if not inst and not base_mat:
            return {"success": False, "error_code": "MATERIAL_NOT_FOUND", "message": f"Material or component '{target_id}' not found."}

        # Snapshot previo para rollback en caso de fallo
        if inst:
            target_obj = inst
            base_ref = self.materials.get_material(inst.base_material_id)
            current_effective = inst.get_effective_parameters(base_ref)
            snapshot = copy.deepcopy(inst.parameter_overrides)
        else:
            target_obj = base_mat
            current_effective = base_mat.parameters.__dict__
            snapshot = copy.deepcopy(base_mat.parameters)

        # 3. Detección NO_OP
        is_identical = True
        for k, v in changes.items():
            if current_effective.get(k) != v:
                is_identical = False
                break
        if is_identical:
            return {"success": True, "status": "NO_OP", "target_id": target_id, "modified_parameters": []}

        # 4. Validar nuevos parámetros PBR
        test_pbr = PBRParameters()
        for k, v in current_effective.items():
            if hasattr(test_pbr, k): setattr(test_pbr, k, v)
        for k, v in changes.items():
            if hasattr(test_pbr, k): setattr(test_pbr, k, v)

        val_ok, val_err = test_pbr.validate()
        if not val_ok:
            return {"success": False, "error_code": "INVALID_MATERIAL_PARAMETER", "message": val_err}

        diff = AppearanceDiff()
        for k, v in changes.items():
            diff.material_changes.append({
                "parameter": k,
                "before": current_effective.get(k),
                "after": v
            })

        if dry_run:
            return {"success": True, "status": "dry_run", "target_id": target_id, "diff": diff.to_dict()}

        try:
            # 5. Aplicar cambios (Si es instancia, sobreescribe solo su instancia; si es base, muta el base)
            if inst:
                for k, v in changes.items():
                    inst.parameter_overrides[k] = v
                inst.version += 1
            else:
                for k, v in changes.items():
                    setattr(base_mat.parameters, k, v)
                base_mat.version += 1

            return {
                "success": True,
                "status": "completed",
                "target_id": target_id,
                "diff": diff.to_dict(),
                "geometry_changes": [] # Garantizado 0 cambios geométricos
            }

        except Exception as e:
            # Rollback exclusivo de material
            if inst: inst.parameter_overrides = snapshot
            else: base_mat.parameters = snapshot
            return {"success": False, "error_code": "MATERIAL_MODIFICATION_FAILED", "message": str(e)}

    def register_texture(self, texture: TextureMetadata) -> Dict[str, Any]:
        # Validar color space
        cs_ok, cs_err = ColorSpaceValidator.validate_color_space(texture.usage, texture.color_space)
        if not cs_ok:
            return {"success": False, "error_code": "INVALID_COLOR_SPACE", "message": cs_err}

        self.textures.register_texture(texture)
        self.context.metrics.texture_count += 1
        return {"success": True, "texture_id": texture.texture_id, "usage": texture.usage.value}

    def generate_uv(self, component_id: str, method: UVMethod = UVMethod.BOX, channel: str = "UV0") -> Dict[str, Any]:
        if not self.geo_engine:
            return {"success": False, "error_code": "GEOMETRY_ENGINE_UNAVAILABLE", "message": "GeometryEngine required for UV generation."}

        comp = self.geo_engine.registry.get(component_id)
        if not comp or not comp.geometry:
            return {"success": False, "error_code": "COMPONENT_NOT_FOUND", "message": f"Component '{component_id}' or geometry not found."}

        uv_set = UVProjection.generate_uv_set(component_id, comp.geometry, method, channel)
        val_ok, val_err = UVValidator.validate_uv_set(uv_set)
        if not val_ok:
            return {"success": False, "error_code": "UV_VALIDATION_FAILED", "message": val_err}

        self.uv_sets[component_id] = uv_set
        self.context.metrics.uv_set_count += 1

        return {
            "success": True,
            "component_id": component_id,
            "uv_set_id": uv_set.uv_set_id,
            "channel": channel,
            "coordinates_count": len(uv_set.coordinates)
        }

    def get_appearance_manifest(self, asset_id: str) -> Dict[str, Any]:
        """Exporta el manifiesto determinista de apariencia del asset."""
        return {
            "asset_id": asset_id,
            "materials": [m.__dict__ for m in self.materials.list_materials()],
            "textures": [t.__dict__ for t in self.textures.list_textures()],
            "uv_sets": {cid: uv.__dict__ for cid, uv in self.uv_sets.items()},
            "assignments": [a.__dict__ for a in self.assignments.list_assignments()]
        }

    def validate_appearance(self) -> Dict[str, Any]:
        val_ok, errors = AppearanceValidator.validate_appearance(self.materials, self.textures, self.uv_sets)
        return {
            "is_valid": val_ok,
            "errors": errors,
            "status": "APPROVED" if val_ok else "REJECTED"
        }
