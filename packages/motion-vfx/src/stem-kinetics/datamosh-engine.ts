import { DatamoshSpec, DatamoshSpecInput, DatamoshSpecSchema } from "./stem-kinetics-types.js";

/**
 * Motor de Datamosh Y2K & P-Frame Motion Vector Glitch (Fase 29).
 * Emula la pérdida deliberada de I-Frames y retención de vectores de movimiento
 * de compresión MPEG-2 / MPEG-4 vista en producciones de Tainy (DATA) y estética Y2K.
 */
export class DatamoshEngine {
  /**
   * Calcula el número de macrobloques horizontales y verticales para la compresión.
   */
  public static computeMacroblockCounts(
    compW: number,
    compH: number,
    macroblockSize: 8 | 16
  ): { horizontalBlocks: number; verticalBlocks: number } {
    const w = compW > 0 ? compW : 1920;
    const h = compH > 0 ? compH : 1080;
    return {
      horizontalBlocks: Math.floor(w / macroblockSize),
      verticalBlocks: Math.floor(h / macroblockSize),
    };
  }

  /**
   * Genera código ExtendScript nativo para inyectar una capa de ajuste de datamosh con macrobloques y mapa de desplazamiento.
   */
  public static exportToExtendScript(
    spec: DatamoshSpecInput,
    options?: { compVarName?: string; sourceLayerVarName?: string; destLayerVarName?: string }
  ): string[] {
    const validated = DatamoshSpecSchema.parse(spec);
    const comp = options?.compVarName ?? "comp";
    const srcLyr = options?.sourceLayerVarName ?? "videoLyrA";
    const destLyr = options?.destLayerVarName ?? "videoLyrB";

    const cutT = validated.cutTimeSeconds;
    const endT = validated.cutTimeSeconds + validated.durationSeconds;

    const lines: string[] = [
      `  // === Y2K DATAMOSH P-FRAME GLITCH: ${validated.id} (${validated.macroblockSize}px Macroblocks) ===`,
      "  try {",
      `    if (${comp}) {`,
      `      var moshAdj = ${comp}.layers.addSolid([0, 0, 0], '[DATAMOSH ARTIFACTS] ' + '${validated.id}', ${comp}.width, ${comp}.height, 1.0);`,
      "      if (moshAdj) {",
      "        moshAdj.adjustmentLayer = true;",
      `        moshAdj.startTime = ${cutT.toFixed(4)};`,
      `        moshAdj.inPoint = ${cutT.toFixed(4)};`,
      `        moshAdj.outPoint = ${endT.toFixed(4)};`,
      "        moshAdj.motionBlur = true;",
      "",
      "        // 1. Cuantización de macrobloques MPEG (ADBE Mosaic)",
      '        var mosaicFx = moshAdj.property("Effects").addProperty("ADBE Mosaic");',
      "        if (mosaicFx) {",
      `          var hBlocks = Math.floor(${comp}.width / ${validated.macroblockSize});`,
      `          var vBlocks = Math.floor(${comp}.height / ${validated.macroblockSize});`,
      "          mosaicFx.property(\"Horizontal Blocks\").setValue(hBlocks);",
      "          mosaicFx.property(\"Vertical Blocks\").setValue(vBlocks);",
      "        }",
      "",
      "        // 2. Desplazamiento por vectores de movimiento (ADBE Displacement Map)",
      '        var dispFx = moshAdj.property("Effects").addProperty("ADBE Displacement Map");',
      "        if (dispFx) {",
      `          var maxDispProp = dispFx.property("Max Horizontal Displacement");`,
      `          maxDispProp.setValueAtTime(${cutT.toFixed(4)}, ${validated.displacementIntensity.toFixed(1)});`,
      `          maxDispProp.setValueAtTime(${endT.toFixed(4)}, 0.0);`,
      "",
      `          var maxVertProp = dispFx.property("Max Vertical Displacement");`,
      `          maxVertProp.setValueAtTime(${cutT.toFixed(4)}, ${(validated.displacementIntensity * 0.75).toFixed(1)});`,
      `          maxVertProp.setValueAtTime(${endT.toFixed(4)}, 0.0);`,
      "        }",
      "      }",
      "    }",
      "  } catch(e) {",
      `    alert('Error in DatamoshEngine: ' + e.toString());`,
      "  }",
    ];

    return lines;
  }
}
