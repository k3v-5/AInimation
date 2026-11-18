import time
from typing import Dict, Any, List, Optional
from ..core.vas_types import (
    RequirementClass, ValidationMethod, RequirementOrigin,
    ContradictionSeverity, AmbiguitySeverity, InformationState
)
from ..core.vas_schema import (
    VisualCompilationInput, VisualAssetSpecification, TraceabilityRecord,
    InvariantSpec, VariableSpec, ToleranceSpec, AcceptanceCriterion,
    AmbiguityReport, ContradictionReport, UnrealRequirementsSpec,
    ProductionBudgetSpec, ValidationResult
)
from ..compiler.input_normalizer import InputNormalizer
from ..compiler.ambiguity_detector import AmbiguityDetector
from ..compiler.contradiction_detector import ContradictionDetector
from ..compiler.criteria_generator import CriteriaGenerator
from ..compiler.specification_hasher import SpecificationHasher

class VisualSpecificationCompiler:
    """
    Visual Specification Compiler (AOE v56)
    
    Regla Fundamental:
    NO CREA GEOMETRÍA DIRECTAMENTE. COMPILA LA INTENCIÓN Y OBSERVACIONES VISUALES
    EN UN CONTRATO CANÓNICO (VisualAssetSpecification - VAS) DETERMINISTA,
    ESTRUCTURADO, VALIDABLE Y VERSIONABLE PARA LAS FASES F57 A F66.
    """
    def __init__(self, compiler_version: str = "1.0.0"):
        self.compiler_version = compiler_version

    def compile(self, comp_input: VisualCompilationInput) -> VisualAssetSpecification:
        if not comp_input.prompt and not comp_input.reference_reports:
            raise ValueError("INVALID_COMPILATION_INPUT: Either prompt or reference_reports must be provided.")

        # 1. Normalizar Entradas y Trazabilidad
        norm, traceability = InputNormalizer.normalize_input(comp_input)

        # 2. Detectar Ambigüedades
        ambiguities = AmbiguityDetector.detect_ambiguities(comp_input.prompt, comp_input.instructions)

        # 3. Detectar Contradicciones
        contradictions = ContradictionDetector.detect_contradictions(
            prompt=comp_input.prompt,
            project_constraints=comp_input.project_constraints,
            visual_requirements=norm["materials"]
        )

        # 4. Configurar Tolerancias Explícitas
        height_val = norm["dimensions"]["height"]
        tolerances = [
            ToleranceSpec("height", height_val, round(height_val * 0.03, 3), "ABSOLUTE", "meters"),
            ToleranceSpec("aspect_ratio", norm["silhouette"]["aspect_ratio"], 0.05, "ABSOLUTE", "ratio"),
            ToleranceSpec("silhouette_similarity", 1.0, 0.10, "PERCENTAGE", "score")
        ]

        # 5. Configurar Invariantes (No modificables en F64)
        invariants = [
            InvariantSpec("INV_SILHOUETTE", "Primary silhouette contour and aspect ratio envelope", 1.0, "SPEC_COMPILER", 0.98, 0.05, ValidationMethod.VISUAL),
            InvariantSpec("INV_FUNCTIONAL_CONFIG", "Functional component count and root anchor", 1.0, "SPEC_COMPILER", 1.0, 0.0, ValidationMethod.SEMANTIC),
            InvariantSpec("INV_BASE_MATERIAL", "Primary material class identity", 0.95, "SPEC_COMPILER", 0.95, 0.0, ValidationMethod.MATERIAL)
        ]

        # 6. Configurar Variables (Modificables por F64 Autonomous Corrector)
        variables = [
            VariableSpec("VAR_BEVEL_WIDTH", "geometry.bevel_width", 0.001, 0.05, 0.01, "meters", 0.70, True),
            VariableSpec("VAR_ROUGHNESS", "materials.roughness", 0.10, 0.95, 0.65, "unitless", 0.80, True),
            VariableSpec("VAR_MICRO_STRENGTH", "surface.micro_detail_strength", 0.0, 1.0, 0.35, "factor", 0.40, True)
        ]

        # 7. Configurar Prioridades Cuantitativas y Clases de Requisitos
        priorities = {
            "silhouette": 1.0,
            "proportions": 0.98,
            "dimensions.height": 0.95,
            "materials.base_material": 0.90,
            "secondary_details": 0.60,
            "micro_detail": 0.30
        }

        req_classes = {
            "dimensions.height": RequirementClass.HARD if "exact" in comp_input.prompt.lower() or "±" in comp_input.prompt else RequirementClass.SOFT,
            "silhouette": RequirementClass.HARD,
            "materials.base_material": RequirementClass.HARD,
            "secondary_details": RequirementClass.PREFERENCE,
            "micro_detail": RequirementClass.INFORMATIONAL
        }

        # 8. Generar Criterios de Aceptación Cuantitativos para F61-F66
        criteria = CriteriaGenerator.generate_criteria(
            dimensions=norm["dimensions"],
            silhouette=norm["silhouette"],
            materials=norm["materials"],
            tolerances=tolerances
        )

        # 9. Configuración Unreal Engine y Presupuesto
        unreal_spec = UnrealRequirementsSpec(
            nanite_enabled=comp_input.project_constraints.get("nanite", True),
            lod_count=comp_input.project_constraints.get("lod_count", 3),
            collision_required=comp_input.project_constraints.get("collision_required", True)
        )
        prod_budget = ProductionBudgetSpec(
            poly_budget=comp_input.project_constraints.get("poly_budget", 15000),
            triangle_budget=comp_input.project_constraints.get("triangle_budget", 30000)
        )

        # 10. Preservación de Historial (F56 no destruye propiedades previamente aceptadas)
        spec_version = "1.0.0"
        if comp_input.previous_vas:
            prev_v = getattr(comp_input.previous_vas, "specification_version", "1.0.0")
            v_parts = prev_v.split(".")
            spec_version = f"{v_parts[0]}.{int(v_parts[1]) + 1}.0"
            # Preservar metadatos aceptados
            if hasattr(comp_input.previous_vas, "semantic_identity"):
                norm["semantic_identity"] = comp_input.previous_vas.semantic_identity

        vas = VisualAssetSpecification(
            schema_version="1.0.0",
            specification_id=f"VAS_{norm['semantic_identity']['asset_id'].upper()}_{spec_version.replace('.', '_')}",
            specification_version=spec_version,
            semantic_identity=norm["semantic_identity"],
            source={"prompt": comp_input.prompt, "reference_count": len(comp_input.reference_reports)},
            intent=norm["intent"],
            asset_classification=comp_input.asset_class_hint,
            visual_identity=norm["style"],
            silhouette=norm["silhouette"],
            proportions=norm["proportions"],
            dimensions=norm["dimensions"],
            components=norm["components"],
            geometry_requirements={"primitive_base": "CYLINDER" if "barrel" in comp_input.prompt.lower() else "BOX", "is_manifold": True},
            material_requirements=norm["materials"],
            unreal_requirements=unreal_spec,
            production_budget=prod_budget,
            invariants=invariants,
            variables=variables,
            tolerances=tolerances,
            priorities=priorities,
            requirement_classes=req_classes,
            acceptance_criteria=criteria,
            ambiguity_report=ambiguities,
            contradiction_report=contradictions,
            overall_confidence=0.95,
            traceability=traceability,
            compilation_metadata={"compiler_version": self.compiler_version}
        )

        # 11. Cálculo de Hash Lógico Canónico
        vas.specification_hash = SpecificationHasher.compute_hash(vas.__dict__)
        return vas

    def validate(self, specification: VisualAssetSpecification) -> ValidationResult:
        errors = []
        warnings = []

        if not specification.specification_id:
            errors.append("MISSING_SPECIFICATION_ID: Specification ID is mandatory.")
        if not specification.semantic_identity.get("semantic_id"):
            errors.append("MISSING_SEMANTIC_ID: Semantic ID from F54 is mandatory.")
        if not specification.specification_hash:
            errors.append("MISSING_SPECIFICATION_HASH: Specification hash is mandatory.")

        for c in specification.contradiction_report:
            if c.severity == ContradictionSeverity.CRITICAL:
                errors.append(f"CRITICAL_CONTRADICTION: {c.description}")
            else:
                warnings.append(f"CONTRADICTION_WARNING: {c.description}")

        for a in specification.ambiguity_report:
            if a.severity == AmbiguitySeverity.HIGH or a.severity == AmbiguitySeverity.CRITICAL:
                warnings.append(f"AMBIGUITY_WARNING: {a.description}")

        return ValidationResult(is_valid=(len(errors) == 0), errors=errors, warnings=warnings)

    def detect_ambiguities(self, specification: VisualAssetSpecification) -> List[AmbiguityReport]:
        return specification.ambiguity_report

    def detect_contradictions(self, specification: VisualAssetSpecification) -> List[ContradictionReport]:
        return specification.contradiction_report

    def compute_hash(self, specification: VisualAssetSpecification) -> str:
        return SpecificationHasher.compute_hash(specification.__dict__)
