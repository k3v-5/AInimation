import crypto from "crypto";
import {
  CentrifugalGyroRollSpecInput,
  CentrifugalGyroRollSpecSchema,
  DynamicMechanicsPlan,
  DynamicMechanicsPlanSchema,
  LensBreathingSpecInput,
  LensBreathingSpecSchema,
  WhipPanMatchCutSpecInput,
  WhipPanMatchCutSpecSchema,
} from "./mechanics-types.js";
import { GyroRollEngine } from "./gyro-roll-engine.js";
import { WhipPanEngine } from "./whip-pan-engine.js";
import { LensBreathingEngine } from "./lens-breathing-engine.js";

export interface CompileDynamicMechanicsOptions {
  id: string;
  fps?: number;
  gyroRoll?: CentrifugalGyroRollSpecInput;
  whipPan?: WhipPanMatchCutSpecInput;
  lensBreathing?: LensBreathingSpecInput;
  compVarName?: string;
  layerVarName?: string;
  sourceLayerVarName?: string;
  destLayerVarName?: string;
  gyroLayerVarName?: string;
  breathingLayerVarName?: string;
}

/**
 * Orquestador consolidado de mecánica de cámara y ópticas dinámicas (Fase 26).
 */
export class DynamicMechanicsOrchestrator {
  /**
   * Compila un plan mecánico completo con código ExtendScript y verificación SHA-256.
   */
  public static compilePlan(options: CompileDynamicMechanicsOptions): DynamicMechanicsPlan {
    const fps = options.fps ?? 30.0;
    const compVar = options.compVarName ?? "comp";
    const layerVar = options.layerVarName ?? "videoLyr";
    const srcVar = options.sourceLayerVarName ?? layerVar;
    const destVar = options.destLayerVarName ?? layerVar;
    const gyroVar = options.gyroLayerVarName ?? srcVar;
    const breathingVar = options.breathingLayerVarName ?? destVar;

    const parsedGyro = options.gyroRoll ? CentrifugalGyroRollSpecSchema.parse(options.gyroRoll) : undefined;
    const parsedWhip = options.whipPan ? WhipPanMatchCutSpecSchema.parse(options.whipPan) : undefined;
    const parsedBreathing = options.lensBreathing
      ? LensBreathingSpecSchema.parse(options.lensBreathing)
      : undefined;

    const lines: string[] = [
      "// ============================================================================",
      "//  FASE 26: DYNAMIC OPTICS & MECHANICS (GYRO ROLLS, WHIP-PANS & BREATHING)",
      `//  ID: ${options.id} | FPS: ${fps}`,
      "// ============================================================================",
      "",
      `app.beginUndoGroup('Apply Dynamic Mechanics: ${options.id}');`,
      "try {",
      `  if (${compVar}) ${compVar}.motionBlur = true; // Invariante obligatoria`,
      "",
    ];

    // 1. Giroscopio Centrífugo 360°
    if (parsedGyro) {
      lines.push("  // --- 1. CENTRIFUGAL GYRO BARREL ROLL ---");
      lines.push(...GyroRollEngine.exportToExtendScript(parsedGyro, fps, { layerVarName: gyroVar }));
      lines.push("");
    }

    // 2. Respiración Óptica en Tirón de Foco
    if (parsedBreathing) {
      lines.push("  // --- 2. PROCEDURAL LENS BREATHING ---");
      lines.push(...LensBreathingEngine.exportToExtendScript(parsedBreathing, { layerVarName: breathingVar }));
      lines.push("");
    }

    // 3. Whip-Pan Match Cut Direccional
    if (parsedWhip) {
      lines.push("  // --- 3. DIRECTIONAL WHIP-PAN MATCH CUT ---");
      lines.push(
        ...WhipPanEngine.exportToExtendScript(parsedWhip, {
          sourceLayerVarName: srcVar,
          destLayerVarName: destVar,
          compVarName: compVar,
        })
      );
      lines.push("");
    }

    lines.push("  app.endUndoGroup();");
    lines.push("} catch(e) {");
    lines.push("  app.endUndoGroup();");
    lines.push("  alert('Error in DynamicMechanicsOrchestrator: ' + e.toString());");
    lines.push("}");

    const hashPayload = JSON.stringify({
      id: options.id,
      fps,
      gyroRoll: parsedGyro,
      whipPan: parsedWhip,
      lensBreathing: parsedBreathing,
    });
    const checksumSha256 = crypto.createHash("sha256").update(hashPayload).digest("hex");

    return DynamicMechanicsPlanSchema.parse({
      id: options.id,
      gyroRoll: parsedGyro,
      whipPan: parsedWhip,
      lensBreathing: parsedBreathing,
      extendScriptLines: lines,
      checksumSha256,
    });
  }
}
