from typing import Dict, Optional, List
from ..core.surface_types import SurfaceTypeTag
from ..core.surface_schema import MaterialDefinition

class MaterialLibrary:
    def __init__(self):
        self._catalog: Dict[str, MaterialDefinition] = {}
        self._seed_default_materials()

    def _seed_default_materials(self):
        # Materiales estándar base
        self.register(MaterialDefinition(
            material_id="M_Wood_Oak",
            material_class=SurfaceTypeTag.WOOD,
            base_color=(0.45, 0.28, 0.15, 1.0),
            metallic=0.0,
            roughness=0.68
        ))
        self.register(MaterialDefinition(
            material_id="M_Iron_Forged",
            material_class=SurfaceTypeTag.METAL,
            base_color=(0.18, 0.18, 0.20, 1.0),
            metallic=0.90,
            roughness=0.35
        ))
        self.register(MaterialDefinition(
            material_id="M_Steel_Polished",
            material_class=SurfaceTypeTag.METAL,
            base_color=(0.75, 0.75, 0.78, 1.0),
            metallic=0.98,
            roughness=0.18
        ))
        self.register(MaterialDefinition(
            material_id="M_Stone_Granite",
            material_class=SurfaceTypeTag.STONE,
            base_color=(0.35, 0.35, 0.36, 1.0),
            metallic=0.0,
            roughness=0.85
        ))

    def find(self, material_id: str) -> Optional[MaterialDefinition]:
        return self._catalog.get(material_id)

    def register(self, material: MaterialDefinition):
        self._catalog[material.material_id] = material

    def resolve_or_create(self, requested_class: SurfaceTypeTag, custom_params: Optional[Dict] = None) -> MaterialDefinition:
        params = custom_params or {}
        # 1. Buscar coincidencia exacta
        for m in self._catalog.values():
            if m.material_class == requested_class and not m.is_instance:
                if not params:
                    return m
                # Crear variante determinista
                param_key = f"{params.get('roughness', m.roughness)}_{params.get('metallic', m.metallic)}".replace('.', '_')
                var_id = f"{m.material_id}_Var_{param_key}"
                var = MaterialDefinition(
                    material_id=var_id,
                    material_class=requested_class,
                    shader_model=m.shader_model,
                    base_color=params.get("base_color", m.base_color),
                    metallic=params.get("metallic", m.metallic),
                    roughness=params.get("roughness", m.roughness),
                    is_instance=True,
                    parent_material_id=m.material_id,
                    parameters=params
                )
                self.register(var)
                return var

        # Crear nuevo material determinista
        new_id = f"M_{requested_class.value}_Custom"
        new_mat = MaterialDefinition(
            material_id=new_id,
            material_class=requested_class,
            base_color=params.get("base_color", (0.5, 0.5, 0.5, 1.0)),
            metallic=params.get("metallic", 0.0),
            roughness=params.get("roughness", 0.5),
            parameters=params
        )
        self.register(new_mat)
        return new_mat
