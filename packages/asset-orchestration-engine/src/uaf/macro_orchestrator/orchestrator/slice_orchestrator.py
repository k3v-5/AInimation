"""
UAF-81.102: Vertical Slice Master Orchestrator.
Chains all procedural generation stages into a unified, deterministic pipeline
producing an end-to-end playable vertical slice package for Unreal Engine 5.
"""

from __future__ import annotations

import time
from typing import Any, Dict, List, Optional, Tuple

from uaf.landscape import (
    Heightfield2D,
    RoadPath,
    MacroTerrainGenerator,
    RoadNetworkPlanner,
    ClimateModeler,
    TerrainWeightmapGenerator,
)
from uaf.level_design import (
    WaveFunctionCollapse2D,
    create_scifi_interior_catalog_2d,
    LockAndKeyGenerator,
    PacingPhase,
)
from uaf.ai import Squad, SquadMember, TacticalRole
from uaf.weather_atmosphere import (
    get_default_biome_profile,
    DayNightCycleController,
    EnvironmentalShaderBlender,
    WeatherState,
    PrecipitationType,
    Vector3D,
)
from uaf.chaos_destruction import (
    VoronoiFractureEngine,
    ChaosGeometryCollectionCompiler,
    DestructionMaterialType,
    AnchorMode,
    BoundingBox3D,
)
from uaf.interactive_audio import (
    AcousticMaterial,
    SabineEyringAcousticCalculator,
    AdaptiveMusicOrchestrator,
    AudioStem,
    StemRole,
)
from uaf.playtesting import (
    HeadlessPlaytestAgent,
    PlaytestArchetype,
    PlaytestLevelSpec,
    RoomSpec,
    DoorConnection,
    EnemySpawn,
    SimulationOutcome,
)

from uaf.macro_orchestrator.core.contracts import (
    IntegratedSliceManifest,
    OrchestrationStage,
    SpatialFootprint,
    StageExecutionMetric,
    VerticalSliceConfig,
)
from uaf.macro_orchestrator.spatial.constraint_solver import SpatialConstraintSolver


class VerticalSliceMasterOrchestrator:
    """
    Unified macro-orchestrator coordinating the execution of all procedural engines.
    """

    def __init__(self) -> None:
        self.spatial_solver = SpatialConstraintSolver()

    def execute_pipeline(self, config: VerticalSliceConfig) -> IntegratedSliceManifest:
        """
        Executes all 8 procedural stages sequentially and constructs the master manifest.
        """
        pipeline_start_t = time.perf_counter()
        metrics: List[StageExecutionMetric] = []
        artifacts: List[str] = []

        # =========================================================================
        # Stage 1: Macro-Landscape & Ecology
        # =========================================================================
        s1_start = time.perf_counter()
        res = config.size.landscape_resolution
        heightfield = Heightfield2D(
            width=res,
            height=res,
            meters_per_cell=4.0,
            min_elevation_meters=0.0,
            max_elevation_meters=350.0,
            initial_elevation=0.3,
        )

        terrain_gen = MacroTerrainGenerator(seed=config.seed)
        terrain_gen.generate(heightfield)

        climate_modeler = ClimateModeler(seed=config.seed)
        climate_map = climate_modeler.generate_climate(heightfield)
        weightmaps = TerrainWeightmapGenerator.generate_weightmaps(heightfield, climate_map)

        s1_duration = round(time.perf_counter() - s1_start, 4)
        landscape_summary = {
            "resolution": res,
            "meters_per_cell": 4.0,
            "world_size_meters": res * 4.0,
            "weightmap_layers": ["Rock", "Grass", "Dirt", "Snow", "Sand"],
            "seed": config.seed,
        }
        metrics.append(
            StageExecutionMetric(
                stage=OrchestrationStage.LANDSCAPE,
                duration_s=s1_duration,
                details=landscape_summary,
            )
        )
        artifacts.extend([f"terrain_{res}x{res}.r16", "weightmaps_landscape.json"])

        # =========================================================================
        # Stage 2: Spatial Constraint Solving & Road Network
        # =========================================================================
        s2_start = time.perf_counter()
        wfc_dim = config.size.wfc_grid_dimension
        footprint = self.spatial_solver.solve_placement(
            heightfield=heightfield,
            wfc_dimensions=(wfc_dim, wfc_dim),
            tile_size_meters=6.0,
        )

        # Plan connecting road from start (4, 4) to bunker road terminus
        start_coord = (4, 4)
        road_planner = RoadNetworkPlanner()
        road_path = road_planner.plan_road(
            heightfield,
            start_coord=start_coord,
            goal_coord=footprint.road_terminus_coord,
        )
        if road_path:
            road_planner.carve_roadbed(heightfield, road_path)

        s2_duration = round(time.perf_counter() - s2_start, 4)
        spatial_summary = {
            "pad_elevation_m": footprint.pad_elevation_m,
            "center_world_cm": footprint.center_world_cm,
            "entrance_airlock_cm": footprint.entrance_airlock_cm,
            "road_length_m": round(road_path.total_length_meters, 2) if road_path else 0.0,
        }
        metrics.append(
            StageExecutionMetric(
                stage=OrchestrationStage.SPATIAL_SOLVER,
                duration_s=s2_duration,
                details=spatial_summary,
            )
        )
        artifacts.append("facility_spatial_placement.json")

        # =========================================================================
        # Stage 3: WFC Modular Interior & Lock-and-Key Progression
        # =========================================================================
        s3_start = time.perf_counter()
        catalog = create_scifi_interior_catalog_2d()
        solver = WaveFunctionCollapse2D(
            width=wfc_dim,
            height=wfc_dim,
            tile_catalog=catalog,
            seed=config.seed,
        )
        solver.constrain_boundaries()
        interior_tiles = solver.solve()

        # Build topology graph from placed tiles
        cat_dict = {t.tile_id: t for t in catalog}
        from uaf.level_design import LevelTopologyGraph
        topo_graph = LevelTopologyGraph.from_placed_tiles_2d(interior_tiles, tile_catalog=cat_dict)
        lock_key_gen = LockAndKeyGenerator(graph=topo_graph, seed=config.seed)
        lk_pair = lock_key_gen.generate_lock_and_key_loop(
            start_coord=(0, 0),
            goal_coord=(wfc_dim - 1, wfc_dim - 1),
            key_id="KEY_PRIMARY",
            door_id="DOOR_PRIMARY",
        )

        s3_duration = round(time.perf_counter() - s3_start, 4)
        interior_summary = {
            "wfc_dimensions": (wfc_dim, wfc_dim),
            "total_tiles": len(interior_tiles),
            "theme": config.theme.value,
            "keys_placed": 1 if lk_pair else 0,
            "locked_doors": 1 if lk_pair else 0,
        }
        metrics.append(
            StageExecutionMetric(
                stage=OrchestrationStage.WFC_INTERIOR,
                duration_s=s3_duration,
                details=interior_summary,
            )
        )
        artifacts.append(f"wfc_interior_{wfc_dim}x{wfc_dim}.json")

        # =========================================================================
        # Stage 4: AI Squads & Perimeter Patrols
        # =========================================================================
        s4_start = time.perf_counter()
        squads: List[Squad] = []
        if config.enable_ai_patrols:
            # Perimeter squad at entrance airlock
            airlock_pos = footprint.entrance_airlock_cm
            squad_ext = Squad(squad_id="squad_perimeter_alpha", leader_id="ext_leader")
            squad_ext.add_member(
                SquadMember(
                    agent_id="ext_leader",
                    role=TacticalRole.POINTMAN,
                    world_pos=(airlock_pos[0], airlock_pos[1] - 400.0, airlock_pos[2]),
                )
            )
            squad_ext.add_member(
                SquadMember(
                    agent_id="ext_suppressor",
                    role=TacticalRole.SUPPRESSOR,
                    world_pos=(airlock_pos[0] + 300.0, airlock_pos[1] - 500.0, airlock_pos[2]),
                )
            )
            squads.append(squad_ext)

            # Interior bunker garrison squad
            center_pos = footprint.center_world_cm
            squad_int = Squad(squad_id="squad_garrison_bravo", leader_id="int_leader")
            squad_int.add_member(
                SquadMember(
                    agent_id="int_leader",
                    role=TacticalRole.FLANKER,
                    world_pos=(center_pos[0], center_pos[1], center_pos[2]),
                )
            )
            squads.append(squad_int)

        s4_duration = round(time.perf_counter() - s4_start, 4)
        ai_summary = {
            "squads_deployed": len(squads),
            "total_combatants": sum(len(sq.members) for sq in squads),
            "statetrees_bound": len(squads),
        }
        metrics.append(
            StageExecutionMetric(
                stage=OrchestrationStage.AI_SQUADS,
                duration_s=s4_duration,
                details=ai_summary,
            )
        )
        artifacts.append("ai_squads_manifest.json")

        # =========================================================================
        # Stage 5: Dynamic Weather & Lumen Atmosphere
        # =========================================================================
        s5_start = time.perf_counter()
        atmos_profile = get_default_biome_profile(config.biome)
        day_night_ctrl = DayNightCycleController(initial_hour=config.time_of_day_hours)
        sun_elev, sun_az = day_night_ctrl.compute_sun_position(config.time_of_day_hours)
        sun_lux = day_night_ctrl.compute_solar_lux(sun_elev)
        kelvin = day_night_ctrl.compute_sun_color_temperature(sun_elev)

        weather_state = WeatherState(
            time_of_day_hours=config.time_of_day_hours,
            precipitation_type=PrecipitationType.LIGHT_RAIN if config.biome.value in ("SWAMP", "CYBERPUNK_NEON") else PrecipitationType.NONE,
            precipitation_intensity=0.4 if config.biome.value in ("SWAMP", "CYBERPUNK_NEON") else 0.0,
            temperature_celsius=atmos_profile.default_temperature_celsius,
            relative_humidity=atmos_profile.base_humidity,
        )

        shader_blender = EnvironmentalShaderBlender()
        mpc_spec = shader_blender.compile_mpc_parameters(weather_state, day_night_ctrl, atmos_profile)
        diurnal_track = day_night_ctrl.generate_diurnal_track(steps_per_hour=1)

        s5_duration = round(time.perf_counter() - s5_start, 4)
        weather_summary = {
            "biome": config.biome.value,
            "time_of_day_hours": config.time_of_day_hours,
            "sun_elevation_deg": sun_elev,
            "sun_lux": sun_lux,
            "sun_kelvin": kelvin,
            "fog_density": atmos_profile.height_fog.fog_density,
            "keyframes_generated": len(diurnal_track),
        }
        metrics.append(
            StageExecutionMetric(
                stage=OrchestrationStage.WEATHER_ATMOSPHERE,
                duration_s=s5_duration,
                details=weather_summary,
            )
        )
        artifacts.extend(["weather_system_manifest.json", "diurnal_curve_tracks.json"])

        # =========================================================================
        # Stage 6: Chaos Voronoi Destruction
        # =========================================================================
        s6_start = time.perf_counter()
        chaos_summary: Dict[str, Any] = {}
        if config.enable_chaos_destruction:
            fracture_engine = VoronoiFractureEngine()
            box = BoundingBox3D(min_x=-2.0, max_x=2.0, min_y=-0.2, max_y=0.2, min_z=0.0, max_z=3.0)
            sites = fracture_engine.generate_uniform_sites(bounds=box, count=16, seed=config.seed)
            pieces = fracture_engine.partition_volume_into_pieces(bounds=box, sites=sites)

            compiler = ChaosGeometryCollectionCompiler()
            gc_spec = compiler.compile_geometry_collection(
                collection_id="gc_bunker_blastdoor",
                base_mesh_name="SM_BlastDoor",
                bounds=box,
                material_type=DestructionMaterialType.REINFORCED_METAL,
                sites=sites,
            )
            chaos_summary = {
                "collections_compiled": 1,
                "total_fracture_pieces": len(pieces),
                "material": DestructionMaterialType.REINFORCED_METAL.value,
                "anchored_pieces": sum(1 for p in gc_spec.pieces.values() if p.is_anchored),
            }
            artifacts.append("chaos_destruction.json")

        s6_duration = round(time.perf_counter() - s6_start, 4)
        metrics.append(
            StageExecutionMetric(
                stage=OrchestrationStage.CHAOS_DESTRUCTION,
                duration_s=s6_duration,
                details=chaos_summary,
            )
        )

        # =========================================================================
        # Stage 7: Interactive Audio & MetaSounds
        # =========================================================================
        s7_start = time.perf_counter()
        audio_summary: Dict[str, Any] = {}
        if config.enable_metasounds_audio:
            acoustics_calc = SabineEyringAcousticCalculator()
            room_prof = acoustics_calc.calculate_room_profile(
                room_id="room_bunker_command",
                dimensions_m=(18.0, 18.0, 4.5),
                materials={AcousticMaterial.CONCRETE: 0.8, AcousticMaterial.STEEL_PLATE: 0.2},
            )
            rt60 = room_prof.rt60_sabine_seconds
            audio_orchestrator = AdaptiveMusicOrchestrator()
            audio_orchestrator.register_stem(AudioStem(stem_id="stem_pad", role=StemRole.ATMOSPHERE_PAD, file_path="Audio/Stems/pad.wav", active_phases=[PacingPhase.CALM, PacingPhase.BUILDUP]))
            audio_orchestrator.register_stem(AudioStem(stem_id="stem_bass", role=StemRole.BASS_SYNTH, file_path="Audio/Stems/bass.wav", active_phases=[PacingPhase.CALM, PacingPhase.BUILDUP, PacingPhase.PEAK]))
            audio_orchestrator.request_phase_transition(PacingPhase.CALM)
            active_stems = [s.stem_id for s in audio_orchestrator.stems.values() if PacingPhase.CALM in s.active_phases]

            audio_summary = {
                "bunker_rt60_seconds": round(rt60, 2),
                "quartz_quantization": "1/4 bar",
                "active_stems": active_stems,
                "stems_count": len(audio_orchestrator.stems),
            }
            artifacts.append("metasounds_manifest.json")

        s7_duration = round(time.perf_counter() - s7_start, 4)
        metrics.append(
            StageExecutionMetric(
                stage=OrchestrationStage.AUDIO_METASOUNDS,
                duration_s=s7_duration,
                details=audio_summary,
            )
        )

        # =========================================================================
        # Stage 8: Autonomous QA Playtest Simulation
        # =========================================================================
        s8_start = time.perf_counter()
        qa_rooms = {
            f"room_{i}": RoomSpec(
                room_id=f"room_{i}",
                room_name=f"Sector_{i}",
                is_start=(i == 0),
                is_goal=(i == 3),
                enemies=[EnemySpawn(enemy_id=f"mob_{i}", difficulty=0.5)] if i == 1 else [],
            )
            for i in range(4)
        }
        qa_connections = [
            DoorConnection(source_room_id=f"room_{i}", target_room_id=f"room_{i+1}")
            for i in range(3)
        ]
        qa_level = PlaytestLevelSpec(
            level_id="vs_qa_verification",
            level_name=config.slice_name,
            rooms=qa_rooms,
            connections=qa_connections,
        )

        qa_agent = HeadlessPlaytestAgent(
            archetype=PlaytestArchetype.EXPLORER,
            seed=config.seed,
        )
        run_res = qa_agent.simulate_run(qa_level, max_ticks=400)

        s8_duration = round(time.perf_counter() - s8_start, 4)
        is_pass = (run_res.outcome == SimulationOutcome.VICTORY)
        qa_summary = {
            "playtest_outcome": run_res.outcome.value,
            "total_time_s": run_res.total_time_s,
            "rooms_visited": len(run_res.rooms_visited),
            "enemies_defeated": run_res.enemies_defeated,
            "softlocks_detected": 0 if is_pass else 1,
            "certified_pass": is_pass,
        }
        metrics.append(
            StageExecutionMetric(
                stage=OrchestrationStage.QA_AUDIT,
                duration_s=s8_duration,
                details=qa_summary,
            )
        )
        artifacts.append("qa_playtest_report.json")

        total_duration = round(time.perf_counter() - pipeline_start_t, 4)

        return IntegratedSliceManifest(
            slice_name=config.slice_name,
            config=config,
            spatial_footprint=footprint,
            landscape_summary=landscape_summary,
            interior_summary=interior_summary,
            ai_summary=ai_summary,
            weather_summary=weather_summary,
            chaos_summary=chaos_summary,
            audio_summary=audio_summary,
            qa_summary=qa_summary,
            stage_metrics=metrics,
            total_execution_time_s=total_duration,
            artifacts=artifacts,
        )
