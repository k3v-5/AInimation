import { MotionEngineError } from "../../errors/index.js";

export class ReframingError extends MotionEngineError {
  constructor(message: string, public readonly context?: Record<string, any>) {
    super(`Reframing Error: ${message}`);
  }
}

export type ReframingMode =
  | "dynamic_pan_and_scan"
  | "split_screen_stacked"
  | "blur_background_boxed";

export interface FocalPointSample {
  timeSec: number;
  normalizedX: number; // 0.0 (izquierda) a 1.0 (derecha) en el marco original 16:9
  normalizedY?: number; // 0.0 a 1.0
  confidence: number;
}

export interface ReframedKeyframe {
  timeSec: number;
  position: [number, number]; // Coordenadas [X, Y] en la composición de destino (1080x1920)
  scale: [number, number]; // Escala [X, Y] en porcentaje
}

export interface ReframingResult {
  mode: ReframingMode;
  targetResolution: { width: number; height: number };
  keyframes: ReframedKeyframe[];
  splitScreenConfig?: {
    topLayer: { bounds: [number, number, number, number]; scale: [number, number] };
    bottomLayer: { bounds: [number, number, number, number]; scale: [number, number] };
    dividerStrokeWidth: number;
  };
  blurredBackgroundConfig?: {
    blurRadiusPx: number;
    dimmingOpacity: number;
  };
}

/**
 * Motor de Auto-Reencuadre Inteligente 16:9 a 9:16 (Active Speaker / Social Re-framing).
 */
export class ActiveSpeakerReframingEngine {
  /**
   * Genera las keyframes de posición y escala para reencuadrar metraje 16:9 en 9:16 vertical.
   */
  public static calculateReframing(
    mode: ReframingMode,
    focalPoints: FocalPointSample[],
    sourceWidth = 1920,
    sourceHeight = 1080,
    targetWidth = 1080,
    targetHeight = 1920,
    deadzonePx = 45.0,
    smoothingAlpha = 0.20
  ): ReframingResult {
    if (sourceWidth <= 0 || sourceHeight <= 0 || targetWidth <= 0 || targetHeight <= 0) {
      throw new ReframingError("Source and target dimensions must be strictly positive.");
    }

    if (mode === "split_screen_stacked") {
      return this.generateSplitScreenStacked(sourceWidth, sourceHeight, targetWidth, targetHeight);
    }

    if (mode === "blur_background_boxed") {
      return this.generateBlurBackgroundBoxed(sourceWidth, sourceHeight, targetWidth, targetHeight);
    }

    // Modo por defecto: dynamic_pan_and_scan
    return this.generateDynamicPanAndScan(
      focalPoints,
      sourceWidth,
      sourceHeight,
      targetWidth,
      targetHeight,
      deadzonePx,
      smoothingAlpha
    );
  }

  private static generateDynamicPanAndScan(
    focalPoints: FocalPointSample[],
    sW: number,
    sH: number,
    tW: number,
    tH: number,
    deadzonePx: number,
    alpha: number
  ): ReframingResult {
    // Escala para cubrir la altura vertical completa
    const scaleFactor = (tH / sH) * 100;
    const scaledSourceWidth = sW * (tH / sH);

    // Límites de desplazamiento X para no dejar bandas negras en los lados
    const minX = tW - scaledSourceWidth / 2;
    const maxX = scaledSourceWidth / 2;

    const keyframes: ReframedKeyframe[] = [];
    let currentX = tW / 2; // Centro inicial

    const sortedSamples = [...focalPoints].sort((a, b) => a.timeSec - b.timeSec);

    if (sortedSamples.length === 0) {
      // Sin muestras: centrado estático
      keyframes.push({
        timeSec: 0.0,
        position: [tW / 2, tH / 2],
        scale: [scaleFactor, scaleFactor],
      });
      return {
        mode: "dynamic_pan_and_scan",
        targetResolution: { width: tW, height: tH },
        keyframes,
      };
    }

    for (const sample of sortedSamples) {
      const focalPx = sample.normalizedX * scaledSourceWidth;
      const targetX = tW / 2 - (focalPx - scaledSourceWidth / 2);
      const clampedTargetX = Math.max(minX, Math.min(maxX, targetX));

      // Aplicar zona muerta (Deadzone) para evitar vibración / jitter
      if (Math.abs(clampedTargetX - currentX) > deadzonePx) {
        currentX = alpha * clampedTargetX + (1 - alpha) * currentX;
      }

      keyframes.push({
        timeSec: sample.timeSec,
        position: [Math.round(currentX * 10) / 10, tH / 2],
        scale: [scaleFactor, scaleFactor],
      });
    }

    return {
      mode: "dynamic_pan_and_scan",
      targetResolution: { width: tW, height: tH },
      keyframes,
    };
  }

  private static generateSplitScreenStacked(sW: number, sH: number, tW: number, tH: number): ReframingResult {
    const halfHeight = tH / 2;
    const scale = Math.max((tW / sW) * 100, (halfHeight / sH) * 100);

    return {
      mode: "split_screen_stacked",
      targetResolution: { width: tW, height: tH },
      keyframes: [
        { timeSec: 0, position: [tW / 2, halfHeight / 2], scale: [scale, scale] },
      ],
      splitScreenConfig: {
        topLayer: { bounds: [0, 0, tW, halfHeight], scale: [scale, scale] },
        bottomLayer: { bounds: [0, halfHeight, tW, halfHeight], scale: [scale, scale] },
        dividerStrokeWidth: 4,
      },
    };
  }

  private static generateBlurBackgroundBoxed(sW: number, sH: number, tW: number, tH: number): ReframingResult {
    const fitScale = (tW / sW) * 100;
    const coverScale = Math.max((tW / sW) * 100, (tH / sH) * 100);

    return {
      mode: "blur_background_boxed",
      targetResolution: { width: tW, height: tH },
      keyframes: [
        { timeSec: 0, position: [tW / 2, tH / 2], scale: [fitScale, fitScale] },
      ],
      blurredBackgroundConfig: {
        blurRadiusPx: 45,
        dimmingOpacity: 40,
      },
    };
  }
}
