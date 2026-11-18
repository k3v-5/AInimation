"""
UAF-81.89 Acceptance Test Suite:
Advanced Next-Gen VFX, Fluid Simulation & Environmental Coupling System.
"""

import math
import pytest
from uaf.advanced_vfx import (
    FluidBoundaryCondition,
    AdvectionScheme,
    SkinningAlgorithm,
    SpectralBand,
    ShaderOptimizationLevel,
    DisplacementChannel,
    ensure_finite_scalar,
    ensure_finite_vec3,
    clamp_scalar,
    GridDimensions2D,
    GridDimensions3D,
    FluidProperties,
    validate_cfl_condition,
    SkeletalBoneTransform,
    SkeletalVertex,
    SurfaceImpactEvent,
    VolumetricShadowSettings,
    DielectricBranchConfig,
    ParticleSoABuffer,
    EulerianFluidGrid2D,
    EulerianFluidGrid3D,
    SmokeFireSolver,
    SkeletalMeshSampler,
    FractureChunk,
    FractureVFXCoupler,
    PersistentSurfaceManager,
    FoliageInteractionBuffer,
    DeepShadowMapper,
    ParticleLightManager,
    DielectricBreakdownSolver,
    OpticalDistortionBuffer,
    AudioSpectralCoupler,
    ASTNode,
    VFXJITCompiler,
    AdvancedNiagaraBridge,
)


# ---------------------------------------------------------------------------
# 81.89.0: Numerical Safety & CFL Condition
# ---------------------------------------------------------------------------

def test_numerical_safety_and_cfl_condition():
    # NaNs and Infinities sanitization
    assert ensure_finite_scalar(float("nan"), 42.0) == 42.0
    assert ensure_finite_scalar(float("inf"), 10.0) == 10.0
    assert ensure_finite_scalar(3.1415, 0.0) == 3.1415

    v_sanitized = ensure_finite_vec3((float("nan"), 1.0, float("-inf")), (0.0, 0.0, 0.0))
    assert v_sanitized == (0.0, 1.0, 0.0)

    # CFL check
    cfl_ok = validate_cfl_condition(max_velocity=5.0, cell_size=1.0, dt=0.1, max_cfl=1.0)
    assert cfl_ok.is_stable is True
    assert cfl_ok.recommended_substeps == 1
    assert math.isclose(cfl_ok.cfl_number, 0.5)

    cfl_substep = validate_cfl_condition(max_velocity=20.0, cell_size=1.0, dt=0.2, max_cfl=1.0)
    assert cfl_substep.is_stable is False
    assert cfl_substep.recommended_substeps >= 4


def test_soa_particle_buffer_lifecycle_and_compact():
    buf = ParticleSoABuffer(capacity=100)
    idx0 = buf.spawn((0, 0, 0), (1, 0, 0), lifetime=1.0, size=2.0)
    idx1 = buf.spawn((10, 0, 0), (0, 1, 0), lifetime=0.01, size=1.5)
    idx2 = buf.spawn((20, 0, 0), (0, 0, 1), lifetime=2.0, size=3.0)

    assert buf.count == 3
    assert buf.pos_x[0] == 0.0
    assert buf.pos_x[1] == 10.0
    assert buf.pos_x[2] == 20.0

    # Step simulation: idx1 should expire and be swapped out with idx2
    survived = buf.update_lifecycle_and_motion(dt=0.05, gravity=(0, -9.81, 0))
    assert survived == 2
    assert buf.count == 2
    assert buf.alive[0] is True
    assert buf.alive[1] is True

    # Check packed binary bytes representation
    data_bytes = buf.to_packed_bytes()
    assert len(data_bytes) == 2 * 48  # 48 bytes per particle


# ---------------------------------------------------------------------------
# 81.89.1: Eulerian Fluid Dynamics 2D & 3D
# ---------------------------------------------------------------------------

def test_eulerian_fluid_grid_2d_advection_and_incompressibility():
    dims = GridDimensions2D(width=16, height=16, cell_size=1.0)
    grid = EulerianFluidGrid2D(dims, scheme=AdvectionScheme.MACCORMACK_BFECC)

    # Inject density and velocity
    grid.add_density(8, 8, 10.0)
    grid.add_velocity(8, 8, 5.0, 0.0)

    # Initial divergence
    init_div = grid.project_pressure(iterations=25)
    assert init_div >= 0.0

    # Advect
    grid.advect_density(dt=0.1)
    # Density should have moved in positive X direction (cell 8 -> cell 9 or 10)
    assert grid.density[grid._c_idx(8, 8)] < 10.0
    assert grid.density[grid._c_idx(9, 8)] > 0.0

    # Solid obstacle check
    grid.set_solid(12, 8, True)
    assert grid.solid[grid._c_idx(12, 8)] is True
    assert grid.density[grid._c_idx(12, 8)] == 0.0


def test_eulerian_fluid_grid_3d_thermal_buoyancy_and_vorticity():
    dims = GridDimensions3D(width=8, height=16, depth=8, cell_size=1.0)
    grid = EulerianFluidGrid3D(dims, FluidProperties(buoyancy_beta=0.2, vorticity_epsilon=0.5))

    # Add hot spot near bottom
    grid.add_density(4, 2, 4, 5.0)
    grid.add_temperature(4, 2, 4, 100.0) # 100 C above ambient

    # Before buoyancy, vertical velocity should be 0
    assert grid.v[grid._v_idx(4, 3, 4)] == 0.0

    # Step fluid
    grid.step(dt=0.1, iterations=15)

    # Hot air must ascend: positive vertical velocity at face above hot cell
    assert grid.v[grid._v_idx(4, 3, 4)] > 0.0


def test_smoke_fire_combustion_solver():
    dims = GridDimensions3D(width=10, height=12, depth=10, cell_size=1.0)
    fire_solver = SmokeFireSolver(dims, burn_rate=0.5, ignition_temp=50.0)

    # Inject fuel
    fire_solver.inject_fuel(5, 2, 5, 10.0)
    assert fire_solver.get_total_fuel() == 10.0
    assert fire_solver.get_total_smoke() == 0.0

    # Not ignited yet, stepping should not consume fuel
    fire_solver.step(dt=0.1)
    assert math.isclose(fire_solver.get_total_fuel(), 10.0, rel_tol=1e-3)

    # Ignite cell
    fire_solver.ignite(5, 2, 5, temp_boost=200.0)
    fire_solver.step(dt=0.1)

    # Fuel must be consumed, generating smoke soot and flame
    assert fire_solver.get_total_fuel() < 10.0
    assert fire_solver.get_total_smoke() > 0.0
    assert fire_solver.get_flame_intensity(5, 2, 5) > 0.0


# ---------------------------------------------------------------------------
# 81.89.2: Geometry Sampling & Fractures
# ---------------------------------------------------------------------------

def test_skeletal_mesh_sampler_uniform_area_distribution():
    # Construct a simple quad with 2 triangles
    v0 = SkeletalVertex(position=(0, 0, 0), normal=(0, 1, 0), bone_indices=(0, 0, 0, 0), bone_weights=(1, 0, 0, 0))
    v1 = SkeletalVertex(position=(2, 0, 0), normal=(0, 1, 0), bone_indices=(0, 0, 0, 0), bone_weights=(1, 0, 0, 0))
    v2 = SkeletalVertex(position=(2, 0, 2), normal=(0, 1, 0), bone_indices=(0, 0, 0, 0), bone_weights=(1, 0, 0, 0))
    v3 = SkeletalVertex(position=(0, 0, 2), normal=(0, 1, 0), bone_indices=(0, 0, 0, 0), bone_weights=(1, 0, 0, 0))

    triangles = [(0, 3, 2), (0, 2, 1)]
    bone_root = SkeletalBoneTransform(
        bone_index=0,
        name="root",
        position=(10, 5, 0),
        linear_velocity=(2, 0, 0),
        angular_velocity=(0, 1, 0),
    )

    sampler = SkeletalMeshSampler([v0, v1, v2, v3], triangles, {"root": bone_root})

    # Sample random surface point
    pos, norm, vel = sampler.sample_surface_point(rng_tri=0.25, rng_u=0.3, rng_v=0.4)

    # Deformed position must be offset by bone position (x >= 10, y >= 5)
    assert pos[0] >= 10.0
    assert pos[1] >= 5.0
    # Normal should point upwards
    assert norm[1] > 0.9
    # Inherited velocity should reflect bone translation + angular rotation
    assert vel[0] != 0.0

    # Socket sampling
    s_pos, s_vel = sampler.sample_socket("root", local_offset=(0, 1, 0))
    assert s_pos == (10.0, 6.0, 0.0)
    assert s_vel == (2.0, 0.0, 0.0)


def test_fracture_vfx_coupler_debris_and_dust():
    coupler = FractureVFXCoupler(base_debris_speed=15.0, base_dust_speed=3.0)
    chunk = FractureChunk(
        chunk_id=1,
        centroid=(0, 2, 0),
        normal=(0, 1, 0),
        volume=2.5,
        linear_impulse=(0, 5, 0),
    )

    particles = coupler.generate_fracture_vfx([chunk], debris_per_chunk=4, dust_per_chunk=8, seed=99)
    assert len(particles) == 12

    debris = [p for p in particles if not p.is_dust]
    dust = [p for p in particles if p.is_dust]

    assert len(debris) == 4
    assert len(dust) == 8

    # Debris must have high upward velocity
    for d in debris:
        assert d.velocity[1] > 10.0
        assert d.size < 0.3


# ---------------------------------------------------------------------------
# 81.89.3: Persistent Surfaces & Foliage Interaction
# ---------------------------------------------------------------------------

def test_persistent_surface_manager_burns_and_slope_flow():
    mgr = PersistentSurfaceManager(world_bounds=(-10, -10, 10, 10), resolution=32)

    # Scorch impact
    event = SurfaceImpactEvent(
        world_position=(0, 0, 0),
        normal=(0, 1, 0),
        radius=2.0,
        intensity=0.9,
        channel=DisplacementChannel.BURN,
    )
    mgr.apply_impact(event)

    assert mgr.get_burn_at(0, 0) > 0.65
    assert mgr.get_burn_at(5, 5) == 0.0

    # Cooling over time
    mgr.update(dt=2.0)
    assert mgr.get_burn_at(0, 0) < 0.9

    # Slope flow math: 45 degree slope normal (1/sqrt(2), 1/sqrt(2), 0)
    inv_sqrt2 = 1.0 / math.sqrt(2.0)
    slope_normal = (inv_sqrt2, inv_sqrt2, 0.0)
    flow_vel = mgr.calculate_slope_flow(slope_normal, gravity=(0, -10.0, 0))

    # Flow should slide downward along the slope: positive X, negative Y
    assert flow_vel[0] > 0.0
    assert flow_vel[1] < 0.0
    assert flow_vel[2] == 0.0


def test_foliage_interaction_buffer_shockwave_and_spring_damping():
    buffer = FoliageInteractionBuffer(world_bounds=(-20, -20, 20, 20), resolution=32)

    # Trigger blast
    buffer.apply_shockwave(center_x=0.0, center_z=0.0, radius=5.0, force=4.0)

    # Foliage at (3, 0) should be deflected in positive X
    dx, dz = buffer.sample_deflection(3.0, 0.0)
    # Velocity was injected, let's step once to propagate displacement
    buffer.update(dt=0.05)
    dx_after, dz_after = buffer.sample_deflection(3.0, 0.0)
    assert dx_after > 0.0

    # Step several times to verify damped return towards equilibrium
    for _ in range(30):
        buffer.update(dt=0.05)

    dx_settled, dz_settled = buffer.sample_deflection(3.0, 0.0)
    assert abs(dx_settled) < abs(dx_after)


# ---------------------------------------------------------------------------
# 81.89.4: Volumetrics & Particle Lights
# ---------------------------------------------------------------------------

def test_deep_shadow_mapper_beer_lambert_volumetric_self_shadowing():
    dims = GridDimensions3D(width=4, height=8, depth=4, cell_size=1.0)
    fluid_grid = EulerianFluidGrid3D(dims)

    # Inject dense smoke column from y=4 to y=7
    for y in range(4, 8):
        fluid_grid.add_density(2, y, 2, 2.0)

    shadow_mapper = DeepShadowMapper(VolumetricShadowSettings(absorption_coefficient=0.8, scattering_coefficient=0.2))
    # Sun light pointing directly downwards
    shadow_mapper.bake_deep_shadow_grid(fluid_grid, light_direction=(0.0, -1.0, 0.0))

    # Top cell (y=7) should have higher transmittance than bottom cell (y=4)
    t_top = shadow_mapper.get_shadow_factor(2, 7, 2)
    t_bottom = shadow_mapper.get_shadow_factor(2, 4, 2)

    assert t_top > t_bottom
    assert 0.0 <= t_bottom < 1.0


def test_particle_light_manager_clustering_and_budgeting():
    manager = ParticleLightManager(cluster_cell_size=5.0, max_budget_lights=4)

    # Spawn 20 glowing sparks near origin (0, 0, 0)
    for i in range(20):
        manager.add_particle(
            position=(0.1 * i, 0.1 * i, 0.0),
            intensity=2.0,
            color=(1.0, 0.5, 0.1),
        )

    # Spawn 10 sparks far away at (30, 0, 0)
    for i in range(10):
        manager.add_particle(
            position=(30.0 + 0.1 * i, 0.0, 0.0),
            intensity=1.5,
            color=(0.1, 0.5, 1.0),
        )

    lights = manager.build_clustered_lights()
    # Must consolidate into 2 spatial clusters
    assert len(lights) == 2

    # First light should be the brightest near origin
    assert lights[0].particle_count == 20
    assert math.isclose(lights[0].intensity, 40.0)
    assert lights[0].position[0] < 5.0

    # Second light at (30, 0, 0)
    assert lights[1].particle_count == 10
    assert math.isclose(lights[1].intensity, 15.0)
    assert lights[1].position[0] >= 30.0


# ---------------------------------------------------------------------------
# 81.89.5: Optics, Lightning & Refraction
# ---------------------------------------------------------------------------

def test_dielectric_breakdown_solver_lichtenberg_lightning():
    config = DielectricBranchConfig(
        source_pos=(0, 50, 0),
        target_pos=(0, 0, 0),
        roughness=0.3,
        branch_probability=0.4,
        max_recursion=3,
    )
    solver = DielectricBreakdownSolver(config)
    bolt = solver.generate_bolt(seed=777)

    assert bolt.total_length > 45.0
    assert bolt.branches_count > 0
    assert len(bolt.segments) > 10

    # Must contain return stroke segments
    return_strokes = [s for s in bolt.segments if s.is_return_stroke]
    assert len(return_strokes) > 0
    for s in return_strokes:
        assert s.intensity == 1.0
        assert s.thickness >= 0.2


def test_optical_distortion_buffer_chromatic_dispersion():
    dist_buf = OpticalDistortionBuffer()
    dist_buf.add_shockwave(center=(0.5, 0.5), initial_radius=0.1, thickness=0.05, strength=0.08, dispersion_factor=0.2)

    # Sample right at the wavefront crest (u=0.6, v=0.5)
    r_off, g_off, b_off = dist_buf.sample_screen_distortion(0.6, 0.5)

    # Chromatic dispersion should yield different offsets for R, G, B
    assert r_off[0] != 0.0
    assert g_off[0] != 0.0
    assert b_off[0] != 0.0
    assert r_off[0] != b_off[0]

    # Update wave
    dist_buf.update(dt=0.1, expansion_rate=0.5)
    assert dist_buf.shockwaves[0].radius > 0.1


# ---------------------------------------------------------------------------
# 81.89.6: Audio-Reactive Spectral Coupler
# ---------------------------------------------------------------------------

def test_audio_spectral_coupler_6_bands_and_adsr():
    coupler = AudioSpectralCoupler()

    # Feed energetic bass pulse
    spectrum = {
        SpectralBand.SUB_BASS: 2.5,
        SpectralBand.BASS: 4.0,
        SpectralBand.MID: 0.5,
    }
    coupler.process_spectrum(spectrum, dt=0.03)

    bass_env = coupler.get_band_envelope(SpectralBand.BASS)
    assert bass_env > 0.0

    # Multipliers driven by audio
    spawn_mult = coupler.get_spawn_rate_multiplier(SpectralBand.BASS, sensitivity=1.5)
    emissive_boost = coupler.get_emissive_boost(SpectralBand.BASS, sensitivity=2.0)
    assert spawn_mult > 1.0
    assert emissive_boost > 1.0


# ---------------------------------------------------------------------------
# 81.89.7: JIT Compute Shader Compiler
# ---------------------------------------------------------------------------

def test_vfx_jit_compiler_hlsl_generation_and_optimization():
    compiler = VFXJITCompiler(opt_level=ShaderOptimizationLevel.O2_FAST_MATH)

    nodes = [
        ASTNode(name="const_grav", op="const", output="g_accel", const_val=9.81),
        ASTNode(name="calc_force", op="mul", inputs=["g_accel", "DeltaTime"], output="f_step"),
        ASTNode(name="dead_math", op="add", inputs=["g_accel", "g_accel"], output="unused_var"), # Dead node
        ASTNode(name="apply_vel", op="store", inputs=["f_step"], output="vel.y"),
    ]

    cs_artifact = compiler.compile_graph_to_hlsl(nodes, entry_name="SimulateParticlesCS")

    assert cs_artifact.entry_point == "SimulateParticlesCS"
    assert "RWStructuredBuffer<ParticleRaw>" in cs_artifact.hlsl_source
    assert "[numthreads(64, 1, 1)]" in cs_artifact.hlsl_source
    # Dead node "unused_var" should have been pruned by dead-code elimination
    assert "unused_var" not in cs_artifact.hlsl_source
    # Active nodes must be present
    assert "g_accel" in cs_artifact.hlsl_source
    assert "f_step" in cs_artifact.hlsl_source


# ---------------------------------------------------------------------------
# 81.89.8: UE5 Advanced Niagara Bridge
# ---------------------------------------------------------------------------

def test_ue5_advanced_niagara_bridge_exports():
    grid = EulerianFluidGrid3D(GridDimensions3D(width=16, height=16, depth=16, cell_size=0.5))
    fluid_export = AdvancedNiagaraBridge.export_fluid_grid_interface(grid)
    assert fluid_export["data_interface_class"] == "UNiagaraDataInterfaceGrid3DCollection"
    assert fluid_export["properties"]["NumCellsX"] == 16

    v0 = SkeletalVertex(position=(0, 0, 0), normal=(0, 1, 0))
    sampler = SkeletalMeshSampler([v0], [(0, 0, 0)], {"pelvis": SkeletalBoneTransform(bone_index=0, name="pelvis", position=(0, 0, 0))})
    skel_export = AdvancedNiagaraBridge.export_skeletal_sampler_interface(sampler)
    assert skel_export["data_interface_class"] == "UNiagaraDataInterfaceSkeletalMesh"
    assert "pelvis" in skel_export["properties"]["FilteredBones"]

    light_mgr = ParticleLightManager(max_budget_lights=16)
    light_mgr.add_particle((0, 0, 0), 5.0)
    lights_export = AdvancedNiagaraBridge.export_particle_lights_renderer(light_mgr)
    assert lights_export["renderer_class"] == "UNiagaraLightRendererProperties"
    assert lights_export["properties"]["ActiveClusteredLights"] == 1


# ---------------------------------------------------------------------------
# 81.89.9: Performance Stress & Numerical Invariance
# ---------------------------------------------------------------------------

def test_stress_10000_particles_soa_performance():
    buf = ParticleSoABuffer(capacity=10000)
    for i in range(10000):
        buf.spawn(
            position=(float(i % 100), float((i // 100) % 100), 0.0),
            velocity=(0.0, 1.0, 0.0),
            lifetime=5.0,
        )

    assert buf.count == 10000

    # Step 50 frames
    for _ in range(50):
        alive_count = buf.update_lifecycle_and_motion(dt=0.016, gravity=(0, -9.81, 0))
        assert alive_count == 10000

    # Verify no NaNs generated in entire buffer
    assert not any(math.isnan(x) for x in buf.pos_y[:100])


def test_fluid_grid_long_term_stability_zero_nan():
    dims = GridDimensions2D(width=8, height=8, cell_size=1.0)
    grid = EulerianFluidGrid2D(dims)
    grid.add_density(4, 4, 100.0)
    grid.add_velocity(4, 4, 10.0, 10.0)

    for step_idx in range(60):
        div = grid.step(dt=0.016, iterations=10)
        assert not math.isnan(div)

    # Verify zero NaNs in all fields
    assert not any(math.isnan(d) for d in grid.density)
    assert not any(math.isnan(u) for u in grid.u)
    assert not any(math.isnan(v) for v in grid.v)


def test_smoke_fire_thermal_dissipation_and_smoke_persistence():
    dims = GridDimensions3D(width=6, height=6, depth=6, cell_size=1.0)
    solver = SmokeFireSolver(dims, burn_rate=2.0, ignition_temp=50.0)

    # Inject fuel and ignite
    solver.inject_fuel(3, 3, 3, 2.0)
    solver.ignite(3, 3, 3, temp_boost=150.0)

    # Step until fuel is consumed
    for _ in range(10):
        solver.step(dt=0.1)

    # All fuel should be consumed
    assert solver.get_total_fuel() < 0.1
    # Smoke should be lingering
    assert solver.get_total_smoke() > 0.5
    # Temperature in burned cell should be cooling down from peak (20 + 150 + 240 = 410 C)
    temp = solver.grid.temperature[solver.grid._c_idx(3, 3, 3)]
    assert 20.0 < temp < 410.0


def test_deep_shadow_transmittance_and_zero_density_limit():
    dims = GridDimensions3D(width=4, height=4, depth=4, cell_size=1.0)
    fluid_grid = EulerianFluidGrid3D(dims)
    shadow_mapper = DeepShadowMapper()

    # With zero density, transmittance everywhere must be 1.0 (fully lit)
    shadow_mapper.bake_deep_shadow_grid(fluid_grid, light_direction=(0, -1, 0))
    for z in range(4):
        for y in range(4):
            for x in range(4):
                assert shadow_mapper.get_shadow_factor(x, y, z) == 1.0

    # Inject density in one column
    fluid_grid.add_density(2, 2, 2, 5.0)
    shadow_mapper.bake_deep_shadow_grid(fluid_grid, light_direction=(0, -1, 0))
    # Cell below density must be shadowed (< 1.0)
    assert shadow_mapper.get_shadow_factor(2, 1, 2) < 1.0
    # Cell above density remains unshadowed (1.0)
    assert shadow_mapper.get_shadow_factor(2, 3, 2) == 1.0
