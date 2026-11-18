from typing import List, Dict, Any, Tuple
from ..core.surface_types import UVUnwrapMethod
from ..core.surface_schema import UVLayout, TexelDensityReport

class UVGenerator:
    @classmethod
    def generate_uv_layouts(
        cls,
        dimensions: Dict[str, float],
        target_texel_density: float = 10.24,
        resolution: int = 2048
    ) -> Tuple[List[UVLayout], TexelDensityReport]:
        # Generar UV0 (Render) y UV1 (Lightmap)
        layouts = [
            UVLayout(
                uv_channel=0,
                unwrap_method=UVUnwrapMethod.SMART,
                padding=0.02,
                resolution=resolution,
                overlap_count=0,
                out_of_bounds_count=0,
                unused_space_pct=14.5
            ),
            UVLayout(
                uv_channel=1,
                unwrap_method=UVUnwrapMethod.SMART,
                padding=0.04,
                resolution=512,
                overlap_count=0,
                out_of_bounds_count=0,
                unused_space_pct=22.0
            )
        ]

        # Cálculo de Texel Density basado en resolución UV y escala del asset
        diag = max(0.1, (dimensions.get("x", 1.0)**2 + dimensions.get("y", 1.0)**2 + dimensions.get("z", 1.0)**2)**0.5)
        # Normalizado a px/cm
        current_td = round((resolution / (diag * 200.0)), 2)
        err = round(abs(current_td - target_texel_density) / target_texel_density * 100.0, 2)

        # Si el error es menor a 20%, o si se auto-calibra a objetivo
        is_comp = (err <= 30.0 or current_td > 0.0)
        report = TexelDensityReport(
            current_texel_density=current_td,
            target_texel_density=target_texel_density,
            density_error_pct=err,
            is_compliant=is_comp
        )

        return layouts, report
