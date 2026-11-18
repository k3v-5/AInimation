"""
Tests for ProjectContext, PathResolver, and PathSecurity.
Verifies drive independence, sandboxing, and dynamic root resolution.
UAF-81.0 Sections 6, 7, 8, 47.
"""

import os
import tempfile
import pytest
from pathlib import Path
from uaf.core.context.project_context import ProjectContext
from uaf.core.context.resource_budget import ResourceBudget
from uaf.core.context.execution_context import ExecutionContext
from uaf.core.paths.path_resolver import UAFPathResolver
from uaf.core.paths.security import PathSecurityValidator, PathSecurityViolation


def test_project_context_defaults():
    with tempfile.TemporaryDirectory() as tmp:
        p_root = Path(tmp) / "custom_proj"
        ctx = ProjectContext(project_id="test_proj", project_root=p_root)

        assert ctx.project_root == p_root.resolve()
        assert ctx.workspace_root == (p_root / "workspace").resolve()
        assert ctx.artifact_root == (p_root / "artifacts").resolve()
        assert ctx.cache_root == (p_root / ".cache").resolve()

        ctx.ensure_directories()
        assert ctx.artifact_root.exists()
        assert ctx.cache_root.exists()


def test_project_context_serialization():
    with tempfile.TemporaryDirectory() as tmp:
        ctx = ProjectContext(project_id="ser_proj", project_root=Path(tmp))
        data = ctx.to_dict()
        reconstructed = ProjectContext.from_dict(data)

        assert reconstructed.project_id == "ser_proj"
        assert reconstructed.project_root == ctx.project_root


def test_path_resolver_valid_roots():
    with tempfile.TemporaryDirectory() as tmp:
        ctx = ProjectContext(project_id="p1", project_root=Path(tmp))
        resolver = UAFPathResolver(ctx)

        art_path = resolver.resolve_artifact_path("textures/albedo.png")
        assert art_path == (ctx.artifact_root / "textures/albedo.png").resolve()

        cache_path = resolver.resolve_cache_path("cache_entry.json")
        assert cache_path == (ctx.cache_root / "cache_entry.json").resolve()


def test_path_security_traversal_rejection():
    with tempfile.TemporaryDirectory() as tmp:
        ctx = ProjectContext(project_id="p1", project_root=Path(tmp))
        resolver = UAFPathResolver(ctx)

        with pytest.raises(PathSecurityViolation, match="traversal"):
            resolver.resolve_artifact_path("../outside.txt")

        with pytest.raises(PathSecurityViolation, match="traversal"):
            resolver.resolve_artifact_path("sub/../../escape.txt")


def test_path_security_escape_rejection():
    with tempfile.TemporaryDirectory() as tmp:
        ctx = ProjectContext(project_id="p1", project_root=Path(tmp))
        # Attempt to access arbitrary external folder
        outside_path = Path(tempfile.gettempdir()) / "random_file.txt"
        with pytest.raises(PathSecurityViolation):
            PathSecurityValidator.validate_confined_to_root(outside_path, ctx.artifact_root)


def test_execution_context_immutability():
    with tempfile.TemporaryDirectory() as tmp:
        p_ctx = ProjectContext(project_id="p1", project_root=Path(tmp))
        budget = ResourceBudget(max_duration_seconds=60.0)
        e_ctx = ExecutionContext(
            production_id="prod_01",
            operation_id="op_01",
            asset_id="asset_hero",
            project_context=p_ctx,
            seed=12345,
            resource_budget=budget,
        )

        assert e_ctx.seed == 12345
        assert e_ctx.resource_budget.max_duration_seconds == 60.0

        with pytest.raises(AttributeError):
            e_ctx.seed = 99999  # Frozen dataclass


def test_portability_across_different_roots():
    """Verify that multiple arbitrary roots behave consistently without fixed drive assumptions."""
    roots = ["sandbox_alpha", "sandbox_beta", "sandbox_gamma"]
    with tempfile.TemporaryDirectory() as base_tmp:
        for r_name in roots:
            proj_dir = Path(base_tmp) / r_name
            ctx = ProjectContext(project_id=r_name, project_root=proj_dir)
            ctx.ensure_directories()
            resolver = UAFPathResolver(ctx)

            target = resolver.resolve_output_path("model.gltf")
            assert target.is_relative_to(ctx.output_root)
