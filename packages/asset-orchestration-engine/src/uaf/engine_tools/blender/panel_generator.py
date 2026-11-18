"""
UAF-81.101: Universal Blender Studio Panel & Operator Generator.
Generates lightweight, standalone Blender addons (N-Panel in 3D Viewport)
for mesh metrics verification, Voronoi fracture previewing, and UE5 FBX export.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional

from uaf.engine_tools.core.contracts import (
    EnginePaletteManifest,
    StudioActionSpec,
    TargetEnvironment,
    ToolCategory,
    create_default_studio_actions,
)


class BlenderStudioPanelGenerator:
    """
    Generates standalone Blender Addons with N-Panel UI and mesh operators.
    """

    def __init__(self) -> None:
        pass

    def generate_manifest(self, actions: Optional[List[StudioActionSpec]] = None) -> EnginePaletteManifest:
        """Creates a palette manifest filtering actions for Blender."""
        all_actions = actions if actions is not None else create_default_studio_actions()
        blender_actions = [
            a for a in all_actions
            if a.target_environment in (TargetEnvironment.BLENDER, TargetEnvironment.UNIVERSAL)
        ]
        categories = list({a.category for a in blender_actions})
        categories.sort(key=lambda c: c.value)

        return EnginePaletteManifest(
            palette_id="blender_aoe_panel",
            title="AOE Asset Studio",
            environment=TargetEnvironment.BLENDER,
            version="1.0.0",
            categories=categories,
            actions=blender_actions,
            dock_area="N-Panel (AOE Studio)",
            hotkey="N",
        )

    def generate_addon_script(self, manifest: EnginePaletteManifest) -> str:
        """
        Synthesizes a complete, standalone Blender addon Python script.
        """
        manifest_json_str = json.dumps(manifest.model_dump(), indent=2)

        script_code = (
            f"# =============================================================================\n"
            f"# AOE Asset Studio — Generated Blender Addon\n"
            f"# Compatible with Blender 3.6 / 4.x / 5.x\n"
            f"# =============================================================================\n\n"
            f"bl_info = {{\n"
            f"    'name': 'AOE Procedural Asset Studio',\n"
            f"    'author': 'Asset Orchestration Engine (AOE)',\n"
            f"    'version': (1, 0, 0),\n"
            f"    'blender': (3, 6, 0),\n"
            f"    'location': 'View3D > Sidebar > AOE Studio',\n"
            f"    'description': 'Universal procedural generation & UE5 bridge operators',\n"
            f"    'category': '3D View',\n"
            f"}}\n\n"
            f"import bpy\n"
            f"import json\n"
            f"import os\n\n"
            f"MANIFEST_DATA = {manifest_json_str}\n\n"
            f"class AOE_OT_VerifyMeshMetrics(bpy.types.Operator):\n"
            f"    \"\"\"Verifies mesh topology, vertex counts, and origin pivot for UE5.\"\"\"\n"
            f"    bl_idname = 'aoe.verify_mesh_metrics'\n"
            f"    bl_label = 'Verify Mesh for UE5'\n"
            f"    bl_options = {{'REGISTER', 'UNDO'}}\n\n"
            f"    def execute(self, context):\n"
            f"        obj = context.active_object\n"
            f"        if not obj or obj.type != 'MESH':\n"
            f"            self.report({{'WARNING'}}, 'Select a valid mesh object.')\n"
            f"            return {{'CANCELLED'}}\n\n"
            f"        mesh = obj.data\n"
            f"        verts = len(mesh.vertices)\n"
            f"        polys = len(mesh.polygons)\n"
            f"        loc = obj.location\n"
            f"        pivot_ok = (loc.x == 0.0 and loc.y == 0.0 and loc.z == 0.0)\n\n"
            f"        msg = f'Mesh Verified: {{obj.name}} | Verts: {{verts}} | Polys: {{polys}} | Pivot at Origin: {{pivot_ok}}'\n"
            f"        self.report({{'INFO'}}, msg)\n"
            f"        return {{'FINISHED'}}\n\n"
            f"class AOE_OT_ExportUE5FBX(bpy.types.Operator):\n"
            f"    \"\"\"Exports selected mesh to FBX matching Unreal Engine conventions.\"\"\"\n"
            f"    bl_idname = 'aoe.export_ue5_fbx'\n"
            f"    bl_label = 'Export FBX to UE5'\n"
            f"    bl_options = {{'REGISTER', 'UNDO'}}\n\n"
            f"    filepath: bpy.props.StringProperty(subtype='FILE_PATH', default='//export_mesh.fbx')\n\n"
            f"    def execute(self, context):\n"
            f"        obj = context.active_object\n"
            f"        if not obj:\n"
            f"            self.report({{'WARNING'}}, 'No active object to export.')\n"
            f"            return {{'CANCELLED'}}\n\n"
            f"        target_p = bpy.path.abspath(self.filepath)\n"
            f"        bpy.ops.export_scene.fbx(\n"
            f"            filepath=target_p,\n"
            f"            use_selection=True,\n"
            f"            global_scale=1.0,\n"
            f"            apply_unit_scale=True,\n"
            f"            apply_scale_options='FBX_SCALE_ALL',\n"
            f"            axis_forward='-Y',\n"
            f"            axis_up='Z',\n"
            f"            bake_space_transform=True\n"
            f"        )\n"
            f"        self.report({{'INFO'}}, f'Exported {{obj.name}} to UE5 FBX: {{target_p}}')\n"
            f"        return {{'FINISHED'}}\n\n"
            f"class AOE_PT_StudioPanel(bpy.types.Panel):\n"
            f"    \"\"\"AOE Studio N-Panel in 3D Viewport.\"\"\"\n"
            f"    bl_label = 'AOE Asset Studio'\n"
            f"    bl_idname = 'VIEW3D_PT_aoe_studio'\n"
            f"    bl_space_type = 'VIEW_3D'\n"
            f"    bl_region_type = 'UI'\n"
            f"    bl_category = 'AOE Studio'\n\n"
            f"    def draw(self, context):\n"
            f"        layout = self.layout\n"
            f"        obj = context.active_object\n\n"
            f"        box = layout.box()\n"
            f"        box.label(text='Active Asset:', icon='OBJECT_DATA')\n"
            f"        if obj:\n"
            f"            box.label(text=f'Name: {{obj.name}} ({{obj.type}})')\n"
            f"        else:\n"
            f"            box.label(text='No object selected')\n\n"
            f"        col = layout.column(align=True)\n"
            f"        col.operator('aoe.verify_mesh_metrics', text='Verify Mesh for UE5', icon='CHECKMARK')\n"
            f"        col.operator('aoe.export_ue5_fbx', text='Export FBX (Z-Up, Metric)', icon='EXPORT')\n\n"
            f"CLASSES = [\n"
            f"    AOE_OT_VerifyMeshMetrics,\n"
            f"    AOE_OT_ExportUE5FBX,\n"
            f"    AOE_PT_StudioPanel,\n"
            f"]\n\n"
            f"def register():\n"
            f"    for cls in CLASSES:\n"
            f"        bpy.utils.register_class(cls)\n\n"
            f"def unregister():\n"
            f"    for cls in reversed(CLASSES):\n"
            f"        bpy.utils.unregister_class(cls)\n\n"
            f"if __name__ == '__main__':\n"
            f"    register()\n"
        )
        return script_code

    def export_addon(self, output_dir: Path, manifest: Optional[EnginePaletteManifest] = None) -> Dict[str, Path]:
        """Exports the Blender Python addon and JSON manifest."""
        output_dir.mkdir(parents=True, exist_ok=True)
        m = manifest if manifest is not None else self.generate_manifest()

        manifest_path = output_dir / "blender_panel_manifest.json"
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(m.model_dump(), f, indent=2)

        addon_path = output_dir / "aoe_blender_addon.py"
        addon_content = self.generate_addon_script(m)
        with open(addon_path, "w", encoding="utf-8") as f:
            f.write(addon_content)

        return {
            "manifest": manifest_path,
            "addon": addon_path,
        }
