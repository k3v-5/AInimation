from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from ..core.template_schema import ParameterDefinition, ComponentDefinition
from ..core.construction_plan import ConstructionPlan
from ...spec_compiler.core.asset_spec import AssetSpec

class IAssetTemplate(ABC):
    @property
    @abstractmethod
    def template_id(self) -> str:
        pass

    @property
    @abstractmethod
    def template_version(self) -> str:
        pass

    @property
    @abstractmethod
    def supported_asset_types(self) -> List[str]:
        pass

    @abstractmethod
    def get_parameter_definitions(self) -> Dict[str, ParameterDefinition]:
        pass

    @abstractmethod
    def build_plan(self, resolved_parameters: Dict[str, Any], seed: int = 42) -> ConstructionPlan:
        pass
