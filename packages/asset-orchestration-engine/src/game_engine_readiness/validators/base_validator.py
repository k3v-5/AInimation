from abc import ABC, abstractmethod
from typing import Dict, Any, List
from ..core.readiness_schema import EngineValidationResult, EngineProfile

class IEngineValidator(ABC):
    @property
    @abstractmethod
    def validator_id(self) -> str:
        pass

    @abstractmethod
    def validate(
        self,
        optimized_asset: Any, # F67 OptimizedAssetResult / Geometry
        profile: EngineProfile,
        context: Dict[str, Any]
    ) -> List[EngineValidationResult]:
        pass
