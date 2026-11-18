import hashlib
import json
from typing import Dict, Any, List, Optional, Tuple
from ..core.production_types import PivotType, QualityGateStatus, ChangeClass
from ..core.production_schema import (
    BlenderExportContract, SocketDefinition, ExportManifest, QualityGateReport
)
from .naming_path_policy import NamingPathPolicy

class ExportValidator:
    @classmethod
    def create_manifest(
        cls,
        asset_id: str,
        version: str,
        parameters: Dict[str, Any],
        sockets: Optional[List[SocketDefinition]] = None,
        contract: Optional[BlenderExportContract] = None
    ) -> ExportManifest:
        contract = contract or BlenderExportContract()
        sockets = sockets or []

        mesh_name = NamingPathPolicy.get_mesh_name(asset_id)
        mat_inst = NamingPathPolicy.get_material_instance_name(asset_id)
        col_name = NamingPathPolicy.get_collision_name(asset_id)

        # Hash determinista de contenido y pipeline
        content_repr = json.dumps({"params": parameters, "sockets": [s.socket_name for s in sockets]}, sort_keys=True)
        content_hash = hashlib.sha256(content_repr.encode()).hexdigest()[:16]
        
        fingerprint_repr = json.dumps({
            "asset_id": asset_id,
            "version": version,
            "units": contract.units,
            "params": parameters
        }, sort_keys=True)
        pipeline_fingerprint = hashlib.sha256(fingerprint_repr.encode()).hexdigest()[:16]

        return ExportManifest(
            asset_id=asset_id,
            version=version,
            mesh_name=mesh_name,
            material_instances=[mat_inst],
            textures=[f"TX_{asset_id}_D", f"TX_{asset_id}_N", f"TX_{asset_id}_ORM"],
            collision_name=col_name,
            lod_count=4,
            sockets=sockets,
            content_hash=content_hash,
            pipeline_fingerprint=pipeline_fingerprint,
            metadata={"data_asset": NamingPathPolicy.get_data_asset_name(asset_id)}
        )

    @classmethod
    def evaluate_socket_breaking_changes(
        cls,
        previous_sockets: List[SocketDefinition],
        new_sockets: List[SocketDefinition]
    ) -> Tuple[ChangeClass, List[str]]:
        new_names = {s.socket_name for s in new_sockets}
        missing_critical = []

        for s in previous_sockets:
            if s.is_critical and s.socket_name not in new_names:
                missing_critical.append(s.socket_name)

        if missing_critical:
            return ChangeClass.BREAKING, missing_critical
        return ChangeClass.COMPATIBLE, []

    @classmethod
    def validate_quality_gate(
        cls,
        manifest: ExportManifest,
        contract: BlenderExportContract
    ) -> QualityGateReport:
        checks = {
            "units_centimeters": contract.units == "CENTIMETERS",
            "pivot_base": contract.pivot_type == PivotType.BASE,
            "manifold_geometry": contract.validate_manifold,
            "valid_naming": manifest.mesh_name.startswith("SM_") and manifest.collision_name.startswith("UCX_"),
            "lods_present": manifest.lod_count >= 1
        }
        errors = [k for k, v in checks.items() if not v]
        status = QualityGateStatus.PASS if not errors else QualityGateStatus.FAIL
        return QualityGateReport(asset_id=manifest.asset_id, status=status, checks=checks, errors=errors)
