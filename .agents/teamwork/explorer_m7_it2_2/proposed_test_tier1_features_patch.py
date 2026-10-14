# Proposed replacement for tests/e2e/test_tier1_features.py
# Replaces facade assertions in test_f_ui_07 and test_f_doc_01

from pathlib import Path
import pytest


@pytest.mark.tier1
def test_f_ui_07_intermediate_asset_cards() -> None:
    """F-UI-07: Intermediate asset cards (stems, 3D mesh, mocap clip, rendered video)."""
    project_root = Path(__file__).resolve().parent.parent.parent
    copilot_chat = project_root / "src" / "components" / "copilot" / "CopilotChat.tsx"
    asset_card = project_root / "src" / "components" / "copilot" / "IntermediateAssetCard.tsx"
    types_file = project_root / "src" / "types" / "index.ts"

    assert copilot_chat.is_file(), "CopilotChat.tsx must exist"
    assert asset_card.is_file(), "IntermediateAssetCard.tsx must exist"
    assert types_file.is_file(), "src/types/index.ts must exist"

    # Verify types declare output_preview
    types_content = types_file.read_text(encoding="utf-8")
    assert "output_preview" in types_content, "PlanStepSchema must declare output_preview"

    # Verify CopilotChat imports and renders IntermediateAssetCard
    chat_content = copilot_chat.read_text(encoding="utf-8")
    assert "IntermediateAssetCard" in chat_content, "CopilotChat must integrate IntermediateAssetCard"
    assert "output_preview" in chat_content, "CopilotChat must pass output_preview to asset cards"

    # Verify IntermediateAssetCard renders all 5 required asset card domains
    card_content = asset_card.read_text(encoding="utf-8")
    assert "analyze_audio" in card_content and "stems" in card_content.lower(), "Must render audio stems card"
    assert "image_to_3d" in card_content and ("glb" in card_content.lower() or "mesh" in card_content.lower()), "Must render 3D mesh card"
    assert "auto_rig" in card_content and ("ue5_mannequin" in card_content or "huesos" in card_content), "Must render auto-rig card"
    assert "extract_mocap" in card_content and ("mocap" in card_content.lower() or "gvhmr" in card_content.lower()), "Must render mocap clip card"
    assert "render_video" in card_content and ("mrq" in card_content.lower() or "video" in card_content.lower()), "Must render rendered video card"


@pytest.mark.tier1
def test_f_doc_01_documentation_completeness() -> None:
    """F-DOC-01: Comprehensive README.md and MCP tool documentation catalog."""
    project_root = Path(__file__).resolve().parent.parent.parent
    readme_path = project_root / "README.md"
    assert readme_path.is_file(), "README.md must exist"

    content = readme_path.read_text(encoding="utf-8")

    # 1. Verify all 6 FastMCP atomic tools are cataloged
    tools = [
        "analyze_audio",
        "image_to_3d",
        "auto_rig",
        "extract_mocap",
        "build_ue5_scene",
        "render_video",
    ]
    for tool in tools:
        assert tool in content, f"Tool '{tool}' must be documented in README.md"

    # 2. Verify JSON Schema specifications are present
    assert "$schema" in content or "JSON Schema" in content, "Must include JSON Schema specifications"
    assert "properties" in content, "Must document tool input properties schema"

    # 3. Verify JSON-RPC 2.0 invocation request and response examples
    assert "jsonrpc" in content and "2.0" in content, "Must include JSON-RPC 2.0 invocation examples"
    assert "tools/call" in content, "Must document tools/call MCP invocation method"

    # 4. Verify environment variables table
    env_vars = [
        "FAL_KEY",
        "TRIPO_API_KEY",
        "REPLICATE_API_TOKEN",
        "CAS_CACHE_DIR",
        "UE5_REMOTE_REST_PORT",
        "UE5_REMOTE_WS_PORT",
        "LOG_LEVEL",
    ]
    for var in env_vars:
        assert var in content, f"Environment variable '{var}' must be documented in README.md"

    # 5. Verify default network ports table
    ports = ["30010", "30020", "8888", "5173"]
    for port in ports:
        assert port in content, f"Network port '{port}' must be documented in README.md"
