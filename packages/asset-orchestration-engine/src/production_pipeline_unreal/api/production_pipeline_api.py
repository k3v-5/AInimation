from typing import Dict, Any, List, Optional, Tuple
from ..core.production_types import (
    AssetLifecycle, PivotType, CollisionStrategy,
    NanitePolicy, ChangeClass, QualityGateStatus, SourceOwnership
)
from ..core.production_schema import (
    SocketDefinition, BlenderExportContract, CollisionContract,
    LODContract, ExportManifest, ProductionAsset, QualityGateReport,
    PublicationRecord
)
from ..contracts.naming_path_policy import NamingPathPolicy
from ..contracts.export_validator import ExportValidator
from ..cache.build_cache import BuildCache
from ..gateway.unreal_execution_gateway import UnrealExecutionGateway

class ProductionPipelineAPI:
    """
    Production Pipeline & Unreal Integration API (AOE v48)
    
    Regla Fundamental:
    BLENDER NO ES LA FUENTE FINAL DE VERDAD DEL JUEGO.
    EL PIPELINE SEPARA SOURCE -> GENERATED -> EXPORTED -> STAGING -> IMPORTED -> PUBLISHED,
    GARANTIZA DETERMINISMO EN NAMING Y PATHS, APLICA QUALITY GATES,
    DETECTA BREAKING CHANGES EN SOCKETS, PROTEGE MODIFICACIONES MANUALES
    Y EJECUTA ACTUALIZACIONES INCREMENTALES Y TRANSACCIONALES CON ROLLBACK.
    """
    def __init__(self):
        self.cache = BuildCache()
        self.gateway = UnrealExecutionGateway()

    def process_and_export_asset(
        self,
        asset_id: str,
        version: str,
        parameters: Dict[str, Any],
        sockets: Optional[List[SocketDefinition]] = None,
        contract: Optional[BlenderExportContract] = None
    ) -> Tuple[ExportManifest, bool]:
        contract = contract or BlenderExportContract()
        sockets = sockets or []

        # 1. Comprobar Caché
        manifest = ExportValidator.create_manifest(asset_id, version, parameters, sockets, contract)
        if self.cache.contains(manifest.pipeline_fingerprint):
            cached = self.cache.get(manifest.pipeline_fingerprint)
            return cached, True # Cache Hit

        # 2. Guardar en Caché
        self.cache.put(manifest.pipeline_fingerprint, manifest)
        return manifest, False # Cache Miss

    def validate_quality_gate(
        self,
        manifest: ExportManifest,
        contract: Optional[BlenderExportContract] = None
    ) -> QualityGateReport:
        contract = contract or BlenderExportContract()
        return ExportValidator.validate_quality_gate(manifest, contract)

    def evaluate_socket_compatibility(
        self,
        previous_sockets: List[SocketDefinition],
        new_sockets: List[SocketDefinition]
    ) -> Tuple[ChangeClass, List[str]]:
        return ExportValidator.evaluate_socket_breaking_changes(previous_sockets, new_sockets)

    def stage_asset_in_unreal(self, manifest: ExportManifest) -> ProductionAsset:
        return self.gateway.import_to_staging(manifest)

    def publish_asset_to_unreal(
        self,
        asset_id: str,
        category: str = "Environment",
        simulate_failure: bool = False
    ) -> PublicationRecord:
        return self.gateway.publish_asset(asset_id, category, simulate_failure)

    def mark_manual_modified_in_unreal(self, asset_id: str):
        self.gateway.mark_manual_modified_in_unreal(asset_id)
