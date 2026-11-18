import uuid
from typing import Dict, Any, Optional, Tuple
from ..core.asset_spec import AssetSpec, ComponentSpecEntry, DimensionValue, StyleSpecEntry
from ..core.ontology_registry import AssetOntology
from ..core.provenance import AttributeProvenance
from ..parsing.intent_extractor import IntentExtractor
from ..parsing.unit_resolver import UnitResolver
from ..parsing.constraint_extractor import ConstraintExtractor, RelationExtractor
from ..validation.conflict_detector import ConflictDetector
from ..validation.ambiguity_detector import AmbiguityDetector

class SpecificationCompiler:
    def __init__(self, ontology: Optional[AssetOntology] = None):
        self.ontology = ontology or AssetOntology()
        self.cache: Dict[str, AssetSpec] = {}

    def compile(self, user_text: str) -> Tuple[bool, Optional[AssetSpec], str]:
        # 0. Cache lookup
        if user_text in self.cache:
            return True, self.cache[user_text], "Retrieved from compiler cache."

        # 1. Detección de Conflictos
        is_conflict, msg_conflict = ConflictDetector.detect_conflicts(user_text)
        if is_conflict:
            return False, None, msg_conflict

        # 2. Detección de Ambigüedad
        is_ambig, msg_ambig = AmbiguityDetector.detect_ambiguity(user_text)
        if is_ambig:
            return False, None, msg_ambig

        # 3. Extracción de Intención y Estilo
        asset_type, style, conf = IntentExtractor.extract_intent(user_text, self.ontology)

        # 4. Extracción de Dimensiones
        dim_val = UnitResolver.parse_dimension_from_text(user_text)

        # 5. Extracción de Componentes y Materiales
        t = user_text.lower()
        components: Dict[str, ComponentSpecEntry] = {}

        # Componente Blade
        if "hoja" in t or "blade" in t or asset_type == "SWORD":
            blade_dims = {}
            if dim_val:
                blade_dims["length"] = dim_val
            components["blade"] = ComponentSpecEntry(
                component_id="blade_spec",
                semantic_role="blade",
                required=True,
                dimensions=blade_dims,
                materials={"metallic": 0.90, "roughness": 0.25} if ("metálica" in t or "metal" in t or "acero" in t) else {},
                provenance=AttributeProvenance.EXPLICIT
            )

        # Componente Guard
        if "guardia" in t or "guarda" in t or "guard" in t or asset_type == "SWORD":
            components["guard"] = ComponentSpecEntry(
                component_id="guard_spec",
                semantic_role="guard",
                required=True,
                materials={"type": "METAL"} if ("metálica" in t or "metal" in t) else {},
                provenance=AttributeProvenance.EXPLICIT if ("guardia" in t or "guarda" in t) else AttributeProvenance.DEFAULT
            )

        # Componente Grip / Handle con Material
        if "empuñadura" in t or "mango" in t or "handle" in t or "cuero" in t or asset_type == "SWORD":
            mat_type = "LEATHER" if "cuero" in t else "WOOD"
            mat_prov = AttributeProvenance.EXPLICIT if "cuero" in t else AttributeProvenance.DEFAULT
            components["grip"] = ComponentSpecEntry(
                component_id="grip_spec",
                semantic_role="grip",
                required=True,
                materials={
                    "material_type": mat_type,
                    "color": "DARK" if ("oscuro" in t or "oscura" in t) else "NATURAL",
                    "roughness": 0.80 # INFERRED
                },
                provenance=mat_prov
            )

        # Componente Pommel
        if asset_type == "SWORD":
            components["pommel"] = ComponentSpecEntry(
                component_id="pommel_spec",
                semantic_role="pommel",
                required=False,
                provenance=AttributeProvenance.DEFAULT
            )

        # 6. Restricciones Negativas y Proporciones
        negative_constraints = ConstraintExtractor.extract_negative_constraints(user_text)
        proportions = RelationExtractor.extract_relative_relations(user_text)

        spec = AssetSpec(
            spec_id=f"spec_{uuid.uuid4().hex[:6]}",
            version=1,
            asset_type=asset_type,
            asset_type_confidence=conf,
            semantic_description=f"{style.category} {style.realism} {asset_type}",
            original_user_request=user_text,
            style=style,
            components=components,
            dimensions={"total_length": dim_val} if dim_val else {},
            proportions=proportions,
            negative_constraints=negative_constraints
        )

        self.cache[user_text] = spec
        return True, spec, "Specification compiled successfully."
