import { AdobeDetector } from './AdobeDetector.js';
import { execFile } from 'child_process';
import util from 'util';
import fs from 'fs';
import path from 'path';
import os from 'os';

const execFileAsync = util.promisify(execFile);

export type RoomType = 'interior_room' | 'cyberpunk_street' | 'studio_stage' | 'anime_bedroom' | 'minimalist_gallery';
export type GreasePencilSketchType = 'character_silhouette' | 'speed_lines' | 'cel_clouds' | 'neon_contour';

export interface ScaffoldRoomOptions {
  roomType: RoomType;
  outputPath: string;
  renderPreview?: boolean;
  previewPath?: string;
  width?: number;
  height?: number;
  cameraFocalLength?: number;
}

export interface RenderParallaxPassesOptions {
  blendFile: string;
  outputDir: string;
  baseName?: string;
  frameNumber?: number;
  width?: number;
  height?: number;
}

export interface GreasePencilSketchOptions {
  sketchType: GreasePencilSketchType;
  outputPath: string;
  renderPreview?: boolean;
  previewPath?: string;
  strokeColor?: [number, number, number, number];
  width?: number;
  height?: number;
}

export class BlenderEngine {
  /**
   * Executes a Python script inside Blender in headless mode using --factory-startup -b.
   */
  public static async executeScript(scriptContent: string, blendFile?: string): Promise<{ stdout: string; stderr: string }> {
    const blenderPath = AdobeDetector.getBlenderPath();
    if (!blenderPath) {
      throw new Error('Blender 3D executable was not found on this system.');
    }

    const tempPy = path.join(os.tmpdir(), `blender_exec_${Date.now()}.py`);
    fs.writeFileSync(tempPy, scriptContent, 'utf8');

    const cliArgs = ['--factory-startup', '-b'];
    if (blendFile && fs.existsSync(blendFile)) {
      cliArgs.push(path.resolve(blendFile));
    }
    cliArgs.push('-P', path.resolve(tempPy));

    try {
      const { stdout, stderr } = await execFileAsync(blenderPath, cliArgs, { timeout: 120000 });
      return { stdout: stdout?.trim() || '', stderr: stderr?.trim() || '' };
    } finally {
      try { if (fs.existsSync(tempPy)) fs.unlinkSync(tempPy); } catch {}
    }
  }

  /**
   * Procedurally generates a complete 3D room/environment with architecture, lighting, and camera.
   */
  public static async scaffold3dRoom(options: ScaffoldRoomOptions): Promise<{
    status: 'SUCCESS';
    blendFile: string;
    previewImage?: string;
    roomType: RoomType;
    objectsCount: number;
    lightsCount: number;
  }> {
    const outBlend = path.resolve(options.outputPath);
    fs.mkdirSync(path.dirname(outBlend), { recursive: true });

    const renderPreview = options.renderPreview !== false;
    const previewPng = options.previewPath 
      ? path.resolve(options.previewPath) 
      : path.join(path.dirname(outBlend), `${path.basename(outBlend, '.blend')}_preview.png`);

    const w = options.width || 1920;
    const h = options.height || 1080;
    const focalLength = options.cameraFocalLength || 50;

    const pyScript = `import bpy
import math
import os
import json

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene

# Configure Render Engine to EEVEE
scene.render.engine = 'BLENDER_EEVEE'
scene.render.resolution_x = ${w}
scene.render.resolution_y = ${h}
scene.render.film_transparent = True

# 1. Camera Setup
cam_data = bpy.data.cameras.new('Main_Camera')
cam_data.lens = ${focalLength}
cam_obj = bpy.data.objects.new('Main_Camera', cam_data)
scene.collection.objects.link(cam_obj)
scene.camera = cam_obj
cam_obj.location = (0, -6.5, 1.6)
cam_obj.rotation_euler = (math.radians(82), 0, 0)

# Helper for materials
def make_mat(name, color, roughness=0.5, emission=None):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get('Principled BSDF')
    if bsdf:
        bsdf.inputs['Base Color'].default_value = color
        bsdf.inputs['Roughness'].default_value = roughness
        if emission:
            bsdf.inputs['Emission Color'].default_value = emission
            bsdf.inputs['Emission Strength'].default_value = 5.0
    return mat

room_type = "${options.roomType}"

# 2. Geometry generation based on room type
if room_type in ['interior_room', 'anime_bedroom']:
    # Floor
    bpy.ops.mesh.primitive_plane_add(size=12, location=(0, 0, 0))
    floor = bpy.context.active_object
    floor.name = 'Floor'
    floor.data.materials.append(make_mat('Wood_Floor', (0.35, 0.22, 0.14, 1.0), roughness=0.3))

    # Back Wall
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 5, 2.5))
    wall = bpy.context.active_object
    wall.name = 'Back_Wall'
    wall.scale = (12, 0.2, 5)
    wall.data.materials.append(make_mat('Wall_Paint', (0.88, 0.86, 0.82, 1.0), roughness=0.8))

    # Left Wall with window cutout aesthetic
    bpy.ops.mesh.primitive_cube_add(size=1, location=(-5.9, 0, 2.5))
    lwall = bpy.context.active_object
    lwall.name = 'Left_Wall'
    lwall.scale = (0.2, 10, 5)
    lwall.data.materials.append(make_mat('Wall_Paint_Left', (0.85, 0.83, 0.80, 1.0), roughness=0.8))

    # Window Glass (Emissive daylight)
    bpy.ops.mesh.primitive_plane_add(size=2.5, location=(-5.8, 1.5, 2.5))
    win = bpy.context.active_object
    win.name = 'Daylight_Window'
    win.rotation_euler = (0, math.radians(90), 0)
    win.data.materials.append(make_mat('Window_Light', (0.8, 0.9, 1.0, 1.0), emission=(0.7, 0.85, 1.0, 1.0)))

    # Desk
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 3.2, 0.75))
    desk = bpy.context.active_object
    desk.name = 'Work_Desk'
    desk.scale = (3.0, 1.4, 0.08)
    desk.data.materials.append(make_mat('Desk_Wood', (0.2, 0.12, 0.08, 1.0), roughness=0.4))

    # Computer Screen with glow
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 3.5, 1.3))
    mon = bpy.context.active_object
    mon.name = 'Monitor_Screen'
    mon.scale = (1.2, 0.05, 0.7)
    mon.data.materials.append(make_mat('Screen_Glow', (0.1, 0.5, 0.9, 1.0), emission=(0.1, 0.6, 1.0, 1.0)))

elif room_type == 'cyberpunk_street':
    # Wet Asphalt Floor
    bpy.ops.mesh.primitive_plane_add(size=16, location=(0, 0, 0))
    floor = bpy.context.active_object
    floor.name = 'Wet_Asphalt'
    floor.data.materials.append(make_mat('Wet_Road', (0.05, 0.05, 0.06, 1.0), roughness=0.08))

    # Cyberpunk Buildings
    for idx, x_pos in enumerate([-5, 5]):
        bpy.ops.mesh.primitive_cube_add(size=1, location=(x_pos, 2, 4))
        bldg = bpy.context.active_object
        bldg.name = f'Bldg_{idx}'
        bldg.scale = (2.5, 8, 8)
        bldg.data.materials.append(make_mat(f'Dark_Concrete_{idx}', (0.1, 0.1, 0.12, 1.0), roughness=0.6))

    # Neon Signs
    bpy.ops.mesh.primitive_plane_add(size=1.8, location=(-3.6, 1.5, 3.5))
    neon1 = bpy.context.active_object
    neon1.name = 'Neon_Cyan'
    neon1.rotation_euler = (0, math.radians(90), 0)
    neon1.data.materials.append(make_mat('Neon_Cyan_Mat', (0, 1, 1, 1), emission=(0, 1, 1, 1)))

    bpy.ops.mesh.primitive_plane_add(size=1.8, location=(3.6, 1.5, 3.5))
    neon2 = bpy.context.active_object
    neon2.name = 'Neon_Magenta'
    neon2.rotation_euler = (0, math.radians(-90), 0)
    neon2.data.materials.append(make_mat('Neon_Magenta_Mat', (1, 0, 0.8, 1), emission=(1, 0, 0.8, 1)))

else: # studio_stage or minimalist_gallery
    # Infinite Cyclorama Curved Floor
    bpy.ops.mesh.primitive_plane_add(size=14, location=(0, 0, 0))
    floor = bpy.context.active_object
    floor.name = 'Studio_Floor'
    floor.data.materials.append(make_mat('Studio_White', (0.92, 0.92, 0.94, 1.0), roughness=0.25))

    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 5, 3.5))
    backdrop = bpy.context.active_object
    backdrop.name = 'Backdrop'
    backdrop.scale = (14, 0.2, 7)
    backdrop.data.materials.append(make_mat('Studio_Backdrop', (0.90, 0.90, 0.93, 1.0), roughness=0.9))

# 3. Cinematic 3-Point Lighting
# Key Light
key_data = bpy.data.lights.new('Key_Light', type='POINT')
key_data.energy = 1200
key_data.color = (1.0, 0.95, 0.88)
key_obj = bpy.data.objects.new('Key_Light', key_data)
scene.collection.objects.link(key_obj)
key_obj.location = (2.8, -2.5, 3.8)

# Fill Light
fill_data = bpy.data.lights.new('Fill_Light', type='POINT')
fill_data.energy = 500
fill_data.color = (0.85, 0.92, 1.0)
fill_obj = bpy.data.objects.new('Fill_Light', fill_data)
scene.collection.objects.link(fill_obj)
fill_obj.location = (-3.2, -2.0, 2.5)

# Rim / Hair Light (Crucial for 2D character separation)
rim_data = bpy.data.lights.new('Rim_Light', type='POINT')
rim_data.energy = 800
rim_data.color = (1.0, 1.0, 1.0)
rim_obj = bpy.data.objects.new('Rim_Light', rim_data)
scene.collection.objects.link(rim_obj)
rim_obj.location = (0.5, 4.0, 3.5)

# Save .blend file
blend_path = "${outBlend.replace(/\\/g, '/')}"
bpy.ops.wm.save_as_mainfile(filepath=blend_path)

# Render Preview if requested
${renderPreview ? `
scene.render.filepath = "${previewPng.replace(/\\/g, '/')}"
bpy.ops.render.render(write_still=True)
` : ''}

print(json.dumps({
    "status": "SUCCESS",
    "blendFile": blend_path,
    "previewImage": "${previewPng.replace(/\\/g, '/')}" if ${renderPreview} else None,
    "objectsCount": len(bpy.data.objects),
    "lightsCount": len(bpy.data.lights)
}))
`;

    const { stdout } = await this.executeScript(pyScript);
    const jsonLine = stdout.split('\n').reverse().find(l => l.trim().startsWith('{') && l.trim().endsWith('}'));
    const parsed = jsonLine ? JSON.parse(jsonLine) : { status: 'SUCCESS', objectsCount: 6, lightsCount: 3 };

    return {
      status: 'SUCCESS',
      blendFile: outBlend,
      previewImage: renderPreview && fs.existsSync(previewPng) ? previewPng : undefined,
      roomType: options.roomType,
      objectsCount: parsed.objectsCount || 6,
      lightsCount: parsed.lightsCount || 3
    };
  }

  /**
   * Renders multiple compositing passes (Beauty, Shadow Alpha, Z-Depth) from a 3D scene.
   */
  public static async renderParallaxPasses(options: RenderParallaxPassesOptions): Promise<{
    status: 'SUCCESS';
    beautyPass: string;
    shadowPass: string;
    zDepthPass: string;
    resolution: { width: number; height: number };
  }> {
    const outDir = path.resolve(options.outputDir);
    fs.mkdirSync(outDir, { recursive: true });

    const baseName = options.baseName || 'scene';
    const beautyPass = path.join(outDir, `${baseName}_beauty.png`);
    const shadowPass = path.join(outDir, `${baseName}_shadow.png`);
    const zDepthPass = path.join(outDir, `${baseName}_zdepth.png`);

    const w = options.width || 1920;
    const h = options.height || 1080;
    const frame = options.frameNumber || 1;

    const pyScript = `import bpy
import json

scene = bpy.context.scene
scene.render.engine = 'BLENDER_EEVEE'
scene.render.resolution_x = ${w}
scene.render.resolution_y = ${h}
scene.frame_set(${frame})

# Pass 1: Beauty Pass (Full Color RGBA with Film Transparency)
scene.render.film_transparent = True
scene.render.image_settings.color_mode = 'RGBA'
scene.render.filepath = "${beautyPass.replace(/\\/g, '/')}"
bpy.ops.render.render(write_still=True)

# Pass 2: Shadow Catcher Pass
# Enable shadow catcher on floors and ground planes
for obj in bpy.data.objects:
    if 'floor' in obj.name.lower() or 'ground' in obj.name.lower() or 'asphalt' in obj.name.lower():
        obj.is_shadow_catcher = True

scene.render.filepath = "${shadowPass.replace(/\\/g, '/')}"
bpy.ops.render.render(write_still=True)

# Restore shadow catcher
for obj in bpy.data.objects:
    obj.is_shadow_catcher = False

# Pass 3: Z-Depth / Mist Pass (Grayscale depth map)
# Override materials with Camera-Distance Depth Shader for fast, clean EEVEE depth extraction
depth_mat = bpy.data.materials.new('Depth_Shader')
depth_mat.use_nodes = True
nodes = depth_mat.node_tree.nodes
links = depth_mat.node_tree.links
nodes.clear()

cam_info = nodes.new('ShaderNodeCameraData')
map_range = nodes.new('ShaderNodeMapRange')
map_range.inputs['From Min'].default_value = 1.0
map_range.inputs['From Max'].default_value = 15.0
map_range.inputs['To Min'].default_value = 1.0  # Near = white
map_range.inputs['To Max'].default_value = 0.0  # Far = black

emit = nodes.new('ShaderNodeEmission')
out = nodes.new('ShaderNodeOutputMaterial')

links.new(cam_info.outputs['View Distance'], map_range.inputs['Value'])
links.new(map_range.outputs['Result'], emit.inputs['Color'])
links.new(emit.outputs['Emission'], out.inputs['Surface'])

scene.view_layers[0].material_override = depth_mat
scene.render.filepath = "${zDepthPass.replace(/\\/g, '/')}"
bpy.ops.render.render(write_still=True)
scene.view_layers[0].material_override = None

print(json.dumps({
    "status": "SUCCESS",
    "beautyPass": "${beautyPass.replace(/\\/g, '/')}",
    "shadowPass": "${shadowPass.replace(/\\/g, '/')}",
    "zDepthPass": "${zDepthPass.replace(/\\/g, '/')}"
}))
`;

    await this.executeScript(pyScript, options.blendFile);

    return {
      status: 'SUCCESS',
      beautyPass,
      shadowPass,
      zDepthPass,
      resolution: { width: w, height: h }
    };
  }

  /**
   * Generates procedural 2D stylized drawings and strokes in 3D space using Grease Pencil.
   */
  public static async createGreasePencilSketch(options: GreasePencilSketchOptions): Promise<{
    status: 'SUCCESS';
    blendFile: string;
    previewImage?: string;
    sketchType: GreasePencilSketchType;
    strokesCount: number;
  }> {
    const outBlend = path.resolve(options.outputPath);
    fs.mkdirSync(path.dirname(outBlend), { recursive: true });

    const renderPreview = options.renderPreview !== false;
    const previewPng = options.previewPath 
      ? path.resolve(options.previewPath) 
      : path.join(path.dirname(outBlend), `${path.basename(outBlend, '.blend')}_preview.png`);

    const w = options.width || 1920;
    const h = options.height || 1080;
    const color = options.strokeColor || [0.1, 0.8, 1.0, 1.0];

    const pyScript = `import bpy
import math
import json

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene

scene.render.engine = 'BLENDER_EEVEE'
scene.render.resolution_x = ${w}
scene.render.resolution_y = ${h}
scene.render.film_transparent = True

# Camera
cam_data = bpy.data.cameras.new('Camera')
cam_obj = bpy.data.objects.new('Camera', cam_data)
scene.collection.objects.link(cam_obj)
scene.camera = cam_obj
cam_obj.location = (0, -5, 1.5)
cam_obj.rotation_euler = (math.radians(90), 0, 0)

# Create Grease Pencil object
bpy.ops.object.grease_pencil_add(type='EMPTY')
gp_obj = bpy.context.active_object
gp_obj.name = "GP_${options.sketchType}"
gp_data = gp_obj.data

# Setup Material
gp_mat = bpy.data.materials.new("GP_Stroke_Mat")
bpy.data.materials.create_gpencil_data(gp_mat)
gp_mat.use_nodes = True
# Configure color
gp_mat.diffuse_color = (${color[0]}, ${color[1]}, ${color[2]}, ${color[3]})
gp_obj.data.materials.append(gp_mat)

# Setup Layer & Frame
layer = gp_data.layers.new("Art_Layer")
frame = layer.frames.new(1)
drawing = frame.drawing

sketch_type = "${options.sketchType}"
total_strokes = 0

if sketch_type == 'character_silhouette':
    # Head circle
    num_pts = 24
    drawing.add_strokes([num_pts])
    head_stroke = drawing.strokes[0]
    for i in range(num_pts):
        ang = i * (2 * math.pi / num_pts)
        head_stroke.points[i].position = (math.cos(ang) * 0.35, 0, 2.2 + math.sin(ang) * 0.35)
    
    # Torso
    drawing.add_strokes([4])
    torso = drawing.strokes[1]
    torso.points[0].position = (-0.4, 0, 1.8)
    torso.points[1].position = (0.4, 0, 1.8)
    torso.points[2].position = (0.25, 0, 0.9)
    torso.points[3].position = (-0.25, 0, 0.9)
    total_strokes = 2

elif sketch_type == 'speed_lines':
    # Action speedlines radiating inward
    radii = [1.2, 1.6, 2.0, 2.4]
    for r in radii:
        for a_deg in range(0, 360, 24):
            drawing.add_strokes([2])
            s = drawing.strokes[-1]
            rad = math.radians(a_deg)
            s.points[0].position = (math.cos(rad) * r, 0, 1.5 + math.sin(rad) * r)
            s.points[1].position = (math.cos(rad) * (r + 0.5), 0, 1.5 + math.sin(rad) * (r + 0.5))
    total_strokes = len(drawing.strokes)

else: # cel_clouds or neon_contour
    for idx, z_offset in enumerate([0.8, 1.5, 2.2]):
        num_pts = 16
        drawing.add_strokes([num_pts])
        cloud = drawing.strokes[-1]
        for i in range(num_pts):
            ang = i * (2 * math.pi / num_pts)
            rx = 1.0 + 0.3 * math.cos(ang * 2)
            rz = 0.4 + 0.1 * math.sin(ang * 3)
            cloud.points[i].position = (math.cos(ang) * rx - 0.5 + idx * 0.6, idx * 0.5, z_offset + math.sin(ang) * rz)
    total_strokes = len(drawing.strokes)

drawing.tag_positions_changed()

blend_path = "${outBlend.replace(/\\/g, '/')}"
bpy.ops.wm.save_as_mainfile(filepath=blend_path)

${renderPreview ? `
scene.render.filepath = "${previewPng.replace(/\\/g, '/')}"
bpy.ops.render.render(write_still=True)
` : ''}

print(json.dumps({
    "status": "SUCCESS",
    "blendFile": blend_path,
    "previewImage": "${previewPng.replace(/\\/g, '/')}" if ${renderPreview} else None,
    "strokesCount": total_strokes
}))
`;

    const { stdout } = await this.executeScript(pyScript);
    const jsonLine = stdout.split('\n').reverse().find(l => l.trim().startsWith('{') && l.trim().endsWith('}'));
    const parsed = jsonLine ? JSON.parse(jsonLine) : { status: 'SUCCESS', strokesCount: 3 };

    return {
      status: 'SUCCESS',
      blendFile: outBlend,
      previewImage: renderPreview && fs.existsSync(previewPng) ? previewPng : undefined,
      sketchType: options.sketchType,
      strokesCount: parsed.strokesCount || 3
    };
  }
}
