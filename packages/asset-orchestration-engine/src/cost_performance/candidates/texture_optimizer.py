from typing import Dict, Any

class TextureOptimizer:
    """Analyzes memory and disk cost across resolution levels (4K, 2K, 1K, 512)."""

    RESOLUTION_MEMORY_MAP = {
        "4K": 64.0,   # MB per set
        "2K": 16.0,
        "1K": 4.0,
        "512": 1.0
    }

    @classmethod
    def evaluate_resolution_tradeoff(cls, current_resolution: str, quality_floor: float = 0.90) -> Dict[str, Any]:
        cur_mem = cls.RESOLUTION_MEMORY_MAP.get(current_resolution, 16.0)
        options = []

        for res, mem in cls.RESOLUTION_MEMORY_MAP.items():
            est_quality = 0.97 if res == "4K" else (0.95 if res == "2K" else (0.88 if res == "1K" else 0.78))
            is_valid = est_quality >= quality_floor
            options.append({
                "resolution": res,
                "memory_mb": mem,
                "estimated_quality": est_quality,
                "approved": is_valid
            })

        optimal = max([o for o in options if o["approved"]], key=lambda x: x["estimated_quality"] / max(1.0, x["memory_mb"]))

        return {
            "current_resolution": current_resolution,
            "current_memory_mb": cur_mem,
            "options": options,
            "optimal_recommendation": optimal["resolution"]
        }
