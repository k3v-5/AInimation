import fs from 'fs';
import path from 'path';

export interface SceneManifestLayer {
  name: string;
  filePath: string;
  layerType: 'character' | 'background' | 'prop' | 'foreground' | 'light' | 'null_controller';
  zDepth?: number;
  scaleCompensation?: boolean;
  opacity?: number;
  expressions?: Array<{
    property: 'Position' | 'Scale' | 'Rotation' | 'Opacity' | 'Time Remap';
    type: 'squash_and_stretch' | 'camera_shake' | 'audio_reactive_bounce' | 'blink_cycle' | 'floating_idle' | 'custom';
    code?: string;
    params?: Record<string, any>;
  }>;
}

export interface SceneManifestAudio {
  name?: string;
  filePath: string;
  inPoint?: number;
  outPoint?: number;
  volumeDb?: number;
}

export interface SceneManifestCamera {
  enabled: boolean;
  createController?: boolean;
  focalLengthMm?: number;
  depthOfField?: boolean;
  zoomSpeed?: number;
}

export interface SceneManifest {
  schemaVersion: string;
  sceneName: string;
  width: number;
  height: number;
  fps: number;
  durationSeconds: number;
  layers: SceneManifestLayer[];
  audioTracks?: SceneManifestAudio[];
  lipSyncMarkersPath?: string;
  camera?: SceneManifestCamera;
  metadata?: Record<string, any>;
}

export class SceneManifestBuilder {
  /**
   * Generates a standard After Effects expression by type and parameters.
   */
  public static getExpressionSnippet(type: string, params: Record<string, any> = {}): string {
    switch (type) {
      case 'squash_and_stretch': {
        const maxAmp = params.maxAmplitude || 15;
        const freq = params.frequency || 3.0;
        const decay = params.decay || 5.0;
        return `// Squash & Stretch Expression
var maxAmp = ${maxAmp};
var freq = ${freq};
var decay = ${decay};
var n = 0;
if (numKeys > 0) {
    n = nearestKey(time).index;
    if (key(n).time > time) n--;
}
if (n > 0) {
    var t = time - key(n).time;
    var amp = maxAmp * Math.sin(freq * t * 2 * Math.PI) / Math.exp(decay * t);
    [value[0] + amp, value[1] - amp];
} else {
    value;
}`;
      }

      case 'camera_shake': {
        const freq = params.frequency || 2.5;
        const amp = params.amplitude || 18;
        return `// Camera Shake Wiggle
wiggle(${freq}, ${amp});`;
      }

      case 'audio_reactive_bounce': {
        const factor = params.scaleMultiplier || 1.2;
        const baseScale = params.baseScale || 100;
        return `// Audio Reactive Bounce
try {
    var audioLayer = thisComp.layer("Audio Amplitude");
    var audioVal = audioLayer.effect("Both Channels")("Slider").value;
    var bounce = audioVal * ${factor};
    [${baseScale} + bounce, ${baseScale} + bounce];
} catch(e) {
    value;
}`;
      }

      case 'blink_cycle': {
        const interval = params.intervalSeconds || 3.5;
        return `// Procedural Eye Blink Cycle
var interval = ${interval};
var seed = index * 37.19;
seedRandom(seed, true);
var rnd = random(-0.8, 0.8);
var cycle = interval + rnd;
var blinkDuration = 0.14;
var phase = time % cycle;
(phase < blinkDuration) ? 0 : 100;`;
      }

      case 'floating_idle': {
        const speed = params.speed || 1.5;
        const amp = params.amplitude || 12;
        return `// Organic 2D/2.5D Idle Float
var offset = Math.sin(time * ${speed} * Math.PI) * ${amp};
[value[0], value[1] + offset, value[2]];`;
      }

      default:
        return params.customCode || 'value;';
    }
  }

  /**
   * Converts a Scene Manifest object into an autonomous, robust ExtendScript (.jsx) file
   * that can be executed directly in Adobe After Effects to assemble the entire 2.5D composition.
   */
  public static toExtendScript(manifest: SceneManifest): string {
    const w = manifest.width || 1920;
    const h = manifest.height || 1080;
    const dur = manifest.durationSeconds || 10;
    const fps = manifest.fps || 24;
    const sceneName = (manifest.sceneName || 'Animation_Scene').replace(/"/g, '\\"');

    // Default camera distance for a 50mm lens in AE at 1080p is ~1777px
    const cameraDistance = (w / (2 * Math.tan((39.6 * Math.PI) / 360)));

    let layerImportsJs = '';
    const layers = manifest.layers || [];

    for (let i = 0; i < layers.length; i++) {
      const l = layers[i];
      const layerName = l.name.replace(/"/g, '\\"');
      const filePath = path.resolve(l.filePath).replace(/\\/g, '/');
      const zDepth = l.zDepth ?? (
        l.layerType === 'background' ? 1500 :
        l.layerType === 'prop' ? 400 :
        l.layerType === 'foreground' ? -400 : 0
      );

      // Scale compensation maintains the apparent size when pushing back in Z space
      const scaleComp = l.scaleCompensation !== false;
      const scaleFactor = scaleComp ? ((cameraDistance + zDepth) / cameraDistance) * 100 : 100;

      let exprInjections = '';
      if (l.expressions && l.expressions.length > 0) {
        for (const exp of l.expressions) {
          const code = (exp.code || this.getExpressionSnippet(exp.type, exp.params || {})).replace(/\\/g, '\\\\').replace(/"/g, '\\"').replace(/\n/g, '\\n');
          exprInjections += `
        try {
            var prop = currentLayer.property("${exp.property}");
            if (prop && prop.canSetExpression) {
                prop.expression = "${code}";
            }
        } catch(e) { $.writeln("Expression warning on layer '${layerName}': " + e.toString()); }
`;
        }
      }

      layerImportsJs += `
    // Layer ${i + 1}: ${layerName} (${l.layerType}, Z: ${zDepth})
    try {
        var fileRef = new File("${filePath}");
        if (fileRef.exists) {
            var importOpts = new ImportOptions(fileRef);
            if (importOpts.canImportAs(ImportAsType.COMP)) {
                importOpts.importAs = ImportAsType.COMP;
            }
            var item = app.project.importFile(importOpts);
            var currentLayer = comp.layers.add(item);
            currentLayer.name = "${layerName}";
            currentLayer.threeDLayer = true;

            // Positioning in 2.5D space
            var posX = comp.width / 2;
            var posY = comp.height / 2;
            var posZ = ${zDepth};
            currentLayer.property("Position").setValue([posX, posY, posZ]);

            // Scale compensation
            var baseScale = ${scaleFactor.toFixed(2)};
            currentLayer.property("Scale").setValue([baseScale, baseScale, baseScale]);

            ${l.opacity !== undefined ? `currentLayer.property("Opacity").setValue(${l.opacity});` : ''}

            ${exprInjections}
        } else {
            $.writeln("Warning: File not found for layer '${layerName}': ${filePath}");
        }
    } catch (err) {
        $.writeln("Error adding layer '${layerName}': " + err.toString());
    }
`;
    }

    // Camera setup
    const hasCamera = manifest.camera?.enabled !== false;
    let cameraSetupJs = '';
    if (hasCamera) {
      cameraSetupJs = `
    // 3D Camera & Controller Setup
    try {
        var cam = comp.layers.addCamera("${sceneName}_Camera", [comp.width / 2, comp.height / 2]);
        var camPos = [comp.width / 2, comp.height / 2, -${cameraDistance.toFixed(2)}];
        cam.property("Position").setValue(camPos);
        cam.property("Point of Interest").setValue([comp.width / 2, comp.height / 2, 0]);

        ${manifest.camera?.depthOfField ? `
        cam.property("Camera Options").property("Depth of Field").setValue(1);
        cam.property("Camera Options").property("Focus Distance").setValue(${cameraDistance.toFixed(2)});
        cam.property("Camera Options").property("Aperture").setValue(45);
        ` : ''}

        // 3D Null Controller for smooth cinematography
        var camController = comp.layers.addNull();
        camController.name = "Camera_Controller";
        camController.threeDLayer = true;
        camController.property("Position").setValue([comp.width / 2, comp.height / 2, 0]);
        cam.parent = camController;
    } catch(e) {
        $.writeln("Camera setup warning: " + e.toString());
    }
`;
    }

    // Audio setup
    let audioSetupJs = '';
    const audioTracks = manifest.audioTracks || [];
    for (let i = 0; i < audioTracks.length; i++) {
      const a = audioTracks[i];
      const audioPath = path.resolve(a.filePath).replace(/\\/g, '/');
      const aName = (a.name || `Audio_${i + 1}`).replace(/"/g, '\\"');
      audioSetupJs += `
    // Audio Track: ${aName}
    try {
        var aFile = new File("${audioPath}");
        if (aFile.exists) {
            var aItem = app.project.importFile(new ImportOptions(aFile));
            var aLayer = comp.layers.add(aItem);
            aLayer.name = "${aName}";
            ${a.inPoint !== undefined ? `aLayer.startTime = ${a.inPoint};` : ''}
        }
    } catch(e) { $.writeln("Audio import error: " + e.toString()); }
`;
    }

    // Lip-sync markers script import if present
    let lipSyncJs = '';
    if (manifest.lipSyncMarkersPath) {
      const markersPath = path.resolve(manifest.lipSyncMarkersPath).replace(/\\/g, '/');
      lipSyncJs = `
    // Import Lip-Sync Markers from JSX
    try {
        var markerFile = new File("${markersPath}");
        if (markerFile.exists && markerFile.name.match(/\\.jsx$/i)) {
            $.evalFile(markerFile);
        }
    } catch(e) { $.writeln("Lip sync markers import warning: " + e.toString()); }
`;
    }

    return `// ExtendScript generated by AdobeEngineSuit (Phase 5 - 2.5D Stage & Interop)
(function() {
    app.beginUndoGroup("Assemble 2.5D Scene: ${sceneName}");
    try {
        // Create Composition
        var comp = app.project.items.addComp("${sceneName}", ${w}, ${h}, 1.0, ${dur}, ${fps});
        if (!comp) {
            throw new Error("Failed to create composition '${sceneName}'");
        }

        ${cameraSetupJs}
        ${layerImportsJs}
        ${audioSetupJs}
        ${lipSyncJs}

        // Select and activate composition in viewer
        comp.openInViewer();
        $.writeln(JSON.stringify({ status: "SUCCESS", message: "Composition created successfully", compName: comp.name }));
    } catch(err) {
        $.writeln(JSON.stringify({ status: "ERROR", error: err.toString() }));
    }
    app.endUndoGroup();
})();
`;
  }

  /**
   * Generates a Scene Manifest JSON file on disk along with the corresponding ExtendScript (.jsx) constructor.
   */
  public static saveManifestAndScript(manifest: SceneManifest, outJsonPath: string): { jsonPath: string; jsxPath: string } {
    const resolvedJson = path.resolve(outJsonPath);
    const baseDir = path.dirname(resolvedJson);
    fs.mkdirSync(baseDir, { recursive: true });

    const baseName = path.basename(resolvedJson, path.extname(resolvedJson));
    const resolvedJsx = path.join(baseDir, `${baseName}.jsx`);

    // Ensure schema version
    manifest.schemaVersion = manifest.schemaVersion || '1.0.0';

    fs.writeFileSync(resolvedJson, JSON.stringify(manifest, null, 2), 'utf-8');
    const scriptContent = this.toExtendScript(manifest);
    fs.writeFileSync(resolvedJsx, scriptContent, 'utf-8');

    return { jsonPath: resolvedJson, jsxPath: resolvedJsx };
  }
}
