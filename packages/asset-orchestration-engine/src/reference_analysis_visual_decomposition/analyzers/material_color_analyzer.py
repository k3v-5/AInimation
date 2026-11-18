from typing import Dict, Any, Tuple
from ..core.reference_types import ExtractedMaterialType
from ..core.reference_schema import MaterialPalette, ColorPalette

class MaterialColorAnalyzer:
    @classmethod
    def extract_materials_and_colors(cls, image_metadata: Dict[str, Any]) -> Tuple[MaterialPalette, ColorPalette]:
        base_mat_str = image_metadata.get("base_material", "WOOD").upper()
        base_mat = getattr(ExtractedMaterialType, base_mat_str, ExtractedMaterialType.WOOD)
        
        roughness = float(image_metadata.get("roughness", 0.70))
        metallic = float(image_metadata.get("metallic", 0.30))
        
        dom_colors = image_metadata.get("dominant_colors", ["#4A2E18", "#2C1D11"])
        acc_colors = image_metadata.get("accent_colors", ["#3A3A3C"])

        mat_pal = MaterialPalette(
            base_material=base_mat,
            secondary_materials=[ExtractedMaterialType.IRON],
            surface_roughness=roughness,
            metallic_ratio=metallic
        )

        col_pal = ColorPalette(
            dominant_colors=dom_colors,
            accent_colors=acc_colors,
            brightness_profile=image_metadata.get("brightness", "MEDIUM_DARK"),
            saturation_profile=image_metadata.get("saturation", "MUTED")
        )

        return mat_pal, col_pal
