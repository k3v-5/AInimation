"""
UAF-81.101: Universal Unreal Engine 5 Studio Palette Generator.
Generates project-agnostic Python Editor Utility tools and Slate menus
for in-engine procedural generation control inside any UE5 project.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional

from uaf.engine_tools.core.contracts import (
    EnginePaletteManifest,
    ParameterType,
    StudioActionSpec,
    TargetEnvironment,
    ToolCategory,
    create_default_studio_actions,
)


class UE5StudioPaletteGenerator:
    """
    Generates standalone, dockable Python palette scripts for Unreal Engine 5 Editor.
    """

    def __init__(self) -> None:
        pass

    def generate_manifest(self, actions: Optional[List[StudioActionSpec]] = None) -> EnginePaletteManifest:
        """Creates a palette manifest filtering actions for Unreal Engine 5."""
        all_actions = actions if actions is not None else create_default_studio_actions()
        ue5_actions = [
            a for a in all_actions
            if a.target_environment in (TargetEnvironment.UNREAL_ENGINE_5, TargetEnvironment.UNIVERSAL)
        ]
        categories = list({a.category for a in ue5_actions})
        # Sort categories consistently
        categories.sort(key=lambda c: c.value)

        return EnginePaletteManifest(
            palette_id="ue5_aoe_palette",
            title="AOE Procedural Generation Palette",
            environment=TargetEnvironment.UNREAL_ENGINE_5,
            version="1.0.0",
            categories=categories,
            actions=ue5_actions,
            dock_area="Right",
            hotkey="Ctrl+Shift+A",
        )

    def generate_python_script(self, manifest: EnginePaletteManifest) -> str:
        """
        Synthesizes a complete, standalone Python Editor tool script for UE5.
        Runs inside Unreal Engine 5 via Python plugin or Project /Scripts.
        """
        manifest_json_str = json.dumps(manifest.model_dump(), indent=2)
        total_actions = len(manifest.actions)

        script_code = (
            f"# =============================================================================\n"
            f"# AOE In-Engine Studio Palette — Generated for Unreal Engine 5\n"
            f"# Platform: Universal Headless / Editor Utility Tool\n"
            f"# =============================================================================\n\n"
            f"import json\n"
            f"import urllib.request\n"
            f"import unreal\n\n"
            f"MANIFEST_DATA = {manifest_json_str}\n\n"
            f"class AOEStudioPaletteController:\n"
            f"    \"\"\"In-Engine Controller driving AOE procedural generation commands.\"\"\"\n\n"
            f"    def __init__(self, daemon_url='http://127.0.0.1:8765/rpc'):\n"
            f"        self.daemon_url = daemon_url\n"
            f"        self.cached_params = {{}}\n"
            f"        self._init_defaults()\n\n"
            f"    def _init_defaults(self):\n"
            f"        for action in MANIFEST_DATA.get('actions', []):\n"
            f"            act_id = action['action_id']\n"
            f"            self.cached_params[act_id] = {{}}\n"
            f"            for p in action.get('parameters', []):\n"
            f"                self.cached_params[act_id][p['param_id']] = p.get('default_value')\n\n"
            f"    def set_parameter(self, action_id, param_id, value):\n"
            f"        if action_id in self.cached_params:\n"
            f"            self.cached_params[action_id][param_id] = value\n"
            f"            unreal.log(f'[AOE] Updated param {{action_id}}.{{param_id}} = {{value}}')\n\n"
            f"    def execute_action(self, action_id):\n"
            f"        params = self.cached_params.get(action_id, {{}})\n"
            f"        unreal.log(f'[AOE] Executing {{action_id}} with parameters: {{params}}')\n"
            f"        try:\n"
            f"            # Direct in-engine Python dispatch if uaf package is available\n"
            f"            from uaf.engine_tools.dispatch.action_dispatcher import StudioActionDispatcher\n"
            f"            dispatcher = StudioActionDispatcher()\n"
            f"            result = dispatcher.dispatch(action_id, params)\n"
            f"            unreal.log(f'[AOE] {{action_id}} completed successfully: {{result.message}}')\n"
            f"            return result.output_data\n"
            f"        except ImportError:\n"
            f"            # Fallback to local RPC daemon\n"
            f"            return self._dispatch_rpc(action_id, params)\n"
            f"        except Exception as e:\n"
            f"            unreal.log_error(f'[AOE] Execution failed for {{action_id}}: {{str(e)}}')\n"
            f"            return None\n\n"
            f"    def _dispatch_rpc(self, action_id, params):\n"
            f"        payload = json.dumps({{'action_id': action_id, 'parameters': params}}).encode('utf-8')\n"
            f"        req = urllib.request.Request(self.daemon_url, data=payload, headers={{'Content-Type': 'application/json'}})\n"
            f"        try:\n"
            f"            with urllib.request.urlopen(req, timeout=3.0) as resp:\n"
            f"                data = json.loads(resp.read().decode('utf-8'))\n"
            f"                unreal.log(f'[AOE Daemon] Response: {{data}}')\n"
            f"                return data\n"
            f"        except Exception as err:\n"
            f"            unreal.log_warning(f'[AOE Daemon] RPC unavailable ({{err}}). Action {{action_id}} staged locally.')\n"
            f"            return {{'status': 'staged_locally', 'action_id': action_id}}\n\n"
            f"def register_palette_menu():\n"
            f"    \"\"\"Registers AOE Palette in the Unreal Editor Level Editor Window menu.\"\"\"\n"
            f"    menus = unreal.ToolMenus.get()\n"
            f"    main_menu = menus.find_menu('LevelEditor.MainMenu.Window')\n"
            f"    if not main_menu:\n"
            f"        unreal.log_warning('[AOE] Could not find LevelEditor.MainMenu.Window')\n"
            f"        return\n\n"
            f"    entry = unreal.ToolMenuEntry(\n"
            f"        name='AOE_Studio_Palette',\n"
            f"        type=unreal.MultiBlockType.MENU_ENTRY,\n"
            f"        insert_position=unreal.ToolMenuInsert('', unreal.ToolMenuInsertType.DEFAULT)\n"
            f"    )\n"
            f"    entry.set_label('AOE Procedural Generation Palette')\n"
            f"    entry.set_tool_tip('Open the Universal AOE Procedural Generation in-engine controller')\n"
            f"    entry.set_string_command(\n"
            f"        unreal.ToolMenuStringCommandType.PYTHON,\n"
            f"        '',\n"
            f"        'import aoe_ue5_palette; aoe_ue5_palette.open_palette_window()'\n"
            f"    )\n"
            f"    main_menu.add_menu_entry('WindowLayout', entry)\n"
            f"    menus.refresh_all_widgets()\n"
            f"    unreal.log('[AOE] Registered AOE Procedural Palette in Editor Window Menu.')\n\n"
            f"def open_palette_window():\n"
            f"    controller = AOEStudioPaletteController()\n"
            f"    msg = 'AOE In-Engine Studio Palette Active! Available Actions: {total_actions}'\n"
            f"    unreal.EditorDialog.show_message('AOE Studio', msg, unreal.AppMsgType.OK)\n\n"
            f"if __name__ == '__main__':\n"
            f"    register_palette_menu()\n"
        )
        return script_code

    def export_tool(self, output_dir: Path, manifest: Optional[EnginePaletteManifest] = None) -> Dict[str, Path]:
        """Exports the UE5 Python palette script and JSON manifest."""
        output_dir.mkdir(parents=True, exist_ok=True)
        m = manifest if manifest is not None else self.generate_manifest()

        manifest_path = output_dir / "ue5_palette_manifest.json"
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(m.model_dump(), f, indent=2)

        script_path = output_dir / "aoe_ue5_palette.py"
        script_content = self.generate_python_script(m)
        with open(script_path, "w", encoding="utf-8") as f:
            f.write(script_content)

        return {
            "manifest": manifest_path,
            "script": script_path,
        }
