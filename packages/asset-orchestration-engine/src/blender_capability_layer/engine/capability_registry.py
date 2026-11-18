from typing import Dict, Any, List, Optional
from ..core.capability_types import CapabilityCategory
from ..core.capability_schema import CapabilityContract

class CapabilityRegistry:
    def __init__(self):
        self._contracts: Dict[str, CapabilityContract] = {}
        self._init_standard_capabilities()

    def _init_standard_capabilities(self):
        standards = [
            CapabilityContract("object.create", CapabilityCategory.OBJECT, "v1", ["object_id"]),
            CapabilityContract("geometry.create", CapabilityCategory.GEOMETRY, "v1", ["object_id", "geometry_type"]),
            CapabilityContract("transform.set", CapabilityCategory.TRANSFORM, "v1", ["object_id"]),
            CapabilityContract("modifier.add", CapabilityCategory.MODIFIER, "v1", ["object_id", "modifier_type"]),
            CapabilityContract("material.create", CapabilityCategory.MATERIAL, "v1", ["material_name"]),
            CapabilityContract("material.assign", CapabilityCategory.MATERIAL, "v1", ["object_id", "material_name"]),
            CapabilityContract("object.inspect", CapabilityCategory.INSPECTION, "v1", ["object_id"]),
            CapabilityContract("scene.inspect", CapabilityCategory.INSPECTION, "v1", []),
            CapabilityContract("object.delete", CapabilityCategory.OBJECT, "v1", ["object_id"]),
            CapabilityContract("export.fbx", CapabilityCategory.EXPORT, "v1", ["output_path"])
        ]
        for c in standards:
            self._contracts[c.capability_id] = c

    def get_contract(self, capability_id: str) -> Optional[CapabilityContract]:
        return self._contracts.get(capability_id)

    def validate_request_parameters(self, capability_id: str, parameters: Dict[str, Any]) -> bool:
        contract = self.get_contract(capability_id)
        if not contract:
            raise KeyError(f"CAPABILITY_UNSUPPORTED: Unknown capability '{capability_id}'.")
        
        for req in contract.required_parameters:
            if req not in parameters:
                raise ValueError(f"INVALID_REQUEST: Missing required parameter '{req}' for capability '{capability_id}'.")
        return True
