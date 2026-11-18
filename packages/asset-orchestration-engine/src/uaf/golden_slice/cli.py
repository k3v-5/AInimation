"""CLI commands for Golden Vertical Slice autonomous production and certification."""

from __future__ import annotations
import argparse
import sys
from typing import List, Optional

from uaf.golden_slice.manifest.models import CertificationLevel, GoldenSliceManifest, QualityProfile
from uaf.golden_slice.orchestrator.orchestrator import GoldenSliceOrchestrator


def create_cli_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="aoe golden-slice",
        description="Universal Production Golden Vertical Slice & Autonomous Certification System",
    )
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # Commands: plan, generate, test, profile, repair, package, certify, all
    subparsers.add_parser("plan", help="Plan generation DAG and resolve dependencies")
    subparsers.add_parser("generate", help="Generate all vertical slice subsystems")
    subparsers.add_parser("test", help="Execute automated QA functional suites and bot scenario")
    subparsers.add_parser("profile", help="Measure frame times, percentiles, and budget limits")
    subparsers.add_parser("repair", help="Execute autonomous failure analysis and self-repair")
    subparsers.add_parser("package", help="Cook, stage, and package artifacts for target platform")

    cert_parser = subparsers.add_parser("certify", help="Evaluate certification gates and generate reports")
    cert_parser.add_argument("--profile", choices=["BRONZE", "SILVER", "GOLD", "PLATINUM"], default="GOLD")

    all_parser = subparsers.add_parser("all", help="Execute complete autonomous production pipeline")
    all_parser.add_argument("--profile", choices=["BRONZE", "SILVER", "GOLD", "PLATINUM"], default="GOLD")

    export_parser = subparsers.add_parser("export-bundle", help="Export portable drop-in bundle for Unreal Engine 5")
    export_parser.add_argument("--output", default="dist/AOE_UE5_Bundle.zip", help="Output zip or directory path")
    export_parser.add_argument("--no-zip", action="store_true", help="Export as directory instead of zip archive")

    return parser


def run_cli(args: Optional[List[str]] = None) -> int:
    parser = create_cli_parser()
    parsed = parser.parse_args(args)

    manifest = GoldenSliceManifest()
    orchestrator = GoldenSliceOrchestrator(manifest)

    if parsed.command == "plan":
        dag = orchestrator.plan()
        print(f"[OK] Planned generation DAG with {dag.count} tasks.")
        return 0
    elif parsed.command == "generate":
        orchestrator.plan()
        slices = orchestrator.generate()
        print(f"[OK] Generated {len(slices)} vertical slice subsystems.")
        return 0
    elif parsed.command == "test":
        orchestrator.plan()
        orchestrator.generate()
        report = orchestrator.test()
        print(f"[OK] QA completed: {report.passed_tests}/{report.total_tests} suites passed.")
        return 0 if report.is_success else 1
    elif parsed.command == "profile":
        summary = orchestrator.profile()
        print(f"[OK] Profiling completed: Avg {summary.average_ms:.2f}ms | P99 {summary.p99_ms:.2f}ms.")
        return 0
    elif parsed.command == "repair":
        res = orchestrator.repair("Simulated missing texture map")
        print(f"[OK] Repair executed: {res.repair_action if res else 'No defects'}.")
        return 0
    elif parsed.command == "package":
        res = orchestrator.package()
        print(f"[OK] Packaged for {res.platform.value}: {len(res.artifact_manifest.artifacts)} artifacts.")
        return 0 if res.is_success else 1
    elif parsed.command in ("certify", "all"):
        lvl = CertificationLevel(getattr(parsed, "profile", "GOLD"))
        report = orchestrator.run_full_pipeline(target_level=lvl)
        print("======================================")
        print(" UAF GOLDEN SLICE CERTIFICATION")
        print("======================================")
        print(f"Generation ........ {'PASS' if report.generation_passed else 'FAIL'}")
        print(f"Integration ....... {'PASS' if report.integration_passed else 'FAIL'}")
        print(f"QA Tests .......... {'PASS' if report.qa_tests_passed else 'FAIL'}")
        print(f"Performance ....... {'PASS' if report.performance_compliant else 'FAIL'}")
        print(f"Determinism ....... {'PASS' if report.determinism_verified else 'FAIL'}")
        print(f"Recovery .......... {'PASS' if report.recovery_verified else 'FAIL'}")
        print(f"Packaging ......... {'PASS' if report.packaging_passed else 'FAIL'}")
        print()
        print(f"CRITICAL FAILURES : {report.critical_failures}")
        print(f"BLOCKING WARNINGS  : {report.blocking_warnings}")
        print(f"REPLAY MISMATCHES  : {report.replay_mismatches}")
        print()
        print(f"FINAL STATUS: {report.final_status}")
        print("======================================")
        return 0 if report.is_certified else 1
    elif parsed.command == "export-bundle":
        from uaf.golden_slice.packaging.bundle_exporter import UE5BundleExporter
        exporter = UE5BundleExporter()
        out_path = getattr(parsed, "output", "dist/AOE_UE5_Bundle.zip")
        as_zip = not getattr(parsed, "no_zip", False)
        bundle_res = exporter.create_bundle(manifest, output_path=out_path, as_zip=as_zip)
        print("======================================")
        print(" AOE PORTABLE UE5 BUNDLE EXPORT")
        print("======================================")
        print(f"Project ......: {bundle_res.get('project_id', 'GoldenSlice')}")
        print(f"Bundle Path ..: {bundle_res['bundle_path']}")
        print(f"Format .......: {'ZIP Archive' if bundle_res['is_zip'] else 'Directory'}")
        print(f"Total Files ..: {bundle_res['total_files']}")
        print(f"Bundle Size ..: {bundle_res['bundle_bytes'] / 1024:.2f} KB")
        print(f"SHA-256 ......: {bundle_res['sha256'][:16]}...")
        print("======================================")
        print("[OK] Portable bundle ready to transfer to your UE5 workstation!")
        return 0
    else:
        parser.print_help()
        return 0


if __name__ == "__main__":
    sys.exit(run_cli())
