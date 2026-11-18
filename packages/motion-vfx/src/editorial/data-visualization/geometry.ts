import {
  VisualizationViewport,
  VisualizationIR,
  VisualizationElement,
} from "./types.js";
import { SafeZoneViolationError } from "./errors.js";

/**
 * REQ-025 §9: Geometría y cálculo de áreas seguras (Safe Zones).
 */
export interface PlotArea {
  x: number;
  y: number;
  width: number;
  height: number;
  right: number;
  bottom: number;
}

export function computePlotArea(viewport: VisualizationViewport): PlotArea {
  const x = viewport.safeMarginLeft;
  const y = viewport.safeMarginTop;
  const width = Math.max(10, viewport.width - viewport.safeMarginLeft - viewport.safeMarginRight);
  const height = Math.max(10, viewport.height - viewport.safeMarginTop - viewport.safeMarginBottom);

  return {
    x,
    y,
    width,
    height,
    right: x + width,
    bottom: y + height,
  };
}

/**
 * REQ-025 §48: Valida que los elementos estructurales y de texto de la visualización
 * se mantengan dentro de la Safe Zone obligatoria.
 */
export function assertVisualizationSafeZone(ir: VisualizationIR): void {
  const plot = computePlotArea(ir.viewport);
  const tolerance = 5.0; // Píxeles de tolerancia para alineación de borde

  for (const el of ir.elements) {
    // Los fondos generales (background) pueden cubrir todo el canvas
    if (el.id.includes("bg") || el.id.includes("background")) {
      continue;
    }

    // Comprobar coordenadas base
    const elX = el.x;
    const elY = el.y;
    const elW = el.width ?? 0;
    const elH = el.height ?? 0;

    const minX = elX;
    const maxX = elX + elW;
    const minY = elY;
    const maxY = elY + elH;

    // Verificar desborde exterior significativo
    if (
      minX < plot.x - tolerance ||
      maxX > plot.right + tolerance ||
      minY < plot.y - tolerance ||
      maxY > plot.bottom + tolerance
    ) {
      // Elementos críticos como textos o ejes
      if (el.type === "TEXT" || el.id.includes("axis") || el.id.includes("label")) {
        throw new SafeZoneViolationError(
          `Elemento crítico '${el.id}' (${el.type}) fuera de la Safe Zone: ` +
            `bounds=[${minX.toFixed(1)}, ${minY.toFixed(1)}, ${maxX.toFixed(1)}, ${maxY.toFixed(1)}], ` +
            `safeZone=[${plot.x}, ${plot.y}, ${plot.right}, ${plot.bottom}]`
        );
      }
    }
  }
}
