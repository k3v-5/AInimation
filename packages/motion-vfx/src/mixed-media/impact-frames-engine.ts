import { ImpactFrameSpec, ImpactFrameSpecInput, ImpactFrameSpecSchema } from "./mixed-media-types.js";

/**
 * Motor de 1-Frame Manga Impact Frames (Fase 28).
 * Inserta cortes estroboscópicos de 1 o 2 fotogramas con inversión negativa
 * o blanco y negro hiper-contrastado en el momento exacto del impacto del beat.
 */
export class ImpactFramesEngine {
  /**
   * Cuantiza un tiempo en segundos a la grilla discreta de fotogramas según la tasa fps.
   */
  public static quantizeToFrameGrid(timeSeconds: number, fps: number): number {
    const validFps = fps > 0 ? fps : 30.0;
    const frameIndex = Math.round(timeSeconds * validFps);
    return frameIndex / validFps;
  }

  /**
   * Calcula la ventana temporal exacta [startSeconds, endSeconds] para el frame de impacto.
   */
  public static calculateFrameWindow(
    timeSeconds: number,
    frameDuration: 1 | 2,
    fps: number
  ): { startSeconds: number; endSeconds: number; frameCount: number } {
    const validFps = fps > 0 ? fps : 30.0;
    const startSeconds = this.quantizeToFrameGrid(timeSeconds, validFps);
    const endSeconds = startSeconds + frameDuration / validFps;
    return {
      startSeconds,
      endSeconds,
      frameCount: frameDuration,
    };
  }

  /**
   * Genera código ExtendScript nativo para inyectar una capa de impacto temporal cuantizada.
   */
  public static exportToExtendScript(
    spec: ImpactFrameSpecInput,
    fps: number = 30.0,
    options?: { compVarName?: string }
  ): string[] {
    const validated = ImpactFrameSpecSchema.parse(spec);
    const comp = options?.compVarName ?? "comp";
    const window = this.calculateFrameWindow(validated.impactTimeSeconds, validated.frameDuration, fps);

    const lines: string[] = [
      `  // === 1-FRAME MANGA IMPACT: ${validated.id} (${validated.mode}, ${validated.frameDuration} frames) ===`,
      "  try {",
      `    if (${comp}) {`,
      `      var impactSolid = ${comp}.layers.addSolid([1, 1, 1], '[IMPACT FRAME ' + '${validated.frameDuration}F] ' + '${validated.id}', ${comp}.width, ${comp}.height, 1.0);`,
      "      if (impactSolid) {",
      `        impactSolid.startTime = ${window.startSeconds.toFixed(4)};`,
      `        impactSolid.inPoint = ${window.startSeconds.toFixed(4)};`,
      `        impactSolid.outPoint = ${window.endSeconds.toFixed(4)};`,
      "        impactSolid.motionBlur = true; // Invariante obligatoria",
      "",
    ];

    if (validated.mode === "INVERT_NEGATIVE") {
      lines.push(
        "        // Modo negativo invertido estroboscópico (Difference puro)",
        "        impactSolid.blendingMode = BlendingMode.DIFFERENCE;"
      );
    } else if (validated.mode === "HIGH_CONTRAST_BW") {
      lines.push(
        "        // Blanco y negro entintado manga hiper-contrastado",
        "        impactSolid.adjustmentLayer = true;",
        '        var tintFx = impactSolid.property("Effects").addProperty("ADBE Tint");',
        '        var threshFx = impactSolid.property("Effects").addProperty("ADBE Threshold");',
        "        if (threshFx) threshFx.property(1).setValue(128);",
        "        impactSolid.blendingMode = BlendingMode.NORMAL;"
      );
    } else {
      // CHROMATIC_FLASH
      lines.push(
        "        // Destello cromático estroboscópico",
        "        impactSolid.blendingMode = BlendingMode.CLASSIC_COLOR_DODGE;",
        '        impactSolid.property("Transform").property("Opacity").setValue(90.0);'
      );
    }

    lines.push(
      "      }",
      "    }",
      "  } catch(e) {",
      `    alert('Error in ImpactFramesEngine: ' + e.toString());`,
      "  }"
    );

    return lines;
  }
}
