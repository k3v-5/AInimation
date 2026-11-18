"""
Tests for UAFConfig and 5-level ConfigResolver precedence.
Verifies DEFAULT -> PROJECT -> ENVIRONMENT -> RUNTIME -> OPERATION overriding.
UAF-81.0 Sections 34, 35.
"""

from uaf.core.configuration.uaf_config import UAFConfig
from uaf.core.configuration.precedence import ConfigResolver, deep_merge


def test_uaf_config_defaults():
    cfg = UAFConfig.create_default()
    assert cfg.execution["deterministic"] is True
    assert cfg.execution["seed"] == 42
    assert cfg.storage["backend"] == "FILESYSTEM"
    assert cfg.security["sandbox_paths"] is True


def test_deep_merge_preserves_unmodified_subkeys():
    base = {"execution": {"seed": 42, "retries": 3}, "storage": {"backend": "FS"}}
    override = {"execution": {"seed": 99}}
    merged = deep_merge(base, override)

    assert merged["execution"]["seed"] == 99
    assert merged["execution"]["retries"] == 3  # Unmodified preserved
    assert merged["storage"]["backend"] == "FS"


def test_five_level_precedence_resolution():
    default_layer = {
        "execution": {"seed": 1, "threads": 4},
        "storage": {"backend": "DEFAULT_FS"},
    }
    project_layer = {
        "execution": {"seed": 2},
        "storage": {"backend": "PROJECT_FS"},
    }
    env_layer = {
        "execution": {"seed": 3},
    }
    runtime_layer = {
        "execution": {"seed": 4},
    }
    op_layer = {
        "execution": {"seed": 5},
    }

    # Level 1: Default only
    c1 = ConfigResolver.resolve(default_cfg=default_layer)
    assert c1.execution["seed"] == 1
    assert c1.execution["threads"] == 4

    # Level 2: Project overrides Default
    c2 = ConfigResolver.resolve(default_cfg=default_layer, project_cfg=project_layer)
    assert c2.execution["seed"] == 2
    assert c2.storage["backend"] == "PROJECT_FS"

    # Level 3: Environment overrides Project
    c3 = ConfigResolver.resolve(default_cfg=default_layer, project_cfg=project_layer, environment_cfg=env_layer)
    assert c3.execution["seed"] == 3

    # Level 4: Runtime overrides Environment
    c4 = ConfigResolver.resolve(
        default_cfg=default_layer,
        project_cfg=project_layer,
        environment_cfg=env_layer,
        runtime_cfg=runtime_layer,
    )
    assert c4.execution["seed"] == 4

    # Level 5: Operation overrides Runtime (highest priority)
    c5 = ConfigResolver.resolve(
        default_cfg=default_layer,
        project_cfg=project_layer,
        environment_cfg=env_layer,
        runtime_cfg=runtime_layer,
        operation_cfg=op_layer,
    )
    assert c5.execution["seed"] == 5
    assert c5.execution["threads"] == 4  # Inherited all the way from default
