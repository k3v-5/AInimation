import time
from typing import Dict, Any, List, Optional, Tuple
from ..core.surface_types import (
    SurfaceTypeTag, ShaderModelType, ColorSpaceType,
    UVUnwrapMethod, BakeChannelType, AttributeSemanticName,
    InvalidationState, SurfaceValidationSeverity
)
from ..core.surface_schema import (
    SurfaceRegion, MaterialDefinition, ShaderGraphSpec,
    MaterialAssignment, UVLayout, TexelDensityReport,
    VertexAttributeSpec, TextureRequirement, BakePlan,
    UnrealMaterialInterface, GeneratedSurfaceResult,
    SurfaceValidationResult
)
from ..library.material_library import MaterialLibrary
from ..uv.uv_generator import UVGenerator
from ..shaders.shader_graph_builder import ShaderGraphBuilder
from ..engine.baking_planner import BakingPlanner
from ..engine.surface_invalidation_tracker import SurfaceInvalidationTracker
from ..engine.surface_hasher import SurfaceHasher

class MaterialSurfaceGenerationEngine:
    """
    Material & Surface Generation Engine (AOE v59)
    
    Regla Fundamental:
    GENERA MATERIALES PBR, ASIGNACIONES SUPERFICIALES, UVs, TEXEL DENSITY Y PLANES DE BAKING
    SIN IMPORTAR DIRECTAMENTE BPY NI DEPENDER DE MCP DIRECTO.
    """
    def __init__(self, engine_version: str = "1.0.0"):
        self.engine_version = engine_version
        self.library = MaterialLibrary()

    def generate(
        self,
        geometry: Any, # GeneratedGeometryResult from F58
        specification: Optional[Any] = None, # VisualAssetSpecification from F56
        strategy: Optional[Any] = None, # ModelingStrategyPlan from F57
        generation_seed: int = 42
    ) -> GeneratedSurfaceResult:
        sem_id = getattr(geometry, "semantic_id", "asset.root")
        geom_id = getattr(geometry, "generation_id", "GEN_DEFAULT")
        surf_id = f"SURF_{geom_id.replace('GEN_', '')}"

        # 1. Identificación y Creación de Regiones y Materiales
        material_defs: Dict[str, MaterialDefinition] = {}
        assignments: List[MaterialAssignment] = []
        regions: List[SurfaceRegion] = []
        shader_graphs: Dict[str, ShaderGraphSpec] = {}
        unreal_interfaces: Dict[str, UnrealMaterialInterface] = {}

        geom_objs = getattr(geometry, "geometry_objects", [])
        if not geom_objs:
            # Fallback objeto principal si está vacío
            geom_objs = []

        for obj in geom_objs:
            comp_id = getattr(obj, "semantic_component_id", "comp_main")
            obj_name = getattr(obj, "name", "").lower()
            # Determinar tipo de material según componente y contexto semántico
            if "blade" in comp_id.lower() or "metal" in comp_id.lower() or "ring" in comp_id.lower() or "iron" in comp_id.lower() or "sword" in sem_id.lower():
                surf_type = SurfaceTypeTag.METAL
                mat_def = self.library.resolve_or_create(SurfaceTypeTag.METAL, {"roughness": 0.25, "metallic": 0.95})
            elif "wood" in comp_id.lower() or "body" in comp_id.lower() or "part_body" in comp_id.lower() or "barrel" in sem_id.lower() or "wood" in sem_id.lower():
                surf_type = SurfaceTypeTag.WOOD
                mat_def = self.library.resolve_or_create(SurfaceTypeTag.WOOD, {"roughness": 0.65, "metallic": 0.0})
            else:
                surf_type = SurfaceTypeTag.STONE
                mat_def = self.library.resolve_or_create(SurfaceTypeTag.STONE, {"roughness": 0.80, "metallic": 0.0})

            material_defs[mat_def.material_id] = mat_def
            
            region_id = f"REGION_{comp_id.upper()}"
            region = SurfaceRegion(
                surface_region_id=region_id,
                semantic_id=sem_id,
                component_id=comp_id,
                material_id=mat_def.material_id,
                surface_type=surf_type
            )
            regions.append(region)

            assignment = MaterialAssignment(
                surface_region_id=region_id,
                object_id=getattr(obj, "object_id", f"OBJ_{comp_id.upper()}"),
                material_id=mat_def.material_id,
                face_selection_mode="MATERIAL_SLOT"
            )
            assignments.append(assignment)

            # Shader Graph
            if mat_def.material_id not in shader_graphs:
                shader_graphs[mat_def.material_id] = ShaderGraphBuilder.build_pbr_shader_graph(mat_def)

            # Unreal Material Interface
            if mat_def.material_id not in unreal_interfaces:
                unreal_interfaces[mat_def.material_id] = UnrealMaterialInterface(
                    material_name=mat_def.material_id,
                    parent_shader="/Engine/MasterMaterials/M_PBR_Master",
                    parameters={"Roughness": mat_def.roughness, "Metallic": mat_def.metallic},
                    textures={
                        "BaseColor": f"T_{sem_id}_BaseColor",
                        "Normal": f"T_{sem_id}_Normal",
                        "ORM": f"T_{sem_id}_ORM"
                    }
                )

        # 2. Generación de UVs y Texel Density
        dims = getattr(geometry, "dimensions", {"x": 1.0, "y": 1.0, "z": 1.0})
        uv_layouts, texel_report = UVGenerator.generate_uv_layouts(dims)

        # 3. Atributos de Vértices y Máscaras
        vertex_attributes = [
            VertexAttributeSpec("AO", "RGB", AttributeSemanticName.AO, (0.0, 1.0)),
            VertexAttributeSpec("WEAR", "RGB", AttributeSemanticName.WEAR, (0.0, 1.0)),
            VertexAttributeSpec("DAMAGE", "A", AttributeSemanticName.DAMAGE, (0.0, 1.0))
        ]

        # 4. Baking Plan y Requisitos de Textura
        bake_plan, tex_reqs = BakingPlanner.generate_bake_and_texture_requirements(sem_id)

        # 5. Cálculo de Hash Lógico de Superficie
        surf_hash = SurfaceHasher.compute_surface_hash(
            materials=material_defs,
            assignments=assignments,
            uv_layouts=uv_layouts,
            attributes=vertex_attributes,
            surface_version=self.engine_version
        )

        trace = [
            {"step": "GENERATE_MATERIALS", "count": len(material_defs), "status": "SUCCESS"},
            {"step": "ASSIGN_SURFACES", "count": len(assignments), "status": "SUCCESS"},
            {"step": "GENERATE_UVS", "channels": len(uv_layouts), "status": "SUCCESS"},
            {"step": "GENERATE_BAKE_PLAN", "bake_id": bake_plan.bake_id, "status": "SUCCESS"}
        ]

        result = GeneratedSurfaceResult(
            surface_generation_id=surf_id,
            semantic_id=sem_id,
            geometry_generation_id=geom_id,
            surface_version=self.engine_version,
            surface_hash=surf_hash,
            material_definitions=material_defs,
            material_assignments=assignments,
            surface_regions=regions,
            uv_layouts=uv_layouts,
            texel_density_report=texel_report,
            vertex_attributes=vertex_attributes,
            masks={"curvature": "PROCEDURAL", "ao": "BAKED"},
            texture_requirements=tex_reqs,
            procedural_parameters={"wood_grain_scale": 12.0, "metal_scratch_density": 0.35},
            variation_parameters={"seed": generation_seed, "roughness_jitter": 0.05},
            baking_plan=bake_plan,
            shader_graphs=shader_graphs,
            unreal_material_interface=unreal_interfaces,
            invalidation_state=InvalidationState.VALID,
            warnings=[],
            errors=[],
            execution_trace=trace,
            generation_metadata={"engine_version": self.engine_version, "seed": generation_seed}
        )

        return result

    def generate_material(
        self,
        material_request: Dict[str, Any],
        context: Optional[Dict] = None
    ) -> MaterialDefinition:
        req_class = material_request.get("material_class", SurfaceTypeTag.WOOD)
        if isinstance(req_class, str):
            req_class = SurfaceTypeTag(req_class)
        params = material_request.get("parameters", {})
        return self.library.resolve_or_create(req_class, params)

    def generate_uv(
        self,
        geometry: Any,
        uv_strategy: Optional[Dict] = None
    ) -> Tuple[List[UVLayout], TexelDensityReport]:
        dims = getattr(geometry, "dimensions", {"x": 1.0, "y": 1.0, "z": 1.0})
        return UVGenerator.generate_uv_layouts(dims)

    def generate_bake_plan(self, surface_result: GeneratedSurfaceResult) -> BakePlan:
        if surface_result.baking_plan:
            return surface_result.baking_plan
        bake, _ = BakingPlanner.generate_bake_and_texture_requirements(surface_result.semantic_id)
        return bake

    def validate(self, result: GeneratedSurfaceResult) -> SurfaceValidationResult:
        errors = []
        warnings = []

        if not result.surface_generation_id:
            errors.append("MISSING_SURFACE_GENERATION_ID: Surface ID is mandatory.")
        if not result.material_definitions:
            errors.append("EMPTY_MATERIALS: Surface must contain at least one material definition.")
        if not result.uv_layouts:
            errors.append("MISSING_UV_LAYOUTS: UV layouts are mandatory.")
        if any(u.overlap_count > 0 for u in result.uv_layouts):
            errors.append("UV_OVERLAP: UV layout contains forbidden overlaps.")

        if not result.texel_density_report.is_compliant:
            warnings.append(f"TEXEL_DENSITY_WARNING: Texel density deviation is {result.texel_density_report.density_error_pct}%")

        for e in result.errors:
            errors.append(f"SURFACE_ERROR: {e}")
        for w in result.warnings:
            warnings.append(f"SURFACE_WARNING: {w}")

        return SurfaceValidationResult(is_valid=(len(errors) == 0), errors=errors, warnings=warnings)

    def regenerate(
        self,
        targets: List[str],
        context: Dict[str, Any]
    ) -> GeneratedSurfaceResult:
        # Regeneración parcial de material/superficie sin tocar geometría
        geom = context.get("geometry")
        return self.generate(geom)

    def compute_hash(self, result: GeneratedSurfaceResult) -> str:
        return SurfaceHasher.compute_surface_hash(
            materials=result.material_definitions,
            assignments=result.material_assignments,
            uv_layouts=result.uv_layouts,
            attributes=result.vertex_attributes,
            surface_version=self.engine_version
        )
