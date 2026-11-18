import { TargetPlatform, SOCIAL_PLATFORM_PROFILES } from "../core/TargetPlatform.js";
import { AspectRatioDimension } from "../core/AspectRatio.js";

export class SafeZoneCompliance {
  /**
   * Ajusta la posición vertical y horizontal de un elemento de texto para asegurar que no invada las zonas seguras de la plataforma.
   */
  public static clampToSafeZone(
    platform: TargetPlatform,
    canvasDim: AspectRatioDimension,
    position: { x: number; y: number },
    elementBounds: { width: number; height: number }
  ): { x: number; y: number; clamped: boolean } {
    const profile = SOCIAL_PLATFORM_PROFILES[platform];
    const margins = profile.safeZoneMargins;

    const minX = margins.left + elementBounds.width / 2;
    const maxX = canvasDim.width - margins.right - elementBounds.width / 2;

    const minY = margins.top + elementBounds.height / 2;
    const maxY = canvasDim.height - margins.bottom - elementBounds.height / 2;

    const clampedX = Math.max(minX, Math.min(maxX, position.x));
    const clampedY = Math.max(minY, Math.min(maxY, position.y));

    const wasClamped = clampedX !== position.x || clampedY !== position.y;

    return {
      x: Math.round(clampedX * 100) / 100,
      y: Math.round(clampedY * 100) / 100,
      clamped: wasClamped,
    };
  }
}
