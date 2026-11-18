"""
UAF-81.102: Macro-Orchestrator CLI & One-Click Builder API.
Provides command-line interface and direct python helpers for generating complete vertical slices.
"""

from __future__ import annotations

import argparse
import sys
from typing import List, Optional

from uaf.macro_orchestrator.core.contracts import (
    VerticalSliceConfig,
    SliceSize,
    IntegratedSliceManifest,
)
from uaf.macro_orchestrator.orchestrator.slice_orchestrator import VerticalSliceMasterOrchestrator
from uaf.macro_orchestrator.integrator.package_integrator import MasterPackageIntegrator, PackageResult
from uaf.weather_atmosphere import WeatherBiomeType


def build_vertical_slice(
    config: Optional[VerticalSliceConfig] = None,
    output_dir: Optional[str] = None,
    as_zip: bool = False,
) -> PackageResult:
    """
    Convenience API: Coordinates execution of all 8 procedural engines,
    packages artifacts, and writes out the complete UE5 bundle.
    """
    if config is None:
        config = VerticalSliceConfig(slice_name="Alpha_Vertical_Slice", size=SliceSize.SMALL, seed=42)

    orchestrator = VerticalSliceMasterOrchestrator()
    manifest = orchestrator.execute_pipeline(config)

    integrator = MasterPackageIntegrator()
    package_res = integrator.package_slice(manifest, output_dir=output_dir, as_zip=as_zip)
    return package_res


def create_cli_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="aoe build-slice",
        description="One-Click Full Vertical Slice Builder & Universal Macro-Orchestrator",
    )
    parser.add_argument("--name", default="Autonomous_Vertical_Slice", help="Slice identifier name")
    parser.add_argument(
        "--size",
        choices=[s.value for s in SliceSize],
        default=SliceSize.SMALL.value,
        help="Grid & spatial scale size preset",
    )
    parser.add_argument(
        "--biome",
        choices=[b.value for b in WeatherBiomeType],
        default=WeatherBiomeType.TEMPERATE_FOREST.value,
        help="Atmospheric & vegetation biome preset",
    )
    parser.add_argument("--seed", type=int, default=42, help="Deterministic pseudo-random seed")
    parser.add_argument("--output-dir", default=None, help="Custom output directory for the bundle")
    parser.add_argument("--zip", action="store_true", help="Compress package bundle into a .zip archive")
    parser.add_argument("--no-audio", action="store_true", help="Disable MetaSounds & acoustic simulation")
    parser.add_argument("--no-chaos", action="store_true", help="Disable Chaos Voronoi destruction")
    return parser


def run_cli(args: Optional[List[str]] = None) -> int:
    parser = create_cli_parser()
    parsed = parser.parse_args(args)

    size = SliceSize(parsed.size)
    biome = WeatherBiomeType(parsed.biome)

    cfg = VerticalSliceConfig(
        slice_name=parsed.name,
        size=size,
        biome=biome,
        seed=parsed.seed,
        enable_metasounds_audio=(not parsed.no_audio),
        enable_chaos_destruction=(not parsed.no_chaos),
    )

    print(f"[AOE] Building vertical slice '{cfg.slice_name}' (Size: {cfg.size.value}, Biome: {cfg.biome.value}, Seed: {cfg.seed})...")
    res = build_vertical_slice(config=cfg, output_dir=parsed.output_dir, as_zip=parsed.zip)

    print(f"[AOE] Successfully built vertical slice!")
    print(f"      - Output Directory: {res.bundle_directory}")
    print(f"      - Total Files: {len(res.files_written)}")
    print(f"      - Package Size: {res.total_bytes} bytes")
    print(f"      - UE5 Import Script: {res.ue5_script_path}")
    if res.is_zip:
        print(f"      - Compressed Archive: {res.zip_path}")
    return 0


if __name__ == "__main__":
    sys.exit(run_cli())
