from typing import Dict, Any, List
from ..core.surface_schema import ShaderGraphSpec, ShaderNodeSpec, MaterialDefinition

class ShaderGraphBuilder:
    @classmethod
    def build_pbr_shader_graph(
        cls,
        material: MaterialDefinition,
        enable_procedural_variation: bool = True
    ) -> ShaderGraphSpec:
        nodes = [
            ShaderNodeSpec("NODE_PRINCIPLED_BSDF", "ShaderNodeBsdfPrincipled", {
                "Base Color": material.base_color,
                "Metallic": material.metallic,
                "Roughness": material.roughness,
                "Specular": material.specular
            }, inputs={"Base Color": material.base_color}, outputs={"BSDF": "SHADER"}),
            ShaderNodeSpec("PBR_OUTPUT", "ShaderNodeOutputMaterial", {}, inputs={"Surface": "NODE_PRINCIPLED_BSDF.BSDF"}, outputs={})
        ]

        connections = [
            {"from_node": "NODE_PRINCIPLED_BSDF", "from_socket": "BSDF", "to_node": "PBR_OUTPUT", "to_socket": "Surface"}
        ]

        if enable_procedural_variation:
            nodes.append(ShaderNodeSpec("NODE_NOISE_ROUGHNESS", "ShaderNodeTexNoise", {"scale": 15.0, "detail": 2.0}, outputs={"Fac": "FLOAT"}))
            nodes.append(ShaderNodeSpec("NODE_CURVATURE_WEAR", "ShaderNodeAttribute", {"attribute_name": "WEAR"}, outputs={"Color": "RGBA"}))
            connections.append({"from_node": "NODE_NOISE_ROUGHNESS", "from_socket": "Fac", "to_node": "NODE_PRINCIPLED_BSDF", "to_socket": "Roughness"})

        return ShaderGraphSpec(
            graph_id=f"GRAPH_{material.material_id.upper()}",
            nodes=nodes,
            connections=connections,
            parameters={"roughness_mod": 0.1, "wear_intensity": 0.5},
            output_node_id="PBR_OUTPUT"
        )
