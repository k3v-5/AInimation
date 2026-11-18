from typing import Dict, Any, Optional, Tuple, List
from ..core.amsl_types import (
    AMSLAssetType, AMSLAssetPurpose, DimensionMode, RelationshipType,
    StyleFamily, DetailLevel, MaterialCategory, DamageLevel, CollisionType,
    QualityLevel, RebuildPolicy, ConstraintType, ConstraintPriority, ValidationCategory
)
from ..core.amsl_schema import (
    CoordinateSystem, DimensionValue, DimensionsSpec, StructureSpec,
    ComponentSpec, RelationshipSpec, StyleSpec, GeometrySpec, MaterialSpec,
    DamageSpec, CollisionSpec, GameplaySpec, ReferenceSpec, ConstraintSpec,
    GenerationSpec, ValidationSpec, QualityProfileSpec, ProvenanceSpec,
    AssetSpecification, SpecificationDiff, BuildRequirements
)
from ..compiler.spec_validator import AMSLValidator
from ..compiler.spec_diff_engine import AMSLDiffEngine
from ..compiler.specification_compiler import SpecificationCompiler
from ..registry.schema_registry import SchemaRegistry

class AMSLAPI:
    """
    Asset/Model Specification Language (AMSL) API (AOE v35)
    
    Regla Fundamental:
    SEPARA EL "QUÉ QUIERO" (AssetSpecification en AMSL) DEL "CÓMO LO CONSTRUYO" (BuildPlan / Builders).
    LA IA NUNCA DESCRIBE COMANDOS DE BLENDER DIRECTOS. DEFINE UNA ESPECIFICACIÓN DETERMINISTA,
    VERSIONADA, SERIALIZABLE Y VALIDABLE.
    """
    def __init__(self):
        self.registry = SchemaRegistry()

    @staticmethod
    def create_medieval_house_spec(
        asset_id: str = "HOUSE_001",
        width: float = 6.0,
        depth: float = 4.0,
        height: float = 4.5,
        roof_pitch: float = 40.0,
        door_width: float = 0.90,
        window_count: int = 4,
        seed: int = 42191
    ) -> AssetSpecification:
        """Crea una especificación completa de Medieval House en AMSL sin comandos Blender."""
        spec = AssetSpecification(
            specification_id="SPEC_2026_000823",
            schema_version="1.0.0",
            asset_id=asset_id,
            semantic_id=f"LEVEL_01.VILLAGE.{asset_id}",
            asset_type=AMSLAssetType.BUILDING,
            category="MEDIEVAL_HOUSE",
            purpose=AMSLAssetPurpose.ENVIRONMENT,
            coordinates=CoordinateSystem(units="m", up_axis="Z", forward_axis="Y"),
            dimensions=DimensionsSpec(
                width=DimensionValue(target=width, unit="m"),
                depth=DimensionValue(target=depth, unit="m"),
                height=DimensionValue(target=height, unit="m"),
                proportions={"body_to_roof": 0.72, "window_to_wall": 0.18}
            ),
            structure=StructureSpec(
                floors=2,
                foundation=True,
                roof={"type": "GABLE", "pitch": roof_pitch},
                entrance="front"
            ),
            components=[
                ComponentSpec(id="door_main", type="DOOR", count=1, parameters={"width": door_width, "height": 2.0}),
                ComponentSpec(id="windows_main", type="WINDOW", count=window_count, parameters={"width": 0.8, "height": 1.0})
            ],
            style=StyleSpec(
                era=StyleFamily.MEDIEVAL,
                language="RUSTIC",
                realism="REALISTIC"
            ),
            geometry=GeometrySpec(
                topology="MANIFOLD_QUADS",
                polygon_budget=15000,
                detail_level=DetailLevel.HIGH
            ),
            materials=[
                MaterialSpec(material_id="mat_walls", category=MaterialCategory.STONE, base_color="#808080", roughness=0.85),
                MaterialSpec(material_id="mat_roof", category=MaterialCategory.WOOD, base_color="#4A2511", roughness=0.75),
                MaterialSpec(material_id="mat_door", category=MaterialCategory.WOOD, base_color="#3B1E08", roughness=0.70)
            ],
            generation=GenerationSpec(
                generator="MedievalHouseBuilder",
                generator_version="1.0.0",
                seed=seed,
                deterministic=True,
                rebuild_policy=RebuildPolicy.DEPENDENCIES
            )
        )
        return spec

    @staticmethod
    def validate_spec(spec: AssetSpecification, raw_dict: Optional[Dict[str, Any]] = None) -> bool:
        return AMSLValidator.validate_spec(spec, raw_dict)

    @staticmethod
    def compile_spec(
        spec: AssetSpecification,
        overrides: Optional[Dict[str, Any]] = None
    ) -> Tuple[AssetSpecification, BuildRequirements]:
        return SpecificationCompiler.compile(spec, overrides)

    @staticmethod
    def diff_specs(spec_a: AssetSpecification, spec_b: AssetSpecification) -> SpecificationDiff:
        return AMSLDiffEngine.diff(spec_a, spec_b)

    @staticmethod
    def compute_canonical_hash(spec: AssetSpecification) -> str:
        return spec.compute_specification_hash()
