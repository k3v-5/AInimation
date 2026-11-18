import { TrackMatteType } from "../types/index.js";

/**
 * Compositor de Track Mattes (Alfa y Luma) entre capas (Fase 5G).
 */
export class TrackMatte {
  public static applyTrackMatte(
    sourceAlpha: Float32Array,
    matteAlpha: Float32Array,
    type: TrackMatteType = "alpha"
  ): Float32Array {
    const len = Math.min(sourceAlpha.length, matteAlpha.length);
    const result = new Float32Array(len);

    for (let i = 0; i < len; i++) {
      const src = sourceAlpha[i];
      const m = matteAlpha[i];

      switch (type) {
        case "alpha":
        case "luma":
          result[i] = src * m;
          break;
        case "alpha-inverted":
        case "luma-inverted":
          result[i] = src * (1.0 - m);
          break;
      }
    }

    return result;
  }
}
