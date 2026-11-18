import re
from typing import Dict, Any, List, Tuple
from ..core.vas_types import RequirementOrigin, InformationState
from ..core.vas_schema import TraceabilityRecord, VisualCompilationInput

class InputNormalizer:
    @classmethod
    def normalize_input(
        cls,
        comp_input: VisualCompilationInput
    ) -> Tuple[Dict[str, Any], List[TraceabilityRecord]]:
        traceability = []
        p = comp_input.prompt
        p_low = p.lower()

        # 1. Normalización de Dimensiones
        dimensions = {"height": 1.0, "width": 0.5, "depth": 0.5, "scale": 1.0}
        
        # Regex para capturar dimensiones métricas (ej. "1 metro", "1.8m", "2.0m", "100 cm")
        dim_match = re.search(r"(\d+(?:\.\d+)?)\s*(?:m(?:etros?|s)?|cm)", p_low)
        if dim_match:
            val = float(dim_match.group(1))
            if "cm" in dim_match.group(0):
                val = val / 100.0
            dimensions["height"] = val
            traceability.append(TraceabilityRecord(
                requirement_id="REQ_DIM_HEIGHT",
                source_type=RequirementOrigin.USER_PROMPT,
                source_id="PROMPT_DIMENSION",
                source_location="prompt",
                confidence=1.0
            ))
        else:
            traceability.append(TraceabilityRecord(
                requirement_id="REQ_DIM_HEIGHT",
                source_type=RequirementOrigin.DEFAULT,
                source_id="DEFAULT_DIMENSION",
                confidence=0.70
            ))

        # 2. Normalización de Materiales
        materials = {"base_material": "STEEL" if "acero" in p_low or "steel" in p_low or "espada" in p_low else "WOOD"}
        traceability.append(TraceabilityRecord(
            requirement_id="REQ_BASE_MATERIAL",
            source_type=RequirementOrigin.USER_PROMPT if ("acero" in p_low or "madera" in p_low) else RequirementOrigin.DEFAULT,
            source_id="PROMPT_MATERIAL",
            confidence=0.95
        ))

        # 3. Fusión con Referencias F55
        silhouette = {"aspect_ratio": 1.42, "symmetry": "VERTICAL_Z"}
        proportions = {"component_ratios": {"primary": 0.80, "secondary": 0.20}}
        components = []

        if comp_input.reference_reports:
            primary_rep = comp_input.reference_reports[0]
            if hasattr(primary_rep, "silhouette"):
                silhouette["aspect_ratio"] = primary_rep.silhouette.aspect_ratio
                silhouette["symmetry"] = primary_rep.silhouette.symmetry_axis
            if hasattr(primary_rep, "proportions"):
                proportions["component_ratios"] = primary_rep.proportions.component_ratios
            if hasattr(primary_rep, "parts"):
                for part in primary_rep.parts:
                    components.append({
                        "component_id": getattr(part, "part_id", "part_01"),
                        "semantic_type": getattr(part, "semantic_type", "BODY"),
                        "is_primary": getattr(part, "is_primary", True),
                        "confidence": getattr(part, "confidence", 0.95)
                    })
            traceability.append(TraceabilityRecord(
                requirement_id="REQ_F55_REFERENCE_FUSION",
                source_type=RequirementOrigin.F55_REFERENCE,
                source_id=getattr(primary_rep, "report_id", "F55_REPORT"),
                confidence=getattr(primary_rep, "overall_confidence", 0.90)
            ))
        else:
            components = [
                {"component_id": "comp_main", "semantic_type": "PRIMARY_BODY", "is_primary": True, "confidence": 1.0}
            ]

        # 4. Ingesta de Identidad Semántica F54
        semantic_id = comp_input.semantic_context.get("semantic_id", "asset_001.root")
        asset_id = comp_input.semantic_context.get("asset_id", "asset_001")
        asset_type = comp_input.asset_class_hint

        normalized = {
            "semantic_identity": {
                "semantic_id": semantic_id,
                "asset_id": asset_id,
                "asset_type": asset_type
            },
            "intent": {
                "original_prompt": p,
                "functional_purpose": "Video game asset for real-time engine",
                "information_state": InformationState.EXPLICIT if dim_match else InformationState.INFERRED
            },
            "dimensions": dimensions,
            "materials": materials,
            "silhouette": silhouette,
            "proportions": proportions,
            "components": components,
            "style": {"archetype": "STYLIZED" if "stylized" in p_low or "medieval" in p_low else "SEMI_REALISTIC"}
        }

        return normalized, traceability
