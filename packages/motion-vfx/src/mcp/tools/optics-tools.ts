import {
  CameraMotionOrchestrator,
  CompileOpticsOptions,
  FisheyeLensSpec,
  FisheyeOpticsEngine,
  DollyZoomSpec,
  DollyZoomEngine,
} from "../../optics/index.js";

/**
 * REQ-F20: Herramientas MCP para ópticas extremas y movimiento de cámara cinematográfica (Fase 20).
 */

export async function apply_snap_zooms_to_timeline(params: CompileOpticsOptions) {
  const plan = CameraMotionOrchestrator.compilePlan(params);
  return {
    success: true,
    plan,
  };
}

export async function apply_fisheye_optics(params: FisheyeLensSpec) {
  const extendScriptLines = FisheyeOpticsEngine.exportToExtendScript(params);
  return {
    success: true,
    extendScriptLines,
  };
}

export async function compile_dolly_zoom(params: DollyZoomSpec) {
  const keyframes = DollyZoomEngine.generateKeyframes(params);
  const extendScriptLines = DollyZoomEngine.exportToExtendScript(params);
  return {
    success: true,
    keyframes,
    extendScriptLines,
  };
}
