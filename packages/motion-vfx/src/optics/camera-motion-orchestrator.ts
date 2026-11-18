import crypto from "crypto";
import {
  DollyZoomSpec,
  FisheyeLensSpec,
  OpticsPlan,
  OpticsPlanSchema,
  SnapZoomSpec,
  WhipPanSpec,
} from "./optics-types.js";
import { SnapZoomEngine } from "./snap-zoom-engine.js";
import { FisheyeOpticsEngine } from "./fisheye-optics-engine.js";
import { DollyZoomEngine } from "./dolly-zoom-engine.js";

export interface CompileOpticsOptions {
  id: string;
  targetCompWidth?: number;
  targetCompHeight?: number;
  fps?: number;
  snapZooms?: SnapZoomSpec[];
  fisheye?: FisheyeLensSpec;
  dollyZooms?: DollyZoomSpec[];
  whipPans?: WhipPanSpec[];
  targetLayerVarName?: string;
  compVarName?: string;
}

/**
 * Orquestador unificado de ópticas y movimientos de cámara de videoclip (Fase 20).
 */
export class CameraMotionOrchestrator {
  /**
   * Compila un plan de ópticas y cámara consolidado con sello SHA-256 y código ExtendScript.
   */
  public static compilePlan(options: CompileOpticsOptions): OpticsPlan {
    const width = options.targetCompWidth ?? 1920;
    const height = options.targetCompHeight ?? 1080;
    const fps = options.fps ?? 30.0;
    const snapZooms = options.snapZooms ?? [];
    const dollyZooms = options.dollyZooms ?? [];
    const whipPans = options.whipPans ?? [];
    const fisheye = options.fisheye;

    const layerVar = options.targetLayerVarName ?? "targetLayer";
    const compVar = options.compVarName ?? "mainComp";

    const lines: string[] = [
      "// ============================================================================",
      "//  FASE 20: EXTREME OPTICS & CAMERA MOTION ORCHESTRATOR",
      `//  ID: ${options.id} | Canvas: ${width}x${height} @ ${fps}fps`,
      "// ============================================================================",
      "",
      `app.beginUndoGroup('Apply Optics & Camera: ${options.id}');`,
      "try {",
      `  if (${compVar}) ${compVar}.motionBlur = true; // Invariante obligatoria`,
      `  if (${layerVar}) ${layerVar}.motionBlur = true;`,
      "",
    ];

    // 1. Aplicar Snap Zooms
    if (snapZooms.length > 0) {
      lines.push("  // --- 1. RHYTHMIC SNAP / CRASH ZOOMS ---");
      for (const sz of snapZooms) {
        lines.push(...SnapZoomEngine.exportToExtendScript(sz, { layerVarName: layerVar, fps }));
      }
      lines.push("");
    }

    // 2. Aplicar Fisheye Lens
    if (fisheye) {
      lines.push("  // --- 2. FISHEYE LENS & ABERRATION ---");
      lines.push(...FisheyeOpticsEngine.exportToExtendScript(fisheye, { compVarName: compVar, layerVarName: layerVar }));
      lines.push("");
    }

    // 3. Aplicar Dolly Zooms
    if (dollyZooms.length > 0) {
      lines.push("  // --- 3. DOLLY ZOOM VERTIGO EFFECTS ---");
      for (const dz of dollyZooms) {
        lines.push(...DollyZoomEngine.exportToExtendScript(dz, { layerVarName: layerVar, fps }));
      }
      lines.push("");
    }

    // 4. Aplicar Whip Pans
    if (whipPans.length > 0) {
      lines.push("  // --- 4. DIRECTIONAL WHIP PANS ---");
      for (const wp of whipPans) {
        lines.push(`  // Whip Pan: ${wp.id} (${wp.direction})`);
        lines.push(`  try {`);
        lines.push(`    var dirBlur = ${layerVar}.property("Effects").addProperty("ADBE Directional Blur");`);
        lines.push(`    if (dirBlur) {`);
        lines.push(`      var dirProp = dirBlur.property("Direction");`);
        lines.push(`      var lenProp = dirBlur.property("Blur Length");`);
        const angle = wp.direction === "LEFT" ? 90 : wp.direction === "RIGHT" ? 270 : wp.direction === "UP" ? 0 : 180;
        lines.push(`      dirProp.setValue(${angle});`);
        lines.push(`      lenProp.setValueAtTime(${wp.triggerTimeSeconds.toFixed(3)}, 0);`);
        lines.push(`      lenProp.setValueAtTime(${(wp.triggerTimeSeconds + wp.durationSeconds / 2).toFixed(3)}, ${wp.blurIntensityPx});`);
        lines.push(`      lenProp.setValueAtTime(${(wp.triggerTimeSeconds + wp.durationSeconds).toFixed(3)}, 0);`);
        lines.push(`    }`);
        lines.push(`  } catch(e) {}`);
      }
      lines.push("");
    }

    lines.push("  app.endUndoGroup();");
    lines.push("} catch(e) {");
    lines.push("  app.endUndoGroup();");
    lines.push("  alert('Error en Optics Orchestrator: ' + e.toString());");
    lines.push("}");

    const hashContent = JSON.stringify({
      id: options.id,
      width,
      height,
      snapZoomsCount: snapZooms.length,
      hasFisheye: !!fisheye,
      dollyZoomsCount: dollyZooms.length,
      whipPansCount: whipPans.length,
    });
    const checksumSha256 = crypto.createHash("sha256").update(hashContent).digest("hex");

    return OpticsPlanSchema.parse({
      id: options.id,
      targetCompWidth: width,
      targetCompHeight: height,
      fps,
      snapZooms,
      fisheye,
      dollyZooms,
      whipPans,
      extendScriptLines: lines,
      checksumSha256,
    });
  }
}
