import time
from typing import Dict, Any, List, Optional
from ..core.readiness_types import ReadinessStatus
from ..core.readiness_schema import (
    EngineProfile, ExportProfile, EngineValidationResult,
    EngineReadinessManifest, GameEngineReadyAsset, ReadinessValidationResult
)
from ..validators.validator_registry import EngineValidatorRegistry
from .readiness_evaluator import ReadinessEvaluator
from .readiness_manifest_generator import ReadinessManifestGenerator
from .readiness_hasher import ReadinessHasher

class GameEngineReadinessService:
    """
    Game-Engine Readiness Service (AOE v68)
    
    Regla Fundamental:
    VERIFICA RIGUROSAMENTE QUE EL ASSET OPTIMIZADO POR F67 CUMPLA TODOS LOS REQUISITOS
    TÉCNICOS DE UNREAL ENGINE (GEOMETRÍA, MATERIALES, TEXTURAS, TRANSFORMS, PIVOT, UCX, LOD, NANITE)
    ANTES DE PERMITIR SU EMPAQUETADO Y DESPLIEGUE HACIA EL PROYECTO.
    """
    def __init__(self, service_version: str = "1.0.0"):
        self.service_version = service_version
        self.registry = EngineValidatorRegistry()

    def process_readiness(
        self,
        optimized_asset_result: Any, # F67 OptimizedAssetResult
        engine_profile: Optional[EngineProfile] = None,
        export_profile: Optional[ExportProfile] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> GameEngineReadyAsset:
        ctx = context or {}
        e_prof = engine_profile or EngineProfile()
        exp_prof = export_profile or ExportProfile()

        asset_id = getattr(optimized_asset_result, "asset_id", "asset.root")
        sem_id = getattr(optimized_asset_result, "semantic_id", "asset.root")
        source_hash = getattr(optimized_asset_result, "optimized_state_hash", "") or f"SRC_HASH_{asset_id}"

        # 1. Stale State Protection
        expected_hash = ctx.get("expected_source_hash", "")
        if expected_hash and source_hash and expected_hash != source_hash:
            manifest = EngineReadinessManifest(
                manifest_id=f"MANIFEST_STALE_{asset_id}",
                asset_id=asset_id,
                semantic_id=sem_id,
                readiness_status=ReadinessStatus.FAILED,
                readiness_score=None,
                validation_results=[]
            )
            return GameEngineReadyAsset(
                asset_id=asset_id,
                semantic_id=sem_id,
                source_state_hash=source_hash,
                prepared_state_hash=source_hash,
                engine_profile_id=e_prof.profile_id,
                export_profile_id=exp_prof.profile_id,
                readiness_status=ReadinessStatus.FAILED,
                readiness_score=0.0,
                manifest=manifest,
                readiness_hash="HASH_STALE_STATE"
            )

        # 2. Ejecución de Validadores Registrados
        validation_results: List[EngineValidationResult] = []
        for validator in self.registry.list_validators():
            v_res = validator.validate(optimized_asset_result, e_prof, ctx)
            validation_results.extend(v_res)

        # 3. Evaluación de Estado y Puntuación
        status, score, blockers, warnings = ReadinessEvaluator.evaluate(validation_results)

        # 4. Generación del Manifiesto
        manifest = ReadinessManifestGenerator.generate_manifest(
            asset_id=asset_id,
            semantic_id=sem_id,
            readiness_status=status,
            readiness_score=score,
            validation_results=validation_results,
            engine_profile_id=e_prof.profile_id
        )

        # 5. Hash Determinista
        r_hash = ReadinessHasher.compute_readiness_hash(
            asset_id=asset_id,
            source_hash=source_hash,
            engine_profile_id=e_prof.profile_id,
            status=status.value,
            score=score.total
        )

        return GameEngineReadyAsset(
            asset_id=asset_id,
            semantic_id=sem_id,
            source_state_hash=source_hash,
            prepared_state_hash=f"PREP_{r_hash[:12]}",
            engine_profile_id=e_prof.profile_id,
            export_profile_id=exp_prof.profile_id,
            readiness_status=status,
            readiness_score=score.total,
            manifest=manifest,
            readiness_hash=r_hash,
            generation_metadata={"service_version": self.service_version}
        )

    def validate_ready_asset(self, ready_asset: GameEngineReadyAsset) -> ReadinessValidationResult:
        errors = []
        warnings = []
        if not ready_asset.asset_id:
            errors.append("MISSING_ASSET_ID: Asset ID is mandatory.")
        if ready_asset.readiness_status == ReadinessStatus.NOT_READY:
            warnings.append("ASSET_NOT_READY: Asset contains blockers and cannot enter production without fixing.")
        return ReadinessValidationResult(is_valid=(len(errors) == 0), errors=errors, warnings=warnings)
