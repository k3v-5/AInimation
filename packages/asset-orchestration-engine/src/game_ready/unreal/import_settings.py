from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class UnrealImportSettings:
    import_scale: float = 1.0 # Ya escalado a cm en transforms
    combine_meshes: bool = True
    generate_collision: bool = False # Usar colisiones UCX_ exportadas
    import_materials: bool = True
    import_textures: bool = True
    normal_import_method: str = "COMPUTE_NORMALS"
    convert_scene_unit: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return self.__dict__
