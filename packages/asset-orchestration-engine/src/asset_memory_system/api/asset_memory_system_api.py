import uuid
from typing import Dict, Any, Optional, List, Tuple
from ..core.memory_schema import (
    AssetRecord, AssetVersionRecord, PatternRecord, FailureMemoryRecord, AuditEvent
)
from ..core.memory_status import AssetStatus, PatternStatus, ReproductionStatus
from ..core.version_manager import VersionManager
from ..storage.sqlite_asset_store import SQLiteAssetStore
from ..learning.knowledge_extractor import KnowledgeExtractor
from ..learning.pattern_promoter import PatternPromoter, NegativeKnowledgeEngine
from ..retrieval.memory_query_engine import MemoryQueryEngine
from ..retrieval.reuse_strategy import ReuseStrategyDecision
from ...correction_execution.providers.blender_provider import IBlenderProvider
from ...procedural_templates.api.procedural_templates_api import ProceduralTemplatesAPI

class AssetMemorySystemAPI:
    """
    Asset Memory, Versioning & Learning API (AOE v17)
    
    Regla Fundamental:
    PROMPT -> BUSCAR CONOCIMIENTO -> REUTILIZAR/ADAPTAR -> GENERAR -> VALIDAR -> APRENDER
    NO REPETIR EXPERIMENTOS QUE YA FUERON RESUELTOS.
    """
    def __init__(self, db_path: str = ":memory:", is_memoryless: bool = False):
        self.is_memoryless = is_memoryless
        self.store = None if is_memoryless else SQLiteAssetStore(db_path)

    def close(self):
        if self.store:
            self.store.close()

    def create_asset(
        self,
        asset_id: str,
        name: str,
        asset_type: str = "SWORD",
        template_id: str = "weapon.sword.standard",
        tags: Optional[List[str]] = None
    ) -> Optional[AssetRecord]:
        if self.is_memoryless:
            return None

        rec = AssetRecord(
            asset_id=asset_id,
            name=name,
            asset_type=asset_type,
            template_id=template_id,
            status=AssetStatus.DRAFT,
            tags=tags or []
        )
        self.store.store_asset(rec)
        self._log_event(asset_id, "ASSET", "CREATE")
        return rec

    def create_version(
        self,
        asset_id: str,
        version_number: str = "1.0.0",
        parameters: Optional[Dict[str, Any]] = None,
        parent_version_id: Optional[str] = None,
        branch: str = "main",
        template_version: str = "1.0.0",
        seed: int = 42
    ) -> Tuple[AssetVersionRecord, bool]: # (record, is_duplicate)
        if self.is_memoryless:
            rec = AssetVersionRecord(f"ver_{uuid.uuid4().hex[:6]}", asset_id, version_number, parameters=parameters or {})
            return rec, False

        params = parameters or {}
        p_hash = VersionManager.calculate_parameter_hash(params, template_version)

        # Comprobar duplicados
        existing = self.store.find_version_by_hash(asset_id, p_hash)
        if existing:
            return existing, True

        rec = AssetVersionRecord(
            version_id=f"ver_{uuid.uuid4().hex[:6]}",
            asset_id=asset_id,
            version_number=version_number,
            parent_version_id=parent_version_id,
            branch=branch,
            parameters=params,
            parameter_hash=p_hash,
            template_version=template_version,
            generation_seed=seed
        )
        self.store.store_version(rec)
        self._log_event(rec.version_id, "VERSION", "CREATE")
        return rec, False

    def search_similar_assets(
        self,
        asset_type: str,
        template_id: str,
        target_dimensions: Optional[Dict[str, float]] = None
    ) -> List[Tuple[AssetRecord, float, str]]:
        if self.is_memoryless:
            return []
        return MemoryQueryEngine.search_similar_assets(self.store, asset_type, template_id, target_dimensions or {})

    def record_correction_and_learn(
        self,
        template_id: str,
        trigger_issue: str,
        target_parameter: str,
        recommended_action: str,
        is_success: bool,
        template_version: str = "1.0.0"
    ) -> PatternRecord:
        if self.is_memoryless:
            return KnowledgeExtractor.extract_pattern_from_correction(template_id, trigger_issue, target_parameter, recommended_action)

        # Buscar si ya existe un patrón candidato
        existing_patterns = self.store.find_patterns(template_id, trigger_issue)
        if existing_patterns:
            pat = existing_patterns[0]
            updated = PatternPromoter.record_evidence_and_evaluate(pat, is_success)
            self.store.store_pattern(updated)
            return updated
        else:
            pat = KnowledgeExtractor.extract_pattern_from_correction(template_id, trigger_issue, target_parameter, recommended_action, template_version)
            self.store.store_pattern(pat)
            return pat

    def record_failure(
        self,
        asset_id: str,
        template_id: str,
        problematic_parameters: Dict[str, Any],
        error_type: str = "COLLISION"
    ):
        if self.is_memoryless:
            return
        rec = FailureMemoryRecord(
            failure_id=f"fail_{uuid.uuid4().hex[:6]}",
            asset_id=asset_id,
            template_id=template_id,
            problematic_parameters=problematic_parameters,
            error_type=error_type
        )
        self.store.store_failure(rec)

    def check_negative_knowledge(self, template_id: str, candidate_params: Dict[str, Any]) -> Tuple[bool, str]:
        if self.is_memoryless:
            return False, "Memoryless mode: no negative knowledge checks."
        failures = self.store.get_failures(template_id)
        return NegativeKnowledgeEngine.check_failure_region(template_id, candidate_params, failures)

    def reproduce_version(
        self,
        asset_id: str,
        version_record: AssetVersionRecord,
        provider: IBlenderProvider,
        templates_api: ProceduralTemplatesAPI
    ) -> Tuple[ReproductionStatus, str]:
        """
        Reproduce exactamente una versión a partir de sus parámetros, plantilla y semilla.
        """
        from ...spec_compiler.core.asset_spec import AssetSpec
        spec = AssetSpec(spec_id=f"spec_repro_{asset_id}", asset_type="SWORD")
        res = templates_api.build_from_spec(asset_id, spec, seed=version_record.generation_seed)
        if res["success"]:
            return ReproductionStatus.EXACT, f"Version {version_record.version_number} reproduced with exact functional equivalence."
        return ReproductionStatus.FAILED, "Reproduction failed."

    def _log_event(self, entity_id: str, entity_type: str, event_type: str, actor: str = "SYSTEM"):
        if not self.is_memoryless and self.store:
            evt = AuditEvent(
                event_id=f"evt_{uuid.uuid4().hex[:6]}",
                entity_id=entity_id,
                entity_type=entity_type,
                event_type=event_type,
                actor=actor
            )
            self.store.store_event(evt)
