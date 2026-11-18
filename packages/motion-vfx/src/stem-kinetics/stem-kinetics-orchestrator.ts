import crypto from "crypto";
import {
  AspectRatioBreathingSpecInput,
  AspectRatioBreathingSpecSchema,
  DatamoshSpecInput,
  DatamoshSpecSchema,
  StemKineticsPlan,
  StemKineticsPlanSchema,
  SubBassReactionSpecInput,
  SubBassReactionSpecSchema,
} from "./stem-kinetics-types.js";
import { SubBassReactionEngine } from "./sub-bass-reaction-engine.js";
import { AspectRatioBreathingEngine } from "./aspect-ratio-breathing-engine.js";
import { DatamoshEngine } from "./datamosh-engine.js";

export interface CompileStemKineticsOptions {
  id: string;
  fps?: number;
  compVarName?: string;
  layerVarName?: string;
  sourceLayerVarName?: string;
  destLayerVarName?: string;
  subBass?: SubBassReactionSpecInput;
  aspectRatioBreathing?: AspectRatioBreathingSpecInput;
  datamosh?: DatamoshSpecInput;
}

/**
 * Orquestador consolidado de Cinética de Stems de Audio, Aspect Ratio y Datamosh (Fase 29).
 */
export class StemKineticsOrchestrator {
  /**
   * Compila un plan unificado con código ExtendScript y verificación SHA-256 inmutable.
   */
  public static compilePlan(options: CompileStemKineticsOptions): StemKineticsPlan {
    const fps = options.fps ?? 30.0;
    const compVar = options.compVarName ?? "comp";
    const layerVar = options.layerVarName ?? "videoLyr";
    const srcVar = options.sourceLayerVarName ?? layerVar;
    const destVar = options.destLayerVarName ?? layerVar;

    const parsedSubBass = options.subBass ? SubBassReactionSpecSchema.parse(options.subBass) : undefined;
    const parsedAspect = options.aspectRatioBreathing
      ? AspectRatioBreathingSpecSchema.parse(options.aspectRatioBreathing)
      : undefined;
    const parsedDatamosh = options.datamosh ? DatamoshSpecSchema.parse(options.datamosh) : undefined;

    const lines: string[] = [
      "// ============================================================================",
      "//  FASE 29: AUDIO STEMS, DYNAMIC ASPECT RATIO & DATAMOSH Y2K",
      `//  ID: ${options.id} | FPS: ${fps}`,
      "// ============================================================================",
      "",
      `app.beginUndoGroup('Apply Stem Kinetics: ${options.id}');`,
      "try {",
      `  if (${compVar}) ${compVar}.motionBlur = true; // Invariante obligatoria`,
      "",
    ];

    // 1. Reacción sísmica a sub-bajos 808
    if (parsedSubBass) {
      lines.push("  // --- 1. 808 SUB-BASS ELASTIC BOUNCE REACTION ---");
      lines.push(...SubBassReactionEngine.exportToExtendScript(parsedSubBass, fps, { layerVarName: srcVar }));
      lines.push("");
    }

    // 2. Y2K Datamosh & P-Frame Glitch
    if (parsedDatamosh) {
      lines.push("  // --- 2. Y2K DATAMOSH P-FRAME GLITCH ---");
      lines.push(
        ...DatamoshEngine.exportToExtendScript(parsedDatamosh, {
          compVarName: compVar,
          sourceLayerVarName: srcVar,
          destLayerVarName: destVar,
        })
      );
      lines.push("");
    }

    // 3. Dynamic Aspect Ratio Breathing & Letterboxing
    if (parsedAspect) {
      lines.push("  // --- 3. DYNAMIC ASPECT RATIO BREATHING ---");
      lines.push(...AspectRatioBreathingEngine.exportToExtendScript(parsedAspect, { compVarName: compVar }));
      lines.push("");
    }

    lines.push("  app.endUndoGroup();");
    lines.push("} catch(e) {");
    lines.push("  app.endUndoGroup();");
    lines.push("  alert('Error in StemKineticsOrchestrator: ' + e.toString());");
    lines.push("}");

    const hashPayload = JSON.stringify({
      id: options.id,
      fps,
      subBass: parsedSubBass,
      aspectRatioBreathing: parsedAspect,
      datamosh: parsedDatamosh,
    });
    const checksumSha256 = crypto.createHash("sha256").update(hashPayload).digest("hex");

    return StemKineticsPlanSchema.parse({
      id: options.id,
      fps,
      subBass: parsedSubBass,
      aspectRatioBreathing: parsedAspect,
      datamosh: parsedDatamosh,
      extendScriptLines: lines,
      checksumSha256,
    });
  }
}
