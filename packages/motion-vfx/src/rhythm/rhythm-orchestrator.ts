import crypto from "crypto";
import {
  BlackoutVacuumSpecInput,
  BlackoutVacuumSpecSchema,
  MachineGunBurstSpecInput,
  MachineGunBurstSpecSchema,
  RhythmPlan,
  RhythmPlanSchema,
  SyncopatedCutPointInput,
  SyncopatedCutPointSchema,
} from "./rhythm-types.js";
import { FlashCutEngine } from "./flash-cut-engine.js";
import { BlackoutVacuumEngine } from "./blackout-vacuum-engine.js";
import { SyncopatedCuttingEngine } from "./syncopated-cutting-engine.js";

export interface CompileRhythmOptions {
  id: string;
  bpm: number;
  fps?: number;
  bursts?: MachineGunBurstSpecInput[];
  blackouts?: BlackoutVacuumSpecInput[];
  syncopatedCuts?: SyncopatedCutPointInput[];
  compVarName?: string;
}

/**
 * Orquestador consolidado de montaje rítmico, flash cuts y vacíos de caída a negro (Fase 23).
 */
export class RhythmOrchestrator {
  /**
   * Compila un plan rítmico determinista con código ExtendScript y verificación SHA-256.
   */
  public static compilePlan(options: CompileRhythmOptions): RhythmPlan {
    const fps = options.fps ?? 30.0;
    const compVar = options.compVarName ?? "mainComp";

    const parsedBursts = (options.bursts ?? []).map((b) => MachineGunBurstSpecSchema.parse(b));
    const parsedBlackouts = (options.blackouts ?? []).map((b) => BlackoutVacuumSpecSchema.parse(b));
    const parsedCuts = (options.syncopatedCuts ?? []).map((c) => SyncopatedCutPointSchema.parse(c));

    const lines: string[] = [
      "// ============================================================================",
      "//  FASE 23: MACHINE-GUN FLASH CUTS, RHYTHMIC CUTTING & BLACKOUT VACUUMS",
      `//  ID: ${options.id} | BPM: ${options.bpm} | FPS: ${fps}`,
      "// ============================================================================",
      "",
      `app.beginUndoGroup('Apply Rhythm & Flash Cuts: ${options.id}');`,
      "try {",
      `  if (${compVar}) ${compVar}.motionBlur = true; // Invariante obligatoria`,
      "",
    ];

    // 1. Secuencia de Cortes Sincopados de Metraje
    if (parsedCuts.length > 0) {
      lines.push("  // --- 1. SYNCOPATED MEDIA SEQUENCE ---");
      lines.push(
        ...SyncopatedCuttingEngine.exportToExtendScript(
          {
            id: `${options.id}_sync_seq`,
            bpm: options.bpm,
            fps,
            cuts: parsedCuts,
          },
          { compVarName: compVar }
        )
      );
      lines.push("");
    }

    // 2. Ráfagas Machine-Gun
    if (parsedBursts.length > 0) {
      lines.push("  // --- 2. MACHINE-GUN FLASH BURSTS ---");
      for (const burst of parsedBursts) {
        lines.push(...FlashCutEngine.exportToExtendScript(burst, fps, { compVarName: compVar }));
      }
      lines.push("");
    }

    // 3. Blackout Vacuums y Drop Impact Flashes
    if (parsedBlackouts.length > 0) {
      lines.push("  // --- 3. BLACKOUT VACUUMS & DROP IMPACTS ---");
      for (const blackout of parsedBlackouts) {
        lines.push(...BlackoutVacuumEngine.exportToExtendScript(blackout, fps, { compVarName: compVar }));
      }
      lines.push("");
    }

    lines.push("  app.endUndoGroup();");
    lines.push("} catch(e) {");
    lines.push("  app.endUndoGroup();");
    lines.push("  alert('Error in RhythmOrchestrator: ' + e.toString());");
    lines.push("}");

    const hashPayload = JSON.stringify({
      id: options.id,
      bpm: options.bpm,
      fps,
      bursts: parsedBursts,
      blackouts: parsedBlackouts,
      syncopatedCuts: parsedCuts,
    });
    const checksumSha256 = crypto.createHash("sha256").update(hashPayload).digest("hex");

    return RhythmPlanSchema.parse({
      id: options.id,
      bpm: options.bpm,
      fps,
      bursts: parsedBursts,
      blackouts: parsedBlackouts,
      syncopatedCuts: parsedCuts,
      extendScriptLines: lines,
      checksumSha256,
    });
  }
}
