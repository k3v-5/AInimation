from typing import List, Optional, Dict, Any
from ..core.asset_schema import ReuseDecision, LibraryAssetRecord
from ..core.asset_status import ReuseDecisionType, AssetState
from ..search.query_schema import SearchResultCandidate
from .variant_manager import VariantManager

class ReuseDecisionMaker:
    @staticmethod
    def evaluate_decision(
        candidates: List[SearchResultCandidate],
        target_asset: Optional[LibraryAssetRecord] = None,
        overrides: Optional[Dict[str, Any]] = None,
        variant_manager: Optional[VariantManager] = None
    ) -> ReuseDecision:
        if not candidates:
            return ReuseDecision(
                decision=ReuseDecisionType.GENERATE_NEW,
                selected_asset_id=None,
                confidence=0.90,
                reasons=["NO_ACCEPTABLE_ASSET: No candidates found in library exceeding minimum reuse threshold."]
            )

        top = candidates[0]

        # Comprobar si el activo objetivo está bloqueado en producción
        if target_asset and target_asset.state == AssetState.PRODUCTION_LOCKED:
            var = variant_manager.create_or_get_variant(target_asset.asset_id, overrides or {}) if variant_manager else None
            return ReuseDecision(
                decision=ReuseDecisionType.PARAMETRIC_VARIANT,
                selected_asset_id=target_asset.asset_id,
                variant_id=var.variant_id if var else None,
                confidence=0.95,
                reasons=["PRODUCTION_LOCKED: Asset is locked for production; created parametric variant to preserve original."],
                score_breakdown={"reuse_score": top.reuse_score}
            )

        if top.reuse_score >= 0.92 and not overrides and top.dimension_score >= 0.90:
            return ReuseDecision(
                decision=ReuseDecisionType.EXACT_REUSE,
                selected_asset_id=top.asset_id,
                confidence=top.quality_score,
                reasons=[f"EXACT_REUSE: Asset '{top.asset_id}' matches requirements with score {top.reuse_score:.2f}."],
                score_breakdown={"reuse_score": top.reuse_score}
            )
        elif top.reuse_score >= 0.65:
            var = variant_manager.create_or_get_variant(top.asset_id, overrides or {}) if variant_manager else None
            return ReuseDecision(
                decision=ReuseDecisionType.PARAMETRIC_VARIANT,
                selected_asset_id=top.asset_id,
                variant_id=var.variant_id if var else None,
                confidence=0.90,
                reasons=[f"PARAMETRIC_VARIANT: Asset '{top.asset_id}' is structurally compatible ({top.reuse_score:.2f}); applying parametric variant."],
                score_breakdown={"reuse_score": top.reuse_score}
            )
        else:
            return ReuseDecision(
                decision=ReuseDecisionType.GENERATE_NEW,
                selected_asset_id=None,
                confidence=0.85,
                reasons=[f"GENERATE_NEW: Top candidate '{top.asset_id}' score {top.reuse_score:.2f} is below acceptable threshold."],
                score_breakdown={"reuse_score": top.reuse_score}
            )
