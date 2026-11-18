"""
Universal World Validator for UAF-81.56.
Enforces multi-factor quality scoring, category rules, and non-negotiable Hard Fail conditions.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
import re
from ..models.definition import (
    WorldDefinition,
    WorldSceneGraph,
    BuildingDefinition,
    RiverDefinition,
    WorldBounds,
)


@dataclass
class WorldValidationReport:
    is_valid: bool = True
    quality_score: float = 100.0
    passed_checks: List[str] = field(default_factory=list)
    failed_checks: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    details: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "is_valid": self.is_valid,
            "quality_score": round(self.quality_score, 2),
            "passed_checks": list(self.passed_checks),
            "failed_checks": list(self.failed_checks),
            "warnings": list(self.warnings),
            "details": dict(self.details),
        }


class UniversalWorldValidator:
    """
    Quality gate & structural validator for UAF-81.56 World Assets.
    """

    WINDOWS_DRIVE_PATTERN = re.compile(r"^[A-Za-z]:[/\\]")

    @classmethod
    def validate_world(
        cls,
        world_def: WorldDefinition,
        scene_graph: Optional[WorldSceneGraph] = None,
    ) -> WorldValidationReport:
        report = WorldValidationReport()
        deductions = 0.0

        # --- 1. HARD FAIL: PATH PURITY ---
        # Scan all asset references for local machine drive letters (C:\, D:\, E:\)
        all_asset_refs = []
        if world_def.terrain and world_def.terrain.splatmap:
            # Splatmap or terrain references
            pass
        if world_def.water:
            for wb in world_def.water.water_bodies:
                all_asset_refs.append(wb.material_reference)
            for sh in world_def.water.shorelines:
                all_asset_refs.append(sh.material)
        if world_def.vegetation:
            for sp in world_def.vegetation.species:
                all_asset_refs.extend(sp.asset_variants)
            for f in world_def.vegetation.foliage:
                all_asset_refs.append(f.asset_reference)
        for rk in world_def.rocks:
            all_asset_refs.extend(rk.asset_variants)
        for p in world_def.props:
            all_asset_refs.extend(p.asset_variants)
        for bld in world_def.structures:
            all_asset_refs.append(bld.wall_material)
            all_asset_refs.append(bld.roof_material)
        for rd in world_def.roads:
            all_asset_refs.append(rd.surface_profile)
        all_asset_refs.append(world_def.environment.ambient_soundtrack)

        for ref in all_asset_refs:
            if ref and cls.WINDOWS_DRIVE_PATTERN.match(ref):
                report.is_valid = False
                report.failed_checks.append(f"HARD_FAIL: Machine-dependent path detected: {ref}")
                report.quality_score = 0.0
                return report

        report.passed_checks.append("CHECK_PATH_PURITY")

        # --- 2. HARD FAIL: BOUNDS VALIDITY ---
        b = world_def.bounds
        if b.min_x >= b.max_x or b.min_y >= b.max_y or b.min_z >= b.max_z:
            report.is_valid = False
            report.failed_checks.append(f"HARD_FAIL: Inverted or non-positive world bounds: {b}")
            report.quality_score = 0.0
            return report
        report.passed_checks.append("CHECK_BOUNDS_VALIDITY")

        # --- 3. HARD FAIL: EMPTY CELLS ---
        if not world_def.cells:
            report.is_valid = False
            report.failed_checks.append("HARD_FAIL: World has 0 cells.")
            report.quality_score = 0.0
            return report
        report.passed_checks.append("CHECK_CELLS_NOT_EMPTY")

        # --- 4. HARD FAIL: RIVER UPHILL FLOW & NEGATIVE WIDTH ---
        if world_def.water:
            for riv in world_def.water.rivers:
                if riv.width <= 0.0:
                    report.is_valid = False
                    report.failed_checks.append(f"HARD_FAIL: River {riv.river_id} has non-positive width {riv.width}")
                    report.quality_score = 0.0
                    return report
                if riv.source[2] < riv.destination[2]:
                    report.is_valid = False
                    report.failed_checks.append(
                        f"HARD_FAIL: River {riv.river_id} flows uphill (src_z={riv.source[2]} < dst_z={riv.destination[2]})"
                    )
                    report.quality_score = 0.0
                    return report
        report.passed_checks.append("CHECK_RIVER_FLOW_PHYSICS")

        # --- 5. HARD FAIL: ZERO-FLOOR BUILDINGS ---
        for bld in world_def.structures:
            if bld.floors <= 0:
                report.is_valid = False
                report.failed_checks.append(f"HARD_FAIL: Building {bld.building_id} has zero or negative floors: {bld.floors}")
                report.quality_score = 0.0
                return report
            if bld.height <= 0.0:
                report.is_valid = False
                report.failed_checks.append(f"HARD_FAIL: Building {bld.building_id} has zero or negative height: {bld.height}")
                report.quality_score = 0.0
                return report
        report.passed_checks.append("CHECK_BUILDING_SANITY")

        # --- 6. SCENE GRAPH HIERARCHY VALIDATION ---
        if scene_graph:
            sg_issues = scene_graph.validate_hierarchy()
            for issue in sg_issues:
                if issue.startswith("cyclic_parent"):
                    report.is_valid = False
                    report.failed_checks.append(f"HARD_FAIL: Cyclic parent detected in scene graph: {issue}")
                    report.quality_score = 0.0
                    return report
                elif issue.startswith("missing_parent"):
                    report.warnings.append(f"SceneGraph warning: {issue}")
                    deductions += 5.0
                elif issue.startswith("orphan_node"):
                    report.warnings.append(f"SceneGraph orphan: {issue}")
                    deductions += 2.0
            if not sg_issues:
                report.passed_checks.append("CHECK_SCENE_GRAPH_HIERARCHY")

        # --- 7. TERRAIN CHECKS ---
        if world_def.terrain:
            if not world_def.terrain.samples:
                report.warnings.append("Terrain has empty samples")
                deductions += 10.0
            elif any(s < 0.0 or s > 1.0 for s in world_def.terrain.samples):
                report.warnings.append("Terrain samples exceed [0..1] range")
                deductions += 5.0
            else:
                report.passed_checks.append("CHECK_TERRAIN_SAMPLES")

        # --- 8. BIOME VALIDATION ---
        if not world_def.biomes:
            report.warnings.append("World has no biomes defined")
            deductions += 10.0
        else:
            report.passed_checks.append("CHECK_BIOME_DEFINITIONS")

        # --- 9. ROAD SLOPE LIMIT ---
        for rd in world_def.roads:
            if rd.slope_limit > 45.0:
                report.warnings.append(f"Road {rd.road_id} slope limit ({rd.slope_limit}) is excessively steep")
                deductions += 5.0

        # --- 10. NAVIGATION CONNECTIVITY ---
        if world_def.navigation:
            if not world_def.navigation.connectivity:
                report.warnings.append(f"Navigation {world_def.navigation.nav_id} flagged as disconnected")
                deductions += 10.0
            else:
                report.passed_checks.append("CHECK_NAVIGATION_CONNECTIVITY")

        report.quality_score = max(0.0, 100.0 - deductions)
        return report
