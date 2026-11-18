import { AdobeDetector } from '../core/AdobeDetector.js';
import { SceneManifestBuilder, SceneManifest, SceneManifestLayer, SceneManifestAudio } from '../core/SceneManifestBuilder.js';
import { execFile } from 'child_process';
import util from 'util';
import fs from 'fs';
import path from 'path';
import os from 'os';

const execFileAsync = util.promisify(execFile);

export const afterEffectsTools = [
  {
    name: 'ae_execute_jsx',
    description: 'Executes an ExtendScript (.jsx) script in Adobe After Effects via the native AfterFX CLI bridge.',
    inputSchema: {
      type: 'object',
      properties: {
        script_content: { type: 'string', description: 'ExtendScript code to execute' },
        script_path: { type: 'string', description: 'Path to an existing .jsx file on disk' }
      }
    },
    handler: async (args: any) => {
      const aePath = AdobeDetector.getAfterEffectsPath();
      if (!aePath) {
        return {
          content: [{ type: 'text', text: 'Error: Adobe After Effects executable was not found on this system.' }],
          isError: true
        };
      }

      let jsxPath = args.script_path;
      let tempCreated = false;

      if (args.script_content) {
        jsxPath = path.join(os.tmpdir(), `ae_script_${Date.now()}.jsx`);
        fs.writeFileSync(jsxPath, args.script_content, 'utf8');
        tempCreated = true;
      }

      if (!jsxPath || !fs.existsSync(jsxPath)) {
        return { content: [{ type: 'text', text: 'Error: Valid script_content or script_path must be provided.' }], isError: true };
      }

      try {
        const { stdout, stderr } = await execFileAsync(aePath, ['-r', path.resolve(jsxPath)], { timeout: 60000 });
        return {
          content: [{
            type: 'text',
            text: JSON.stringify({
              status: 'SUCCESS',
              message: 'ExtendScript dispatched to After Effects',
              output: stdout?.trim() || null,
              warnings: stderr?.trim() || null
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
      } finally {
        if (tempCreated && fs.existsSync(jsxPath)) {
          try { fs.unlinkSync(jsxPath); } catch {}
        }
      }
    }
  },

  {
    name: 'ae_import_puppet_scene',
    description: 'Imports a 2D puppet PSD/AI or Character Animator scene into a new or active composition in After Effects, scaling and centering it automatically.',
    inputSchema: {
      type: 'object',
      properties: {
        file_path: { type: 'string', description: 'Path to the puppet PSD/AI or video file' },
        comp_name: { type: 'string', description: 'Name of the composition to create or insert into' },
        width: { type: 'number', description: 'Comp width (default: 1920)' },
        height: { type: 'number', description: 'Comp height (default: 1080)' },
        duration_seconds: { type: 'number', description: 'Comp duration in seconds (default: 10)' }
      },
      required: ['file_path']
    },
    handler: async (args: any) => {
      const targetFile = path.resolve(args.file_path).replace(/\\/g, '/');
      const compName = (args.comp_name || 'Puppet_Comp').replace(/"/g, '\\"');
      const w = args.width || 1920;
      const h = args.height || 1080;
      const dur = args.duration_seconds || 10;

      const jsx = `
        app.beginUndoGroup("Import Puppet");
        try {
          var fileRef = new File("${targetFile}");
          if (!fileRef.exists) {
            throw new Error("Target file does not exist: " + fileRef.fsName);
          }
          var importOpts = new ImportOptions(fileRef);
          if (importOpts.canImportAs(ImportAsType.COMP)) {
            importOpts.importAs = ImportAsType.COMP;
          }
          var importedItem = app.project.importFile(importOpts);
          var comp = app.project.items.addComp("${compName}", ${w}, ${h}, 1.0, ${dur}, 30);
          var layer = comp.layers.add(importedItem);
          
          // Fit into comp bounds
          var scaleX = (${w} / importedItem.width) * 100;
          var scaleY = (${h} / importedItem.height) * 100;
          var finalScale = Math.min(scaleX, scaleY);
          layer.property("Scale").setValue([finalScale, finalScale]);
          
          $.writeln(JSON.stringify({ success: true, comp_name: comp.name }));
        } catch(e) {
          $.writeln(JSON.stringify({ success: false, error: e.toString() }));
        }
        app.endUndoGroup();
      `;

      const aePath = AdobeDetector.getAfterEffectsPath();
      if (!aePath) {
        return { content: [{ type: 'text', text: 'Error: After Effects executable not found' }], isError: true };
      }

      const tempJsx = path.join(os.tmpdir(), `ae_import_${Date.now()}.jsx`);
      fs.writeFileSync(tempJsx, jsx, 'utf8');

      try {
        await execFileAsync(aePath, ['-r', tempJsx], { timeout: 60000 });
        return {
          content: [{
            type: 'text',
            text: JSON.stringify({
              status: 'SUCCESS',
              message: `Asset ${targetFile} staged for After Effects composition "${compName}"`
            }, null, 2)
          }]
        };
      } finally {
        try { if (fs.existsSync(tempJsx)) fs.unlinkSync(tempJsx); } catch {}
      }
    }
  },

  {
    name: 'ae_render_comp',
    description: 'Triggers background rendering of an After Effects composition to a video file using the native aerender command-line tool.',
    inputSchema: {
      type: 'object',
      properties: {
        project_path: { type: 'string', description: 'Path to the .aep After Effects project file' },
        comp_name: { type: 'string', description: 'Name of the composition to render' },
        output_file: { type: 'string', description: 'Output video file path (e.g. "C:/Renders/Final.mp4" or .mov)' }
      },
      required: ['project_path', 'comp_name', 'output_file']
    },
    handler: async (args: any) => {
      const aerenderPath = AdobeDetector.getAerenderPath();
      if (!aerenderPath) {
        return { content: [{ type: 'text', text: 'Error: aerender executable not found.' }], isError: true };
      }

      const outDir = path.dirname(path.resolve(args.output_file));
      fs.mkdirSync(outDir, { recursive: true });

      const aerenderArgs = [
        '-project', path.resolve(args.project_path),
        '-comp', args.comp_name,
        '-output', path.resolve(args.output_file)
      ];

      try {
        const { stdout } = await execFileAsync(aerenderPath, aerenderArgs, { timeout: 300000 });
        return {
          content: [{
            type: 'text',
            text: JSON.stringify({
              status: 'SUCCESS',
              message: `Render completed: ${args.output_file}`,
              log: stdout?.slice(-500) || null
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
    name: 'ae_generate_scene_manifest',
    description: 'Creates a standard Scene Manifest JSON file and matching ExtendScript (.jsx) constructor. This manifest defines 2.5D layer hierarchy (backgrounds, characters, props, foregrounds), camera, depth of field, synchronized audio, and lip-sync cues for seamless interoperability with the user\'s After Effects engine.',
    inputSchema: {
      type: 'object',
      properties: {
        scene_name: { type: 'string', description: 'Name of the scene/composition' },
        output_manifest_path: { type: 'string', description: 'Target path for the .json manifest file' },
        layers: {
          type: 'array',
          description: 'Layers in the scene ordered from back to front',
          items: {
            type: 'object',
            properties: {
              name: { type: 'string' },
              file_path: { type: 'string' },
              layer_type: { type: 'string', enum: ['character', 'background', 'prop', 'foreground', 'null_controller'] },
              z_depth: { type: 'number', description: 'Z position in 3D space (e.g. background: 1500, prop: 400, character: 0, foreground: -400)' },
              scale_compensation: { type: 'boolean', description: 'Auto-adjust scale to preserve framing at depth Z' },
              opacity: { type: 'number' }
            },
            required: ['name', 'file_path', 'layer_type']
          }
        },
        audio_tracks: {
          type: 'array',
          items: {
            type: 'object',
            properties: {
              name: { type: 'string' },
              file_path: { type: 'string' },
              in_point: { type: 'number' }
            },
            required: ['file_path']
          }
        },
        lip_sync_markers_path: { type: 'string', description: 'Path to generated viseme markers .jsx file' },
        width: { type: 'number', description: 'Width in pixels (default: 1920)' },
        height: { type: 'number', description: 'Height in pixels (default: 1080)' },
        fps: { type: 'number', description: 'Framerate (default: 24)' },
        duration_seconds: { type: 'number', description: 'Duration in seconds (default: 10)' },
        enable_camera: { type: 'boolean', description: 'Enable 3D camera and null controller (default: true)' },
        enable_depth_of_field: { type: 'boolean', description: 'Enable optical camera blur and focus distance (default: false)' }
      },
      required: ['scene_name', 'output_manifest_path', 'layers']
    },
    handler: async (args: any) => {
      const manifest: SceneManifest = {
        schemaVersion: '1.0.0',
        sceneName: args.scene_name,
        width: args.width || 1920,
        height: args.height || 1080,
        fps: args.fps || 24,
        durationSeconds: args.duration_seconds || 10,
        layers: (args.layers || []).map((l: any): SceneManifestLayer => ({
          name: l.name,
          filePath: l.file_path,
          layerType: l.layer_type,
          zDepth: l.z_depth,
          scaleCompensation: l.scale_compensation !== false,
          opacity: l.opacity
        })),
        audioTracks: (args.audio_tracks || []).map((a: any): SceneManifestAudio => ({
          name: a.name,
          filePath: a.file_path,
          inPoint: a.in_point
        })),
        lipSyncMarkersPath: args.lip_sync_markers_path,
        camera: {
          enabled: args.enable_camera !== false,
          createController: true,
          depthOfField: args.enable_depth_of_field === true
        }
      };

      const result = SceneManifestBuilder.saveManifestAndScript(manifest, args.output_manifest_path);

      return {
        content: [{
          type: 'text',
          text: JSON.stringify({
            status: 'SUCCESS',
            message: 'Scene Manifest and ExtendScript constructor generated successfully',
            manifest_json: result.jsonPath,
            constructor_jsx: result.jsxPath,
            scene_name: manifest.sceneName,
            total_layers: manifest.layers.length,
            audio_tracks_count: manifest.audioTracks?.length || 0,
            has_camera: manifest.camera?.enabled,
            has_lip_sync: !!manifest.lipSyncMarkersPath,
            interoperability_ready: true
          }, null, 2)
        }]
      };
    }
  },

  {
    name: 'ae_setup_25d_stage',
    description: 'Assembles a full 2.5D camera stage in After Effects with parallax Z-depth layers, optical camera controller, and scale compensation either from a Scene Manifest or directly specified assets.',
    inputSchema: {
      type: 'object',
      properties: {
        manifest_path: { type: 'string', description: 'Path to existing Scene Manifest JSON' },
        scene_name: { type: 'string', description: 'Composition name' },
        character_file: { type: 'string', description: 'Path to Character Animator PSD/AI or asset (Z = 0)' },
        background_file: { type: 'string', description: 'Path to background image or 3D render (Z = +1500)' },
        foreground_file: { type: 'string', description: 'Path to foreground overlay or props (Z = -400)' },
        audio_file: { type: 'string', description: 'Dialogue or soundtrack audio file' },
        lip_sync_jsx_file: { type: 'string', description: 'Lip-sync markers .jsx script' },
        execute_now: { type: 'boolean', description: 'Immediately run script in After Effects via CLI (default: true)' },
        output_script_path: { type: 'string', description: 'Optional path to save the generated .jsx script' }
      }
    },
    handler: async (args: any) => {
      let manifest: SceneManifest;

      if (args.manifest_path && fs.existsSync(args.manifest_path)) {
        manifest = JSON.parse(fs.readFileSync(args.manifest_path, 'utf8'));
      } else {
        const layers: SceneManifestLayer[] = [];
        if (args.background_file) {
          layers.push({ name: 'Background', filePath: args.background_file, layerType: 'background', zDepth: 1500 });
        }
        if (args.character_file) {
          layers.push({ name: 'Character', filePath: args.character_file, layerType: 'character', zDepth: 0 });
        }
        if (args.foreground_file) {
          layers.push({ name: 'Foreground', filePath: args.foreground_file, layerType: 'foreground', zDepth: -400 });
        }

        const audioTracks: SceneManifestAudio[] = [];
        if (args.audio_file) {
          audioTracks.push({ name: 'Dialogue_Track', filePath: args.audio_file });
        }

        manifest = {
          schemaVersion: '1.0.0',
          sceneName: args.scene_name || 'Stage_25D',
          width: 1920,
          height: 1080,
          fps: 24,
          durationSeconds: 10,
          layers,
          audioTracks,
          lipSyncMarkersPath: args.lip_sync_jsx_file,
          camera: { enabled: true, createController: true }
        };
      }

      const scriptContent = SceneManifestBuilder.toExtendScript(manifest);
      const outJsx = args.output_script_path || path.join(os.tmpdir(), `stage_25d_${Date.now()}.jsx`);
      fs.writeFileSync(outJsx, scriptContent, 'utf8');

      const executeNow = args.execute_now !== false;
      const aePath = AdobeDetector.getAfterEffectsPath();

      if (executeNow && aePath) {
        try {
          const { stdout } = await execFileAsync(aePath, ['-r', path.resolve(outJsx)], { timeout: 60000 });
          return {
            content: [{
              type: 'text',
              text: JSON.stringify({
                status: 'SUCCESS',
                message: `2.5D Stage created and dispatched to After Effects`,
                comp_name: manifest.sceneName,
                jsx_path: outJsx,
                ae_output: stdout?.trim() || null
              }, null, 2)
            }]
          };
        } catch (err: any) {
          return {
            content: [{
              type: 'text',
              text: JSON.stringify({
                status: 'PARTIAL_SUCCESS',
                message: `JSX script generated at ${outJsx}, but After Effects execution failed: ${err.message}`,
                jsx_path: outJsx
              }, null, 2)
            }]
          };
        }
      }

      return {
        content: [{
          type: 'text',
          text: JSON.stringify({
            status: 'SUCCESS',
            message: '2.5D Stage ExtendScript constructor generated successfully',
            jsx_path: outJsx,
            comp_name: manifest.sceneName,
            ready_to_execute: true
          }, null, 2)
        }]
      };
    }
  },

  {
    name: 'ae_apply_animation_expressions',
    description: 'Applies automated, non-destructive secondary animation expressions (squash and stretch, camera shake, audio-reactive bounce, procedural blink, or floating idle) to After Effects layers.',
    inputSchema: {
      type: 'object',
      properties: {
        expression_type: {
          type: 'string',
          enum: ['squash_and_stretch', 'camera_shake', 'audio_reactive_bounce', 'blink_cycle', 'floating_idle', 'custom'],
          description: 'Type of secondary animation expression to apply'
        },
        target_layer_name: {
          type: 'string',
          description: 'Name of the target layer (e.g. "Character", "Camera_Controller", "Eyes"). If omitted, applies to the first selected layer.'
        },
        target_property: {
          type: 'string',
          enum: ['Position', 'Scale', 'Rotation', 'Opacity', 'Time Remap'],
          description: 'Target property (e.g. "Scale" for squash & stretch, "Position" for camera shake, "Opacity" for blink)'
        },
        params: {
          type: 'object',
          description: 'Parameters for the expression (e.g. { maxAmplitude: 15, frequency: 3, decay: 5 } or { frequency: 2.5, amplitude: 20 })'
        },
        custom_code: { type: 'string', description: 'Custom expression code if expression_type is "custom"' },
        execute_now: { type: 'boolean', description: 'Immediately dispatch to After Effects (default: true)' }
      },
      required: ['expression_type', 'target_property']
    },
    handler: async (args: any) => {
      const exprCode = SceneManifestBuilder.getExpressionSnippet(args.expression_type, {
        ...(args.params || {}),
        customCode: args.custom_code
      });

      const escapedCode = exprCode.replace(/\\/g, '\\\\').replace(/"/g, '\\"').replace(/\n/g, '\\n');
      const targetLayerName = args.target_layer_name ? `"${args.target_layer_name.replace(/"/g, '\\"')}"` : 'null';

      const jsx = `// Apply Expression: ${args.expression_type}
(function() {
    app.beginUndoGroup("Apply Expression: ${args.expression_type}");
    try {
        var comp = app.project.activeItem;
        if (!comp || !(comp instanceof CompItem)) {
            throw new Error("No active composition found in After Effects.");
        }

        var layer = null;
        var targetName = ${targetLayerName};
        if (targetName) {
            for (var i = 1; i <= comp.numLayers; i++) {
                if (comp.layer(i).name === targetName) {
                    layer = comp.layer(i);
                    break;
                }
            }
        }
        if (!layer && comp.selectedLayers.length > 0) {
            layer = comp.selectedLayers[0];
        }
        if (!layer) {
            throw new Error("Target layer not found and no layer selected.");
        }

        var prop = layer.property("${args.target_property}");
        if (!prop || !prop.canSetExpression) {
            throw new Error("Property '${args.target_property}' cannot receive expressions on layer " + layer.name);
        }

        prop.expression = "${escapedCode}";
        $.writeln(JSON.stringify({ status: "SUCCESS", layer: layer.name, property: "${args.target_property}" }));
    } catch(err) {
        $.writeln(JSON.stringify({ status: "ERROR", error: err.toString() }));
    }
    app.endUndoGroup();
})();
`;

      const outJsx = path.join(os.tmpdir(), `ae_expr_${Date.now()}.jsx`);
      fs.writeFileSync(outJsx, jsx, 'utf8');

      const aePath = AdobeDetector.getAfterEffectsPath();
      if (args.execute_now !== false && aePath) {
        try {
          const { stdout } = await execFileAsync(aePath, ['-r', path.resolve(outJsx)], { timeout: 60000 });
          return {
            content: [{
              type: 'text',
              text: JSON.stringify({
                status: 'SUCCESS',
                message: `Expression applied in After Effects`,
                expression_type: args.expression_type,
                target_property: args.target_property,
                expression_snippet: exprCode,
                ae_output: stdout?.trim() || null
              }, null, 2)
            }]
          };
        } catch (err: any) {
          return {
            content: [{
              type: 'text',
              text: JSON.stringify({
                status: 'PARTIAL_SUCCESS',
                message: `Expression script generated at ${outJsx}, but execution in AE failed: ${err.message}`,
                expression_snippet: exprCode,
                jsx_path: outJsx
              }, null, 2)
            }]
          };
        }
      }

      return {
        content: [{
          type: 'text',
          text: JSON.stringify({
            status: 'SUCCESS',
            message: 'Expression script generated',
            expression_type: args.expression_type,
            target_property: args.target_property,
            expression_snippet: exprCode,
            jsx_path: outJsx
          }, null, 2)
        }]
      };
    }
  },

  {
    name: 'ae_batch_render_queue',
    description: 'Enqueues and batches multiple compositions for headless rendering using aerender.exe, supporting output modules (H.264, ProRes 4444 with alpha, Lossless) and progress tracking.',
    inputSchema: {
      type: 'object',
      properties: {
        project_path: { type: 'string', description: 'Path to .aep After Effects project file' },
        jobs: {
          type: 'array',
          description: 'List of render jobs to process',
          items: {
            type: 'object',
            properties: {
              comp_name: { type: 'string' },
              output_file: { type: 'string' },
              output_module: { type: 'string', description: 'Optional output module template (e.g. "Lossless", "High Quality", "ProRes")' }
            },
            required: ['comp_name', 'output_file']
          }
        },
        reuse_process: { type: 'boolean', description: 'Use -reuse flag to keep aerender loaded across comps (default: true)' }
      },
      required: ['project_path', 'jobs']
    },
    handler: async (args: any) => {
      const aerenderPath = AdobeDetector.getAerenderPath();
      if (!aerenderPath) {
        return { content: [{ type: 'text', text: 'Error: aerender executable not found.' }], isError: true };
      }

      const results = [];
      const projectPath = path.resolve(args.project_path);

      for (const job of args.jobs) {
        const outDir = path.dirname(path.resolve(job.output_file));
        fs.mkdirSync(outDir, { recursive: true });

        const aerenderArgs = [
          '-project', projectPath,
          '-comp', job.comp_name,
          '-output', path.resolve(job.output_file)
        ];

        if (job.output_module) {
          aerenderArgs.push('-OMtemplate', job.output_module);
        }
        if (args.reuse_process !== false) {
          aerenderArgs.push('-reuse');
        }

        try {
          const { stdout } = await execFileAsync(aerenderPath, aerenderArgs, { timeout: 600000 });
          results.push({
            comp_name: job.comp_name,
            output_file: job.output_file,
            status: 'COMPLETED',
            log: stdout?.slice(-250) || null
          });
        } catch (err: any) {
          results.push({
            comp_name: job.comp_name,
            output_file: job.output_file,
            status: 'FAILED',
            error: err.message
          });
        }
      }

      const totalCompleted = results.filter(r => r.status === 'COMPLETED').length;
      return {
        content: [{
          type: 'text',
          text: JSON.stringify({
            status: totalCompleted === args.jobs.length ? 'SUCCESS' : 'PARTIAL_SUCCESS',
            total_jobs: args.jobs.length,
            completed_jobs: totalCompleted,
            failed_jobs: args.jobs.length - totalCompleted,
            jobs: results
          }, null, 2)
        }]
      };
    }
  }
];
