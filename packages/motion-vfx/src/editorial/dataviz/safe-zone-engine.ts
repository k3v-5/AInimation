import { COMPOSITION_PRESET_DIMENSIONS } from "./constants.js";
import { CompositionPreset, Rect } from "./types.js";

/**
 * REQ-025 §40, §82: Safe Zone Engine.
 * Title safe & platform UI exclusion zones.
 */
export class SafeZoneEngine {
  public static getSafeZone(preset: CompositionPreset): Rect {
    const dim = COMPOSITION_PRESET_DIMENSIONS[preset];

    switch (preset) {
      case "VERTICAL_9_16":
        // Reserved: 280px top (header), 460px bottom (social engagement/audio/captions), 140px right, 100px left
        return {
          x: 100,
          y: 280,
          width: dim.width - 100 - 140, // 840px
          height: dim.height - 280 - 460, // 1180px
        };
      case "SQUARE_1_1":
        // 90px uniform margin
        return {
          x: 90,
          y: 90,
          width: dim.width - 180, // 900px
          height: dim.height - 180, // 900px
        };
      case "LANDSCAPE_16_9":
      default:
        // EBU 10% Title Safe
        return {
          x: 192,
          y: 108,
          width: dim.width - 384, // 1536px
          height: dim.height - 216, // 864px
        };
    }
  }

  public static isInsideSafeZone(element: Rect, safeZone: Rect): boolean {
    const elRight = element.x + element.width;
    const elBottom = element.y + element.height;
    const szRight = safeZone.x + safeZone.width;
    const szBottom = safeZone.y + safeZone.height;

    return (
      element.x >= safeZone.x &&
      element.y >= safeZone.y &&
      elRight <= szRight &&
      elBottom <= szBottom
    );
  }
}
