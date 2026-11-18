import {
  CentrifugalGyroRollSpecInput,
  WhipPanMatchCutSpecInput,
  LensBreathingSpecInput,
  GyroRollEngine,
  WhipPanEngine,
  LensBreathingEngine,
  DynamicMechanicsOrchestrator,
  CompileDynamicMechanicsOptions,
} from "../../dynamic-mechanics/index.js";

/**
 * REQ-F26: Herramientas MCP para mecánica de cámara y ópticas dinámicas (Fase 26).
 */

export async function apply_centrifugal_gyro_roll(params: {
  gyroRoll: CentrifugalGyroRollSpecInput;
  fps?: number;
  layerVarName?: string;
}) {
  const fps = params.fps ?? 30.0;
  const extendScriptLines = GyroRollEngine.exportToExtendScript(params.gyroRoll, fps, {
    layerVarName: params.layerVarName,
  });
  return {
    success: true,
    extendScriptLines,
  };
}

export async function apply_directional_whip_pan(params: {
  whipPan: WhipPanMatchCutSpecInput;
  sourceLayerVarName?: string;
  destLayerVarName?: string;
  compVarName?: string;
}) {
  const extendScriptLines = WhipPanEngine.exportToExtendScript(params.whipPan, {
    sourceLayerVarName: params.sourceLayerVarName,
    destLayerVarName: params.destLayerVarName,
    compVarName: params.compVarName,
  });
  return {
    success: true,
    extendScriptLines,
  };
}

export async function compile_dynamic_mechanics_plan(
  params: CompileDynamicMechanicsOptions
) {
  const plan = DynamicMechanicsOrchestrator.compilePlan(params);
  return {
    success: true,
    plan,
  };
}
