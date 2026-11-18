import { AdobeDetector } from '../core/AdobeDetector.js';
import { BlenderEngine, RoomType, GreasePencilSketchType } from '../core/BlenderEngine.js';
import { execFile } from 'child_process';
import util from 'util';
import fs from 'fs';
import path from 'path';
import os from 'os';

const execFileAsync = util.promisify(execFile);

export const blenderTools = [
  {
    name: 'blender_execute_script',
    description: 'Executes a Python script using Blender 3D (bpy) in headless background mode without opening the GUI.',
    inputSchema: {
      type: 'object',
      properties: {
        script_content: { type: 'string', description: 'Python script content using bpy' },
        script_path: { type: 'string', description: 'Path to an existing .py script on disk' },
        blend_file: { type: 'string', description: 'Optional .blend file to open before executing the script' }
      }
    },
    handler: async (args: any) => {
      let pyContent = args.script_content;
      if (!pyContent && args.script_path && fs.existsSync(args.script_path)) {
        pyContent = fs.readFileSync(args.script_path, 'utf8');
      }

      if (!pyContent) {
        return { content: [{ type: 'text', text: 'Error: Valid script_content or script_path must be provided.' }], isError: true };
      }

      try {
        const { stdout, stderr } = await BlenderEngine.executeScript(pyContent, args.blend_file);
        return {
          content: [{
            type: 'text',
            text: JSON.stringify({
              status: 'SUCCESS',
              message: 'Blender script executed successfully',
              output: stdout?.slice(-1000) || null,
              warnings: stderr?.slice(-500) || null
            }, null, 2)
          }]
        };
      } catch (err: any) {
        return {
          content: [{
            type: 'text',
            text: JSON.stringify({
              status: 'ERROR',
              message: err.message,
              stderr: err.stderr || null
            }, null, 2)
          }],
          isError: true
        };
      }
    }
  },

  {
    name: 'blender_render_frame',
    description: 'Renders a 3D scene, background, or Grease Pencil element to a PNG image file for compositing with 2D character animations.',
    inputSchema: {
      type: 'object',
      properties: {
        blend_file: { type: 'string', description: 'Path to the .blend project file' },
        output_image: { type: 'string', description: 'Destination PNG file path' },
        frame_number: { type: 'number', description: 'Frame number to render (default: 1)' }
      },
      required: ['blend_file', 'output_image']
    },
    handler: async (args: any) => {
      const blenderPath = AdobeDetector.getBlenderPath();
      if (!blenderPath) {
        return { content: [{ type: 'text', text: 'Error: Blender executable not found.' }], isError: true };
      }

      const frame = args.frame_number || 1;
      const outImg = path.resolve(args.output_image);
      fs.mkdirSync(path.dirname(outImg), { recursive: true });

      const cliArgs = [
        '--factory-startup',
        '-b', path.resolve(args.blend_file),
        '-o', outImg.replace(/\.png$/i, '_#'),
        '-F', 'PNG',
        '-f', String(frame)
      ];

      try {
        const { stdout } = await execFileAsync(blenderPath, cliArgs, { timeout: 120000 });
        return {
          content: [{
            type: 'text',
            text: JSON.stringify({
              status: 'SUCCESS',
              message: `Frame ${frame} rendered from ${args.blend_file}`,
              output_target: outImg,
              log: stdout?.slice(-400) || null
            }, null, 2)
          }]
        };
      } catch (err: any) {
        return {
          content: [{
            type: 'text',
            text: JSON.stringify({
              status: 'ERROR',
              message: err.message,
              stderr: err.stderr || null
            }, null, 2)
          }],
          isError: true
        };
      }
    }
  },

  {
    name: 'blender_scaffold_3d_room',
    description: 'Procedurally generates a 3D architectural room or environment (interior room, anime bedroom, cyberpunk street, studio cyclorama, minimalist gallery) in Blender with 3-point lighting, materials, props, and camera.',
    inputSchema: {
      type: 'object',
      properties: {
        room_type: {
          type: 'string',
          enum: ['interior_room', 'cyberpunk_street', 'studio_stage', 'anime_bedroom', 'minimalist_gallery'],
          description: 'Type/theme of the 3D environment to construct'
        },
        output_path: {
          type: 'string',
          description: 'Destination file path for the .blend project (e.g. "F:/Projects/3D/room.blend")'
        },
        render_preview: {
          type: 'boolean',
          description: 'Render a preview PNG image of the created room (default: true)'
        },
        preview_path: {
          type: 'string',
          description: 'Optional path for the preview PNG'
        },
        camera_focal_length: {
          type: 'number',
          description: 'Camera lens focal length in mm (default: 50)'
        },
        width: { type: 'number', description: 'Preview resolution width (default: 1920)' },
        height: { type: 'number', description: 'Preview resolution height (default: 1080)' }
      },
      required: ['room_type', 'output_path']
    },
    handler: async (args: any) => {
      try {
        const result = await BlenderEngine.scaffold3dRoom({
          roomType: args.room_type as RoomType,
          outputPath: args.output_path,
          renderPreview: args.render_preview !== false,
          previewPath: args.preview_path,
          cameraFocalLength: args.camera_focal_length,
          width: args.width || 1920,
          height: args.height || 1080
        });

        return {
          content: [{
            type: 'text',
            text: JSON.stringify({
              status: 'SUCCESS',
              message: `3D ${args.room_type} generated successfully`,
              blend_file: result.blendFile,
              preview_image: result.previewImage || null,
              objects_count: result.objectsCount,
              lights_count: result.lightsCount,
              ready_for_parallax_rendering: true
            }, null, 2)
          }]
        };
      } catch (err: any) {
        return {
          content: [{
            type: 'text',
            text: JSON.stringify({
              status: 'ERROR',
              message: `Failed to scaffold 3D room: ${err.message}`
            }, null, 2)
          }],
          isError: true
        };
      }
    }
  },

  {
    name: 'blender_render_parallax_passes',
    description: 'Renders multiple compositing passes (Beauty RGBA with transparent background, Shadow Catcher Alpha, and Z-Depth / Mist pass) from a .blend file for professional 2.5D compositing in After Effects.',
    inputSchema: {
      type: 'object',
      properties: {
        blend_file: {
          type: 'string',
          description: 'Path to existing .blend project file'
        },
        output_dir: {
          type: 'string',
          description: 'Directory where pass images will be saved'
        },
        base_name: {
          type: 'string',
          description: 'Base filename prefix for the passes (default: "scene")'
        },
        frame_number: {
          type: 'number',
          description: 'Frame to render (default: 1)'
        },
        width: { type: 'number', description: 'Render width (default: 1920)' },
        height: { type: 'number', description: 'Render height (default: 1080)' }
      },
      required: ['blend_file', 'output_dir']
    },
    handler: async (args: any) => {
      try {
        const result = await BlenderEngine.renderParallaxPasses({
          blendFile: args.blend_file,
          outputDir: args.output_dir,
          baseName: args.base_name || 'scene',
          frameNumber: args.frame_number || 1,
          width: args.width || 1920,
          height: args.height || 1080
        });

        return {
          content: [{
            type: 'text',
            text: JSON.stringify({
              status: 'SUCCESS',
              message: 'Parallax compositing passes rendered successfully',
              passes: {
                beauty_pass: result.beautyPass,
                shadow_pass: result.shadowPass,
                z_depth_pass: result.zDepthPass
              },
              resolution: result.resolution,
              ready_for_after_effects: true
            }, null, 2)
          }]
        };
      } catch (err: any) {
        return {
          content: [{
            type: 'text',
            text: JSON.stringify({
              status: 'ERROR',
              message: `Failed to render parallax passes: ${err.message}`
            }, null, 2)
          }],
          isError: true
        };
      }
    }
  },

  {
    name: 'blender_grease_pencil_sketch',
    description: 'Generates procedural 2D stylized strokes and elements in 3D space using Blender Grease Pencil (character silhouette, action speedlines, cel clouds, or neon contours).',
    inputSchema: {
      type: 'object',
      properties: {
        sketch_type: {
          type: 'string',
          enum: ['character_silhouette', 'speed_lines', 'cel_clouds', 'neon_contour'],
          description: 'Type of Grease Pencil drawing/element to generate'
        },
        output_path: {
          type: 'string',
          description: 'Target .blend file path'
        },
        render_preview: {
          type: 'boolean',
          description: 'Render a transparent preview PNG (default: true)'
        },
        preview_path: {
          type: 'string',
          description: 'Optional path for the preview PNG'
        },
        stroke_color: {
          type: 'array',
          items: { type: 'number' },
          description: 'RGBA color array [r, g, b, a] with values between 0.0 and 1.0 (e.g. [0.1, 0.8, 1.0, 1.0] for cyan neon)'
        },
        width: { type: 'number', description: 'Resolution width (default: 1920)' },
        height: { type: 'number', description: 'Resolution height (default: 1080)' }
      },
      required: ['sketch_type', 'output_path']
    },
    handler: async (args: any) => {
      try {
        const result = await BlenderEngine.createGreasePencilSketch({
          sketchType: args.sketch_type as GreasePencilSketchType,
          outputPath: args.output_path,
          renderPreview: args.render_preview !== false,
          previewPath: args.preview_path,
          strokeColor: args.stroke_color,
          width: args.width || 1920,
          height: args.height || 1080
        });

        return {
          content: [{
            type: 'text',
            text: JSON.stringify({
              status: 'SUCCESS',
              message: `Grease Pencil ${args.sketch_type} generated successfully`,
              blend_file: result.blendFile,
              preview_image: result.previewImage || null,
              strokes_count: result.strokesCount,
              ready_for_compositing: true
            }, null, 2)
          }]
        };
      } catch (err: any) {
        return {
          content: [{
            type: 'text',
            text: JSON.stringify({
              status: 'ERROR',
              message: `Failed to create Grease Pencil sketch: ${err.message}`
            }, null, 2)
          }],
          isError: true
        };
      }
    }
  }
];
