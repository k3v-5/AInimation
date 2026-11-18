import crypto from "crypto";
import {
  AnamorphicStreakSpecInput,
  AnamorphicStreakSpecSchema,
  FlirThermalSpecInput,
  FlirThermalSpecSchema,
  PhotonicsPlan,
  PhotonicsPlanSchema,
  PrismStarSpecInput,
  PrismStarSpecSchema,
  ShutterDragSpecInput,
  ShutterDragSpecSchema,
} from "./photonics-types.js";
import { ShutterDragEngine } from "./shutter-drag-engine.js";
import { AnamorphicStreakEngine } from "./anamorphic-streak-engine.js";
import { PrismStarEngine } from "./prism-star-engine.js";
import { FlirThermalEngine } from "./flir-thermal-engine.js";

export interface CompilePhotonicsOptions {
  id: string;
  fps?: number;
  compVarName?: string;
  layerVarName?: string;
  shutterLayerVarName?: string;
  thermalLayerVarName?: string;
  shutterDrag?: ShutterDragSpecInput;
  anamorphicStreak?: AnamorphicStreakSpecInput;
  prismStar?: PrismStarSpecInput;
  flirThermal?: FlirThermalSpecInput;
}

/**
 * Orquestador consolidado de Cinematografía Fotónica Nocturna y Artefactos Ópticos (Fase 27).
 */
export class PhotonicsOrchestrator {
  /**
   * Compila un plan fotónico completo con código ExtendScript y verificación SHA-256 inmutable.
   */
  public static compilePlan(options: CompilePhotonicsOptions): PhotonicsPlan {
    const fps = options.fps ?? 30.0;
    const compVar = options.compVarName ?? "comp";
    const baseLayerVar = options.layerVarName ?? "videoLyr";
    const shutterVar = options.shutterLayerVarName ?? baseLayerVar;
    const thermalVar = options.thermalLayerVarName ?? baseLayerVar;

    const parsedShutter = options.shutterDrag ? ShutterDragSpecSchema.parse(options.shutterDrag) : undefined;
    const parsedStreak = options.anamorphicStreak
      ? AnamorphicStreakSpecSchema.parse(options.anamorphicStreak)
      : undefined;
    const parsedStar = options.prismStar ? PrismStarSpecSchema.parse(options.prismStar) : undefined;
    const parsedThermal = options.flirThermal ? FlirThermalSpecSchema.parse(options.flirThermal) : undefined;

    const lines: string[] = [
      "// ============================================================================",
      "//  FASE 27: NOCTURNAL PHOTONICS & OPTICAL ARTEFACTS",
      `//  ID: ${options.id} | FPS: ${fps}`,
      "// ============================================================================",
      "",
      `app.beginUndoGroup('Apply Nocturnal Photonics: ${options.id}');`,
      "try {",
      `  if (${compVar}) ${compVar}.motionBlur = true; // Invariante obligatoria`,
      "",
    ];

    // 1. Shutter Drag & Echo Trails
    if (parsedShutter) {
      lines.push("  // --- 1. SHUTTER DRAG ECHO TRAILS ---");
      lines.push(...ShutterDragEngine.exportToExtendScript(parsedShutter, { layerVarName: shutterVar }));
      lines.push("");
    }

    // 2. FLIR Thermal Vision
    if (parsedThermal) {
      lines.push("  // --- 2. FLIR INFRARED THERMAL VISION ---");
      lines.push(...FlirThermalEngine.exportToExtendScript(parsedThermal, { layerVarName: thermalVar, compVarName: compVar }));
      lines.push("");
    }

    // 3. Anamorphic Streak Flare
    if (parsedStreak) {
      lines.push("  // --- 3. ANAMORPHIC HORIZONTAL STREAK FLARE ---");
      lines.push(
        ...AnamorphicStreakEngine.exportToExtendScript(parsedStreak, {
          compVarName: compVar,
          layerVarName: baseLayerVar,
        })
      );
      lines.push("");
    }

    // 4. Prism Star Diffraction
    if (parsedStar) {
      lines.push("  // --- 4. PRISM STAR CROSS-SCREEN DIFFRACTION ---");
      lines.push(...PrismStarEngine.exportToExtendScript(parsedStar, { compVarName: compVar }));
      lines.push("");
    }

    lines.push("  app.endUndoGroup();");
    lines.push("} catch(e) {");
    lines.push("  app.endUndoGroup();");
    lines.push("  alert('Error in PhotonicsOrchestrator: ' + e.toString());");
    lines.push("}");

    const hashPayload = JSON.stringify({
      id: options.id,
      fps,
      shutterDrag: parsedShutter,
      anamorphicStreak: parsedStreak,
      prismStar: parsedStar,
      flirThermal: parsedThermal,
    });
    const checksumSha256 = crypto.createHash("sha256").update(hashPayload).digest("hex");

    return PhotonicsPlanSchema.parse({
      id: options.id,
      shutterDrag: parsedShutter,
      anamorphicStreak: parsedStreak,
      prismStar: parsedStar,
      flirThermal: parsedThermal,
      extendScriptLines: lines,
      checksumSha256,
    });
  }
}
