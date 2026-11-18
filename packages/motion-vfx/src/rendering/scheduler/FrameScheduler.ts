import { FrameContext, RenderFrame, RenderProgress, RenderStage } from "../types/index.js";

/**
 * Planificador y generador de fotogramas con cálculo de progreso y subframes (Fase 9).
 */
export class FrameScheduler {
  /**
   * Genera los timestamps de subframes para simulación de Motion Blur por acumulación temporal.
   */
  public static calculateSubframeSamples(
    frameTime: number,
    fps: number,
    samplesCount = 5,
    shutterAngle = 180 // Grados de obturador (180° = mitad del frame)
  ): number[] {
    if (samplesCount <= 1) return [frameTime];

    const frameDuration = 1 / fps;
    const exposureDuration = frameDuration * (shutterAngle / 360);
    const halfExposure = exposureDuration / 2;

    const timestamps: number[] = [];
    const step = exposureDuration / (samplesCount - 1);

    for (let i = 0; i < samplesCount; i++) {
      timestamps.push(frameTime - halfExposure + i * step);
    }

    return timestamps;
  }

  /**
   * Generador asíncrono de contextos de fotogramas secuenciales.
   */
  public static async *generateFrames(
    totalFrames: number,
    fps: number,
    width: number,
    height: number,
    onProgress?: (progress: RenderProgress) => void
  ): AsyncIterable<FrameContext> {
    const startTime = performance.now();

    for (let f = 0; f < totalFrames; f++) {
      const time = f / fps;
      const progressPercent = ((f + 1) / totalFrames) * 100;

      const elapsedSec = (performance.now() - startTime) / 1000;
      const currentFps = f > 0 && elapsedSec > 0 ? f / elapsedSec : fps;
      const remainingFrames = totalFrames - (f + 1);
      const etaSeconds = currentFps > 0 ? remainingFrames / currentFps : 0;

      if (onProgress) {
        onProgress({
          frame: f + 1,
          totalFrames,
          timeRendered: time,
          percentage: Math.round(progressPercent * 10) / 10,
          fps: Math.round(currentFps * 10) / 10,
          etaSeconds: Math.round(etaSeconds * 10) / 10,
          stage: "evaluating" as RenderStage,
        });
      }

      yield {
        frame: f,
        time,
        fps,
        width,
        height,
        quality: "final",
      };
    }
  }
}
