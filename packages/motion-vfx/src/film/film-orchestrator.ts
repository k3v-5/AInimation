import crypto from "crypto";
import {
  AuteurColorGradingSpec,
  AuteurColorGradingSpecInput,
  AuteurColorGradingSpecSchema,
  FilmGrainSpec,
  FilmGrainSpecInput,
  FilmGrainSpecSchema,
  FilmHalationSpec,
  FilmHalationSpecInput,
  FilmHalationSpecSchema,
  FilmPlan,
  FilmPlanSchema,
  ShutterFlickerSpec,
  ShutterFlickerSpecInput,
  ShutterFlickerSpecSchema,
} from "./film-types.js";
import { FilmGrainEngine } from "./film-grain-engine.js";
import { FilmHalationEngine } from "./film-halation-engine.js";
import { FilmShutterFlickerEngine } from "./film-shutter-flicker-engine.js";
import { AuteurColorGradingEngine } from "./auteur-color-grading-engine.js";

export interface CompileFilmOptions {
  id: string;
  grain?: FilmGrainSpecInput;
  halation?: FilmHalationSpecInput;
  flicker?: ShutterFlickerSpecInput;
  colorGrading?: AuteurColorGradingSpecInput;
  targetLayerVarName?: string;
  compVarName?: string;
}

/**
 * Orquestador unificado de textura analógica y color grading de autor (Fase 22).
 */
export class FilmOrchestrator {
  /**
   * Compila un plan de emulación fílmica y color con sello SHA-256 y código ExtendScript.
   */
  public static compilePlan(options: CompileFilmOptions): FilmPlan {
    const layerVar = options.targetLayerVarName ?? "targetLayer";
    const compVar = options.compVarName ?? "mainComp";

    const lines: string[] = [
      "// ============================================================================",
      "//  FASE 22: ANALOG FILM EMULATION & AUTEUR COLOR GRADING ORCHESTRATOR",
      `//  ID: ${options.id} | Auteur Profile: ${options.colorGrading?.profile ?? "DEFAULT"}`,
      "// ============================================================================",
      "",
      `app.beginUndoGroup('Apply Film & Color: ${options.id}');`,
      "try {",
      `  if (${compVar}) ${compVar}.motionBlur = true; // Invariante obligatoria`,
      `  if (${layerVar}) ${layerVar}.motionBlur = true;`,
      "",
    ];

    // 1. Color Grading de Autor
    if (options.colorGrading) {
      lines.push("  // --- 1. AUTEUR COLOR PALETTE ---");
      lines.push(...AuteurColorGradingEngine.exportToExtendScript(options.colorGrading, { layerVarName: layerVar }));
      lines.push("");
    }

    // 2. Grano Fílmico Procedural
    if (options.grain) {
      lines.push("  // --- 2. ORGANIC FILM GRAIN ---");
      lines.push(...FilmGrainEngine.exportToExtendScript(options.grain, { compVarName: compVar, layerVarName: layerVar }));
      lines.push("");
    }

    // 3. Shutter Flicker & Gate Weave
    if (options.flicker) {
      lines.push("  // --- 3. SHUTTER FLICKER & GATE WEAVE ---");
      lines.push(...FilmShutterFlickerEngine.exportToExtendScript(options.flicker, { layerVarName: layerVar }));
      lines.push("");
    }

    // 4. Film Halation (Red High-Contrast Glow)
    if (options.halation) {
      lines.push("  // --- 4. KODAK FILM HALATION ---");
      lines.push(...FilmHalationEngine.exportToExtendScript(options.halation, { compVarName: compVar, layerVarName: layerVar }));
      lines.push("");
    }

    lines.push("  app.endUndoGroup();");
    lines.push("} catch(e) {");
    lines.push("  app.endUndoGroup();");
    lines.push("  alert('Error en Film Orchestrator: ' + e.toString());");
    lines.push("}");

    const parsedGrain = options.grain ? FilmGrainSpecSchema.parse(options.grain) : undefined;
    const parsedHalation = options.halation ? FilmHalationSpecSchema.parse(options.halation) : undefined;
    const parsedFlicker = options.flicker ? ShutterFlickerSpecSchema.parse(options.flicker) : undefined;
    const parsedColorGrading = options.colorGrading ? AuteurColorGradingSpecSchema.parse(options.colorGrading) : undefined;

    const hashContent = JSON.stringify({
      id: options.id,
      grain: parsedGrain,
      halation: parsedHalation,
      flicker: parsedFlicker,
      colorGrading: parsedColorGrading,
    });
    const checksumSha256 = crypto.createHash("sha256").update(hashContent).digest("hex");

    return FilmPlanSchema.parse({
      id: options.id,
      grain: parsedGrain,
      halation: parsedHalation,
      flicker: parsedFlicker,
      colorGrading: parsedColorGrading,
      extendScriptLines: lines,
      checksumSha256,
    });
  }
}
