"""
Tests for Lighting, Atmosphere, VFX and Presentation Models.
UAF-81.25 Sections 3, 4, 5, 6, 7, 27, 28, 29.
"""

from uaf.lighting_vfx.models.lighting import (
    LightType25,
    LightMobility,
    LightRole,
    LightSourceDefinition,
)
from uaf.lighting_vfx.models.atmosphere import (
    SkyAtmosphereProfile,
)
from uaf.lighting_vfx.models.vfx import (
    VFXEffectType,
    VFXEffectDefinition,
)
from uaf.lighting_vfx.models.presentation import (
    PresentationDefinition25,
)


def test_lighting_source_definition():
    light = LightSourceDefinition(
        "L_Spot_Main",
        LightType25.SPOT,
        LightMobility.MOVABLE,
        LightRole.KEY,
        intensity_lux=15000.0,
        color_temperature_k=5500.0,
        shadow_enabled=True,
    )
    assert light.light_type == "SPOT"
    assert light.intensity_lux == 15000.0
    data = light.to_dict()
    assert data["role"] == "KEY"


def test_presentation_definition_and_hashing():
    sky = SkyAtmosphereProfile("SUNSET", sun_intensity_lux=50000.0, fog_density=0.03)
    sun = LightSourceDefinition("L_Sun", LightType25.DIRECTIONAL, LightMobility.STATIONARY, LightRole.KEY, 50000.0)
    vfx = VFXEffectDefinition("VFX_Embers", VFXEffectType.NIAGARA_PARTICLE, max_particles=200, spawn_rate=15.0)

    pres = PresentationDefinition25("Pres_Dusk", sky, [sun], [vfx], seed=987654)
    assert len(pres.definition_hash) == 64
    data = pres.to_dict()
    assert data["sky_atmosphere"]["sky_type"] == "SUNSET"
    assert len(data["lights"]) == 1
    assert len(data["vfx_effects"]) == 1
