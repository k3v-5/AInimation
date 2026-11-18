import crypto from "crypto";
import {
  PosterizeTimeSpec,
  QuantizedSpeedRampSpec,
  StutterFreezeSpec,
  TemporalPlan,
  TemporalPlanSchema,
  TimeRemapKeyframe,
} from "./temporal-types.js";
import { PosterizeTimeEngine } from "./posterize-time-engine.js";
import { SpeedRampEngine } from "./speed-ramp-engine.js";
import { StutterFreezeEngine } from "./stutter-freeze-engine.js";

export interface CompileTemporalOptions {
  id: string;
  posterizeTime?: PosterizeTimeSpec;
  speedRamps?: QuantizedSpeedRampSpec[];
  stutters?: StutterFreezeSpec[];
  targetLayerVarName?: string;
  compVarName?: string;
  fps?: number;
}

/**
 * Orquestador unificado de modulación temporal y estilizado de fotogramas (Fase 21).
 */
export class TemporalOrchestrator {
  /**
   * Compila un plan temporal consolidado con sello SHA-256 y código ExtendScript.
   */
  public static compilePlan(options: CompileTemporalOptions): TemporalPlan {
    const fps = options.fps ?? 30.0;
    const layerVar = options.targetLayerVarName ?? "targetLayer";
    const compVar = options.compVarName ?? "mainComp";

    const lines: string[] = [
      "// ============================================================================",
      "//  FASE 21: TEMPORAL RATE MODULATION & QUANTIZED SPEED RAMPING",
      `//  ID: ${options.id} | FPS: ${fps}`,
      "// ============================================================================",
      "",
      `app.beginUndoGroup('Apply Temporal Stylization: ${options.id}');`,
      "try {",
      `  if (${compVar}) ${compVar}.motionBlur = true; // Invariante obligatoria`,
      `  if (${layerVar}) ${layerVar}.motionBlur = true;`,
      "",
    ];

    let allKeyframes: TimeRemapKeyframe[] = [];

    // 1. Procesar Speed Ramping
    if (options.speedRamps && options.speedRamps.length > 0) {
      lines.push("  // --- 1. QUANTIZED SPEED RAMPING CURVES ---");
      for (const sr of options.speedRamps) {
        let keyframes = SpeedRampEngine.generateTimeRemapKeyframes(sr, fps);

        // Inyectar Stutters si aplican sobre este segmento
        if (options.stutters && options.stutters.length > 0) {
          for (const st of options.stutters) {
            keyframes = StutterFreezeEngine.injectFreezeIntoKeyframes(keyframes, st);
          }
        }

        allKeyframes = keyframes;

        // Inyectar Time Remap en ExtendScript
        lines.push(`  try {`);
        lines.push(`    ${layerVar}.enableTimeRemapping();`);
        lines.push(`    var trProp = ${layerVar}.property("Time Remap");`);
        lines.push(`    if (trProp) {`);
        lines.push(`      while (trProp.numKeys > 0) { trProp.removeKey(1); }`);
        for (const kf of keyframes) {
          lines.push(`      trProp.setValueAtTime(${kf.timelineSeconds.toFixed(3)}, ${kf.sourceSeconds.toFixed(3)});`);
        }
        lines.push(`    }`);
        lines.push(`  } catch(eTr) {}`);
      }
      lines.push("");
    }

    // 2. Procesar Posterize Time
    if (options.posterizeTime) {
      lines.push("  // --- 2. POSTERIZE TIME EFFECT (VARIABLE FRAME RATE) ---");
      lines.push(...PosterizeTimeEngine.exportToExtendScript(options.posterizeTime, { layerVarName: layerVar }));
      lines.push("");
    }

    lines.push("  app.endUndoGroup();");
    lines.push("} catch(e) {");
    lines.push("  app.endUndoGroup();");
    lines.push("  alert('Error en Temporal Orchestrator: ' + e.toString());");
    lines.push("}");

    const hashContent = JSON.stringify({
      id: options.id,
      hasPosterize: !!options.posterizeTime,
      speedRampsCount: options.speedRamps?.length ?? 0,
      stuttersCount: options.stutters?.length ?? 0,
      keyframesCount: allKeyframes.length,
    });
    const checksumSha256 = crypto.createHash("sha256").update(hashContent).digest("hex");

    return TemporalPlanSchema.parse({
      id: options.id,
      posterizeTime: options.posterizeTime,
      speedRamps: options.speedRamps ?? [],
      stutters: options.stutters ?? [],
      timeRemapKeyframes: allKeyframes,
      extendScriptLines: lines,
      checksumSha256,
    });
  }
}
