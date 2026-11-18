import { AspectRatioDimension } from "../core/AspectRatio.js";
import { ReframeStrategy } from "./ReframeStrategy.js";

export interface ReframedTransform {
  position: { x: number; y: number };
  scale: { x: number; y: number };
  anchor: { x: number; y: number };
  rotation: number;
  opacity: number;
}

export class LayoutReframer {
  /**
   * Reencuadra una posición y escala espacial desde una resolución origen a una resolución destino.
   */
  public static reframe(
    srcDim: { width: number; height: number },
    dstDim: AspectRatioDimension,
    originalTransform: {
      position?: { x: number; y: number };
      scale?: { x: number; y: number };
      anchor?: { x: number; y: number };
      rotation?: number;
      opacity?: number;
    },
    strategy: ReframeStrategy = "smart_recenter"
  ): ReframedTransform {
    const origPos = originalTransform.position ?? { x: srcDim.width / 2, y: srcDim.height / 2 };
    const origScale = originalTransform.scale ?? { x: 1.0, y: 1.0 };
    const origAnchor = originalTransform.anchor ?? { x: 0.5, y: 0.5 };
    const origRot = originalTransform.rotation ?? 0;
    const origOpacity = originalTransform.opacity ?? 1.0;

    const scaleX = dstDim.width / srcDim.width;
    const scaleY = dstDim.height / srcDim.height;

    let finalScaleMultiplier = 1.0;
    let offsetX = 0;
    let offsetY = 0;

    if (strategy === "fit" || strategy === "letterbox") {
      finalScaleMultiplier = Math.min(scaleX, scaleY);
      offsetX = (dstDim.width - srcDim.width * finalScaleMultiplier) / 2;
      offsetY = (dstDim.height - srcDim.height * finalScaleMultiplier) / 2;
    } else if (strategy === "fill") {
      finalScaleMultiplier = Math.max(scaleX, scaleY);
      offsetX = (dstDim.width - srcDim.width * finalScaleMultiplier) / 2;
      offsetY = (dstDim.height - srcDim.height * finalScaleMultiplier) / 2;
    } else {
      // smart_recenter: escala proporcional ponderada manteniendo el centro visual
      finalScaleMultiplier = Math.min(scaleX, scaleY);
      offsetX = (dstDim.width - srcDim.width * finalScaleMultiplier) / 2;
      offsetY = (dstDim.height - srcDim.height * finalScaleMultiplier) / 2;
    }

    const newX = origPos.x * finalScaleMultiplier + offsetX;
    const newY = origPos.y * finalScaleMultiplier + offsetY;

    return {
      position: { x: Math.round(newX * 100) / 100, y: Math.round(newY * 100) / 100 },
      scale: {
        x: Math.round(origScale.x * finalScaleMultiplier * 1000) / 1000,
        y: Math.round(origScale.y * finalScaleMultiplier * 1000) / 1000,
      },
      anchor: { ...origAnchor },
      rotation: origRot,
      opacity: origOpacity,
    };
  }
}
