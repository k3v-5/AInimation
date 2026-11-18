"""
UE5 PostProcessSettings Serializer for UAF-81.85.
"""

from __future__ import annotations
from typing import Any, Dict

from uaf.runtime_lighting.postprocess import PostProcessSettings
from uaf.runtime_lighting.core import ToneMapperType, ExposureMode


class UE5PostProcessExporter:
    """
    Translates UAF PostProcessSettings to Unreal Engine 5 FPostProcessSettings struct.
    """

    @staticmethod
    def export_settings(settings: PostProcessSettings) -> Dict[str, Any]:
        return {
            "struct_type": "FPostProcessSettings",
            # Global Illumination & Reflections
            "dynamic_global_illumination_method": "EDynamicGlobalIlluminationMethod::Lumen",
            "reflection_method": "EReflectionMethod::Lumen",
            "lumen_surface_cache_resolution": 1.0,
            # Exposure
            "auto_exposure_method": "AEM_Histogram" if settings.exposure.mode == ExposureMode.HISTOGRAM else "AEM_Basic",
            "auto_exposure_min_brightness": settings.exposure.min_ev100,
            "auto_exposure_max_brightness": settings.exposure.max_ev100,
            "auto_exposure_speed_up": settings.exposure.adaptation_speed_up,
            "auto_exposure_speed_down": settings.exposure.adaptation_speed_down,
            # Bloom
            "bloom_intensity": settings.bloom.intensity if settings.bloom.enabled else 0.0,
            "bloom_threshold": settings.bloom.threshold,
            # Ambient Occlusion
            "ambient_occlusion_intensity": settings.ao.intensity if settings.ao.enabled else 0.0,
            "ambient_occlusion_radius": settings.ao.radius * 100.0,
            # Depth of Field
            "depth_of_field_focal_distance": settings.dof.focus_distance * 100.0,
            "depth_of_field_fstop": settings.dof.aperture_f_stop,
            # Motion Blur
            "motion_blur_amount": settings.motion_blur.amount if settings.motion_blur.enabled else 0.0,
            "motion_blur_max": settings.motion_blur.max_distortion_percent,
            # Color Grading
            "color_saturation": {
                "x": settings.color_grading.saturation,
                "y": settings.color_grading.saturation,
                "z": settings.color_grading.saturation,
                "w": 1.0,
            },
            "color_contrast": {
                "x": settings.color_grading.contrast,
                "y": settings.color_grading.contrast,
                "z": settings.color_grading.contrast,
                "w": 1.0,
            },
            "color_gamma": {
                "x": settings.color_grading.gamma,
                "y": settings.color_grading.gamma,
                "z": settings.color_grading.gamma,
                "w": 1.0,
            },
            # Lens
            "vignette_intensity": settings.lens.vignette_intensity,
            "scene_fringe_intensity": settings.lens.chromatic_aberration,
        }
