from typing import Dict, Any, Optional
from ..core.strategy_types import AssetComplexityLevel
from ..core.strategy_schema import AssetComplexityReport

class AssetComplexityAnalyzer:
    @classmethod
    def analyze(
        cls,
        asset_class: str,
        components_count: int,
        batch_size: int = 1
    ) -> AssetComplexityReport:
        is_batch = batch_size > 1
        repeatability = "FAMILY" if is_batch else "SINGLE"
        
        if "BUILDING" in asset_class.upper() or components_count >= 5:
            complexity = AssetComplexityLevel.HIGHLY_MODULAR
        elif "CHARACTER" in asset_class.upper():
            complexity = AssetComplexityLevel.ORGANIC
        elif components_count > 2:
            complexity = AssetComplexityLevel.MEDIUM
        else:
            complexity = AssetComplexityLevel.SIMPLE

        return AssetComplexityReport(
            asset_class=asset_class,
            complexity_level=complexity,
            component_count=components_count,
            is_batch=is_batch,
            batch_size=batch_size,
            repeatability=repeatability
        )
