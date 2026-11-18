from typing import Dict, Any, List, Tuple
from ..materials.material_registry import MaterialRegistry
from ..textures.texture_registry import TextureRegistry
from ..textures.color_space_validator import ColorSpaceValidator
from ..uv.uv_validator import UVValidator
from ..uv.uv_schema import UVSet

class AppearanceValidator:
    @staticmethod
    def validate_appearance(
        materials: MaterialRegistry,
        textures: TextureRegistry,
        uv_sets: Dict[str, UVSet]
    ) -> Tuple[bool, List[str]]:
        errors = []

        # 1. Validar Materiales
        for mat in materials.list_materials():
            val_ok, val_err = mat.parameters.validate()
            if not val_ok:
                errors.append(val_err)

        # 2. Validar Texturas y Color Spaces
        for tex in textures.list_textures():
            cs_ok, cs_err = ColorSpaceValidator.validate_color_space(tex.usage, tex.color_space)
            if not cs_ok:
                errors.append(cs_err)

        # 3. Validar UV Sets
        for cid, uv in uv_sets.items():
            uv_ok, uv_err = UVValidator.validate_uv_set(uv)
            if not uv_ok:
                errors.append(uv_err)

        return len(errors) == 0, errors
