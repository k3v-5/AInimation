import { AspectRatio, parseAspectRatio } from "../core/AspectRatio.js";
import { TargetPlatform } from "../core/TargetPlatform.js";
import { ReframeStrategy } from "./ReframeStrategy.js";
import { LayoutReframer } from "./LayoutReframer.js";
import { SafeZoneCompliance } from "./SafeZoneCompliance.js";
import { Composition } from "../../core/composition.js";
import { ProjectSerializer } from "../../persistence/ProjectSerializer.js";

export interface AdaptedCompositionResult {
  aspectRatio: AspectRatio;
  composition: Composition;
  contentHash: string;
}

export class AspectRatioAdapter {
  /**
   * Adapta determinísticamente una composición a un nuevo aspect ratio.
   */
  public static adapt(
    sourceComp: Composition,
    targetRatio: AspectRatio,
    platform?: TargetPlatform,
    strategy: ReframeStrategy = "smart_recenter"
  ): AdaptedCompositionResult {
    const targetDim = parseAspectRatio(targetRatio);
    const srcDim = { width: sourceComp.width, height: sourceComp.height };

    const newComp = new Composition({
      id: `${sourceComp.id}_${targetRatio.replace(":", "x")}`,
      name: `${sourceComp.name} [${targetRatio}]`,
      width: targetDim.width,
      height: targetDim.height,
      fps: sourceComp.fps,
      duration: sourceComp.duration,
    });

    // Reencuadrar y adaptar cada elemento
    for (const elem of sourceComp.getElements()) {
      const cloned = elem.clone();

      if (cloned.transform) {
        const currentPos = cloned.transform.position.getValue();
        const currentScale = cloned.transform.scale.getValue();

        const reframed = LayoutReframer.reframe(
          srcDim,
          targetDim,
          {
            position: currentPos,
            scale: currentScale,
            rotation: cloned.transform.rotation.getValue(),
            opacity: cloned.transform.opacity.getValue(),
          },
          strategy
        );

        // Si es texto y hay plataforma definida, proteger safe zone
        if (cloned.type === "text" && platform) {
          const clamped = SafeZoneCompliance.clampToSafeZone(
            platform,
            targetDim,
            reframed.position,
            { width: 400, height: 100 }
          );
          reframed.position = { x: clamped.x, y: clamped.y };
        }

        cloned.transform.position.setValue({ x: reframed.position.x, y: reframed.position.y });
        cloned.transform.scale.setValue({ x: reframed.scale.x, y: reframed.scale.y });
      }

      newComp.addElement(cloned);
    }

    const contentHash = ProjectSerializer.hashCanonical({
      id: newComp.id,
      width: newComp.width,
      height: newComp.height,
      fps: newComp.fps,
      duration: newComp.duration,
      elementsCount: newComp.getElements().length,
    });

    return {
      aspectRatio: targetRatio,
      composition: newComp,
      contentHash,
    };
  }
}
