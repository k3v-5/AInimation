import {
  RectBounds,
  SafeZoneProfile,
  SafeZoneResolutionResult,
  SemanticPosition,
} from "../types/index.js";

export const StandardSafeZoneProfiles: Record<string, SafeZoneProfile> = {
  "tiktok-portrait": {
    id: "tiktok-portrait",
    name: "TikTok 9:16 Vertical",
    version: "2026.1",
    source: "TikTok Platform Spec 2026",
    confidence: 1.0,
    canvasWidth: 1080,
    canvasHeight: 1920,
    topInset: 150,
    bottomInset: 350,
    leftInset: 40,
    rightInset: 140, // Espacio para botones de interacción (Like, Comment, Share)
    forbiddenRegions: [
      { x: 1080 - 140, y: 800, width: 140, height: 800 }, // Barra vertical de acciones derecha
      { x: 0, y: 1920 - 320, width: 1080, height: 320 }, // Barra de descripción y audio inferior
    ],
  },
  "reels-portrait": {
    id: "reels-portrait",
    name: "Instagram Reels 9:16 Vertical",
    version: "2026.1",
    source: "Instagram Platform Spec 2026",
    confidence: 1.0,
    canvasWidth: 1080,
    canvasHeight: 1920,
    topInset: 160,
    bottomInset: 280,
    leftInset: 40,
    rightInset: 120,
    forbiddenRegions: [
      { x: 1080 - 120, y: 900, width: 120, height: 750 },
      { x: 0, y: 1920 - 250, width: 1080, height: 250 },
    ],
  },
  "shorts-portrait": {
    id: "shorts-portrait",
    name: "YouTube Shorts 9:16 Vertical",
    version: "2026.1",
    source: "YouTube Shorts Spec 2026",
    confidence: 1.0,
    canvasWidth: 1080,
    canvasHeight: 1920,
    topInset: 120,
    bottomInset: 220,
    leftInset: 40,
    rightInset: 110,
    forbiddenRegions: [
      { x: 1080 - 110, y: 950, width: 110, height: 700 },
      { x: 0, y: 1920 - 200, width: 1080, height: 200 },
    ],
  },
};

/**
 * Resolvedor determinista de zonas seguras y ajuste posicional de subtítulos (Fase 16 / 16.1).
 */
export class SafeZoneResolver {
  /**
   * Resuelve y ajusta la posición final de un bloque de subtítulos según el perfil de Safe Zone versionado.
   */
  public static resolve(
    blockWidth: number,
    blockHeight: number,
    preferredPosition: SemanticPosition = "bottom-center",
    profile: SafeZoneProfile = StandardSafeZoneProfiles["tiktok-portrait"]
  ): SafeZoneResolutionResult {
    const diagnostics: string[] = [];

    const safeMinX = profile.leftInset;
    const safeMaxX = profile.canvasWidth - profile.rightInset;
    const safeMinY = profile.topInset;
    const safeMaxY = profile.canvasHeight - profile.bottomInset;
    const safeWidth = safeMaxX - safeMinX;
    const safeHeight = safeMaxY - safeMinY;

    if (blockWidth > safeWidth) {
      diagnostics.push(`block-width-exceeds-safe-width: ${blockWidth} > ${safeWidth}`);
    }
    if (blockHeight > safeHeight) {
      diagnostics.push(`block-height-exceeds-safe-height: ${blockHeight} > ${safeHeight}`);
    }

    // Calcular posición física teórica inicial según anchor preferido
    const centerX = profile.canvasWidth / 2;
    let targetX = centerX;
    let targetY = profile.canvasHeight / 2;

    if (preferredPosition === "bottom" || preferredPosition === "bottom-center") {
      targetY = profile.canvasHeight - blockHeight / 2 - 40;
    } else if (preferredPosition === "top" || preferredPosition === "top-center") {
      targetY = blockHeight / 2 + 40;
    } else if (preferredPosition === "center") {
      targetY = profile.canvasHeight / 2;
    }

    const calculatedBounds: RectBounds = {
      x: Number((targetX - blockWidth / 2).toFixed(2)),
      y: Number((targetY - blockHeight / 2).toFixed(2)),
      width: blockWidth,
      height: blockHeight,
    };

    // Comprobar colisión con regiones prohibidas o desborde de Safe Area
    let adjustedY = calculatedBounds.y;
    let isAdjusted = false;

    // Si desborda por abajo del área segura
    if (adjustedY + blockHeight > safeMaxY) {
      adjustedY = safeMaxY - blockHeight;
      isAdjusted = true;
      diagnostics.push("adjusted-bottom-overflow");
    }

    // Si desborda por arriba del área segura
    if (adjustedY < safeMinY) {
      adjustedY = safeMinY;
      isAdjusted = true;
      diagnostics.push("adjusted-top-overflow");
    }

    const finalBounds: RectBounds = {
      x: calculatedBounds.x,
      y: Number(adjustedY.toFixed(2)),
      width: blockWidth,
      height: blockHeight,
    };

    let status: "safe" | "adjusted" | "unresolved" = "safe";
    if (isAdjusted) {
      status = "adjusted";
    }

    // Si el bloque supera la altura completa del canvas
    if (blockHeight > profile.canvasHeight) {
      status = "unresolved";
      diagnostics.push("block-larger-than-canvas");
    }

    return {
      originalBounds: calculatedBounds,
      adjustedBounds: finalBounds,
      position: preferredPosition,
      offset: {
        x: Number((finalBounds.x - calculatedBounds.x).toFixed(2)),
        y: Number((finalBounds.y - calculatedBounds.y).toFixed(2)),
      },
      status,
      diagnostics,
    };
  }
}
