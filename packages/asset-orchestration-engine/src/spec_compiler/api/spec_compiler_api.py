from typing import Dict, Any, Optional, Tuple
from ..core.asset_spec import AssetSpec
from ..core.ontology_registry import AssetOntology
from ..compiler.specification_compiler import SpecificationCompiler
from ..lifecycle.spec_patch import SpecificationPatcher
from ..lifecycle.drift_detector import SpecificationDriftDetector

class SpecificationCompilerAPI:
    """
    Asset Specification Compiler API (AOE v14)
    
    Regla Fundamental:
    USER REQUEST -> SPEC COMPILER -> ASSET SPEC -> VALIDATOR -> PLANNER -> EXECUTION
    ELIMINACIÓN TOTAL DE AMBIGÜEDAD ANTES DE TOCAR BLENDER.
    """
    def __init__(self):
        self.ontology = AssetOntology()
        self.compiler = SpecificationCompiler(self.ontology)

    def compile_request(self, user_text: str) -> Tuple[bool, Optional[AssetSpec], str]:
        return self.compiler.compile(user_text)

    def apply_patch(self, base_spec: AssetSpec, property_path: str, new_value: Any) -> Tuple[AssetSpec, Dict[str, Any]]:
        return SpecificationPatcher.apply_patch(base_spec, property_path, new_value)

    def check_drift(self, actual_measurements: Dict[str, float], spec: AssetSpec) -> Tuple[str, float, str]:
        return SpecificationDriftDetector.check_drift(actual_measurements, spec)

    def register_asset_type(self, asset_type: str):
        self.ontology.register_asset_type(asset_type)
