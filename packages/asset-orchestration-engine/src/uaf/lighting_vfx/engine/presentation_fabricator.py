"""
LightingVFXFabricationPlatform manufactures all 6 canonical golden presentation scenes from Sections 148 to 153.
UAF-81.25 Sections 148, 149, 150, 151, 152, 153.
"""

from typing import Tuple, List, Dict, Any
from ..models.lighting import LightSourceDefinition, LightType25, LightMobility, LightRole
from ..models.atmosphere import SkyAtmosphereProfile
from ..models.vfx import VFXEffectDefinition, VFXEffectType
from ..models.presentation import PresentationDefinition25


class LightingVFXFabricationPlatform:
    """
    Synthesizes complete lighting rigs, skies, atmospheric fog, and VFX particle systems.
    """

    @classmethod
    def build_empty_world_presentation(cls, pres_id: str = "Pres_EmptyWorld") -> Tuple[PresentationDefinition25, str]:
        """1. EMPTY WORLD (Section 148: minimal lighting, zero VFX)."""
        sky = SkyAtmosphereProfile(sky_type="CLEAR", sun_intensity_lux=80000.0, fog_density=0.0, volumetric_fog_enabled=False)
        sun = LightSourceDefinition("L_Sun_Directional", LightType25.DIRECTIONAL, LightMobility.STATIONARY, LightRole.KEY, intensity_lux=80000.0)
        p_def = PresentationDefinition25(pres_id, sky, [sun], [])
        return p_def, "PP_Default_Unlit"

    @classmethod
    def build_full_scifi_scene_presentation(cls, pres_id: str = "Pres_SciFiComplex") -> Tuple[PresentationDefinition25, str]:
        """2. FULL SCI-FI SCENE (Section 149: terrain, architecture, lights, volumetric fog, energy VFX, post-process)."""
        sky = SkyAtmosphereProfile(sky_type="SCI_FI", sun_intensity_lux=40000.0, fog_density=0.05, volumetric_fog_enabled=True)
        lights = [
            LightSourceDefinition("L_Sun", LightType25.DIRECTIONAL, LightMobility.STATIONARY, LightRole.KEY, 40000.0, 7500.0),
            LightSourceDefinition("L_Neon_Cyan", LightType25.RECT, LightMobility.MOVABLE, LightRole.PRACTICAL, 12000.0, 9000.0),
            LightSourceDefinition("L_Warning_Amber", LightType25.POINT, LightMobility.MOVABLE, LightRole.WARNING, 8000.0, 3000.0),
        ]
        vfx = [
            VFXEffectDefinition("VFX_HoloConsole_Energy", VFXEffectType.ENERGY, max_particles=1500, spawn_rate=120.0),
            VFXEffectDefinition("VFX_Vent_Steam", VFXEffectType.SMOKE, max_particles=800, spawn_rate=40.0),
        ]
        p_def = PresentationDefinition25(pres_id, sky, lights, vfx)
        return p_def, "PP_SciFi_Grade"

    @classmethod
    def build_night_scene_presentation(cls, pres_id: str = "Pres_NightCity") -> Tuple[PresentationDefinition25, str]:
        """3. NIGHT SCENE (Section 150: exposure, moon, accent lights, combat readability)."""
        sky = SkyAtmosphereProfile(sky_type="NIGHT", sun_intensity_lux=200.0, fog_density=0.03, volumetric_fog_enabled=True)
        lights = [
            LightSourceDefinition("L_Moon_Directional", LightType25.DIRECTIONAL, LightMobility.STATIONARY, LightRole.KEY, 500.0, 4500.0),
            LightSourceDefinition("L_Streetlight_01", LightType25.SPOT, LightMobility.STATIC, LightRole.PRACTICAL, 6500.0, 3200.0),
            LightSourceDefinition("L_Streetlight_02", LightType25.SPOT, LightMobility.STATIC, LightRole.PRACTICAL, 6500.0, 3200.0),
        ]
        vfx = [
            VFXEffectDefinition("VFX_Mote_Dust", VFXEffectType.AMBIENT_DUST, max_particles=500, spawn_rate=25.0),
        ]
        p_def = PresentationDefinition25(pres_id, sky, lights, vfx)
        return p_def, "PP_Night_HighDynamic"

    @classmethod
    def build_storm_scene_presentation(cls, pres_id: str = "Pres_ThunderStorm") -> Tuple[PresentationDefinition25, str]:
        """4. STORM (Section 151: rain, fog, wind, lightning, particle & light budget)."""
        sky = SkyAtmosphereProfile(sky_type="STORM", sun_intensity_lux=5000.0, fog_density=0.08, volumetric_fog_enabled=True)
        lights = [
            LightSourceDefinition("L_Sky_Ambience", LightType25.DIRECTIONAL, LightMobility.STATIONARY, LightRole.AMBIENT, 5000.0, 6000.0),
            LightSourceDefinition("L_Lightning_Flash", LightType25.POINT, LightMobility.MOVABLE, LightRole.ACCENT, 75000.0, 8500.0),
        ]
        vfx = [
            VFXEffectDefinition("VFX_Heavy_Rain", VFXEffectType.WEATHER_RAIN, max_particles=10000, spawn_rate=2000.0),
            VFXEffectDefinition("VFX_Ground_Splash", VFXEffectType.NIAGARA_PARTICLE, max_particles=4000, spawn_rate=800.0),
        ]
        p_def = PresentationDefinition25(pres_id, sky, lights, vfx)
        return p_def, "PP_Storm_Desaturated"

    @classmethod
    def build_combat_scene_presentation(cls, pres_id: str = "Pres_CombatArena") -> Tuple[PresentationDefinition25, str]:
        """5. COMBAT (Section 152: enemy readability, cover readability, sparks, explosions)."""
        sky = SkyAtmosphereProfile(sky_type="OVERCAST", sun_intensity_lux=35000.0, fog_density=0.01, volumetric_fog_enabled=True)
        lights = [
            LightSourceDefinition("L_Sun_Filtered", LightType25.DIRECTIONAL, LightMobility.STATIONARY, LightRole.KEY, 35000.0, 6000.0),
            LightSourceDefinition("L_Combat_Fill", LightType25.POINT, LightMobility.MOVABLE, LightRole.COMBAT, 10000.0, 5000.0),
        ]
        vfx = [
            VFXEffectDefinition("VFX_Sparks_Hit", VFXEffectType.NIAGARA_PARTICLE, max_particles=1200, spawn_rate=300.0),
            VFXEffectDefinition("VFX_Ground_Fire", VFXEffectType.FIRE, max_particles=2000, spawn_rate=250.0),
        ]
        p_def = PresentationDefinition25(pres_id, sky, lights, vfx)
        return p_def, "PP_Combat_Readability"

    @classmethod
    def build_cinematic_scene_presentation(cls, pres_id: str = "Pres_HeroCinematic") -> Tuple[PresentationDefinition25, str]:
        """6. CINEMATIC (Section 153: 3-point key/fill/rim presentation for hero showcase)."""
        sky = SkyAtmosphereProfile(sky_type="SUNSET", sun_intensity_lux=25000.0, fog_density=0.02, volumetric_fog_enabled=True)
        lights = [
            LightSourceDefinition("L_Hero_Key", LightType25.SPOT, LightMobility.MOVABLE, LightRole.KEY, 18000.0, 4800.0),
            LightSourceDefinition("L_Hero_Fill", LightType25.RECT, LightMobility.MOVABLE, LightRole.FILL, 6000.0, 6500.0),
            LightSourceDefinition("L_Hero_Rim", LightType25.SPOT, LightMobility.MOVABLE, LightRole.RIM, 22000.0, 7200.0),
        ]
        vfx = [
            VFXEffectDefinition("VFX_Atmospheric_Embers", VFXEffectType.NIAGARA_PARTICLE, max_particles=600, spawn_rate=40.0),
        ]
        p_def = PresentationDefinition25(pres_id, sky, lights, vfx)
        return p_def, "PP_Cinematic_ColorGraded"
