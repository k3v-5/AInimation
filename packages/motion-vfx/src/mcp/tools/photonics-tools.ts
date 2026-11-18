import {
  ShutterDragSpecInput,
  AnamorphicStreakSpecInput,
  FlirThermalSpecInput,
  ShutterDragEngine,
  AnamorphicStreakEngine,
  FlirThermalEngine,
  PhotonicsOrchestrator,
  CompilePhotonicsOptions,
} from "../../photonics/index.js";

/**
 * REQ-F27: Herramientas MCP para Cinematografía Fotónica Nocturna y Artefactos Ópticos (Fase 27).
 */

export async function apply_shutter_drag_echo(params: {
  shutterDrag: ShutterDragSpecInput;
  layerVarName?: string;
}) {
  const extendScriptLines = ShutterDragEngine.exportToExtendScript(params.shutterDrag, {
    layerVarName: params.layerVarName,
  });
  return {
    success: true,
    extendScriptLines,
  };
}

export async function apply_anamorphic_streak_flare(params: {
  anamorphicStreak: AnamorphicStreakSpecInput;
  compVarName?: string;
  layerVarName?: string;
}) {
  const extendScriptLines = AnamorphicStreakEngine.exportToExtendScript(params.anamorphicStreak, {
    compVarName: params.compVarName,
    layerVarName: params.layerVarName,
  });
  return {
    success: true,
    extendScriptLines,
  };
}

export async function apply_flir_thermal_vision(params: {
  flirThermal: FlirThermalSpecInput;
  layerVarName?: string;
  compVarName?: string;
}) {
  const extendScriptLines = FlirThermalEngine.exportToExtendScript(params.flirThermal, {
    layerVarName: params.layerVarName,
    compVarName: params.compVarName,
  });
  return {
    success: true,
    extendScriptLines,
  };
}

export async function compile_photonics_plan(
  params: CompilePhotonicsOptions
) {
  const plan = PhotonicsOrchestrator.compilePlan(params);
  return {
    success: true,
    plan,
  };
}
