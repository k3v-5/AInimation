import {
  SubBassReactionSpecInput,
  AspectRatioBreathingSpecInput,
  DatamoshSpecInput,
  SubBassReactionEngine,
  AspectRatioBreathingEngine,
  DatamoshEngine,
  StemKineticsOrchestrator,
  CompileStemKineticsOptions,
} from "../../stem-kinetics/index.js";

/**
 * REQ-F29: Herramientas MCP para Audio Stem Kinetics, Aspect Ratio Breathing y Datamosh (Fase 29).
 */

export async function apply_audio_reactive_physics(params: {
  subBass: SubBassReactionSpecInput;
  fps?: number;
  layerVarName?: string;
}) {
  const fps = params.fps ?? 30.0;
  const extendScriptLines = SubBassReactionEngine.exportToExtendScript(params.subBass, fps, {
    layerVarName: params.layerVarName,
  });
  return {
    success: true,
    extendScriptLines,
  };
}

export async function apply_dynamic_aspect_ratio_breathing(params: {
  aspectRatioBreathing: AspectRatioBreathingSpecInput;
  compVarName?: string;
}) {
  const extendScriptLines = AspectRatioBreathingEngine.exportToExtendScript(params.aspectRatioBreathing, {
    compVarName: params.compVarName,
  });
  return {
    success: true,
    extendScriptLines,
  };
}

export async function apply_datamosh_pframe_glitch(params: {
  datamosh: DatamoshSpecInput;
  compVarName?: string;
  sourceLayerVarName?: string;
  destLayerVarName?: string;
}) {
  const extendScriptLines = DatamoshEngine.exportToExtendScript(params.datamosh, {
    compVarName: params.compVarName,
    sourceLayerVarName: params.sourceLayerVarName,
    destLayerVarName: params.destLayerVarName,
  });
  return {
    success: true,
    extendScriptLines,
  };
}

export async function compile_stem_kinetics_plan(
  params: CompileStemKineticsOptions
) {
  const plan = StemKineticsOrchestrator.compilePlan(params);
  return {
    success: true,
    plan,
  };
}
