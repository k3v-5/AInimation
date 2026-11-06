"""
Render Authentic Red Raven Flight Animation Directly with Blender 5.2.0 LTS.

Constructs:
1. Multi-component anatomical assembly: Torso, Ventral Wing, Dorsal Wing, and Branch prop.
2. Full PBR Shader Materials in Blender (Albedo, Tangent Normal, Roughness, AO).
3. Avian Armature: Root, Spine, Head, Tail, 3-Bone Wing chains.
4. Aerodynamic flapping action in 3D with phase wave propagation.
5. 3-Point studio lighting rig (Key, Fill, Rim) and 55mm portrait camera.
6. Blender EEVEE 3D rendering generating authentic .blend, .glb, .mp4, and .gif.

100% Zero-Any compliant with strict typing and Pydantic v2.
"""

from __future__ import annotations

from pathlib import Path
import shutil
import sys
import time

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.blender.rigging import BlenderRigger


def main() -> None:
    print("=================================================================")
    print("   IANIMATION - RED RAVEN NATIVE BLENDER 5.2 RENDERER            ")
    print("=================================================================")
    start_total = time.time()

    rigger = BlenderRigger()
    print(f"Blender Binary: {rigger.blender_bin}")
    if not rigger.health_check():
        raise RuntimeError(f"Blender binary not healthy or not found at {rigger.blender_bin}")
    print("Blender 5.2.0 LTS Health Check: PASS")

    comp_dir = PROJECT_ROOT / "outputs" / "component_rig_refined"
    renders_dir = PROJECT_ROOT / "outputs" / "renders"
    scenes_dir = PROJECT_ROOT / "outputs" / "scenes"
    renders_dir.mkdir(parents=True, exist_ok=True)
    scenes_dir.mkdir(parents=True, exist_ok=True)

    torso_obj = comp_dir / "subject_torso.obj"
    wing_v_obj = comp_dir / "subject_wing_ventral.obj"
    wing_d_obj = comp_dir / "subject_wing_dorsal.obj"
    branch_obj = comp_dir / "prop_branch.obj"

    components = [
        {
            "name": "Subject_Torso",
            "role": "torso",
            "mesh_path": str(torso_obj.resolve()),
            "pivot_point": [0.0, 0.0, 0.0],
            "z_offset": 0.0,
            "parent_bone": "Spine",
            "is_prop": False,
            "albedo_path": str((comp_dir / "subject_torso_albedo.png").resolve()),
            "normal_path": str((comp_dir / "subject_torso_normal.png").resolve()),
        },
        {
            "name": "Subject_Wing_Ventral",
            "role": "wing_ventral",
            "mesh_path": str(wing_v_obj.resolve()),
            "pivot_point": [-0.3967, 0.4542, 0.16],
            "z_offset": 0.16,
            "parent_bone": "Wing_Shoulder_L",
            "is_prop": False,
            "albedo_path": str((comp_dir / "subject_wing_ventral_albedo.png").resolve()),
            "normal_path": str((comp_dir / "subject_wing_ventral_normal.png").resolve()),
        },
        {
            "name": "Subject_Wing_Dorsal",
            "role": "wing_dorsal",
            "mesh_path": str(wing_d_obj.resolve()),
            "pivot_point": [-0.2767, 0.4542, -0.10],
            "z_offset": -0.10,
            "parent_bone": "Wing_Shoulder_R",
            "is_prop": False,
            "albedo_path": str((comp_dir / "subject_wing_dorsal_albedo.png").resolve()),
            "normal_path": str((comp_dir / "subject_wing_dorsal_normal.png").resolve()),
        },
        {
            "name": "Prop_Branch",
            "role": "branch",
            "mesh_path": str(branch_obj.resolve()),
            "pivot_point": [0.0, 0.0, 0.0],
            "z_offset": 0.0,
            "parent_bone": "",
            "is_prop": True,
            "albedo_path": str((comp_dir / "prop_branch_albedo.png").resolve()),
            "normal_path": str((comp_dir / "prop_branch_normal.png").resolve()),
        },
    ]

    out_blend = scenes_dir / "raven_flight_blender_master.blend"
    out_glb = scenes_dir / "raven_flight_blender_master.glb"
    out_video = renders_dir / "raven_flight_blender_master.mp4"
    out_gif = renders_dir / "raven_flight_blender_master.gif"

    print("\nExecuting multi-component 3D rigging and 360-degree turntable flight rendering inside Blender...")
    res = rigger.rig_multi_component_scene(
        components=components,
        output_blend=str(out_blend),
        output_glb=str(out_glb),
        output_video=str(out_video),
        fps=24,
        total_frames=72,  # 3.0 seconds: 3 complete flap cycles + exactly 1 full 360-degree seamless turn
        samples=16,
        render_engine="BLENDER_EEVEE",
        rotate_360=True,
        elevate_flight=True,
    )

    if not res.success:
        print(f"\n[ERROR] Blender execution failed: {res.message}")
        sys.exit(1)

    print("\n[SUCCESS] Blender Multi-Component 3D Render Complete!")
    print(f"  * Bone Count: {res.bone_count} (Hierarchy: {', '.join(res.hierarchy)})")
    print(f"  * Blend Scene File: {out_blend} ({out_blend.stat().st_size:,} bytes)")
    if out_glb.exists():
        print(f"  * Rigged 3D GLB: {out_glb} ({out_glb.stat().st_size:,} bytes)")
    if out_video.exists():
        print(f"  * Master Video MP4: {out_video} ({out_video.stat().st_size:,} bytes)")
    if out_gif.exists():
        print(f"  * Web Preview GIF: {out_gif} ({out_gif.stat().st_size:,} bytes)")

    # Copy to artifacts directory so user can preview directly in chat
    artifacts_dir = Path(r"C:\Users\sasuk\.gemini\antigravity\brain\25a9dd69-1a8e-409b-85e3-41655796e664")
    if out_video.exists():
        shutil.copy2(out_video, artifacts_dir / "raven_flight_blender_master.mp4")
    if out_gif.exists():
        shutil.copy2(out_gif, artifacts_dir / "raven_flight_blender_master.gif")
    if out_glb.exists():
        shutil.copy2(out_glb, artifacts_dir / "raven_flight_blender_master.glb")
    if out_blend.exists():
        shutil.copy2(out_blend, artifacts_dir / "raven_flight_blender_master.blend")

    total_time = round(time.time() - start_total, 2)
    print(f"\nCompleted in {total_time}s with native Blender 3D engine.")


if __name__ == "__main__":
    main()
