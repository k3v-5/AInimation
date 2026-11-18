import crypto from "crypto";
import {
  BrutalistTypeSpecInput,
  BrutalistTypeSpecSchema,
  KineticTypographyPlan,
  KineticTypographyPlanSchema,
  LiquidChromeSpecInput,
  LiquidChromeSpecSchema,
  PerspectiveAnchorSpecInput,
  PerspectiveAnchorSpecSchema,
  WordSlamSpecInput,
  WordSlamSpecSchema,
} from "./kinetic-typography-types.js";
import { BrutalistTypeEngine } from "./brutalist-type-engine.js";
import { LiquidChromeEngine } from "./liquid-chrome-engine.js";
import { PerspectiveAnchorEngine } from "./perspective-anchor-engine.js";
import { WordSlamEngine } from "./word-slam-engine.js";

export interface CompileKineticTypographyOptions {
  id: string;
  fps?: number;
  brutalist: BrutalistTypeSpecInput;
  chrome?: LiquidChromeSpecInput;
  perspective?: PerspectiveAnchorSpecInput;
  slam?: WordSlamSpecInput;
  compVarName?: string;
  layerVarName?: string;
}

/**
 * Orquestador consolidado de tipografía cinética de vanguardia (Fase 24).
 */
export class KineticTypographyOrchestrator {
  /**
   * Compila un plan tipográfico completo con código ExtendScript y verificación SHA-256.
   */
  public static compilePlan(options: CompileKineticTypographyOptions): KineticTypographyPlan {
    const fps = options.fps ?? 30.0;
    const compVar = options.compVarName ?? "comp";
    const layerVar = options.layerVarName ?? "textLyr";

    const parsedBrutalist = BrutalistTypeSpecSchema.parse(options.brutalist);
    const parsedChrome = options.chrome ? LiquidChromeSpecSchema.parse(options.chrome) : undefined;
    const parsedPerspective = options.perspective
      ? PerspectiveAnchorSpecSchema.parse(options.perspective)
      : undefined;
    const parsedSlam = options.slam ? WordSlamSpecSchema.parse(options.slam) : undefined;

    const lines: string[] = [
      "// ============================================================================",
      "//  FASE 24: AVANT-GARDE BRUTALIST KINETIC TYPOGRAPHY & LIQUID CHROME",
      `//  ID: ${options.id} | Font: ${parsedBrutalist.fontFamily} | Vertical Stretch: ${parsedBrutalist.verticalStretchPercent}%`,
      "// ============================================================================",
      "",
      `app.beginUndoGroup('Apply Kinetic Typography: ${options.id}');`,
      "try {",
      `  if (${compVar}) ${compVar}.motionBlur = true; // Invariante obligatoria`,
      "",
    ];

    // 1. Maquetación Brutalista (Base Text Layer)
    lines.push("  // --- 1. BRUTALIST EDITORIAL TEXT ---");
    lines.push(...BrutalistTypeEngine.exportToExtendScript(parsedBrutalist, { compVarName: compVar, layerVarName: layerVar }));
    lines.push("");

    // 2. Anclaje en Perspectiva 3D
    if (parsedPerspective) {
      lines.push("  // --- 2. 3D PERSPECTIVE ANCHORING ---");
      lines.push(...PerspectiveAnchorEngine.exportToExtendScript(parsedPerspective, { layerVarName: layerVar }));
      lines.push("");
    }

    // 3. Efecto Cromo Líquido Metálico
    if (parsedChrome) {
      lines.push("  // --- 3. LIQUID CHROME METALLIC SHADER ---");
      lines.push(...LiquidChromeEngine.exportToExtendScript(parsedChrome, { layerVarName: layerVar }));
      lines.push("");
    }

    // 4. Word Slam Rítmico con Rebote
    if (parsedSlam) {
      lines.push("  // --- 4. PERCUSSIVE WORD SLAM ---");
      const stretchMultiplier = parsedBrutalist.verticalStretchPercent / 100.0;
      lines.push(...WordSlamEngine.exportToExtendScript(parsedSlam, fps, stretchMultiplier, { layerVarName: layerVar }));
      lines.push("");
    }

    lines.push("  app.endUndoGroup();");
    lines.push("} catch(e) {");
    lines.push("  app.endUndoGroup();");
    lines.push("  alert('Error in KineticTypographyOrchestrator: ' + e.toString());");
    lines.push("}");

    const hashPayload = JSON.stringify({
      id: options.id,
      brutalist: parsedBrutalist,
      chrome: parsedChrome,
      perspective: parsedPerspective,
      slam: parsedSlam,
    });
    const checksumSha256 = crypto.createHash("sha256").update(hashPayload).digest("hex");

    return KineticTypographyPlanSchema.parse({
      id: options.id,
      brutalist: parsedBrutalist,
      chrome: parsedChrome,
      perspective: parsedPerspective,
      slam: parsedSlam,
      extendScriptLines: lines,
      checksumSha256,
    });
  }
}
