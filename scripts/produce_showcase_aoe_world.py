"""Generate genuine Asset Orchestration Engine (AOE + UAF) world & WFC assets for 'Cross-Dimension Rescue'.

Runs live code from ``packages/asset-orchestration-engine/src/uaf``:
1. Macro-Landscape terrain synthesis + Hydraulic & Thermal Erosion + Whittaker Climate + 16-bit UE5 ``.r16`` export.
2. 2D Wave Function Collapse (WFC) Sci-Fi Sector 7 interior level solving + UE5 level manifest export.
3. Topographic radar map preview (``aoe_sector7_radar.png``) and summary telemetry JSON for the 6-engine showcase HUD.

Usage:
  C:\\Python314\\python.exe scripts\\produce_showcase_aoe_world.py
"""

from __future__ import annotations

import json
from pathlib import Path
import sys
from typing import Dict, List

import cv2
import numpy as np

PROJECT_ROOT = Path(r"E:\Disco F\Dev\IANIMATION")
AOE_ROOT = PROJECT_ROOT / "packages" / "asset-orchestration-engine"
OUT_DIR = PROJECT_ROOT / "outputs" / "showcase_monorepo"
AOE_WORLD_DIR = OUT_DIR / "aoe_world"

if str(AOE_ROOT) not in sys.path:
    sys.path.insert(0, str(AOE_ROOT))
if str(AOE_ROOT / "src") not in sys.path:
    sys.path.insert(1, str(AOE_ROOT / "src"))

from src.uaf.landscape import (  # noqa: E402
    ClimateModeler,
    Heightfield2D,
    HydraulicErosionSimulator,
    MacroTerrainGenerator,
    TerrainWeightmapGenerator,
    ThermalErosionSimulator,
    UE5LandscapeExporter,
)
from src.uaf.level_design import (  # noqa: E402
    UE5LevelExporter,
    WaveFunctionCollapse2D,
    create_scifi_interior_catalog_2d,
)


def render_topographic_radar(hf: Heightfield2D, wfc_cells: List[Dict[str, object]], out_png: Path) -> None:
    """Render a crisp 256x256 topographic contour & WFC overlay radar from real AOE heightfield data."""
    arr_u16 = np.array(hf.to_uint16_array(), dtype=np.float32).reshape((hf.height, hf.width))
    lo, hi = float(arr_u16.min()), float(arr_u16.max())
    norm = (arr_u16 - lo) / max(1.0, hi - lo)

    # Upscale cleanly to 256x256 and clamp bicubic overshoot to [0, 1]
    h_map = np.clip(cv2.resize(norm, (256, 256), interpolation=cv2.INTER_CUBIC), 0.0, 1.0)

    # Compute hillshade + dark tactical thermal colormap
    gy, gx = np.gradient(h_map * 18.0)
    shade = np.clip(0.55 + 0.45 * (gx * 0.65 - gy * 0.65), 0.15, 1.0)

    radar = np.zeros((256, 256, 3), dtype=np.uint8)
    # Deep slate blue-cyan lowlands -> warm crimson peaks
    radar[:, :, 0] = np.clip((18 + 135 * (1.0 - h_map) * 0.7) * shade, 0, 255).astype(np.uint8)   # B
    radar[:, :, 1] = np.clip((26 + 150 * (1.0 - abs(h_map - 0.45) * 1.4)) * shade, 0, 255).astype(np.uint8)  # G
    radar[:, :, 2] = np.clip((35 + 220 * (h_map ** 1.35)) * shade, 0, 255).astype(np.uint8)       # R

    # Crisp elevation isoline contours every 10%
    levels = np.floor(h_map * 10.0)
    edge_x = np.abs(np.diff(levels, axis=1, prepend=levels[:, :1])) > 0
    edge_y = np.abs(np.diff(levels, axis=0, prepend=levels[:1, :])) > 0
    contour = edge_x | edge_y
    radar[contour] = (255, 229, 0)  # Cyan isolines (BGR)

    # Overlay solved WFC 7x7 Sector 7 room grid softly in center region
    grid_n = 7
    cell_px = 24
    ox = (256 - grid_n * cell_px) // 2
    oy = (256 - grid_n * cell_px) // 2
    for cell in wfc_cells:
        cx = int(cell["x"])  # type: ignore[arg-type]
        cy = int(cell["y"])  # type: ignore[arg-type]
        tid = str(cell["tile_id"])
        x0, y0 = ox + cx * cell_px, oy + cy * cell_px
        is_wall_empty = "empty" in tid.lower() or "solid" in tid.lower()
        col = (60, 75, 95) if is_wall_empty else (255, 229, 0)
        cv2.rectangle(radar, (x0 + 2, y0 + 2), (x0 + cell_px - 2, y0 + cell_px - 2), col, 1, cv2.LINE_AA)

    # Reactor core hotspot marker at center cell (3, 3)
    rcx, rcy = ox + 3 * cell_px + cell_px // 2, oy + 3 * cell_px + cell_px // 2
    cv2.circle(radar, (rcx, rcy), 8, (36, 20, 255), -1, cv2.LINE_AA)
    cv2.circle(radar, (rcx, rcy), 13, (255, 255, 255), 1, cv2.LINE_AA)

    cv2.imwrite(str(out_png), radar)


def generate_aoe_showcase_world() -> None:
    """Execute genuine AOE Landscape + WFC Level Design pipelines and export showcase artifacts."""
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    AOE_WORLD_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Macro-Landscape with Hydraulic + Thermal Erosion & UE5 .r16 export
    hf = Heightfield2D(width=128, height=128, meters_per_cell=4.0, min_elevation_meters=-20.0, max_elevation_meters=420.0)
    hf = MacroTerrainGenerator(seed=7).generate(hf)
    hf = HydraulicErosionSimulator(seed=7).simulate(hf, num_droplets=3500)
    hf = ThermalErosionSimulator().simulate(hf, iterations=6)

    climate = ClimateModeler(seed=7).generate_climate(hf)
    weightmaps = TerrainWeightmapGenerator.generate_weightmaps(hf, climate)

    exporter = UE5LandscapeExporter(landscape_name="Sector7_ThermalBasin")
    first_out, second_out = exporter.export_all(hf, weightmaps, AOE_WORLD_DIR)
    if first_out.suffix.lower() == ".r16":
        r16_path, land_manifest_path = first_out, second_out
    else:
        land_manifest_path, r16_path = first_out, second_out
    if not r16_path.suffix.lower() == ".r16":
        r16_candidates = list(AOE_WORLD_DIR.glob("*.r16"))
        if r16_candidates:
            r16_path = r16_candidates[0]

    # 2. Procedural Level Design via 2D Wave Function Collapse (Sci-Fi Interior Catalog)
    catalog = create_scifi_interior_catalog_2d()
    wfc = WaveFunctionCollapse2D(width=7, height=7, tile_catalog=catalog, seed=7, tile_size_meters=4.0)
    wfc.constrain_boundaries()
    placed_tiles = wfc.solve()

    tile_map = {t.tile_id: t for t in catalog}
    level_exporter = UE5LevelExporter()
    level_manifest = level_exporter.build_manifest(placed_tiles, tile_map)
    wfc_json_path = OUT_DIR / "aoe_sector7_wfc_level.json"
    level_exporter.export_to_json(level_manifest, wfc_json_path)

    wfc_cells: List[Dict[str, object]] = [
        {
            "x": int(coord[0]),
            "y": int(coord[1]),
            "tile_id": placed.tile_id,
            "rotation_deg": int(placed.rotation_deg),
        }
        for coord, placed in sorted(placed_tiles.items())
    ]

    radar_path = OUT_DIR / "aoe_sector7_radar.png"
    render_topographic_radar(hf, wfc_cells, radar_path)

    u16_vals = hf.to_uint16_array()
    summary = {
        "engine": "aoe-blender-mcp",
        "package": "packages/asset-orchestration-engine",
        "landscape": {
            "name": "Sector7_ThermalBasin",
            "resolution": [hf.width, hf.height],
            "meters_per_cell": hf.meters_per_cell,
            "hydraulic_droplets": 3500,
            "thermal_iterations": 6,
            "r16_path": str(r16_path.relative_to(PROJECT_ROOT)).replace("\\", "/"),
            "r16_bytes": r16_path.stat().st_size,
            "manifest_path": str(land_manifest_path.relative_to(PROJECT_ROOT)).replace("\\", "/"),
            "elevation_u16_min": int(min(u16_vals)),
            "elevation_u16_max": int(max(u16_vals)),
        },
        "wfc_level": {
            "grid": [7, 7],
            "total_tiles_solved": len(placed_tiles),
            "unique_tile_types": len({p.tile_id for p in placed_tiles.values()}),
            "manifest_path": str(wfc_json_path.relative_to(PROJECT_ROOT)).replace("\\", "/"),
        },
        "radar_preview": str(radar_path.relative_to(PROJECT_ROOT)).replace("\\", "/"),
    }
    summary_path = OUT_DIR / "aoe_sector7_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

    print(f"AOE Landscape .r16 exported: {r16_path} ({r16_path.stat().st_size} bytes)")
    print(f"AOE WFC 7x7 Level solved: {len(placed_tiles)} tiles -> {wfc_json_path}")
    print(f"AOE Topographic Radar rendered: {radar_path}")
    print(f"AOE Summary manifest written: {summary_path}")


if __name__ == "__main__":
    generate_aoe_showcase_world()
