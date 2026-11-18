import { PlatformProfile, SafeArea, SemanticPosition } from "../types/index.js";

export const DEFAULT_TIKTOK_PROFILE: PlatformProfile = {
  id: "tiktok-vertical",
  name: "TikTok Vertical (9:16)",
  width: 1080,
  height: 1920,
  safeArea: {
    top: 150,
    bottom: 350,
    left: 60,
    right: 120,
  },
};

/**
 * Calculador de coordenadas globales de subtítulos respetando la zona segura de la plataforma (Fase 5E).
 */
export class CaptionPositionResolver {
  public static resolve(
    position: SemanticPosition,
    blockWidth: number,
    blockHeight: number,
    profile: PlatformProfile = DEFAULT_TIKTOK_PROFILE
  ): { x: number; y: number } {
    const { width: screenW, height: screenH, safeArea } = profile;

    const usableW = screenW - safeArea.left - safeArea.right;
    const usableH = screenH - safeArea.top - safeArea.bottom;

    let x = safeArea.left + (usableW - blockWidth) / 2; // Default horizontal center
    let y = safeArea.top + (usableH - blockHeight) / 2; // Default vertical center

    if (position === "top" || position === "top-left" || position === "top-right") {
      y = safeArea.top;
    } else if (position === "bottom" || position === "bottom-center" || position === "bottom-left" || position === "bottom-right") {
      y = screenH - safeArea.bottom - blockHeight;
    }

    if (position === "top-left" || position === "bottom-left") {
      x = safeArea.left;
    } else if (position === "top-right" || position === "bottom-right") {
      x = screenW - safeArea.right - blockWidth;
    }

    return {
      x: Math.round(x),
      y: Math.round(y),
    };
  }
}
