import crypto from "crypto";
import {
  InfiniteZoomPortalSpecInput,
  InfiniteZoomPortalSpecSchema,
  ParallaxOcclusionWipeSpecInput,
  ParallaxOcclusionWipeSpecSchema,
  SnorricamSpecInput,
  SnorricamSpecSchema,
  SpatialCinematographyPlan,
  SpatialCinematographyPlanSchema,
} from "./spatial-types.js";
import { SnorricamEngine } from "./snorricam-engine.js";
import { InfiniteZoomPortalEngine } from "./infinite-zoom-portal-engine.js";
import { ParallaxOcclusionWipeEngine } from "./parallax-occlusion-wipe-engine.js";

export interface CompileSpatialCinematographyOptions {
  id: string;
  fps?: number;
  snorricam?: SnorricamSpecInput;
  portal?: InfiniteZoomPortalSpecInput;
  occlusionWipe?: ParallaxOcclusionWipeSpecInput;
  compVarName?: string;
  sourceLayerVarName?: string;
  destLayerVarName?: string;
}

/**
 * Orquestador consolidado de cinematografía espacial de autor (Fase 25).
 */
export class SpatialCinematographyOrchestrator {
  /**
   * Compila un plan cinematográfico completo con código ExtendScript y verificación SHA-256.
   */
  public static compilePlan(options: CompileSpatialCinematographyOptions): SpatialCinematographyPlan {
    const fps = options.fps ?? 30.0;
    const compVar = options.compVarName ?? "comp";
    const srcVar = options.sourceLayerVarName ?? "sourceLayer";
    const destVar = options.destLayerVarName ?? "destLayer";

    const parsedSnorricam = options.snorricam ? SnorricamSpecSchema.parse(options.snorricam) : undefined;
    const parsedPortal = options.portal ? InfiniteZoomPortalSpecSchema.parse(options.portal) : undefined;
    const parsedWipe = options.occlusionWipe
      ? ParallaxOcclusionWipeSpecSchema.parse(options.occlusionWipe)
      : undefined;

    const lines: string[] = [
      "// ============================================================================",
      "//  FASE 25: SPATIAL CINEMATOGRAPHY (SNORRICAM, PORTALS & OCCLUSION WIPES)",
      `//  ID: ${options.id} | FPS: ${fps}`,
      "// ============================================================================",
      "",
      `app.beginUndoGroup('Apply Spatial Cinematography: ${options.id}');`,
      "try {",
      `  if (${compVar}) ${compVar}.motionBlur = true; // Invariante obligatoria`,
      "",
    ];

    // 1. Snorricam Body Lock
    if (parsedSnorricam) {
      lines.push("  // --- 1. SNORRICAM BODY-RIG RIGID ANCHOR ---");
      lines.push(...SnorricamEngine.exportToExtendScript(parsedSnorricam, { compVarName: compVar, layerVarName: srcVar }));
      lines.push("");
    }

    // 2. Infinite Zoom Portal
    if (parsedPortal) {
      lines.push("  // --- 2. INFINITE ZOOM WORMHOLE PORTAL ---");
      lines.push(...InfiniteZoomPortalEngine.exportToExtendScript(parsedPortal, fps, { layerVarName: srcVar }));
      lines.push("");
    }

    // 3. Parallax Occlusion Wipe
    if (parsedWipe) {
      lines.push("  // --- 3. PARALLAX OCCLUSION FOREGROUND WIPE ---");
      lines.push(...ParallaxOcclusionWipeEngine.exportToExtendScript(parsedWipe, { destLayerVarName: destVar, compVarName: compVar }));
      lines.push("");
    }

    lines.push("  app.endUndoGroup();");
    lines.push("} catch(e) {");
    lines.push("  app.endUndoGroup();");
    lines.push("  alert('Error in SpatialCinematographyOrchestrator: ' + e.toString());");
    lines.push("}");

    const hashPayload = JSON.stringify({
      id: options.id,
      fps,
      snorricam: parsedSnorricam,
      portal: parsedPortal,
      occlusionWipe: parsedWipe,
    });
    const checksumSha256 = crypto.createHash("sha256").update(hashPayload).digest("hex");

    return SpatialCinematographyPlanSchema.parse({
      id: options.id,
      snorricam: parsedSnorricam,
      portal: parsedPortal,
      occlusionWipe: parsedWipe,
      extendScriptLines: lines,
      checksumSha256,
    });
  }
}
