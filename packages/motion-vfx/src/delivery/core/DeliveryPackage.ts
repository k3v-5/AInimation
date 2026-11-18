import { AspectRatio } from "./AspectRatio.js";
import { TargetPlatform } from "./TargetPlatform.js";
import { ProjectSerializer } from "../../persistence/ProjectSerializer.js";

export interface AdaptedMediaVariant {
  aspectRatio: AspectRatio;
  width: number;
  height: number;
  compositionId: string;
  renderArtifactHash: string;
  measuredLufs: number;
  truePeakDb: number;
}

export interface ThumbnailCandidate {
  timeSeconds: number;
  aspectRatio: AspectRatio;
  score: number;
  artifactHash: string;
  description: string;
}

export interface DeliveryPackage {
  packageId: string;
  projectId: string;
  sourceRevisionId: string;
  variants: Record<AspectRatio, AdaptedMediaVariant>;
  thumbnails: ThumbnailCandidate[];
  platformsSupported: TargetPlatform[];
  manifestHash: string;
}

export function createDeliveryPackage(params: {
  packageId: string;
  projectId: string;
  sourceRevisionId: string;
  variants: Record<AspectRatio, AdaptedMediaVariant>;
  thumbnails: ThumbnailCandidate[];
  platformsSupported: TargetPlatform[];
}): DeliveryPackage {
  const manifestHash = ProjectSerializer.hashCanonical({
    packageId: params.packageId,
    projectId: params.projectId,
    sourceRevisionId: params.sourceRevisionId,
    variants: params.variants,
    thumbnails: params.thumbnails,
    platformsSupported: [...params.platformsSupported].sort(),
  });

  return {
    packageId: params.packageId,
    projectId: params.projectId,
    sourceRevisionId: params.sourceRevisionId,
    variants: params.variants,
    thumbnails: params.thumbnails,
    platformsSupported: params.platformsSupported,
    manifestHash,
  };
}
