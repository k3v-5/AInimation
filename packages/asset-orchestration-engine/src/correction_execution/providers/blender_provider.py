from abc import ABC, abstractmethod
from typing import Dict, Any, Tuple, List, Optional

class IBlenderProvider(ABC):
    @abstractmethod
    def get_component_dimensions(self, asset_id: str, component_id: str) -> Optional[Tuple[float, float, float]]:
        pass

    @abstractmethod
    def set_component_dimensions(self, asset_id: str, component_id: str, dimensions: Tuple[float, float, float]) -> bool:
        pass

    @abstractmethod
    def scale_component(self, asset_id: str, component_id: str, factor: float) -> bool:
        pass

    @abstractmethod
    def get_material_property(self, asset_id: str, component_id: str, prop_name: str) -> Any:
        pass

    @abstractmethod
    def set_material_property(self, asset_id: str, component_id: str, prop_name: str, value: Any) -> bool:
        pass

    @abstractmethod
    def get_asset_state(self, asset_id: str) -> Dict[str, Any]:
        pass

    @abstractmethod
    def restore_asset_state(self, asset_id: str, state_data: Dict[str, Any]) -> bool:
        pass
