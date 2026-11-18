import { VbsRunner } from '../core/VbsRunner.js';
import { AdobeDetector } from '../core/AdobeDetector.js';
import path from 'path';
import fs from 'fs';

export const COLOR_PALETTES: Record<string, { skin: string; primary: string; secondary: string; accent: string; dark: string }> = {
  cyberpunk: {
    skin: '#f2c4b2',
    primary: '#05d9e8',
    secondary: '#ff2a6d',
    accent: '#d1f7ff',
    dark: '#01012b'
  },
  pastel: {
    skin: '#ffe5d9',
    primary: '#b8c0ff',
    secondary: '#ffd6a5',
    accent: '#caffbf',
    dark: '#4a4e69'
  },
  anime: {
    skin: '#ffdfba',
    primary: '#3a86ff',
    secondary: '#ff006e',
    accent: '#ffbe0b',
    dark: '#1a1a2e'
  },
  retro: {
    skin: '#fed9b7',
    primary: '#00afb9',
    secondary: '#f07167',
    accent: '#fed9b7',
    dark: '#003049'
  },
  monochrome: {
    skin: '#e0e0e0',
    primary: '#9e9e9e',
    secondary: '#757575',
    accent: '#f5f5f5',
    dark: '#212121'
  }
};

export const illustratorTools = [
  {
    name: 'ai_execute_jsx',
    description: 'Executes an ExtendScript (.jsx) script or inline code snippet directly inside Adobe Illustrator via native Windows automation.',
    inputSchema: {
      type: 'object',
      properties: {
        script_content: {
          type: 'string',
          description: 'The JavaScript / ExtendScript code to execute'
        },
        script_path: {
          type: 'string',
          description: 'Alternative path to an existing .jsx file on disk'
        }
      }
    },
    handler: async (args: any) => {
      const isContent = !!args.script_content;
      const target = args.script_content || args.script_path;

      if (!target) {
        return {
          content: [{ type: 'text', text: 'Error: Either script_content or script_path must be provided.' }],
          isError: true
        };
      }

      const result = await VbsRunner.runIllustratorScript(target, isContent);
      return {
        content: [{
          type: 'text',
          text: JSON.stringify(result, null, 2)
        }],
        isError: !result.success
      };
    }
  },

  {
    name: 'ai_create_document',
    description: 'Creates a new vector document in Adobe Illustrator with custom dimensions and color mode.',
    inputSchema: {
      type: 'object',
      properties: {
        document_name: { type: 'string', description: 'Name of the new document' },
        width: { type: 'number', description: 'Width in points/pixels (default: 1920)' },
        height: { type: 'number', description: 'Height in points/pixels (default: 1080)' }
      },
      required: ['document_name']
    },
    handler: async (args: any) => {
      const w = args.width || 1920;
      const h = args.height || 1080;
      const docName = args.document_name;

      const jsx = `
        var docPreset = new DocumentPreset();
        docPreset.title = "${docName.replace(/"/g, '\\"')}";
        docPreset.width = ${w};
        docPreset.height = ${h};
        docPreset.colorMode = DocumentColorSpace.RGB;
        var doc = app.documents.addDocument(DocumentPresetType.BasicRGB, docPreset);
        JSON.stringify({ success: true, name: doc.name, width: doc.width, height: doc.height });
      `;

      const result = await VbsRunner.runIllustratorScript(jsx, true);
      return {
        content: [{ type: 'text', text: JSON.stringify(result, null, 2) }],
        isError: !result.success
      };
    }
  },

  {
    name: 'ai_trace_and_clean_sketch',
    description: 'Vectorizes a raster image (sketch, concept art, character illustration) inside Adobe Illustrator using the native Image Trace engine, expanding it into clean editable vector paths.',
    inputSchema: {
      type: 'object',
      properties: {
        image_path: {
          type: 'string',
          description: 'Absolute or relative path to the PNG, JPG, or PSD image to vectorize'
        },
        preset: {
          type: 'string',
          enum: ['color_16', 'line_art', 'silhouette', 'high_fidelity'],
          description: 'Vectorization preset profile (default: color_16)'
        },
        ignore_white: {
          type: 'boolean',
          description: 'Whether to ignore white background pixels (default: true)'
        }
      },
      required: ['image_path']
    },
    handler: async (args: any) => {
      const resolvedImg = path.resolve(args.image_path).replace(/\\/g, '/');
      if (!fs.existsSync(resolvedImg)) {
        return { content: [{ type: 'text', text: `Image file not found: ${resolvedImg}` }], isError: true };
      }

      const preset = args.preset || 'color_16';
      const ignoreWhite = args.ignore_white !== false;

      const jsx = `
        var imgFile = new File("${resolvedImg}");
        if (!imgFile.exists) {
          JSON.stringify({ success: false, error: "File not found: " + imgFile.fsName });
        } else {
          var doc;
          if (app.documents.length === 0) {
            doc = app.documents.add(DocumentColorSpace.RGB, 2000, 2000);
          } else {
            doc = app.activeDocument;
          }

          var placed = doc.placedItems.add();
          placed.file = imgFile;
          placed.embed();

          var raster = doc.rasterItems[0];
          var trace = raster.trace();
          var opts = trace.tracing.tracingOptions;

          // Preset customization
          if ("${preset}" === "line_art") {
            opts.tracingMode = TracingModeType.TRACINGMODEBLACKANDWHITE;
            opts.threshold = 128;
          } else if ("${preset}" === "silhouette") {
            opts.tracingMode = TracingModeType.TRACINGMODEBLACKANDWHITE;
            opts.threshold = 180;
          } else {
            opts.tracingMode = TracingModeType.TRACINGMODECOLOR;
            opts.maxColors = 16;
          }

          opts.ignoreWhite = ${ignoreWhite};
          app.redraw();

          // Expand trace to standard paths
          var expandedGroup = trace.tracing.expandTracing();

          JSON.stringify({
            success: true,
            message: "Image trace successfully expanded into editable vector paths",
            preset_used: "${preset}",
            paths_count: doc.pathItems.length
          });
        }
      `;

      const result = await VbsRunner.runIllustratorScript(jsx, true);
      return {
        content: [{ type: 'text', text: JSON.stringify(result, null, 2) }],
        isError: !result.success
      };
    }
  },

  {
    name: 'ai_auto_rig_slice',
    description: 'Anatomically analyzes vector artwork in Adobe Illustrator and slices/sorts paths by spatial coordinates into a Character Animator ready layer structure (+Head, Torso, +Left Arm, +Right Arm, +Left Leg, +Right Leg).',
    inputSchema: {
      type: 'object',
      properties: {
        character_name: {
          type: 'string',
          description: 'Name for the root character group (e.g. "Hero")'
        },
        target_file: {
          type: 'string',
          description: 'Optional path to save the resulting .ai file'
        }
      },
      required: ['character_name']
    },
    handler: async (args: any) => {
      const charName = args.character_name;
      const targetFile = args.target_file ? path.resolve(args.target_file).replace(/\\/g, '/') : null;

      const jsx = `
        if (app.documents.length === 0) {
          JSON.stringify({ success: false, error: "No active document open in Illustrator" });
        } else {
          var doc = app.activeDocument;
          
          // Calculate overall artwork bounding box
          var minX = 999999, maxX = -999999, minY = 999999, maxY = -999999;
          for (var i = 0; i < doc.pageItems.length; i++) {
            var item = doc.pageItems[i];
            if (item.parent.name && item.parent.name.indexOf("+") === 0) continue;
            var b = item.geometricBounds; // [left, top, right, bottom]
            if (b[0] < minX) minX = b[0];
            if (b[1] > maxY) maxY = b[1];
            if (b[2] > maxX) maxX = b[2];
            if (b[3] < minY) minY = b[3];
          }

          var totalHeight = maxY - minY;
          var totalWidth = maxX - minX;
          var headThreshold = maxY - (totalHeight * 0.38);
          var pelvisThreshold = minY + (totalHeight * 0.42);
          var centerX = minX + (totalWidth / 2);

          // Create Character Animator hierarchy
          var rootLayer = doc.layers.add();
          rootLayer.name = "${charName}";
          
          var headLayer = doc.layers.add();
          headLayer.name = "+Head";
          
          var rArmLayer = doc.layers.add();
          rArmLayer.name = "+Right Arm";

          var lArmLayer = doc.layers.add();
          lArmLayer.name = "+Left Arm";

          var torsoLayer = doc.layers.add();
          torsoLayer.name = "Torso";

          var rLegLayer = doc.layers.add();
          rLegLayer.name = "+Right Leg";

          var lLegLayer = doc.layers.add();
          lLegLayer.name = "+Left Leg";

          // Classify and move paths into layers
          var itemsToMove = [];
          for (var j = 0; j < doc.pageItems.length; j++) {
            var it = doc.pageItems[j];
            if (it.layer === rootLayer || it.layer === headLayer || it.layer === torsoLayer || it.layer === lArmLayer || it.layer === rArmLayer || it.layer === lLegLayer || it.layer === rLegLayer) continue;
            itemsToMove.push(it);
          }

          var sortedCount = 0;
          for (var k = 0; k < itemsToMove.length; k++) {
            var pi = itemsToMove[k];
            var bounds = pi.geometricBounds;
            var centerY = (bounds[1] + bounds[3]) / 2;
            var itemX = (bounds[0] + bounds[2]) / 2;

            if (centerY > headThreshold) {
              pi.move(headLayer, ElementPlacement.PLACEATEND);
            } else if (centerY < pelvisThreshold) {
              if (itemX < centerX) {
                pi.move(lLegLayer, ElementPlacement.PLACEATEND);
              } else {
                pi.move(rLegLayer, ElementPlacement.PLACEATEND);
              }
            } else {
              if (itemX < minX + (totalWidth * 0.28)) {
                pi.move(lArmLayer, ElementPlacement.PLACEATEND);
              } else if (itemX > minX + (totalWidth * 0.72)) {
                pi.move(rArmLayer, ElementPlacement.PLACEATEND);
              } else {
                pi.move(torsoLayer, ElementPlacement.PLACEATEND);
              }
            }
            sortedCount++;
          }

          ${targetFile ? `
            var saveOpts = new IllustratorSaveOptions();
            saveOpts.compatibility = Compatibility.ILLUSTRATOR24;
            saveOpts.pdfCompatible = true;
            doc.saveAs(new File("${targetFile}"), saveOpts);
          ` : ''}

          JSON.stringify({
            success: true,
            character: "${charName}",
            layers_configured: ["+Head", "+Right Arm", "Torso", "+Left Arm", "+Right Leg", "+Left Leg"],
            items_sorted: sortedCount,
            saved_to: "${targetFile || 'unsaved'}"
          });
        }
      `;

      const result = await VbsRunner.runIllustratorScript(jsx, true);
      return {
        content: [{ type: 'text', text: JSON.stringify(result, null, 2) }],
        isError: !result.success
      };
    }
  },

  {
    name: 'ai_apply_color_palette',
    description: 'Harmonizes and shifts colors across the active character illustration in Illustrator using designer color palettes (cyberpunk, pastel, anime, retro, monochrome) or custom hex colors.',
    inputSchema: {
      type: 'object',
      properties: {
        palette: {
          type: 'string',
          enum: ['cyberpunk', 'pastel', 'anime', 'retro', 'monochrome'],
          description: 'Predefined harmonious color scheme'
        },
        custom_hex_colors: {
          type: 'array',
          items: { type: 'string' },
          description: 'Optional array of custom HEX color codes (e.g. ["#ff5500", "#00aaff"])'
        }
      }
    },
    handler: async (args: any) => {
      const paletteName = args.palette || 'anime';
      const selectedPalette = COLOR_PALETTES[paletteName] || COLOR_PALETTES.anime;

      const colorsToInject = args.custom_hex_colors || [
        selectedPalette.primary,
        selectedPalette.secondary,
        selectedPalette.accent,
        selectedPalette.dark
      ];

      // Convert hex strings to RGB
      const rgbArray = colorsToInject.map((hex: string) => {
        const clean = hex.replace('#', '');
        return [
          parseInt(clean.substring(0, 2), 16) || 0,
          parseInt(clean.substring(2, 4), 16) || 0,
          parseInt(clean.substring(4, 6), 16) || 0
        ];
      });

      const jsx = `
        if (app.documents.length === 0) {
          JSON.stringify({ success: false, error: "No active document open in Illustrator" });
        } else {
          var doc = app.activeDocument;
          var colors = ${JSON.stringify(rgbArray)};
          var count = 0;

          for (var i = 0; i < doc.pathItems.length; i++) {
            var path = doc.pathItems[i];
            if (path.filled) {
              var targetRgb = colors[i % colors.length];
              var c = new RGBColor();
              c.red = targetRgb[0];
              c.green = targetRgb[1];
              c.blue = targetRgb[2];
              path.fillColor = c;
              count++;
            }
          }

          app.redraw();
          JSON.stringify({
            success: true,
            palette_applied: "${paletteName}",
            paths_recolored: count
          });
        }
      `;

      const result = await VbsRunner.runIllustratorScript(jsx, true);
      return {
        content: [{ type: 'text', text: JSON.stringify(result, null, 2) }],
        isError: !result.success
      };
    }
  },

  {
    name: 'ai_export_character_package',
    description: 'Exports the active character illustration from Illustrator into a ready-to-import Character Animator .ai file and an optimized preview .svg simultaneously.',
    inputSchema: {
      type: 'object',
      properties: {
        output_dir: {
          type: 'string',
          description: 'Directory where the package files should be written'
        },
        character_name: {
          type: 'string',
          description: 'Base name for the exported files (e.g. "Hero")'
        }
      },
      required: ['output_dir', 'character_name']
    },
    handler: async (args: any) => {
      const outDir = path.resolve(args.output_dir).replace(/\\/g, '/');
      const baseName = args.character_name;
      fs.mkdirSync(path.resolve(args.output_dir), { recursive: true });

      const aiOut = `${outDir}/${baseName}.ai`;
      const svgOut = `${outDir}/${baseName}.svg`;

      const jsx = `
        if (app.documents.length === 0) {
          JSON.stringify({ success: false, error: "No active document open in Illustrator" });
        } else {
          var doc = app.activeDocument;

          // Export .AI for Character Animator
          var aiOpts = new IllustratorSaveOptions();
          aiOpts.compatibility = Compatibility.ILLUSTRATOR24;
          aiOpts.pdfCompatible = true;
          doc.saveAs(new File("${aiOut}"), aiOpts);

          // Export .SVG for preview
          var svgOpts = new ExportOptionsSVG();
          svgOpts.embedRasterImages = true;
          svgOpts.cssProperties = SVGCSSPropertyLocation.STYLEATTRIBUTES;
          doc.exportFile(new File("${svgOut}"), ExportType.SVG, svgOpts);

          JSON.stringify({
            success: true,
            character: "${baseName}",
            exported_ai: "${aiOut}",
            exported_svg: "${svgOut}"
          });
        }
      `;

      const result = await VbsRunner.runIllustratorScript(jsx, true);
      return {
        content: [{ type: 'text', text: JSON.stringify(result, null, 2) }],
        isError: !result.success
      };
    }
  }
];
