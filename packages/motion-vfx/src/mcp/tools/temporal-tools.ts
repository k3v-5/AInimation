import {
  PosterizeTimeSpec,
  PosterizeTimeEngine,
  QuantizedSpeedRampSpec,
  SpeedRampEngine,
  TemporalOrchestrator,
  CompileTemporalOptions,
} from "../../temporal/index.js";

/**
 * REQ-F21: Herramientas MCP para modulación temporal, tasa de cuadros y speed ramping (Fase 21).
 */

export async function apply_posterize_time(params: PosterizeTimeSpec) {
  const extendScriptLines = PosterizeTimeEngine.exportToExtendScript(params);
  return {
    success: true,
    extendScriptLines,
  };
}

export async function compile_speed_ramp_to_beat(params: QuantizedSpeedRampSpec) {
  const keyframes = SpeedRampEngine.generateTimeRemapKeyframes(params);
  const extendScriptLines = SpeedRampEngine.exportToExtendScript(params);
  return {
    success: true,
    keyframes,
    extendScriptLines,
  };
}

export async function compile_temporal_orchestration(params: CompileTemporalOptions) {
  const plan = TemporalOrchestrator.compilePlan(params);
  return {
    success: true,
    plan,
  };
}
