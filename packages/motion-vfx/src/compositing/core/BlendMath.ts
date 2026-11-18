import { AlphaMode, BlendMode } from "../../scene/types/index.js";

export interface PixelRGBA {
  r: number; // [0, 1]
  g: number; // [0, 1]
  b: number; // [0, 1]
  a: number; // [0, 1]
}

/**
 * Fórmulas matemáticas deterministas de modos de fusión y composición alfa (Fase 5H).
 */
export class BlendMath {
  public static blendChannel(base: number, blend: number, mode: BlendMode): number {
    switch (mode) {
      case "normal":
        return blend;
      case "multiply":
        return base * blend;
      case "screen":
        return base + blend - base * blend;
      case "add":
        return Math.min(1.0, base + blend);
      case "darken":
        return Math.min(base, blend);
      case "lighten":
        return Math.max(base, blend);
      case "overlay":
        return base < 0.5 ? 2 * base * blend : 1 - 2 * (1 - base) * (1 - blend);
      default:
        return blend;
    }
  }

  public static blendPixels(
    bottom: PixelRGBA,
    top: PixelRGBA,
    mode: BlendMode = "normal",
    alphaMode: AlphaMode = "premultiplied"
  ): PixelRGBA {
    const outA = top.a + bottom.a * (1 - top.a);
    if (outA <= 0) {
      return { r: 0, g: 0, b: 0, a: 0 };
    }

    const blendR = this.blendChannel(bottom.r, top.r, mode);
    const blendG = this.blendChannel(bottom.g, top.g, mode);
    const blendB = this.blendChannel(bottom.b, top.b, mode);

    // Compositing Alfa estándar de Porter-Duff (Source Over)
    const outR = (blendR * top.a + bottom.r * bottom.a * (1 - top.a)) / outA;
    const outG = (blendG * top.a + bottom.g * bottom.a * (1 - top.a)) / outA;
    const outB = (blendB * top.a + bottom.b * bottom.a * (1 - top.a)) / outA;

    return {
      r: Math.max(0, Math.min(1, outR)),
      g: Math.max(0, Math.min(1, outG)),
      b: Math.max(0, Math.min(1, outB)),
      a: Math.max(0, Math.min(1, outA)),
    };
  }
}
