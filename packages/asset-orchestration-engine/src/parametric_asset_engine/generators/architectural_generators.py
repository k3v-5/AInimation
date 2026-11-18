from typing import Dict, Any, List
from ..core.parametric_types import ComponentState
from ..core.parametric_schema import GeneratedComponent

class WallGenerator:
    @staticmethod
    def generate(asset_id: str, params: Dict[str, Any]) -> GeneratedComponent:
        comp_id = f"{asset_id}_WALLS"
        w = params.get("width", 8.0)
        d = params.get("depth", 6.0)
        h = params.get("wall_height", 3.0)
        mat = params.get("wall_material", "STONE")
        return GeneratedComponent(
            component_id=comp_id,
            object_ids=[f"{comp_id}_mesh"],
            parameters={"width": w, "depth": d, "height": h},
            materials={"wall_mat": mat},
            state=ComponentState.VALID,
            triangles=240,
            bounds={"w": w, "d": d, "h": h}
        )

class RoofGenerator:
    @staticmethod
    def generate(asset_id: str, params: Dict[str, Any]) -> GeneratedComponent:
        comp_id = f"{asset_id}_ROOF"
        w = params.get("width", 8.0)
        d = params.get("depth", 6.0)
        h = params.get("roof_height", 1.8)
        rtype = params.get("roof_type", "GABLE")
        mat = params.get("roof_material", "WOOD")
        return GeneratedComponent(
            component_id=comp_id,
            object_ids=[f"{comp_id}_mesh"],
            parameters={"width": w, "depth": d, "height": h, "type": rtype},
            materials={"roof_mat": mat},
            state=ComponentState.VALID,
            triangles=180,
            bounds={"w": w, "d": d, "h": h}
        )

class WindowGenerator:
    @staticmethod
    def generate(asset_id: str, params: Dict[str, Any]) -> GeneratedComponent:
        comp_id = f"{asset_id}_WINDOWS"
        count = params.get("window_count", 4)
        return GeneratedComponent(
            component_id=comp_id,
            object_ids=[f"{comp_id}_{i:02d}" for i in range(1, count + 1)],
            parameters={"count": count, "width": 0.8, "height": 1.2},
            materials={"frame": "WOOD", "glass": "GLASS"},
            state=ComponentState.VALID,
            triangles=count * 60,
            bounds={"count": count}
        )

class DoorGenerator:
    @staticmethod
    def generate(asset_id: str, params: Dict[str, Any]) -> GeneratedComponent:
        comp_id = f"{asset_id}_DOOR"
        count = params.get("door_count", 1)
        return GeneratedComponent(
            component_id=comp_id,
            object_ids=[f"{comp_id}_01"],
            parameters={"count": count, "width": 0.9, "height": 2.0},
            materials={"door_mat": "WOOD"},
            state=ComponentState.VALID,
            triangles=80,
            bounds={"w": 0.9, "h": 2.0}
        )

class FoundationGenerator:
    @staticmethod
    def generate(asset_id: str, params: Dict[str, Any]) -> GeneratedComponent:
        comp_id = f"{asset_id}_FOUNDATION"
        w = params.get("width", 8.0)
        d = params.get("depth", 6.0)
        return GeneratedComponent(
            component_id=comp_id,
            object_ids=[f"{comp_id}_slab"],
            parameters={"width": w + 0.4, "depth": d + 0.4, "height": 0.3},
            materials={"foundation_mat": "STONE"},
            state=ComponentState.VALID,
            triangles=12,
            bounds={"w": w + 0.4, "d": d + 0.4, "h": 0.3}
        )

class GeneratorRegistry:
    GENERATORS = {
        "foundation": FoundationGenerator,
        "walls": WallGenerator,
        "roof": RoofGenerator,
        "windows": WindowGenerator,
        "doors": DoorGenerator
    }

    @classmethod
    def get_generator(cls, component_type: str):
        c_type = component_type.lower()
        if c_type not in cls.GENERATORS:
            raise ValueError(f"UNSUPPORTED_COMPONENT: Component type '{component_type}' is not supported by GeneratorRegistry.")
        return cls.GENERATORS[c_type]
