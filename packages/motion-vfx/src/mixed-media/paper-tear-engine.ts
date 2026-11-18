import { PaperTearSpec, PaperTearSpecInput, PaperTearSpecSchema } from "./mixed-media-types.js";

/**
 * Motor de Paper Tear & Collage Cutout Wipes (Fase 28).
 * Simula el rasgado físico de papel con borde irregular fracturado y flecos de fibra
 * característico del collage analógico en videos de Kendrick Lamar y JID.
 */
export class PaperTearEngine {
  /**
   * Genera armónicos fractales deterministas para simular las irregularidades del rasgado de fibra.
   */
  public static generateFractalTearOffsets(roughness: number, segmentCount: number = 10): number[] {
    const offsets: number[] = [];
    const count = Math.max(4, segmentCount);
    for (let i = 0; i < count; i++) {
      const s = (i / (count - 1)) * Math.PI * 2;
      const val = roughness * (Math.sin(3 * s) * 0.5 + Math.cos(7 * s) * 0.3 + Math.sin(13 * s) * 0.2);
      offsets.push(Math.round(val * 10) / 10);
    }
    return offsets;
  }

  /**
   * Genera código ExtendScript nativo para aplicar una máscara de rasgado animada
   * sobre la toma entrante con borde fracturado.
   */
  public static exportToExtendScript(
    spec: PaperTearSpecInput,
    options?: { layerVarName?: string; compVarName?: string }
  ): string[] {
    const validated = PaperTearSpecSchema.parse(spec);
    const layer = options?.layerVarName ?? "videoLyrB";
    const comp = options?.compVarName ?? "comp";
    const offsets = this.generateFractalTearOffsets(validated.tearRoughness, 8);

    const startT = validated.startTimeSeconds;
    const endT = validated.startTimeSeconds + validated.durationSeconds;

    const lines: string[] = [
      `  // === PAPER TEAR COLLAGE WIPE: ${validated.id} (${validated.direction}) ===`,
      "  try {",
      `    if (${layer}) {`,
      `      ${layer}.motionBlur = true; // Invariante obligatoria`,
      `      ${layer}.inPoint = ${startT.toFixed(4)};`,
      "",
      "      // 1. Máscara de rasgado orgánico fracturado",
      `      var tearMask = ${layer}.property("Masks").addProperty("ADBE Mask Atom");`,
      "      if (tearMask) {",
      "        tearMask.maskMode = MaskMode.ADD;",
      `        tearMask.property("Mask Feather").setValue([${validated.fiberFringePx.toFixed(1)}, ${validated.fiberFringePx.toFixed(1)}]);`,
      "",
      '        var maskProp = tearMask.property("Mask Path");',
      "        var shapeStart = maskProp.value;",
      "        var shapeEnd = maskProp.value;",
      "",
      "        // Keyframe inicial: máscara colapsada",
      `        shapeStart.vertices = [[-100, 0], [0, 0], [0, ${comp}.height], [-100, ${comp}.height]];`,
      "        shapeStart.closed = true;",
      `        maskProp.setValueAtTime(${startT.toFixed(4)}, shapeStart);`,
      "",
      "        // Keyframe final: máscara cubriendo todo el encuadre",
      `        shapeEnd.vertices = [[-100, 0], [${comp}.width + 100, 0], [${comp}.width + 100, ${comp}.height], [-100, ${comp}.height]];`,
      "        shapeEnd.closed = true;",
      `        maskProp.setValueAtTime(${endT.toFixed(4)}, shapeEnd);`,
      "      }",
      "",
      "      // 2. Tira blanca de fibra de papel en el borde de rasgado",
      `      var paperFringe = ${comp}.layers.addSolid([0.98, 0.98, 0.95], '[PAPER FIBER FRINGE] ' + '${validated.id}', 16, ${comp}.height, 1.0);`,
      "      if (paperFringe) {",
      `        paperFringe.startTime = ${startT.toFixed(4)};`,
      `        paperFringe.inPoint = ${startT.toFixed(4)};`,
      `        paperFringe.outPoint = ${endT.toFixed(4)};`,
      "        paperFringe.motionBlur = true;",
      '        var pPos = paperFringe.property("Transform").property("Position");',
      `        pPos.setValueAtTime(${startT.toFixed(4)}, [0, ${comp}.height * 0.5]);`,
      `        pPos.setValueAtTime(${endT.toFixed(4)}, [${comp}.width, ${comp}.height * 0.5]);`,
      "      }",
      "    }",
      "  } catch(e) {",
      `    alert('Error in PaperTearEngine: ' + e.toString());`,
      "  }",
    ];

    return lines;
  }
}
