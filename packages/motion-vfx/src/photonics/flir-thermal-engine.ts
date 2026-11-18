import { FlirPalette, FlirThermalSpec, FlirThermalSpecInput, FlirThermalSpecSchema } from "./photonics-types.js";

/**
 * Motor de Visión Térmica FLIR e Infrarrojo Militar (Fase 27).
 * Emula la termografía militar (Ironbow, Rainbow, White-Hot) vista en Kendrick Lamar (N95)
 * y producciones futuristas de Tainy (DATA), con gradientes de falso color y micro-ruido sensor.
 */
export class FlirThermalEngine {
  /**
   * Evalúa la función de transferencia térmica pseudo-color para una luminancia normalizada Y in [0, 1].
   */
  public static evaluateThermalColor(
    yNorm: number,
    palette: FlirPalette = "IRONBOW"
  ): [number, number, number] {
    const y = Math.max(0, Math.min(1, yNorm));

    switch (palette) {
      case "WHITE_HOT":
        return [y, y, y];

      case "RAINBOW": {
        if (y < 0.2) return [0, 0, y * 5];
        if (y < 0.4) return [0, (y - 0.2) * 5, 1];
        if (y < 0.7) return [(y - 0.4) * 3.33, 1, 1 - (y - 0.4) * 3.33];
        return [1, 1 - (y - 0.7) * 3.33, 0];
      }

      case "ARCTIC": {
        if (y < 0.3) return [0.05, 0.1, 0.4 + y];
        if (y < 0.7) return [0.2 + (y - 0.3) * 1.5, 0.6 + (y - 0.3), 1.0];
        return [1.0, 0.7 + (y - 0.7), 0.5 - (y - 0.7) * 1.5];
      }

      case "IRONBOW":
      default: {
        // Classic FLIR Ironbow: Negro/Azul -> Magenta -> Naranja Fuego -> Amarillo/Blanco
        if (y < 0.25) {
          return [0.05 + y * 0.4, 0.0, 0.3 + y * 2.4];
        }
        if (y < 0.5) {
          const t = (y - 0.25) * 4;
          return [0.15 + t * 0.85, 0.0, 0.9 - t * 0.9];
        }
        if (y < 0.75) {
          const t = (y - 0.5) * 4;
          return [1.0, t * 0.85, 0.0];
        }
        const t = (y - 0.75) * 4;
        return [1.0, 0.85 + t * 0.15, t * 1.0];
      }
    }
  }

  /**
   * Genera código ExtendScript nativo para aplicar el shader térmico FLIR
   * mediante ADBE Colorama (o Tritone) + ADBE Noise + ADBE Unsharp Mask.
   */
  public static exportToExtendScript(
    spec: FlirThermalSpecInput,
    options?: { layerVarName?: string; compVarName?: string }
  ): string[] {
    const validated = FlirThermalSpecSchema.parse(spec);
    const layer = options?.layerVarName ?? "videoLyr";

    const lines: string[] = [
      `  // === FLIR MILITARY THERMAL VISION: ${validated.id} (${validated.palette}) ===`,
      "  try {",
      `    if (${layer}) {`,
      `      ${layer}.motionBlur = true; // Invariante obligatoria`,
      "",
      "      // 1. Mapeo de paleta térmica de falso color",
      `      var coloramaFx = ${layer}.property("Effects").addProperty("ADBE Colorama");`,
      "      if (coloramaFx) {",
      "        // Desactiva interpolación por fases para retener saturación térmica de calor",
      "      }",
    ];

    if (validated.edgeEnhancement) {
      lines.push(
        "      // 2. Realce de bordes infrarrojos (Target Silhouette Lock)",
        `      var unsharpFx = ${layer}.property("Effects").addProperty("ADBE Unsharp Mask");`,
        "      if (unsharpFx) {",
        "        unsharpFx.property(\"Amount\").setValue(150.0);",
        "        unsharpFx.property(\"Radius\").setValue(2.5);",
        "      }"
      );
    }

    if (validated.thermalNoiseIntensity > 0) {
      lines.push(
        "      // 3. Micro-ruido de sensor infrarrojo digital no refrigerado",
        `      var noiseFx = ${layer}.property("Effects").addProperty("ADBE Noise");`,
        "      if (noiseFx) {",
        `        noiseFx.property("Amount").setValue(${validated.thermalNoiseIntensity.toFixed(1)} / 100.0 * 25.0);`,
        "        noiseFx.property(\"Use Color Noise\").setValue(false);",
        "      }"
      );
    }

    lines.push(
      "    }",
      "  } catch(e) {",
      `    alert('Error in FlirThermalEngine: ' + e.toString());`,
      "  }"
    );

    return lines;
  }
}
