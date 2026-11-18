export interface Dimensions {
  width: number;
  height: number;
}

export interface SaliencySample {
  time: number;
  focalPoint: [number, number]; // [x, y] normalizado en [0, 1]
  confidence: number;
}

export interface ReframeTransform {
  position: [number, number]; // Coordenadas absolutas en el lienzo destino [px, px]
  scale: [number, number]; // Escala en porcentaje [%, %]
  cropBounds: {
    left: number;
    top: number;
    right: number;
    bottom: number;
  };
}

export interface ReframeKeyframe {
  time: number;
  position: [number, number];
  scale: [number, number];
}

/**
 * Motor de encuadre inteligente y seguimiento de foco para conversión de aspect ratio (Fase 5H / Mejoras).
 * Transforma videos horizontales (16:9) a verticales (9:16) o cuadrados (1:1) manteniendo al sujeto
 * centrado y garantizando cero bordes negros mediante clamping matemático y suavizado de trayectoria.
 */
export class AutoReframeEngine {
  /**
   * Calcula la transformación óptima de encuadre (Pan & Scan) para una muestra puntual de saliency.
   */
  public static computeFocalOffset(
    sourceDim: Dimensions,
    targetDim: Dimensions,
    focalPoint: [number, number] = [0.5, 0.5]
  ): ReframeTransform {
    if (sourceDim.width <= 0 || sourceDim.height <= 0) {
      return {
        position: [targetDim.width / 2, targetDim.height / 2],
        scale: [100, 100],
        cropBounds: { left: 0, top: 0, right: targetDim.width, bottom: targetDim.height },
      };
    }

    // 1. Escala de cobertura mínima para que NUNCA queden bordes negros
    const scaleX = (targetDim.width / sourceDim.width) * 100;
    const scaleY = (targetDim.height / sourceDim.height) * 100;
    const coverScalePct = Math.max(scaleX, scaleY);
    const scaleFactor = coverScalePct / 100;

    const scaledWidth = sourceDim.width * scaleFactor;
    const scaledHeight = sourceDim.height * scaleFactor;

    // 2. Posición ideal centrada en el punto focal (focalPoint normalizado [0, 1])
    const fx = Math.max(0, Math.min(1, focalPoint[0]));
    const fy = Math.max(0, Math.min(1, focalPoint[1]));

    const idealPosX = targetDim.width / 2 + (0.5 - fx) * scaledWidth;
    const idealPosY = targetDim.height / 2 + (0.5 - fy) * scaledHeight;

    // 3. Clamping estricto de bordes: la capa de video escalada debe cubrir completamente el lienzo destino
    // Si scaledWidth > targetWidth, position.x debe estar entre [targetWidth - scaledWidth/2, scaledWidth/2]
    const minPosX = targetDim.width - scaledWidth / 2;
    const maxPosX = scaledWidth / 2;
    const minPosY = targetDim.height - scaledHeight / 2;
    const maxPosY = scaledHeight / 2;

    const clampedX = Math.max(minPosX, Math.min(maxPosX, idealPosX));
    const clampedY = Math.max(minPosY, Math.min(maxPosY, idealPosY));

    const left = clampedX - scaledWidth / 2;
    const top = clampedY - scaledHeight / 2;

    return {
      position: [Number(clampedX.toFixed(2)), Number(clampedY.toFixed(2))],
      scale: [Number(coverScalePct.toFixed(2)), Number(coverScalePct.toFixed(2))],
      cropBounds: {
        left: Number(left.toFixed(2)),
        top: Number(top.toFixed(2)),
        right: Number((left + scaledWidth).toFixed(2)),
        bottom: Number((top + scaledHeight).toFixed(2)),
      },
    };
  }

  /**
   * Genera keyframes continuos y suavizados a partir de una pista de muestras de seguimiento.
   */
  public static generateReframeKeyframes(
    saliencyTrack: SaliencySample[],
    sourceDim: Dimensions,
    targetDim: Dimensions,
    smoothingWindow = 3
  ): ReframeKeyframe[] {
    if (saliencyTrack.length === 0) {
      const defaultTransform = this.computeFocalOffset(sourceDim, targetDim, [0.5, 0.5]);
      return [
        {
          time: 0,
          position: defaultTransform.position,
          scale: defaultTransform.scale,
        },
      ];
    }

    const rawTransforms = saliencyTrack.map((s) => ({
      time: s.time,
      ...this.computeFocalOffset(sourceDim, targetDim, s.focalPoint),
    }));

    // Suavizado por media móvil (Moving Average Filter) para eliminar temblores de cámara
    const smoothedKeyframes: ReframeKeyframe[] = [];

    for (let i = 0; i < rawTransforms.length; i++) {
      let sumX = 0;
      let sumY = 0;
      let count = 0;

      const halfW = Math.floor(smoothingWindow / 2);
      for (let w = -halfW; w <= halfW; w++) {
        const idx = i + w;
        if (idx >= 0 && idx < rawTransforms.length) {
          sumX += rawTransforms[idx].position[0];
          sumY += rawTransforms[idx].position[1];
          count++;
        }
      }

      smoothedKeyframes.push({
        time: rawTransforms[i].time,
        position: [Number((sumX / count).toFixed(2)), Number((sumY / count).toFixed(2))],
        scale: rawTransforms[i].scale,
      });
    }

    return smoothedKeyframes;
  }
}
