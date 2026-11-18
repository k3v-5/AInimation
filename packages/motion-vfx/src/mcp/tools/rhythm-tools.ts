import {
  MachineGunBurstSpecInput,
  BlackoutVacuumSpecInput,
  SyncopatedSequenceSpecInput,
  FlashCutEngine,
  BlackoutVacuumEngine,
  SyncopatedCuttingEngine,
  RhythmOrchestrator,
  CompileRhythmOptions,
} from "../../rhythm/index.js";

/**
 * REQ-F23: Herramientas MCP para montaje rítmico, flash cuts y vacíos de caída a negro (Fase 23).
 */

export async function apply_machine_gun_flash_cuts(params: {
  burst: MachineGunBurstSpecInput;
  fps?: number;
}) {
  const fps = params.fps ?? 30.0;
  const slices = FlashCutEngine.calculateSlices(params.burst, fps);
  const extendScriptLines = FlashCutEngine.exportToExtendScript(params.burst, fps);
  return {
    success: true,
    slicesCount: slices.length,
    slices,
    extendScriptLines,
  };
}

export async function apply_blackout_vacuum_drop(params: {
  blackout: BlackoutVacuumSpecInput;
  fps?: number;
}) {
  const fps = params.fps ?? 30.0;
  const window = BlackoutVacuumEngine.calculateVacuumWindow(params.blackout, fps);
  const extendScriptLines = BlackoutVacuumEngine.exportToExtendScript(params.blackout, fps);
  return {
    success: true,
    window,
    extendScriptLines,
  };
}

export async function compile_syncopated_rhythm_cut(params: CompileRhythmOptions) {
  const plan = RhythmOrchestrator.compilePlan(params);
  return {
    success: true,
    plan,
  };
}
