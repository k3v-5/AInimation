"""
UAF-81.89.8: Advanced Unreal Engine 5 Niagara Interoperability Bridge.
Translates Eulerian 3D grids, skeletal samplers, and particle light clusters to native UE5 Niagara Data Interfaces.
"""

from __future__ import annotations

from typing import Dict, Any, List
from ..fluids.grid3d import EulerianFluidGrid3D
from ..geometry.skeletal_sampler import SkeletalMeshSampler
from ..volumetrics.particle_lights import ParticleLightManager
from ..volumetrics.deep_shadows import DeepShadowMapper


class AdvancedNiagaraBridge:
    """
    Exports UAF Advanced VFX simulations into Unreal Engine 5 Niagara assets and Data Interfaces.
    Supports UNiagaraDataInterfaceGrid3DCollection, UNiagaraDataInterfaceSkeletalMesh, and Light Renderers.
    """

    @staticmethod
    def export_fluid_grid_interface(grid: EulerianFluidGrid3D) -> Dict[str, Any]:
        """
        Maps Eulerian 3D fluid grid to UNiagaraDataInterfaceGrid3DCollection configuration.
        """
        return {
            "data_interface_class": "UNiagaraDataInterfaceGrid3DCollection",
            "properties": {
                "NumCellsX": grid.w,
                "NumCellsY": grid.h,
                "NumCellsZ": grid.d,
                "CellSize": grid.dx,
                "NumAttributes": 4,
                "Attributes": [
                    {"Name": "Density", "Type": "Float", "Default": 0.0},
                    {"Name": "Temperature", "Type": "Float", "Default": grid.props.ambient_temp},
                    {"Name": "Velocity", "Type": "Vector3", "Default": [0.0, 0.0, 0.0]},
                    {"Name": "Pressure", "Type": "Float", "Default": 0.0},
                ],
                "ClearBeforeNonIterationStages": False,
            },
        }

    @staticmethod
    def export_skeletal_sampler_interface(sampler: SkeletalMeshSampler) -> Dict[str, Any]:
        """
        Maps SkeletalMeshSampler to UNiagaraDataInterfaceSkeletalMesh configuration.
        """
        bone_names = [b.name for b in sampler.bone_list]
        return {
            "data_interface_class": "UNiagaraDataInterfaceSkeletalMesh",
            "properties": {
                "SourceMode": "Default",
                "MeshUserParameter": "User.SkeletalMesh",
                "SamplingRegions": ["Default"],
                "WholeMeshLOD": 0,
                "FilteredBones": bone_names,
                "RequireVelocity": True,
                "SampleBoneWeights": True,
            },
        }

    @staticmethod
    def export_particle_lights_renderer(manager: ParticleLightManager) -> Dict[str, Any]:
        """
        Maps ParticleLightManager to UNiagaraLightRendererProperties.
        """
        clustered_lights = manager.build_clustered_lights()
        return {
            "renderer_class": "UNiagaraLightRendererProperties",
            "properties": {
                "bEnabled": True,
                "bUseInverseSquaredFalloff": True,
                "bAffectsTranslucentLighting": True,
                "RadiusScale": 1.0,
                "DefaultExponent": 2.0,
                "MaxLightCount": manager.max_budget_lights,
                "ActiveClusteredLights": len(clustered_lights),
            },
        }

    @staticmethod
    def export_deep_shadow_module(shadow_mapper: DeepShadowMapper) -> Dict[str, Any]:
        """
        Exports Niagara module definition for volumetric self-shadowing.
        """
        return {
            "module_name": "UAF_Module_VolumetricDeepShadow",
            "parameters": {
                "AbsorptionCoeff": shadow_mapper.settings.absorption_coefficient,
                "ScatteringCoeff": shadow_mapper.settings.scattering_coefficient,
                "StepSize": shadow_mapper.settings.step_size,
                "NumSlices": shadow_mapper.settings.num_slices,
            },
            "execution_stage": "ParticleUpdate",
        }
