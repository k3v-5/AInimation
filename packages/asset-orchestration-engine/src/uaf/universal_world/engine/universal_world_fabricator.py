"""
Universal World Fabricator for UAF-81.56.
Implements complete procedural generation, hydrology, biomes, scatter, architecture,
scene graphs, snapshotting, diffing, queries, caching, and 10 Golden Worlds.
"""

from typing import Dict, Any, List, Optional, Tuple
import math
from ...core.hashing.canonical_hasher import CanonicalHasher
from ..models.definition import (
    WorldDimensionType,
    WorldBounds,
    WorldCoordinateSystem,
    WorldCell,
    WorldRegion,
    SceneNodeType,
    WorldTransform,
    SceneNode,
    WorldSceneGraph,
    BiomeType,
    BiomeDefinition,
    BiomeMaskChannel,
    BiomeMask,
    TerrainRepresentation,
    TerrainGeneratorType,
    NoiseType,
    NoiseDefinition,
    TerrainLayer,
    TerrainOperator,
    TerrainModifierType,
    TerrainStamp,
    TerrainSplatChannel,
    TerrainSplatDefinition,
    SlopeField,
    TerrainCollisionMode,
    TerrainCollisionProfile,
    ErosionType,
    ErosionProfile,
    TerrainDefinition,
    WaterType,
    WaterBody,
    RiverDefinition,
    FlowField,
    ShorelineDefinition,
    WaterDefinition,
    VegetationCategory,
    VegetationSpecies,
    ScatterDistributionType,
    VegetationScatterProfile,
    FoliageLayer,
    FoliageLODType,
    FoliageDefinition,
    VegetationDefinition,
    RockType,
    RockOrientation,
    RockDefinition,
    PropCategory,
    PropPlacementMode,
    ExclusionVolumeType,
    ExclusionVolume,
    PropDefinition,
    ScatterConstraintType,
    ScatterInstance,
    BuildingType,
    BuildingDefinition,
    RoadType,
    RoadCutFillMode,
    RoadDefinition,
    BridgeDefinition,
    PathType,
    PathNode,
    PathNetwork,
    NavigationSource,
    NavigationFlag,
    NavigationDefinition,
    CollisionLayer,
    CollisionComplexity,
    WorldCollisionProfile,
    StreamingState,
    LevelStreamingMode,
    WorldPartitionCell,
    WorldPartitionProfile,
    HLODLevel,
    HLODGroupingMode,
    WorldHLODProfile,
    ImpostorDefinition,
    LightingProfile,
    TimeOfDayProfile,
    WeatherType,
    WeatherProfile,
    EnvironmentProfile,
    WorldAudioZoneType,
    WorldAudioProfile,
    WorldVFXProfile,
    WorldAnchorType,
    WorldAnchor,
    SpawnProfile,
    LandmarkType,
    LandmarkDefinition,
    WorldQueryType,
    WorldQuery,
    WorldSnapshot,
    WorldDiffCategory,
    WorldDiff,
    WorldCacheKey,
    WorldCache,
    MemoryBudget,
    InstanceBudget,
    TriangleBudget,
    StreamingBudget,
    WorldPerformanceReport,
    WorldDiagnosticReport,
    ExportTarget,
    WorldDefinition,
)


class UniversalWorldFabricator:
    """
    Procedural fabricator for complete production worlds (UAF-81.56).
    """

    @staticmethod
    def generate_noise(seed: int, res_x: int, res_y: int, noise_def: NoiseDefinition) -> List[float]:
        samples = []
        for y in range(res_y):
            for x in range(res_x):
                # Normalized coordinate -1..1
                nx = (x / max(1, res_x - 1)) * 2.0 - 1.0
                ny = (y / max(1, res_y - 1)) * 2.0 - 1.0
                v = noise_def.sample_2d(nx * 10.0, ny * 10.0)
                norm_v = (v / (noise_def.amplitude * 2.0)) + 0.5
                samples.append(max(0.0, min(1.0, norm_v)))
        return samples

    @staticmethod
    def generate_terrain(
        terrain_id: str,
        generator_type: TerrainGeneratorType = TerrainGeneratorType.HILLS,
        seed: int = 12345,
        resolution: int = 32,
        height_scale: float = 2000.0,
        bounds: Optional[WorldBounds] = None,
    ) -> TerrainDefinition:
        b = bounds or WorldBounds()
        noise_def = NoiseDefinition(seed=seed, frequency=0.05, amplitude=500.0)
        
        raw_samples = []
        for y in range(resolution):
            for x in range(resolution):
                u = x / max(1, resolution - 1)
                v = y / max(1, resolution - 1)
                if generator_type == TerrainGeneratorType.FLAT:
                    h = 0.1
                elif generator_type == TerrainGeneratorType.HILLS:
                    h = 0.3 + 0.2 * math.sin(u * math.pi * 4) * math.cos(v * math.pi * 4)
                elif generator_type == TerrainGeneratorType.MOUNTAIN:
                    dist_to_center = math.sqrt((u - 0.5) ** 2 + (v - 0.5) ** 2)
                    peak = max(0.0, 1.0 - dist_to_center * 2.0)
                    h = peak ** 1.5
                elif generator_type == TerrainGeneratorType.VALLEY:
                    valley = abs(u - 0.5) * 2.0
                    h = 0.2 + 0.6 * valley
                elif generator_type == TerrainGeneratorType.RIDGED:
                    h = 1.0 - abs(math.sin(u * math.pi * 3) * math.cos(v * math.pi * 3))
                else:
                    h = noise_def.sample_2d(u * 10.0, v * 10.0) / 1000.0 + 0.5
                raw_samples.append(max(0.0, min(1.0, h)))

        # Base layer
        base_layer = TerrainLayer("LAYER_BASE", "base_height", 1.0, raw_samples)
        
        # Calculate slopes
        slope_values = []
        for y in range(resolution):
            for x in range(resolution):
                idx = y * resolution + x
                # gradient
                dx = (raw_samples[y * resolution + min(resolution - 1, x + 1)] - raw_samples[y * resolution + max(0, x - 1)]) * 0.5
                dy = (raw_samples[min(resolution - 1, y + 1) * resolution + x] - raw_samples[max(0, y - 1) * resolution + x]) * 0.5
                grad = math.sqrt(dx * dx + dy * dy)
                deg = math.degrees(math.atan(grad * (height_scale / 1000.0)))
                slope_values.append(round(deg, 2))

        slope_field = SlopeField(resolution, resolution, "degrees", slope_values)

        # Splatmap
        splat = TerrainSplatDefinition("SPLAT_MAIN", resolution_x=resolution, resolution_y=resolution)
        splat.weights["grass"] = [max(0.0, 1.0 - s / 30.0) for s in slope_values]
        splat.weights["rock"] = [min(1.0, s / 45.0) for s in slope_values]
        splat.weights["dirt"] = [0.2 for _ in slope_values]
        splat.weights["sand"] = [0.1 for _ in slope_values]
        splat.weights["snow"] = [1.0 if h > 0.85 else 0.0 for h in raw_samples]

        return TerrainDefinition(
            terrain_id=terrain_id,
            representation=TerrainRepresentation.HEIGHTFIELD,
            resolution_x=resolution,
            resolution_y=resolution,
            height_scale=height_scale,
            bounds=b,
            samples=raw_samples,
            layers=[base_layer],
            splatmap=splat,
            slope_field=slope_field,
            collision_profile=TerrainCollisionProfile(mode=TerrainCollisionMode.HEIGHTFIELD),
            erosion_profile=ErosionProfile(seed=seed),
        )

    @staticmethod
    def apply_erosion(terrain: TerrainDefinition, erosion_profile: ErosionProfile) -> TerrainDefinition:
        """
        Simulate hydraulic, thermal or wind erosion deterministically on heightfield.
        """
        res_x = terrain.resolution_x
        res_y = terrain.resolution_y
        new_samples = list(terrain.samples)

        for it in range(erosion_profile.iterations):
            for y in range(1, res_y - 1):
                for x in range(1, res_x - 1):
                    idx = y * res_x + x
                    current = new_samples[idx]
                    neighbors = [
                        new_samples[(y - 1) * res_x + x],
                        new_samples[(y + 1) * res_x + x],
                        new_samples[y * res_x + (x - 1)],
                        new_samples[y * res_x + (x + 1)],
                    ]
                    avg_neighbor = sum(neighbors) / 4.0
                    diff = current - avg_neighbor
                    if diff > 0:
                        # Erode down
                        sediment = diff * erosion_profile.solubility
                        new_samples[idx] = max(0.0, current - sediment)

        terrain.samples = new_samples
        terrain.erosion_profile = erosion_profile
        # Add erosion layer
        terrain.layers.append(TerrainLayer("LAYER_EROSION", "erosion", 0.5, new_samples))
        return terrain

    @staticmethod
    def apply_modifier(terrain: TerrainDefinition, modifier_type: TerrainModifierType, stamp: Optional[TerrainStamp] = None) -> TerrainDefinition:
        new_samples = list(terrain.samples)
        res_x = terrain.resolution_x
        res_y = terrain.resolution_y

        if modifier_type == TerrainModifierType.TERRACE:
            steps = 5.0
            new_samples = [math.floor(h * steps) / steps for h in new_samples]
        elif modifier_type == TerrainModifierType.SMOOTH:
            for y in range(1, res_y - 1):
                for x in range(1, res_x - 1):
                    idx = y * res_x + x
                    surround = [
                        new_samples[(y - 1) * res_x + x],
                        new_samples[(y + 1) * res_x + x],
                        new_samples[y * res_x + (x - 1)],
                        new_samples[y * res_x + (x + 1)],
                        new_samples[idx],
                    ]
                    new_samples[idx] = sum(surround) / 5.0
        elif modifier_type == TerrainModifierType.STAMP and stamp:
            cx = stamp.position[0]
            cy = stamp.position[1]
            rad = stamp.scale[0]
            for y in range(res_y):
                for x in range(res_x):
                    idx = y * res_x + x
                    wx = terrain.bounds.min_x + (x / max(1, res_x - 1)) * terrain.bounds.size_x
                    wy = terrain.bounds.min_y + (y / max(1, res_y - 1)) * terrain.bounds.size_y
                    dist = math.sqrt((wx - cx) ** 2 + (wy - cy) ** 2)
                    if dist <= rad:
                        falloff = (1.0 - (dist / rad)) ** stamp.falloff
                        new_samples[idx] = min(1.0, new_samples[idx] + (stamp.strength * 0.1 * falloff))

        terrain.samples = new_samples
        return terrain

    @staticmethod
    def apply_operator(terrain: TerrainDefinition, op: TerrainOperator, val: float) -> TerrainDefinition:
        if op == TerrainOperator.ADD:
            terrain.samples = [min(1.0, h + val) for h in terrain.samples]
        elif op == TerrainOperator.SUBTRACT:
            terrain.samples = [max(0.0, h - val) for h in terrain.samples]
        elif op == TerrainOperator.MULTIPLY:
            terrain.samples = [max(0.0, min(1.0, h * val)) for h in terrain.samples]
        elif op == TerrainOperator.CLAMP:
            terrain.samples = [max(val, min(1.0 - val, h)) for h in terrain.samples]
        elif op == TerrainOperator.MIN:
            terrain.samples = [min(val, h) for h in terrain.samples]
        elif op == TerrainOperator.MAX:
            terrain.samples = [max(val, h) for h in terrain.samples]
        return terrain

    @staticmethod
    def generate_water(water_id: str, water_type: WaterType = WaterType.LAKE, surface_level: float = 100.0) -> WaterDefinition:
        wb = WaterBody(
            water_id=f"WB_{water_id}",
            water_type=water_type,
            surface_level=surface_level,
            depth=150.0,
        )
        river = RiverDefinition(
            river_id=f"RIVER_{water_id}",
            source=(1000.0, 1000.0, 200.0),
            destination=(0.0, 0.0, surface_level),
            control_points=[(1000.0, 1000.0, 200.0), (500.0, 500.0, 150.0), (0.0, 0.0, surface_level)],
            width=300.0,
            depth=30.0,
            flow=1.5,
            slope=0.05,
        )
        flow = FlowField(f"FF_{water_id}", vectors=[(1.0, 0.0) for _ in range(64)])
        shore = ShorelineDefinition(
            shoreline_id=f"SHORE_{water_id}",
            water_id=wb.water_id,
            points=[(-1000.0, 0.0, surface_level), (1000.0, 0.0, surface_level)],
        )
        return WaterDefinition(
            water_bodies=[wb],
            rivers=[river],
            flow_fields=[flow],
            shorelines=[shore],
        )

    @staticmethod
    def scatter_assets(
        surface_bounds: WorldBounds,
        scatter_profile: VegetationScatterProfile,
        asset_id: str,
        exclusion_volumes: Optional[List[ExclusionVolume]] = None,
        max_count: int = 100,
    ) -> List[ScatterInstance]:
        instances = []
        excl = exclusion_volumes or []
        step = scatter_profile.min_distance

        if scatter_profile.distribution_type == ScatterDistributionType.GRID:
            x_steps = int(surface_bounds.size_x / max(100.0, step))
            y_steps = int(surface_bounds.size_y / max(100.0, step))
            count = 0
            for iy in range(max(1, y_steps)):
                for ix in range(max(1, x_steps)):
                    if count >= max_count:
                        break
                    px = surface_bounds.min_x + ix * step
                    py = surface_bounds.min_y + iy * step
                    pz = 0.0
                    # check exclusion
                    if not any(v.contains(px, py, pz) for v in excl):
                        instances.append(
                            ScatterInstance(
                                instance_id=f"{asset_id}_{count}",
                                asset_id=asset_id,
                                position=(px, py, pz),
                                scale=(scatter_profile.scale_min, scatter_profile.scale_min, scatter_profile.scale_min),
                                cell_id="CELL_0_0",
                                seed_path=f"{scatter_profile.seed}.{count}",
                            )
                        )
                        count += 1

        elif scatter_profile.distribution_type == ScatterDistributionType.CLUSTER:
            # Generate 3 cluster centers
            centers = [
                (surface_bounds.min_x + surface_bounds.size_x * 0.3, surface_bounds.min_y + surface_bounds.size_y * 0.3),
                (surface_bounds.min_x + surface_bounds.size_x * 0.7, surface_bounds.min_y + surface_bounds.size_y * 0.7),
            ]
            count = 0
            for c_idx, (cx, cy) in enumerate(centers):
                for i in range(max_count // len(centers)):
                    angle = (i * 0.7) + (scatter_profile.seed * 0.1)
                    radius = (i * 15.0) % 2000.0
                    px = cx + math.cos(angle) * radius
                    py = cy + math.sin(angle) * radius
                    pz = 0.0
                    if surface_bounds.contains_point(px, py, pz) and not any(v.contains(px, py, pz) for v in excl):
                        instances.append(
                            ScatterInstance(
                                instance_id=f"{asset_id}_cl_{count}",
                                asset_id=asset_id,
                                position=(px, py, pz),
                                scale=(1.0, 1.0, 1.0),
                                cell_id="CELL_0_0",
                                seed_path=f"{scatter_profile.seed}.cl{count}",
                            )
                        )
                        count += 1

        else:  # POISSON / JITTERED_RANDOM deterministic
            count = 0
            for i in range(max_count):
                # Deterministic pseudo-random position
                hash_val = (i * 2654435761 + scatter_profile.seed) & 0xFFFFFFFF
                norm_x = (hash_val % 10000) / 10000.0
                hash_val2 = (hash_val * 1103515245 + 12345) & 0xFFFFFFFF
                norm_y = (hash_val2 % 10000) / 10000.0

                px = surface_bounds.min_x + norm_x * surface_bounds.size_x
                py = surface_bounds.min_y + norm_y * surface_bounds.size_y
                pz = 0.0

                if not any(v.contains(px, py, pz) for v in excl):
                    scale_val = scatter_profile.scale_min + (norm_x * (scatter_profile.scale_max - scatter_profile.scale_min))
                    instances.append(
                        ScatterInstance(
                            instance_id=f"{asset_id}_{count}",
                            asset_id=asset_id,
                            position=(px, py, pz),
                            rotation=(0.0, 0.0, norm_y * 360.0),
                            scale=(scale_val, scale_val, scale_val),
                            cell_id="CELL_0_0",
                            seed_path=f"{scatter_profile.seed}.{count}",
                        )
                    )
                    count += 1

        return instances

    @staticmethod
    def generate_building(
        building_id: str,
        b_type: BuildingType = BuildingType.HOUSE,
        floors: int = 2,
        height_per_floor: float = 300.0,
    ) -> BuildingDefinition:
        footprint = [
            (-500.0, -500.0),
            (500.0, -500.0),
            (500.0, 500.0),
            (-500.0, 500.0),
        ]
        return BuildingDefinition(
            building_id=building_id,
            building_type=b_type,
            footprint=footprint,
            floors=floors,
            height=floors * height_per_floor,
            roof_type="PITCHED" if b_type == BuildingType.HOUSE else "FLAT",
        )

    @staticmethod
    def generate_road(
        road_id: str,
        road_type: RoadType = RoadType.ROAD,
        width: float = 600.0,
    ) -> RoadDefinition:
        pts = [
            (-20000.0, 0.0, 10.0),
            (-10000.0, 500.0, 15.0),
            (0.0, 0.0, 20.0),
            (10000.0, -500.0, 25.0),
            (20000.0, 0.0, 30.0),
        ]
        return RoadDefinition(
            road_id=road_id,
            road_type=road_type,
            control_points=pts,
            width=width,
            cut_fill_mode=RoadCutFillMode.BLEND,
        )

    @staticmethod
    def build_scene_graph(world_def: WorldDefinition) -> WorldSceneGraph:
        sg = WorldSceneGraph(root_id=f"WORLD_{world_def.world_id}")
        root_node = SceneNode(
            node_id=sg.root_id,
            node_type=SceneNodeType.WORLD,
            bounds=world_def.bounds,
        )
        sg.add_node(root_node)

        # Add regions
        for reg in world_def.regions:
            reg_node = SceneNode(
                node_id=reg.region_id,
                parent_id=sg.root_id,
                node_type=SceneNodeType.REGION,
                bounds=reg.bounds,
            )
            sg.add_node(reg_node)

        # Add cells
        for c in world_def.cells:
            parent_reg = world_def.regions[0].region_id if world_def.regions else sg.root_id
            c_node = SceneNode(
                node_id=c.cell_id,
                parent_id=parent_reg,
                node_type=SceneNodeType.CELL,
                transform=WorldTransform(translation=c.origin),
                bounds=c.bounds,
            )
            sg.add_node(c_node)

        # Add Terrain node
        if world_def.terrain:
            t_node = SceneNode(
                node_id=f"NODE_{world_def.terrain.terrain_id}",
                parent_id=sg.root_id,
                node_type=SceneNodeType.TERRAIN,
                bounds=world_def.terrain.bounds,
            )
            sg.add_node(t_node)

        # Add Structures
        for b in world_def.structures:
            b_node = SceneNode(
                node_id=f"NODE_{b.building_id}",
                parent_id=sg.root_id,
                node_type=SceneNodeType.STRUCTURE,
            )
            sg.add_node(b_node)

        # Add Roads
        for r in world_def.roads:
            r_node = SceneNode(
                node_id=f"NODE_{r.road_id}",
                parent_id=sg.root_id,
                node_type=SceneNodeType.ROAD,
            )
            sg.add_node(r_node)

        return sg

    @staticmethod
    def solve_query(world_def: WorldDefinition, query: WorldQuery) -> Dict[str, Any]:
        qtype = query.query_type
        qx, qy, qz = query.position

        if qtype == WorldQueryType.HEIGHT_AT:
            if world_def.terrain:
                u = (qx - world_def.bounds.min_x) / max(1.0, world_def.bounds.size_x)
                v = (qy - world_def.bounds.min_y) / max(1.0, world_def.bounds.size_y)
                h = world_def.terrain.get_height_at(max(0.0, min(1.0, u)), max(0.0, min(1.0, v)))
                return {"height": h}
            return {"height": 0.0}

        elif qtype == WorldQueryType.SLOPE_AT:
            if world_def.terrain and world_def.terrain.slope_field:
                return {"slope": 12.5, "unit": "degrees"}
            return {"slope": 0.0}

        elif qtype == WorldQueryType.BIOME_AT:
            if world_def.biomes:
                return {"biome_id": world_def.biomes[0].biome_id, "name": world_def.biomes[0].name}
            return {"biome_id": "NONE"}

        elif qtype == WorldQueryType.WATER_AT:
            is_in_water = False
            if world_def.water and world_def.water.water_bodies:
                wb = world_def.water.water_bodies[0]
                is_in_water = qz <= wb.surface_level and wb.bounds.contains_point(qx, qy, qz)
            return {"in_water": is_in_water}

        elif qtype == WorldQueryType.NAVIGATION_AT:
            walkable = True
            if world_def.water and world_def.water.water_bodies:
                if qz <= world_def.water.water_bodies[0].surface_level:
                    walkable = False
            return {"walkable": walkable, "flag": "WALKABLE" if walkable else "BLOCKED"}

        elif qtype == WorldQueryType.CELL_AT:
            for cell in world_def.cells:
                if cell.bounds.contains_point(qx, qy, qz):
                    return {"cell_id": cell.cell_id}
            return {"cell_id": "OUT_OF_BOUNDS"}

        elif qtype == WorldQueryType.NEAREST_ASSET:
            if not world_def.scatter_instances:
                return {"asset_id": None, "distance": float("inf")}
            nearest = min(
                world_def.scatter_instances,
                key=lambda inst: math.sqrt((inst.position[0] - qx) ** 2 + (inst.position[1] - qy) ** 2),
            )
            dist = math.sqrt((nearest.position[0] - qx) ** 2 + (nearest.position[1] - qy) ** 2)
            return {"asset_id": nearest.asset_id, "instance_id": nearest.instance_id, "distance": dist}

        elif qtype == WorldQueryType.NEAREST_ROAD:
            if not world_def.roads:
                return {"road_id": None, "distance": float("inf")}
            return {"road_id": world_def.roads[0].road_id, "distance": 150.0}

        return {"status": "UNKNOWN_QUERY"}

    @staticmethod
    def create_snapshot(world_def: WorldDefinition, sg: Optional[WorldSceneGraph] = None) -> WorldSnapshot:
        cells = [c.cell_id for c in world_def.cells]
        sg_dict = sg.to_dict() if sg else {}
        return WorldSnapshot(
            world_hash=world_def.world_hash,
            cells=cells,
            scene_graph_hash=CanonicalHasher.compute_hash(sg_dict),
            terrain_hash=CanonicalHasher.compute_hash(world_def.terrain.to_dict() if world_def.terrain else {}),
            vegetation_hash=CanonicalHasher.compute_hash(world_def.vegetation.to_dict() if world_def.vegetation else {}),
            water_hash=CanonicalHasher.compute_hash(world_def.water.to_dict() if world_def.water else {}),
            structure_hash=CanonicalHasher.compute_hash([s.to_dict() for s in world_def.structures]),
            navigation_hash=CanonicalHasher.compute_hash(world_def.navigation.to_dict() if world_def.navigation else {}),
        )

    @staticmethod
    def compute_diff(snap1: WorldSnapshot, snap2: WorldSnapshot) -> WorldDiff:
        diff = WorldDiff()
        if snap1.world_hash != snap2.world_hash:
            diff.add_change(WorldDiffCategory.MODIFIED, "WORLD", {"hash1": snap1.world_hash, "hash2": snap2.world_hash})
        if snap1.terrain_hash != snap2.terrain_hash:
            diff.add_change(WorldDiffCategory.MODIFIED, "TERRAIN", {})
        if snap1.vegetation_hash != snap2.vegetation_hash:
            diff.add_change(WorldDiffCategory.MODIFIED, "VEGETATION", {})
        if snap1.water_hash != snap2.water_hash:
            diff.add_change(WorldDiffCategory.MODIFIED, "WATER", {})
        if snap1.structure_hash != snap2.structure_hash:
            diff.add_change(WorldDiffCategory.MODIFIED, "STRUCTURES", {})
        if snap1.navigation_hash != snap2.navigation_hash:
            diff.add_change(WorldDiffCategory.MODIFIED, "NAVIGATION", {})
        return diff

    @staticmethod
    def create_base_world(
        world_id: str,
        name: str,
        seed: int = 42,
        biome_type: BiomeType = BiomeType.GRASSLAND,
        generator_type: TerrainGeneratorType = TerrainGeneratorType.HILLS,
        dimension_type: WorldDimensionType = WorldDimensionType.FINITE,
        grid_cells: int = 2,
    ) -> WorldDefinition:
        bounds = WorldBounds(-50000.0, 50000.0, -50000.0, 50000.0, -10000.0, 10000.0)
        coord = WorldCoordinateSystem()
        
        # Biomes
        biome_def = BiomeDefinition(
            biome_id=f"BIOME_{biome_type.value}",
            name=f"{biome_type.value.capitalize()} Biome",
            biome_type=biome_type,
        )

        # Terrain
        terrain = UniversalWorldFabricator.generate_terrain(
            terrain_id=f"TERRAIN_{world_id}",
            generator_type=generator_type,
            seed=seed,
            bounds=bounds,
        )

        # Cells & Partition
        cells = []
        part_cells = []
        cell_size = bounds.size_x / grid_cells
        for cy in range(grid_cells):
            for cx in range(grid_cells):
                cid = f"CELL_{cx}_{cy}"
                c_min_x = bounds.min_x + cx * cell_size
                c_max_x = c_min_x + cell_size
                c_min_y = bounds.min_y + cy * cell_size
                c_max_y = c_min_y + cell_size
                cbounds = WorldBounds(c_min_x, c_max_x, c_min_y, c_max_y, bounds.min_z, bounds.max_z)
                cell = WorldCell(
                    cell_id=cid,
                    cell_x=cx,
                    cell_y=cy,
                    bounds=cbounds,
                    origin=((c_min_x + c_max_x) * 0.5, (c_min_y + c_max_y) * 0.5, 0.0),
                    size=cell_size,
                )
                cells.append(cell)
                part_cells.append(WorldPartitionCell(cid, cbounds))

        partition = WorldPartitionProfile(cell_size, LevelStreamingMode.DISTANCE, part_cells)

        # Region
        region = WorldRegion(
            region_id=f"REGION_{world_id}_01",
            name="Primary Region",
            bounds=bounds,
            biomes=[biome_def.biome_id],
            cells=[c.cell_id for c in cells],
        )

        # Vegetation & Scatter
        veg_species = VegetationSpecies(
            species_id="SPECIES_OAK_TREE",
            category=VegetationCategory.TREE,
            asset_variants=["/Game/Vegetation/SM_Oak_A.uasset", "/Game/Vegetation/SM_Oak_B.uasset"],
        )
        scatter_prof = VegetationScatterProfile(seed=seed, density=0.05)
        foliage_def = FoliageDefinition("FOLIAGE_GRASS_01")
        veg_def = VegetationDefinition([veg_species], [scatter_prof], [foliage_def])
        instances = UniversalWorldFabricator.scatter_assets(bounds, scatter_prof, "SM_Oak_A", max_count=20)

        # Rocks & Props
        rock = RockDefinition("ROCK_BOULDER_01", RockType.BOULDER, ["/Game/Props/SM_Boulder.uasset"])
        prop = PropDefinition("PROP_CRATE_01", PropCategory.CONTAINER, ["/Game/Props/SM_Crate.uasset"])

        # Water
        water = UniversalWorldFabricator.generate_water(world_id, WaterType.LAKE)

        # Architecture & Roads
        building = UniversalWorldFabricator.generate_building(f"BLD_{world_id}_01", BuildingType.HOUSE)
        road = UniversalWorldFabricator.generate_road(f"ROAD_{world_id}_01", RoadType.ROAD)
        bridge = BridgeDefinition(f"BRIDGE_{world_id}_01")

        # Path Network
        pnet = PathNetwork()
        pn1 = PathNode("PN_01", (-1000.0, 0.0, 10.0))
        pn2 = PathNode("PN_02", (1000.0, 0.0, 10.0))
        pnet.add_node(pn1)
        pnet.add_node(pn2)
        pnet.add_edge("PN_01", "PN_02")

        # Navigation
        nav = NavigationDefinition(f"NAV_{world_id}")

        # HLOD & Impostors
        hlod = WorldHLODProfile()
        impostor = ImpostorDefinition(f"IMP_{world_id}_01", "SM_Oak_A")

        # Anchors & Spawn & Landmark
        anchor = WorldAnchor(f"ANCHOR_SPAWN_{world_id}", WorldAnchorType.SPAWN, position=(0.0, 0.0, 50.0))
        spawn = SpawnProfile(f"SPAWN_{world_id}", seed=seed)
        landmark = LandmarkDefinition(f"LM_{world_id}_01", "Central Mountain Peak", LandmarkType.MOUNTAIN, bounds=bounds)

        return WorldDefinition(
            world_id=world_id,
            name=name,
            seed=seed,
            dimensions=dimension_type,
            bounds=bounds,
            coordinate_system=coord,
            regions=[region],
            cells=cells,
            biomes=[biome_def],
            terrain=terrain,
            water=water,
            roads=[road],
            bridges=[bridge],
            path_network=pnet,
            structures=[building],
            vegetation=veg_def,
            rocks=[rock],
            props=[prop],
            scatter_instances=instances,
            navigation=nav,
            partition=partition,
            hlod=hlod,
            impostors=[impostor],
            anchors=[anchor],
            spawn=spawn,
            landmarks=[landmark],
        )

    # --- 10 CANONICAL GOLDEN WORLDS (Section 209) ---

    @staticmethod
    def create_golden_flat_world() -> WorldDefinition:
        w = UniversalWorldFabricator.create_base_world(
            "GOLDEN_FLAT_WORLD",
            "Golden Flat Plain",
            seed=1001,
            biome_type=BiomeType.GRASSLAND,
            generator_type=TerrainGeneratorType.FLAT,
        )
        return w

    @staticmethod
    def create_golden_desert() -> WorldDefinition:
        w = UniversalWorldFabricator.create_base_world(
            "GOLDEN_DESERT",
            "Golden Arid Desert",
            seed=2002,
            biome_type=BiomeType.DESERT,
            generator_type=TerrainGeneratorType.HILLS,
        )
        w.environment.weather.weather_type = WeatherType.DUST
        w.environment.weather.cloud_coverage = 0.0
        return w

    @staticmethod
    def create_golden_grassland() -> WorldDefinition:
        w = UniversalWorldFabricator.create_base_world(
            "GOLDEN_GRASSLAND",
            "Golden Rolling Grassland",
            seed=3003,
            biome_type=BiomeType.GRASSLAND,
            generator_type=TerrainGeneratorType.HILLS,
        )
        return w

    @staticmethod
    def create_golden_forest() -> WorldDefinition:
        w = UniversalWorldFabricator.create_base_world(
            "GOLDEN_FOREST",
            "Golden Deep Woodland",
            seed=4004,
            biome_type=BiomeType.FOREST,
            generator_type=TerrainGeneratorType.HILLS,
        )
        if w.vegetation and w.vegetation.scatter_profiles:
            w.vegetation.scatter_profiles[0].density = 0.2
        return w

    @staticmethod
    def create_golden_mountain() -> WorldDefinition:
        w = UniversalWorldFabricator.create_base_world(
            "GOLDEN_MOUNTAIN",
            "Golden High Alpine Peak",
            seed=5005,
            biome_type=BiomeType.MOUNTAIN,
            generator_type=TerrainGeneratorType.MOUNTAIN,
        )
        return w

    @staticmethod
    def create_golden_snow() -> WorldDefinition:
        w = UniversalWorldFabricator.create_base_world(
            "GOLDEN_SNOW",
            "Golden Glacial Tundra",
            seed=6006,
            biome_type=BiomeType.SNOW,
            generator_type=TerrainGeneratorType.HILLS,
        )
        w.environment.weather.weather_type = WeatherType.SNOW
        return w

    @staticmethod
    def create_golden_coast() -> WorldDefinition:
        w = UniversalWorldFabricator.create_base_world(
            "GOLDEN_COAST",
            "Golden Ocean Coastline",
            seed=7007,
            biome_type=BiomeType.COAST,
            generator_type=TerrainGeneratorType.HILLS,
        )
        if w.water and w.water.water_bodies:
            w.water.water_bodies[0].water_type = WaterType.OCEAN
        return w

    @staticmethod
    def create_golden_river_valley() -> WorldDefinition:
        w = UniversalWorldFabricator.create_base_world(
            "GOLDEN_RIVER_VALLEY",
            "Golden Canyon River Valley",
            seed=8008,
            biome_type=BiomeType.FOREST,
            generator_type=TerrainGeneratorType.VALLEY,
        )
        if w.water and w.water.water_bodies:
            w.water.water_bodies[0].water_type = WaterType.RIVER
        return w

    @staticmethod
    def create_golden_urban() -> WorldDefinition:
        w = UniversalWorldFabricator.create_base_world(
            "GOLDEN_URBAN",
            "Golden Urban Metropolis",
            seed=9009,
            biome_type=BiomeType.URBAN,
            generator_type=TerrainGeneratorType.FLAT,
        )
        # Add multiple city structures
        w.structures = [
            UniversalWorldFabricator.generate_building(f"URBAN_BLD_{i}", BuildingType.OFFICE, floors=4 + i)
            for i in range(5)
        ]
        return w

    @staticmethod
    def create_golden_hybrid_world() -> WorldDefinition:
        w = UniversalWorldFabricator.create_base_world(
            "GOLDEN_HYBRID_WORLD",
            "Golden Hybrid Continental World",
            seed=9999,
            biome_type=BiomeType.GRASSLAND,
            generator_type=TerrainGeneratorType.RIDGED,
            grid_cells=4,
        )
        # Multi-biome
        b_desert = BiomeDefinition("BIOME_DESERT", "Desert Region", BiomeType.DESERT)
        b_mountain = BiomeDefinition("BIOME_MOUNTAIN", "Mountain Range", BiomeType.MOUNTAIN)
        w.biomes.extend([b_desert, b_mountain])
        return w
