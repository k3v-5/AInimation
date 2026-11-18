import { IndexedAsset } from "../types/index.js";

/**
 * Optimizador de subclips temporales para extraer la mejor ventana dentro del metraje (Fase 15).
 */
export class SubclipOptimizer {
  /**
   * Encuentra el mejor intervalo [start, end] de duración `targetDuration` dentro del asset.
   */
  public static findBestSubclip(
    asset: IndexedAsset,
    targetDuration: number
  ): { start: number; end: number } {
    if (asset.duration <= targetDuration) {
      return { start: 0, end: asset.duration };
    }

    // Buscar si alguna toma individual coincide con la duración deseada con alta calidad
    for (const shot of asset.shots) {
      const shotDur = shot.end - shot.start;
      if (shotDur >= targetDuration) {
        return {
          start: Math.round(shot.start * 100) / 100,
          end: Math.round((shot.start + targetDuration) * 100) / 100,
        };
      }
    }

    // Por defecto, seleccionar desde el inicio o centro
    const start = Math.max(0, Math.min(asset.duration - targetDuration, 0.5));
    return {
      start: Math.round(start * 100) / 100,
      end: Math.round((start + targetDuration) * 100) / 100,
    };
  }
}
