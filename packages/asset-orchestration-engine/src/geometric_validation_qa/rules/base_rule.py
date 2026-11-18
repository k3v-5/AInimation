from abc import ABC, abstractmethod
from typing import Dict, Any, List, Tuple
from ..core.qa_types import GeometricDefectCategory
from ..core.qa_schema import GeometricDefect, GeometryValidationConfiguration

class IGeometryValidationRule(ABC):
    @property
    @abstractmethod
    def rule_id(self) -> str:
        pass

    @property
    @abstractmethod
    def category(self) -> GeometricDefectCategory:
        pass

    @abstractmethod
    def validate(
        self,
        geometry_data: Any,
        context: Dict[str, Any],
        config: GeometryValidationConfiguration
    ) -> Tuple[float, List[GeometricDefect]]:
        """
        Retorna (score_normalizado, lista_de_defectos)
        """
        pass
