import crypto from "crypto";
import {
  DoodleBoilSpecInput,
  DoodleBoilSpecSchema,
  ImpactFrameSpecInput,
  ImpactFrameSpecSchema,
  MixedMediaPlan,
  MixedMediaPlanSchema,
  PaperTearSpecInput,
  PaperTearSpecSchema,
  SpeedLinesSpecInput,
  SpeedLinesSpecSchema,
  SprocketHolesSpecInput,
  SprocketHolesSpecSchema,
} from "./mixed-media-types.js";
import { ImpactFramesEngine } from "./impact-frames-engine.js";
import { SpeedLinesEngine } from "./speed-lines-engine.js";
import { SprocketHolesEngine } from "./sprocket-holes-engine.js";
import { PaperTearEngine } from "./paper-tear-engine.js";
import { DoodleBoilEngine } from "./doodle-boil-engine.js";

export interface CompileMixedMediaOptions {
  id: string;
  fps?: number;
  compVarName?: string;
  layerVarName?: string;
  sourceLayerVarName?: string;
  destLayerVarName?: string;
  impactFrame?: ImpactFrameSpecInput;
  speedLines?: SpeedLinesSpecInput;
  sprocketHoles?: SprocketHolesSpecInput;
  paperTear?: PaperTearSpecInput;
  doodleBoil?: DoodleBoilSpecInput;
}

/**
 * Orquestador consolidado de Mixed-Media y Anime Kinetics (Fase 28).
 */
export class MixedMediaOrchestrator {
  /**
   * Compila un plan de técnicas mixtas y anime con código ExtendScript y hash SHA-256.
   */
  public static compilePlan(options: CompileMixedMediaOptions): MixedMediaPlan {
    const fps = options.fps ?? 30.0;
    const compVar = options.compVarName ?? "comp";
    const layerVar = options.layerVarName ?? "videoLyr";
    const srcVar = options.sourceLayerVarName ?? layerVar;
    const destVar = options.destLayerVarName ?? layerVar;

    const parsedImpact = options.impactFrame ? ImpactFrameSpecSchema.parse(options.impactFrame) : undefined;
    const parsedSpeed = options.speedLines ? SpeedLinesSpecSchema.parse(options.speedLines) : undefined;
    const parsedSprocket = options.sprocketHoles ? SprocketHolesSpecSchema.parse(options.sprocketHoles) : undefined;
    const parsedTear = options.paperTear ? PaperTearSpecSchema.parse(options.paperTear) : undefined;
    const parsedDoodle = options.doodleBoil ? DoodleBoilSpecSchema.parse(options.doodleBoil) : undefined;

    const lines: string[] = [
      "// ============================================================================",
      "//  FASE 28: MIXED-MEDIA & ANIME KINETICS",
      `//  ID: ${options.id} | FPS: ${fps}`,
      "// ============================================================================",
      "",
      `app.beginUndoGroup('Apply Mixed-Media Kinetics: ${options.id}');`,
      "try {",
      `  if (${compVar}) ${compVar}.motionBlur = true; // Invariante obligatoria`,
      "",
    ];

    // 1. 1-Frame Manga Impact Frame
    if (parsedImpact) {
      lines.push("  // --- 1. MANGA IMPACT FRAME ---");
      lines.push(...ImpactFramesEngine.exportToExtendScript(parsedImpact, fps, { compVarName: compVar }));
      lines.push("");
    }

    // 2. Procedural Speed Lines
    if (parsedSpeed) {
      lines.push("  // --- 2. PROCEDURAL SPEED LINES ---");
      lines.push(...SpeedLinesEngine.exportToExtendScript(parsedSpeed, { compVarName: compVar }));
      lines.push("");
    }

    // 3. 35mm Sprocket Holes
    if (parsedSprocket) {
      lines.push("  // --- 3. 35MM SPROCKET HOLES & GATE WEAVE ---");
      lines.push(...SprocketHolesEngine.exportToExtendScript(parsedSprocket, { compVarName: compVar }));
      lines.push("");
    }

    // 4. Paper Tear Collage Wipe
    if (parsedTear) {
      lines.push("  // --- 4. PAPER TEAR COLLAGE WIPE ---");
      lines.push(
        ...PaperTearEngine.exportToExtendScript(parsedTear, {
          layerVarName: destVar,
          compVarName: compVar,
        })
      );
      lines.push("");
    }

    // 5. Stop-Motion Doodle Boil
    if (parsedDoodle) {
      lines.push("  // --- 5. STOP-MOTION DOODLE BOIL ---");
      lines.push(...DoodleBoilEngine.exportToExtendScript(parsedDoodle, { layerVarName: srcVar }));
      lines.push("");
    }

    lines.push("  app.endUndoGroup();");
    lines.push("} catch(e) {");
    lines.push("  app.endUndoGroup();");
    lines.push("  alert('Error in MixedMediaOrchestrator: ' + e.toString());");
    lines.push("}");

    const hashPayload = JSON.stringify({
      id: options.id,
      fps,
      impactFrame: parsedImpact,
      speedLines: parsedSpeed,
      sprocketHoles: parsedSprocket,
      paperTear: parsedTear,
      doodleBoil: parsedDoodle,
    });
    const checksumSha256 = crypto.createHash("sha256").update(hashPayload).digest("hex");

    return MixedMediaPlanSchema.parse({
      id: options.id,
      fps,
      impactFrame: parsedImpact,
      speedLines: parsedSpeed,
      sprocketHoles: parsedSprocket,
      paperTear: parsedTear,
      doodleBoil: parsedDoodle,
      extendScriptLines: lines,
      checksumSha256,
    });
  }
}
