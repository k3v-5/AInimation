import { BlendMath } from "../../compositing/core/BlendMath.js";
import { BlendMode } from "../../compositing/types/index.js";
import { FrameContext, RenderFrame } from "../types/index.js";

export interface RenderLayerItem {
  id: string;
  frame: RenderFrame;
  opacity: number;
  blendMode: BlendMode;
}

/**
 * Compositor de fotogramas y mezcla de capas con canal Alfa (Fase 9).
 */
export class Compositor {
  /**
   * Compone una pila de capas ordenadas de fondo a frente en un único fotograma resultante.
   */
  public static composite(
    layers: RenderLayerItem[],
    context: FrameContext
  ): RenderFrame {
    // Si no hay capas, devolver fotograma vacío transparente/negro
    if (layers.length === 0) {
      return {
        frameNumber: context.frame,
        time: context.time,
        width: context.width,
        height: context.height,
        channels: 4,
      };
    }

    // Inicializar color base acumulado con la primera capa (o transparente)
    let accR = 0,
      accG = 0,
      accB = 0,
      accA = 0;

    for (const layer of layers) {
      const topColor = {
        r: 1.0,
        g: 1.0,
        b: 1.0,
        a: Math.max(0, Math.min(1, layer.opacity)),
      };
      const bottomColor = { r: accR, g: accG, b: accB, a: accA };

      // Aplicar Blend Mode matemático de 5H
      const blended = BlendMath.blendPixels(bottomColor, topColor, layer.blendMode);
      accR = blended.r;
      accG = blended.g;
      accB = blended.b;
      accA = blended.a;
    }

    return {
      frameNumber: context.frame,
      time: context.time,
      width: context.width,
      height: context.height,
      channels: 4,
      metadata: {
        compositeLayersCount: layers.length,
        finalColor: { r: accR, g: accG, b: accB, a: accA },
      },
    };
  }
}
