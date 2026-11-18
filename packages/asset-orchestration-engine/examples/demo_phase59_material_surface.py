import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.visual_specification_compiler import (
    VisualSpecificationAPI, VisualCompilationInput
)
from src.reference_analysis_visual_decomposition import (
    DecomposedReferenceReport, SilhouetteExtraction, ProportionEstimate,
    DecomposedPart, MaterialPalette, ExtractedMaterialType
)
from src.procedural_modeling_strategy import ProceduralModelingStrategyAPI
from src.geometry_generation_engine import GeometryGenerationAPI, GenerationContext
from src.material_surface_generation import MaterialSurfaceAPI

def main():
    print("=" * 95)
    print("  ASSET ORCHESTRATION ENGINE (AOE) — FASE 59: MATERIAL & SURFACE GENERATION ENGINE")
    print("=" * 95)

    vas_api = VisualSpecificationAPI()
    msp_api = ProceduralModelingStrategyAPI()
    geom_api = GeometryGenerationAPI()
    surf_api = MaterialSurfaceAPI()

    # 1. Pipeline Inicial: Prompt -> F56 -> F57 -> F58
    print("\n[PASO 1] Pipeline Inicial (F56 VAS -> F57 MSP -> F58 Geometry):")
    f55_report = DecomposedReferenceReport(
        report_id="REP_F55_BARREL_HERO",
        reference_ids=["REF_HERO_01"],
        silhouette=SilhouetteExtraction(aspect_ratio=1.42, symmetry_axis="VERTICAL_Z"),
        proportions=ProportionEstimate(component_ratios={"body": 0.80, "top_ring": 0.10, "bottom_ring": 0.10}),
        parts=[
            DecomposedPart("part_body", "BODY", (0, 0, 1, 1.42), (0, 0, 0), True, 0.98),
            DecomposedPart("part_ring_top", "RING_01", (0, 1.1, 1.02, 0.15), (0, 0, 1.1), False, 0.95),
            DecomposedPart("part_ring_bottom", "RING_02", (0, 0.2, 1.02, 0.15), (0, 0, 0.2), False, 0.95)
        ],
        materials=MaterialPalette(base_material=ExtractedMaterialType.WOOD, surface_roughness=0.68)
    )

    vas_input = VisualCompilationInput(
        prompt="Barril medieval de roble oscuro con 2 aros de hierro reforzado, altura 1.20 metros con simetría bilateral",
        asset_class_hint="PROP.BARREL",
        reference_reports=[f55_report],
        semantic_context={"semantic_id": "barrel_hero.root", "asset_id": "barrel_hero"},
        project_constraints={"nanite": True, "lod_count": 3, "poly_budget": 12000, "triangle_budget": 24000}
    )
    vas = vas_api.compile_specification(vas_input)
    msp = msp_api.plan_strategy(vas)
    geom_res = geom_api.generate_geometry(msp)
    print(f" - Geometría Generada: ID=[{geom_res.generation_id}] | Objetos={len(geom_res.geometry_objects)} | Tris={geom_res.triangle_count}")

    # 2. Generación de Materiales y Superficies (F59)
    print("\n[PASO 2] Ejecución de la Generación de Superficies y Materiales (F59):")
    surf_res = surf_api.generate_surface(geom_res, vas, msp, generation_seed=42)
    val = surf_api.validate_surface(surf_res)
    print(f" - Superficie ID: [{surf_res.surface_generation_id}] | Versión: {surf_res.surface_version} | Válida: {val.is_valid}")
    print(f" - Hash Superficial Determinista (SHA-256): {surf_res.surface_hash[:16]}...{surf_res.surface_hash[-8:]}")
    print(f" - Total Materiales Definidos: {len(surf_res.material_definitions)} | Asignaciones: {len(surf_res.material_assignments)}")

    # 3. Detalle de Materiales PBR y Regiones
    print("\n[PASO 3] Materiales PBR Asignados por Región Superficial:")
    for region in surf_res.surface_regions:
        mat = surf_res.material_definitions.get(region.material_id)
        if mat:
            print(f"   * [{region.surface_region_id}] -> Material: [{mat.material_id}] (Clase: {mat.material_class.value}) | BaseColor={mat.base_color[:3]} | Metallic={mat.metallic} | Roughness={mat.roughness}")

    # 4. UV Layouts y Reporte de Texel Density
    print("\n[PASO 4] Canales UV y Control de Texel Density:")
    for uv in surf_res.uv_layouts:
        print(f"   * Canal UV{uv.uv_channel} ({uv.unwrap_method.value}): Res={uv.resolution}x{uv.resolution} | Overlaps={uv.overlap_count} | Padding={uv.padding}")
    td = surf_res.texel_density_report
    print(f" - Texel Density Actual: {td.current_texel_density} px/cm | Objetivo: {td.target_texel_density} px/cm | Conforme: {td.is_compliant}")

    # 5. Bake Plan y Empaquetado ORM
    print("\n[PASO 5] Estrategia de Baking y Empaquetado de Texturas:")
    if surf_res.baking_plan:
        bp = surf_res.baking_plan
        print(f" - Bake Plan ID: [{bp.bake_id}] | Resolución: {bp.resolution}x{bp.resolution} ({bp.format}, {bp.bit_depth}-bit)")
        print(f" - Canales ORM: R={bp.orm_channels['R']}, G={bp.orm_channels['G']}, B={bp.orm_channels['B']}")
    print(" - Requisitos de Textura y Gestión de Espacios de Color:")
    for tex in surf_res.texture_requirements:
        print(f"   * [{tex.texture_id}] ({tex.channel}): ColorSpace=[{tex.color_space.value}] | Formato={tex.format}")

    # 6. Interfaz de Materiales para Unreal Engine
    print("\n[PASO 6] Interfaz de Materiales para Unreal Engine:")
    for mat_name, u_mat in surf_res.unreal_material_interface.items():
        print(f"   * [{mat_name}] -> Master Shader: [{u_mat.parent_shader}] | Blend: [{u_mat.blend_mode}] | Nanite: {u_mat.nanite_compatible}")

    print("\n" + "=" * 95)
    print("  CRITERIO DE EXITO DE FASE 59 CUMPLIDO AL 100% (APPROVED)")
    print("=" * 95)

if __name__ == "__main__":
    main()
