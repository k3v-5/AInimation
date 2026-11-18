from typing import Dict, Any, List, Optional, Tuple
from ..core.asset_status import AssetState, ReuseDecisionType
from ..core.asset_schema import (
    LibraryAssetRecord, AssetMetadata, AssetVariant, ReuseDecision
)
from ..core.asset_registry import AssetRegistry
from ..search.query_schema import AssetSearchQuery, SearchResultCandidate
from ..search.retrieval_engine import AssetRetrievalEngine
from ..search.fingerprint_matcher import FingerprintMatcher
from ..reuse.variant_manager import VariantManager
from ..reuse.instancing_engine import InstancingEngine
from ..reuse.reuse_decision_maker import ReuseDecisionMaker

class AssetReuseEngineAPI:
    """
    Asset Library, Retrieval & Reuse Engine API (AOE v23)
    
    Regla Fundamental:
    LA CREACIÓN DESDE CERO ES EL ÚLTIMO RECURSO.
    1. EXACT REUSE
    2. PARAMETRIC VARIANT
    3. DUPLICATE + MODIFY
    4. TEMPLATE
    5. COMPONENT COMPOSITION
    6. NEW GENERATION (Solo si la búsqueda no encuentra ningún activo aceptable).
    """
    def __init__(self):
        self.registry = AssetRegistry()
        self.retrieval = AssetRetrievalEngine(self.registry)
        self.variant_mgr = VariantManager()

    def register_asset(self, asset: LibraryAssetRecord):
        self.registry.register_asset(asset)

    def search_candidates(self, query: AssetSearchQuery) -> List[SearchResultCandidate]:
        return self.retrieval.search(query)

    def search_and_decide_reuse(
        self,
        query: AssetSearchQuery,
        overrides: Optional[Dict[str, Any]] = None
    ) -> ReuseDecision:
        candidates = self.retrieval.search(query)
        target_asset = self.registry.get_asset(candidates[0].asset_id) if candidates else None
        return ReuseDecisionMaker.evaluate_decision(
            candidates=candidates,
            target_asset=target_asset,
            overrides=overrides,
            variant_manager=self.variant_mgr
        )

    def instantiate_batch(self, canonical_asset_id: str, count: int) -> Dict[str, Any]:
        return InstancingEngine.create_instances(canonical_asset_id, count)

    def find_duplicate_geometries(self) -> List[Tuple[str, str]]:
        return FingerprintMatcher.find_duplicates(self.registry.list_all())

    def validate_creation_policy(self, performed_retrieval: bool) -> Tuple[bool, str]:
        if not performed_retrieval:
            return False, "POLICY_DENIED: Attempting to create new asset from scratch without executing library retrieval first."
        return True, "Policy compliant."
