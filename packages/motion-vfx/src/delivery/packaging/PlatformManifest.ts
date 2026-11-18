import { DeliveryPackage } from "../core/DeliveryPackage.js";
import { ProjectSerializer } from "../../persistence/ProjectSerializer.js";

export interface PlatformManifest {
  manifestVersion: string;
  packageId: string;
  projectId: string;
  sourceRevisionId: string;
  generatedAtLogical: number;
  platforms: string[];
  variants: Record<string, {
    aspectRatio: string;
    resolution: string;
    renderArtifactHash: string;
    measuredLufs: number;
  }>;
  thumbnails: Array<{
    timeSeconds: number;
    score: number;
    hash: string;
  }>;
  manifestHash: string;
}

export function generatePlatformManifest(pkg: DeliveryPackage, logicalTime = 1): PlatformManifest {
  const variantMap: Record<string, any> = {};

  for (const [ratio, v] of Object.entries(pkg.variants)) {
    variantMap[ratio] = {
      aspectRatio: v.aspectRatio,
      resolution: `${v.width}x${v.height}`,
      renderArtifactHash: v.renderArtifactHash,
      measuredLufs: v.measuredLufs,
    };
  }

  const thumbList = pkg.thumbnails.map((t) => ({
    timeSeconds: t.timeSeconds,
    score: t.score,
    hash: t.artifactHash,
  }));

  const base = {
    manifestVersion: "2.5.0",
    packageId: pkg.packageId,
    projectId: pkg.projectId,
    sourceRevisionId: pkg.sourceRevisionId,
    generatedAtLogical: logicalTime,
    platforms: [...pkg.platformsSupported].sort(),
    variants: variantMap,
    thumbnails: thumbList,
  };

  const manifestHash = ProjectSerializer.hashCanonical(base);

  return {
    ...base,
    manifestHash,
  };
}
