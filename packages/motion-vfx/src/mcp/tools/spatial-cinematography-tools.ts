import {
  SnorricamSpecInput,
  InfiniteZoomPortalSpecInput,
  ParallaxOcclusionWipeSpecInput,
  SnorricamEngine,
  InfiniteZoomPortalEngine,
  ParallaxOcclusionWipeEngine,
  SpatialCinematographyOrchestrator,
  CompileSpatialCinematographyOptions,
} from "../../spatial-cinematography/index.js";

/**
 * REQ-F25: Herramientas MCP para cinematografía espacial (Snorricam, Portals, Occlusion Wipes) (Fase 25).
 */

export async function apply_snorricam_body_lock(params: {
  snorricam: SnorricamSpecInput;
  compVarName?: string;
  layerVarName?: string;
}) {
  const extendScriptLines = SnorricamEngine.exportToExtendScript(params.snorricam, {
    compVarName: params.compVarName,
    layerVarName: params.layerVarName,
  });
  return {
    success: true,
    extendScriptLines,
  };
}

export async function apply_infinite_zoom_portal(params: {
  portal: InfiniteZoomPortalSpecInput;
  fps?: number;
  layerVarName?: string;
}) {
  const fps = params.fps ?? 30.0;
  const extendScriptLines = InfiniteZoomPortalEngine.exportToExtendScript(params.portal, fps, {
    layerVarName: params.layerVarName,
  });
  return {
    success: true,
    extendScriptLines,
  };
}

export async function compile_spatial_cinematography_plan(
  params: CompileSpatialCinematographyOptions
) {
  const plan = SpatialCinematographyOrchestrator.compilePlan(params);
  return {
    success: true,
    plan,
  };
}
