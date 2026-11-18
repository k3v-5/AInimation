"""Automated Integrity & Discovery Test Suite for Unified IANIMATION Monorepo.

Verifies:
1. All 5 unified subsystems exist under packages/ with non-empty READMEs.
2. Zero corrupted/blank/null-filled files anywhere in packages/.
3. UnifiedAnimationRegistry reports exact verified counts (5 subsystems,
   144 MCP tools, 123 procedural Blender scripts).
4. Cross-domain tool discovery and MCP invocation via unified_mcp_server.
5. Master AI documentation (AGENTS.md, docs/*, mcp_servers.config.json) validity.
6. Path-traversal boundary enforcement.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from backend.mcp import (
    FastMCPServer,
    SubsystemDomain,
    UnifiedAnimationRegistry,
    get_unified_registry,
    list_monorepo_subsystems,
    mcp_server,
    search_monorepo_tools,
    unified_mcp_server,
)
from backend.mcp.unified_registry import (
    MonorepoIntegrityReport,
    MonorepoToolSearchResult,
    _confine_to_root,
)

MONOREPO_ROOT = Path(__file__).resolve().parents[2]
PACKAGES_DIR = MONOREPO_ROOT / "packages"


def test_monorepo_packages_and_readmes_exist() -> None:
    """Every unified subsystem directory and its README.md must exist and be non-empty."""
    expected_packages = [
        "3d-ai-engine",
        "adobe-suite",
        "motion-vfx",
        "stick-animator",
        "blender-procedural-lab",
    ]
    for pkg in expected_packages:
        pkg_dir = PACKAGES_DIR / pkg
        readme = pkg_dir / "README.md"
        assert pkg_dir.is_dir(), f"Missing unified package directory: {pkg_dir}"
        assert readme.is_file(), f"Missing README.md for package: {readme}"
        assert len(readme.read_text(encoding="utf-8").strip()) > 100


def test_zero_corrupt_or_blank_files_in_packages() -> None:
    """Zero disk-recovery blank/null-filled files may reside anywhere inside packages/."""
    assert PACKAGES_DIR.is_dir()
    corrupt_files = []
    scanned = 0
    for item in PACKAGES_DIR.rglob("*"):
        if item.is_file():
            scanned += 1
            raw = item.read_bytes()
            if len(raw.strip(b" \t\r\n\x00")) == 0:
                corrupt_files.append(str(item.relative_to(MONOREPO_ROOT)))
    assert scanned > 2000, f"Expected >2000 migrated clean files, scanned {scanned}"
    assert corrupt_files == [], f"Detected blank/corrupt files: {corrupt_files[:20]}"


def test_unified_registry_integrity_report() -> None:
    """validate_monorepo_integrity must return 100% valid metrics across all 5 packages."""
    registry = get_unified_registry()
    assert isinstance(registry, UnifiedAnimationRegistry)

    report = registry.validate_monorepo_integrity()
    assert isinstance(report, MonorepoIntegrityReport)
    assert report.is_valid is True, f"Integrity errors: {report.missing_paths}"
    assert report.total_subsystems == 5
    assert report.total_mcp_tools == 144
    assert report.total_procedural_generators == 123
    assert report.corrupt_files_detected == 0
    assert report.missing_paths == []
    assert all(report.subsystems_status.values())


@pytest.mark.parametrize(
    ("query", "expected_subsystem"),
    [
        ("viseme", "adobe-animation-mcp"),
        ("after effects", "after-effects-motion-engine"),
        ("dolly", "after-effects-motion-engine"),
        ("stick", "stykanimate-mcp"),
        ("pbr", "blender-procedural-lab"),
        ("ue5", "ianimation-3d"),
    ],
)
def test_cross_domain_tool_search(query: str, expected_subsystem: str) -> None:
    """Keyword queries must resolve matching tools/generators in the expected subsystem."""
    res = search_monorepo_tools(query=query)
    assert isinstance(res, MonorepoToolSearchResult)
    assert res.total_matches >= 1, f"No tools matched query '{query}'"
    subsystem_ids = {item.subsystem_id for item in res.matches}
    assert expected_subsystem in subsystem_ids


def test_domain_filtered_search_and_lookup() -> None:
    """Filtering by domain returns strictly tools belonging to that domain."""
    registry = get_unified_registry()
    adobe_sub = registry.get_subsystem("adobe-animation-mcp")
    assert adobe_sub.domain == SubsystemDomain.ADOBE_2D_SUITE
    assert adobe_sub.tool_count == 38

    filtered = registry.search_tools(query="", domain="stick_2d_ik")
    assert len(filtered) == 26
    assert all(item.domain == SubsystemDomain.STICK_2D_IK for item in filtered)


def test_mcp_server_invocation_parity() -> None:
    """Verify both default mcp_server contract (6 tools) and unified_mcp_server (8 tools)."""
    assert len(mcp_server.list_tools()) == 6
    assert isinstance(unified_mcp_server, FastMCPServer)
    assert len(unified_mcp_server.list_tools()) == 8

    rep = unified_mcp_server.call_tool("list_monorepo_subsystems", include_details=True)
    assert isinstance(rep, MonorepoIntegrityReport)
    assert rep.is_valid is True

    direct_rep = list_monorepo_subsystems()
    assert direct_rep.total_mcp_tools == rep.total_mcp_tools == 144

    search_res = unified_mcp_server.call_tool("search_monorepo_tools", query="viseme")
    assert isinstance(search_res, MonorepoToolSearchResult)
    assert search_res.total_matches >= 4


def test_ai_documentation_and_mcp_config_files() -> None:
    """All master AI docs, ingestion manifest, and mcp_servers.config.json must exist and parse cleanly."""
    required_files = [
        MONOREPO_ROOT / "AGENTS.md",
        MONOREPO_ROOT / "README.md",
        MONOREPO_ROOT / "PROJECT_STATUS.md",
        MONOREPO_ROOT / "mcp_servers.config.json",
        MONOREPO_ROOT / "docs" / "ARCHITECTURE.md",
        MONOREPO_ROOT / "docs" / "MCP_CATALOG.md",
        MONOREPO_ROOT / "docs" / "WORKFLOW_RECIPES.md",
        PACKAGES_DIR / "INGESTION_MANIFEST.json",
    ]
    for path in required_files:
        assert path.is_file(), f"Missing documentation/config file: {path}"
        assert len(path.read_text(encoding="utf-8").strip()) > 200

    mcp_cfg = json.loads((MONOREPO_ROOT / "mcp_servers.config.json").read_text(encoding="utf-8"))
    assert "mcpServers" in mcp_cfg
    assert set(mcp_cfg["mcpServers"].keys()) == {
        "ianimation-3d",
        "adobe-animation-mcp",
        "after-effects-motion-engine",
        "stykanimate-mcp",
    }

    manifest = json.loads((PACKAGES_DIR / "INGESTION_MANIFEST.json").read_text(encoding="utf-8"))
    assert manifest["total_valid_files_copied"] > 2000
    assert len(manifest["packages"]) == 5


def test_path_traversal_protection() -> None:
    """_confine_to_root must reject paths escaping the monorepo root."""
    with pytest.raises(ValueError, match="Path traversal rejected"):
        _confine_to_root(MONOREPO_ROOT, "../outside_secret.txt")
