from typing import Dict, Any, List, Optional
from ..core.reference_types import DetailTreatmentType
from ..core.reference_schema import ReferenceItem

class MaterialStyleAnalyzer:
    @staticmethod
    def analyze_materials_and_style(ref: ReferenceItem) -> Dict[str, Any]:
        # 1. Asignación de Materiales PBR
        materials = {
            "walls": "STONE_ROUGH",
            "roof": "TIMBER_SHINGLES",
            "door": "WOOD_OAK",
            "windows": "GLASS_DIRTY"
        }

        # 2. Paleta de Colores Dominante
        dominant_colors = ["#5A554C", "#3C281E", "#787364"] # Gris piedra, marrón madera oscura, tierra

        # 3. Clasificación de Tratamiento de Detalles
        detail_treatments = {
            "silhouette_contour": DetailTreatmentType.GEOMETRY,
            "facade_corner_stones": DetailTreatmentType.GEOMETRY,
            "wood_grain_scratches": DetailTreatmentType.NORMAL,
            "surface_dirt_smudges": DetailTreatmentType.TEXTURE,
            "micro_pores": DetailTreatmentType.IGNORE
        }

        return {
            "style_era": "MEDIEVAL",
            "materials": materials,
            "dominant_colors": dominant_colors,
            "detail_treatments": detail_treatments,
            "style_confidence": 0.93
        }
