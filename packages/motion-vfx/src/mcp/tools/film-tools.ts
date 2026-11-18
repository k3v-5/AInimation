import {
  FilmGrainSpec,
  FilmGrainEngine,
  FilmHalationSpec,
  FilmHalationEngine,
  AuteurColorGradingSpec,
  AuteurColorGradingEngine,
  FilmOrchestrator,
  CompileFilmOptions,
} from "../../film/index.js";

/**
 * REQ-F22: Herramientas MCP para textura fílmica analógica y color grading de autor (Fase 22).
 */

export async function apply_film_grain_and_halation(params: {
  grain?: FilmGrainSpec;
  halation?: FilmHalationSpec;
}) {
  const lines: string[] = [];
  if (params.grain) {
    lines.push(...FilmGrainEngine.exportToExtendScript(params.grain));
  }
  if (params.halation) {
    lines.push(...FilmHalationEngine.exportToExtendScript(params.halation));
  }
  return {
    success: true,
    extendScriptLines: lines,
  };
}

export async function apply_auteur_color_grading(params: AuteurColorGradingSpec) {
  const settings = AuteurColorGradingEngine.resolveProfileSettings(params);
  const extendScriptLines = AuteurColorGradingEngine.exportToExtendScript(params);
  return {
    success: true,
    settings,
    extendScriptLines,
  };
}

export async function compile_film_emulation_plan(params: CompileFilmOptions) {
  const plan = FilmOrchestrator.compilePlan(params);
  return {
    success: true,
    plan,
  };
}
