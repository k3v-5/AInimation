from typing import List, Optional
from ..core.asset_registry import AssetRegistry
from ..core.asset_status import AssetState
from .query_schema import AssetSearchQuery, SearchResultCandidate

class AssetRetrievalEngine:
    def __init__(self, registry: AssetRegistry):
        self.registry = registry

    def search(self, query: AssetSearchQuery) -> List[SearchResultCandidate]:
        candidates: List[SearchResultCandidate] = []

        for asset in self.registry.list_all():
            # 1. Filtro estricto: Descartar activos en cuarentena
            if asset.state == AssetState.QUARANTINED:
                continue

            # 2. Puntuación Semántica
            if query.type_name.lower() not in asset.metadata.type_name.lower():
                continue # No coincide el tipo básico
            sem_score = 1.00

            # 3. Puntuación de Estilo (Hard Filter si hay discrepancia total)
            style_score = 1.00
            if query.style:
                if query.style.lower() in asset.metadata.style.lower():
                    style_score = 1.00
                else:
                    # Discrepancia de estilo: descartar candidato (Hard Filter)
                    continue

            # 4. Puntuación de Dimensiones
            dim_score = 1.00
            reasons = []
            for d_name, exp_val in query.target_dimensions.items():
                act_val = asset.metadata.dimensions.get(d_name)
                if act_val is not None:
                    if abs(act_val - exp_val) < 0.05:
                        reasons.append(f"Dimension '{d_name}' exact match ({act_val}m).")
                    elif query.allow_parametric_variant:
                        dim_score = min(dim_score, 0.60)
                        reasons.append(f"Dimension '{d_name}' adaptable ({act_val}m -> {exp_val}m).")
                    else:
                        dim_score = min(dim_score, 0.10)

            # 5. Puntuación Visual de Referencia
            vis_score = query.reference_visual_score if query.reference_visual_score is not None else 1.00

            # 6. Puntuación Compuesta
            quality = asset.quality_score
            reuse_score = (
                sem_score * 0.25 +
                style_score * 0.25 +
                dim_score * 0.25 +
                vis_score * 0.15 +
                quality * 0.10
            )

            candidates.append(SearchResultCandidate(
                asset_id=asset.asset_id,
                semantic_score=sem_score,
                visual_score=vis_score,
                style_score=style_score,
                dimension_score=dim_score,
                quality_score=quality,
                reuse_score=round(reuse_score, 4),
                reasons=reasons
            ))

        # Ordenar de mayor a menor puntuación
        candidates.sort(key=lambda c: c.reuse_score, reverse=True)
        return candidates
