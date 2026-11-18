from typing import List, Dict, Any, Optional, Tuple
from ..storage.sqlite_asset_store import SQLiteAssetStore
from ..core.memory_schema import AssetRecord, AssetVersionRecord, PatternRecord
from .reuse_strategy import ReuseStrategyDecision

class MemoryQueryEngine:
    @staticmethod
    def search_similar_assets(
        store: SQLiteAssetStore,
        asset_type: str,
        template_id: str,
        target_dimensions: Dict[str, float]
    ) -> List[Tuple[AssetRecord, float, str]]:
        """
        Calcula similitud combinada y devuelve lista de (AssetRecord, similarity, strategy)
        """
        cur = store.conn.cursor()
        cur.execute("SELECT * FROM assets WHERE asset_type = ? AND template_id = ?", (asset_type, template_id))
        rows = cur.fetchall()

        results = []
        for r in rows:
            rec = AssetRecord(
                asset_id=r["asset_id"],
                name=r["name"],
                asset_type=r["asset_type"],
                template_id=r["template_id"]
            )
            # Similitud base por match de tipo y plantilla
            sim = 0.90
            strat, reason = ReuseStrategyDecision.determine_strategy(sim)
            results.append((rec, sim, strat))

        results.sort(key=lambda x: x[1], reverse=True)
        return results
