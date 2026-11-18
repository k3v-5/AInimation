import {
  ImpactFrameSpecInput,
  SpeedLinesSpecInput,
  SprocketHolesSpecInput,
  ImpactFramesEngine,
  SpeedLinesEngine,
  SprocketHolesEngine,
  MixedMediaOrchestrator,
  CompileMixedMediaOptions,
} from "../../mixed-media/index.js";

/**
 * REQ-F28: Herramientas MCP para Mixed-Media y Anime Kinetics (Fase 28).
 */

export async function apply_manga_impact_frame(params: {
  impactFrame: ImpactFrameSpecInput;
  fps?: number;
  compVarName?: string;
}) {
  const fps = params.fps ?? 30.0;
  const extendScriptLines = ImpactFramesEngine.exportToExtendScript(params.impactFrame, fps, {
    compVarName: params.compVarName,
  });
  return {
    success: true,
    extendScriptLines,
  };
}

export async function apply_procedural_speed_lines(params: {
  speedLines: SpeedLinesSpecInput;
  compVarName?: string;
}) {
  const extendScriptLines = SpeedLinesEngine.exportToExtendScript(params.speedLines, {
    compVarName: params.compVarName,
  });
  return {
    success: true,
    extendScriptLines,
  };
}

export async function apply_film_sprocket_holes(params: {
  sprocketHoles: SprocketHolesSpecInput;
  compVarName?: string;
}) {
  const extendScriptLines = SprocketHolesEngine.exportToExtendScript(params.sprocketHoles, {
    compVarName: params.compVarName,
  });
  return {
    success: true,
    extendScriptLines,
  };
}

export async function compile_mixed_media_plan(
  params: CompileMixedMediaOptions
) {
  const plan = MixedMediaOrchestrator.compilePlan(params);
  return {
    success: true,
    plan,
  };
}
