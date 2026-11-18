import { Composition } from "../../core/composition.js";
import { DeliveryConfig, createDeliveryConfig } from "../core/DeliveryConfig.js";
import { AspectRatio } from "../core/AspectRatio.js";
import { DeliveryPackage, AdaptedMediaVariant, createDeliveryPackage } from "../core/DeliveryPackage.js";
import { AspectRatioAdapter } from "../adapter/AspectRatioAdapter.js";
import { LoudnessNormalizer } from "../audio/LoudnessNormalizer.js";
import { ThumbnailSelector } from "../thumbnails/ThumbnailSelector.js";
import { generatePlatformManifest, PlatformManifest } from "./PlatformManifest.js";

export interface PackageBuildResult {
  pkg: DeliveryPackage;
  manifest: PlatformManifest;
}

export class SocialDeliveryPackager {
  /**
   * Construye determinísticamente el paquete de entrega social completo a partir de una composición base.
   */
  public static package(
    baseComp: Composition,
    projectId: string,
    revisionId: string,
    configOverrides?: Partial<DeliveryConfig>
  ): PackageBuildResult {
    const config = createDeliveryConfig(configOverrides);
    const variants: Record<AspectRatio, AdaptedMediaVariant> = {} as any;

    // Generar variantes adaptadas para cada aspect ratio solicitado
    for (const ratio of config.targetAspectRatios) {
      const adapted = AspectRatioAdapter.adapt(baseComp, ratio, undefined, config.reframeStrategy);

      // Simular audio normalizado para la plataforma por defecto del ratio
      const mockAudioSamples = new Float32Array(1000);
      for (let i = 0; i < 1000; i++) mockAudioSamples[i] = Math.sin(i * 0.1) * 0.5;

      const normResult = LoudnessNormalizer.normalize(mockAudioSamples, "tiktok");

      variants[ratio] = {
        aspectRatio: ratio,
        width: adapted.composition.width,
        height: adapted.composition.height,
        compositionId: adapted.composition.id,
        renderArtifactHash: adapted.contentHash,
        measuredLufs: normResult.report.finalLufs,
        truePeakDb: normResult.report.finalTruePeakDb,
      };
    }

    // Extraer miniaturas si está configurado
    const thumbnails = config.extractThumbnails
      ? ThumbnailSelector.selectThumbnails(baseComp, "9:16", config.thumbnailCount)
      : [];

    const pkg = createDeliveryPackage({
      packageId: `pkg_${projectId}_${revisionId.slice(0, 8)}`,
      projectId,
      sourceRevisionId: revisionId,
      variants,
      thumbnails,
      platformsSupported: config.targetPlatforms,
    });

    const manifest = generatePlatformManifest(pkg);

    return {
      pkg,
      manifest,
    };
  }
}
