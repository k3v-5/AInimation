import {
  AspectRatioBreathingSpec,
  AspectRatioBreathingSpecInput,
  AspectRatioBreathingSpecSchema,
  AspectRatioFormat,
} from "./stem-kinetics-types.js";

/**
 * Motor de Dynamic Aspect Ratio Breathing & Letterboxing Cinematográfico (Fase 29).
 * Modela la dilatación y contracción fluida del encuadre entre relaciones de aspecto canónicas
 * (9:16 vertical, 1:1 cuadrado, 4:3 IMAX, 16:9 estándar, 2.39:1 anamórfico Scope).
 */
export class AspectRatioBreathingEngine {
  /**
   * Obtiene la relación numérica anchura / altura para cada formato canónico.
   */
  public static getFormatRatio(format: AspectRatioFormat): number {
    switch (format) {
      case "9:16":
        return 9.0 / 16.0; // 0.5625
      case "1:1":
        return 1.0;
      case "4:3":
        return 4.0 / 3.0; // 1.3333...
      case "16:9":
        return 16.0 / 9.0; // 1.7777...
      case "2.39:1":
      default:
        return 2.39;
    }
  }

  /**
   * Calcula las dimensiones analíticas de la ventana visible y las barras de letterbox/pillarbox.
   */
  public static computeMatteDimensions(
    compW: number,
    compH: number,
    ratio: number
  ): {
    visibleWidth: number;
    visibleHeight: number;
    topBottomBarHeight: number;
    leftRightBarWidth: number;
  } {
    const compRatio = compW / compH;
    let visibleWidth = compW;
    let visibleHeight = compH;

    if (ratio < compRatio) {
      // Pillarbox (barras laterales verticales)
      visibleHeight = compH;
      visibleWidth = compH * ratio;
    } else {
      // Letterbox (barras horizontales superior/inferior)
      visibleWidth = compW;
      visibleHeight = compW / ratio;
    }

    const topBottomBarHeight = Math.max(0, (compH - visibleHeight) / 2.0);
    const leftRightBarWidth = Math.max(0, (compW - visibleWidth) / 2.0);

    return {
      visibleWidth: Math.round(visibleWidth * 100) / 100,
      visibleHeight: Math.round(visibleHeight * 100) / 100,
      topBottomBarHeight: Math.round(topBottomBarHeight * 100) / 100,
      leftRightBarWidth: Math.round(leftRightBarWidth * 100) / 100,
    };
  }

  /**
   * Genera código ExtendScript nativo para inyectar una capa de matte negro con máscara animada.
   */
  public static exportToExtendScript(
    spec: AspectRatioBreathingSpecInput,
    options?: { compVarName?: string }
  ): string[] {
    const validated = AspectRatioBreathingSpecSchema.parse(spec);
    const comp = options?.compVarName ?? "comp";
    const [br, bg, bb] = validated.barColor;

    const lines: string[] = [
      `  // === DYNAMIC ASPECT RATIO BREATHING: ${validated.id} ===`,
      "  try {",
      `    if (${comp}) {`,
      `      var matteSolid = ${comp}.layers.addSolid([${br.toFixed(3)}, ${bg.toFixed(3)}, ${bb.toFixed(3)}], '[CINEMATIC LETTERBOX] ' + '${validated.id}', ${comp}.width, ${comp}.height, 1.0);`,
      "      if (matteSolid) {",
      "        matteSolid.motionBlur = true;",
      "",
      "        // Máscara sustractiva central que define la ventana de aspect ratio",
      '        var mask = matteSolid.property("Masks").addProperty("ADBE Mask Atom");',
      "        if (mask) {",
      "          mask.maskMode = MaskMode.SUBTRACT;",
      '          var maskProp = mask.property("Mask Path");',
    ];

    for (const tr of validated.transitions) {
      const r = this.getFormatRatio(tr.targetFormat);
      const startT = tr.startTimeSeconds;
      const endT = tr.startTimeSeconds + tr.durationSeconds;

      lines.push(
        "",
        `          // Transición a formato ${tr.targetFormat} (ratio: ${r.toFixed(4)})`,
        `          var compW = ${comp}.width; var compH = ${comp}.height;`,
        `          var targetR = ${r.toFixed(4)};`,
        "          var visW = compW; var visH = compH;",
        "          if (targetR < (compW / compH)) { visH = compH; visW = compH * targetR; }",
        "          else { visW = compW; visH = compW / targetR; }",
        "          var barY = (compH - visH) / 2.0; var barX = (compW - visW) / 2.0;",
        "",
        "          var shapeAtT = maskProp.value;",
        "          shapeAtT.vertices = [[barX, barY], [compW - barX, barY], [compW - barX, compH - barY], [barX, compH - barY]];",
        "          shapeAtT.closed = true;",
        `          maskProp.setValueAtTime(${endT.toFixed(4)}, shapeAtT);`
      );
    }

    lines.push(
      "        }",
      "      }",
      "    }",
      "  } catch(e) {",
      `    alert('Error in AspectRatioBreathingEngine: ' + e.toString());`,
      "  }"
    );

    return lines;
  }
}
