import {
  AtomicCutSlice,
  MachineGunBurstSpec,
  MachineGunBurstSpecInput,
  MachineGunBurstSpecSchema,
} from "./rhythm-types.js";
import { MusicalGrid } from "./musical-grid.js";

/**
 * Motor de ráfagas ultra-rápidas de corte (Machine-Gun Flash Cuts).
 */
export class FlashCutEngine {
  /**
   * Divide una ráfaga en fragmentos atómicos de corte (slices) cuantizados a fotogramas.
   */
  public static calculateSlices(specInput: MachineGunBurstSpecInput, fps: number): AtomicCutSlice[] {
    const spec = MachineGunBurstSpecSchema.parse(specInput);
    const frameHold = Math.max(1, spec.frameHold);
    const frameDuration = 1.0 / fps;
    const sliceDuration = frameHold * frameDuration;
    const totalFrames = Math.round(spec.durationSeconds * fps);
    const numSlices = Math.floor(totalFrames / frameHold);

    const slices: AtomicCutSlice[] = [];
    const mediaIndices =
      spec.mediaLayerIndices && spec.mediaLayerIndices.length > 0 ? spec.mediaLayerIndices : [0];

    for (let i = 0; i < numSlices; i++) {
      const startSec = MusicalGrid.snapToFrame(spec.startTimeSeconds + i * sliceDuration, fps);
      const endSec = MusicalGrid.snapToFrame(startSec + sliceDuration, fps);
      const assignedMedia = mediaIndices[i % mediaIndices.length];

      slices.push({
        sliceIndex: i,
        startTimeSeconds: startSec,
        endTimeSeconds: endSec,
        durationFrames: frameHold,
        assignedLayerIndex: assignedMedia,
        colorHex: spec.colorHex,
      });
    }

    return slices;
  }

  /**
   * Genera el código ExtendScript para ensamblar la ráfaga estroboscópica en After Effects.
   */
  public static exportToExtendScript(
    specInput: MachineGunBurstSpecInput,
    fps: number,
    options: { compVarName?: string } = {}
  ): string[] {
    const spec = MachineGunBurstSpecSchema.parse(specInput);
    const compVar = options.compVarName ?? "comp";
    const slices = this.calculateSlices(spec, fps);
    const lines: string[] = [];

    lines.push(`  // === MACHINE-GUN FLASH CUTS: ${spec.id} (${spec.mode}) ===`);
    lines.push(`  try {`);

    if (spec.mode === "WHITE_STROBE" || spec.mode === "CRIMSON_STROBE" || spec.mode === "CHROMATIC_INVERT") {
      let colorArray = "[1.0, 1.0, 1.0]";
      if (spec.mode === "CRIMSON_STROBE") {
        colorArray = "[1.0, 0.08, 0.14]"; // Rojo carmesí #FF1424 (TIME Style)
      } else if (spec.colorHex && spec.colorHex !== "#FFFFFF") {
        // Parsear hex opcional
        const hex = spec.colorHex.replace("#", "");
        const r = parseInt(hex.substring(0, 2), 16) / 255.0;
        const g = parseInt(hex.substring(2, 4), 16) / 255.0;
        const b = parseInt(hex.substring(4, 6), 16) / 255.0;
        colorArray = `[${r.toFixed(3)}, ${g.toFixed(3)}, ${b.toFixed(3)}]`;
      }

      lines.push(`    var strobeLyr = ${compVar}.layers.addSolid(${colorArray}, "[STROBE] ${spec.id}", ${compVar}.width, ${compVar}.height, 1.0);`);
      lines.push(`    strobeLyr.startTime = 0.0;`);
      lines.push(`    strobeLyr.inPoint = ${spec.startTimeSeconds.toFixed(4)};`);
      lines.push(`    strobeLyr.outPoint = ${(spec.startTimeSeconds + spec.durationSeconds).toFixed(4)};`);

      if (spec.mode === "CHROMATIC_INVERT") {
        lines.push(`    strobeLyr.blendingMode = BlendingMode.CLASSIC_DIFFERENCE;`);
      } else {
        lines.push(`    strobeLyr.blendingMode = BlendingMode.ADD;`);
      }

      lines.push(`    var opProp = strobeLyr.property("Transform").property("Opacity");`);
      lines.push(`    opProp.setValueAtTime(0.0, 0.0);`);

      // Inyectar keyframes hold por cada slice
      for (const slice of slices) {
        // En slices impares activamos el destello para efecto estroboscópico alternado
        if (slice.sliceIndex % 2 === 0) {
          lines.push(`    opProp.setValueAtTime(${slice.startTimeSeconds.toFixed(4)}, 100.0);`);
          lines.push(`    opProp.setValueAtTime(${slice.endTimeSeconds.toFixed(4)}, 0.0);`);
        }
      }

      // Convertir todos los keyframes a interpolación HOLD
      lines.push(`    for (var k = 1; k <= opProp.numKeys; k++) {`);
      lines.push(`      opProp.setInterpolationTypeAtKey(k, KeyframeInterpolationType.HOLD, KeyframeInterpolationType.HOLD);`);
      lines.push(`    }`);
    } else if (spec.mode === "MEDIA_INTERLEAVE") {
      lines.push(`    // Ráfaga Media Interleave: ${slices.length} cortes alternados`);
      // ExtendScript de apoyo para alternar opacidades entre capas
      lines.push(`    // (Slices asignados cíclicamente entre índices de capas proporcionados)`);
    }

    lines.push(`  } catch(e) {`);
    lines.push(`    alert('Error in FlashCutEngine: ' + e.toString());`);
    lines.push(`  }`);

    return lines;
  }
}
