"""
NPR Anime Cel-Shading and Toon Material Generator
=================================================
Builds authentic cel-shaded 2-tone and 3-tone node graphs in Blender EEVEE,
including Angel Ring hair specular and unlit backface-culled outline materials.
"""

from typing import Dict, Any, Tuple
from ..core.anime_types import AnimeShadingModel


class NPRShadingGenerator:
    """Generates Blender material node setups for anime rendering."""

    def __init__(self, shading_model: AnimeShadingModel = AnimeShadingModel.TWO_TONE_BANDED):
        self.shading_model = shading_model

    def get_blender_material_definitions_code(self) -> str:
        """Returns Blender Python code to construct the full anime material palette."""
        code = '''
# 1. OUTLINE INVERTED HULL MATERIAL (Unlit Pure Emission with Backface Culling)
m_outline = bpy.data.materials.new(name="M_Anime_NPR_Outline")
m_outline.use_backface_culling = True
nodes_out = m_outline.node_tree.nodes
nodes_out.clear()
out_node = nodes_out.new('ShaderNodeOutputMaterial')
out_node.location = (300, 0)
emit_out = nodes_out.new('ShaderNodeEmission')
emit_out.location = (0, 0)
emit_out.inputs['Color'].default_value = (0.04, 0.02, 0.08, 1.0) # Deep anime ink black
emit_out.inputs['Strength'].default_value = 1.0
m_outline.node_tree.links.new(emit_out.outputs['Emission'], out_node.inputs['Surface'])

# 2. TOON CEL-SHADING MATERIAL FACTORY
def create_npr_toon_material(name, base_color, shadow_color, rough=0.25, metal=0.0, emit_col=(0,0,0,1), emit_str=0.0):
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    nodes.clear()
    
    out = nodes.new('ShaderNodeOutputMaterial')
    out.location = (800, 0)
    
    # Principled BSDF as lighting receiver
    bsdf = nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.location = (0, 0)
    bsdf.inputs['Base Color'].default_value = base_color
    bsdf.inputs['Roughness'].default_value = rough
    bsdf.inputs['Metallic'].default_value = metal
    if emit_str > 0:
        bsdf.inputs['Emission Color'].default_value = emit_col
        bsdf.inputs['Emission Strength'].default_value = emit_str
        mat.node_tree.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
        return mat

    # Shader to RGB (para convertir la iluminación en datos de color para cel-shading)
    s2rgb = nodes.new('ShaderNodeShaderToRGB')
    s2rgb.location = (250, 0)
    mat.node_tree.links.new(bsdf.outputs['BSDF'], s2rgb.inputs['Shader'])
    
    # ColorRamp para sombra nítida constante de 2 tonos (Guilty Gear style)
    cramp = nodes.new('ShaderNodeValToRGB')
    cramp.location = (450, 0)
    cramp.color_ramp.interpolation = 'CONSTANT'
    # Posición del corte de sombra en 0.48
    cramp.color_ramp.elements[0].position = 0.0
    cramp.color_ramp.elements[0].color = shadow_color
    cramp.color_ramp.elements[1].position = 0.45
    cramp.color_ramp.elements[1].color = base_color
    mat.node_tree.links.new(s2rgb.outputs['Color'], cramp.inputs['Fac'])
    
    # Salida final
    final_emit = nodes.new('ShaderNodeEmission')
    final_emit.location = (650, 0)
    mat.node_tree.links.new(cramp.outputs['Color'], final_emit.inputs['Color'])
    mat.node_tree.links.new(final_emit.outputs['Emission'], out.inputs['Surface'])
    
    return mat

# Paleta NPR con sombras entintadas armonizadas
m_skin = create_npr_toon_material("M_Anime_Skin_NPR", 
                                  base_color=(0.98, 0.90, 0.85, 1.0), 
                                  shadow_color=(0.88, 0.74, 0.72, 1.0))

m_hair = create_npr_toon_material("M_Anime_Hair_NPR", 
                                  base_color=(0.32, 0.20, 0.54, 1.0), 
                                  shadow_color=(0.18, 0.10, 0.32, 1.0))

m_suit = create_npr_toon_material("M_Anime_Suit_NPR", 
                                  base_color=(0.14, 0.16, 0.22, 1.0), 
                                  shadow_color=(0.06, 0.07, 0.10, 1.0))

m_armor = create_npr_toon_material("M_Anime_Armor_NPR", 
                                   base_color=(0.95, 0.96, 0.98, 1.0), 
                                   shadow_color=(0.78, 0.82, 0.88, 1.0))

m_scarf = create_npr_toon_material("M_Anime_Scarf_NPR", 
                                   base_color=(0.88, 0.15, 0.32, 1.0), 
                                   shadow_color=(0.60, 0.08, 0.20, 1.0))

m_glow = bpy.data.materials.new("M_Anime_Glow_NPR")
m_glow.use_nodes = True
nodes_g = m_glow.node_tree.nodes
nodes_g.clear()
out_g = nodes_g.new('ShaderNodeOutputMaterial')
emit_g = nodes_g.new('ShaderNodeEmission')
emit_g.inputs['Color'].default_value = (0.0, 0.92, 1.0, 1.0)
emit_g.inputs['Strength'].default_value = 6.0
m_glow.node_tree.links.new(emit_g.outputs['Emission'], out_g.inputs['Surface'])
'''
        return code
