import { COMPOSITION_PRESET_DIMENSIONS } from "./constants.js";
import { CompositionPreset, DataVizLayout, Margins, Rect } from "./types.js";
import { SafeZoneEngine } from "./safe-zone-engine.js";

/**
 * REQ-025 §11, §12, §39: Coordinate & Layout Engine.
 * Transforms relative compositions to exact virtual pixel bounds with origin = top-left.
 */
export class LayoutEngine {
  public static computeLayout(preset: CompositionPreset, customMargins?: Margins): DataVizLayout {
    const dim = COMPOSITION_PRESET_DIMENSIONS[preset];
    const bounds: Rect = {
      x: 0,
      y: 0,
      width: dim.width,
      height: dim.height,
    };

    const safeZone = SafeZoneEngine.getSafeZone(preset);

    // Margins default to safe zone offsets
    const margins: Margins = customMargins ?? {
      top: safeZone.y,
      left: safeZone.x,
      right: bounds.width - (safeZone.x + safeZone.width),
      bottom: bounds.height - (safeZone.y + safeZone.height),
    };

    const contentBounds: Rect = {
      x: margins.left,
      y: margins.top,
      width: bounds.width - margins.left - margins.right,
      height: bounds.height - margins.top - margins.bottom,
    };

    return {
      bounds,
      margins,
      safeZone,
      contentBounds,
    };
  }

  public static isOutOfBounds(box: Rect, bounds: Rect): boolean {
    return (
      box.x < bounds.x ||
      box.y < bounds.y ||
      box.x + box.width > bounds.x + bounds.width ||
      box.y + box.height > bounds.y + bounds.height
    );
  }
}
