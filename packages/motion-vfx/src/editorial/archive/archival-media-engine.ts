import crypto from "crypto";
import {
  ArchivalAsset,
  ArchivalMediaPlan,
  ArchivalMediaPlanSchema,
  ArchivalTreatment,
  ArchivalTreatmentSchema,
  KenBurnsParams,
} from "../contracts/archive.types.js";

/**
 * REQ-016 & REQ-087: Archival Media Engine.
 * Formulates historical archive treatments, computes deterministic Ken Burns pan/zoom moves,
 * formats date stamps and enforces license compliance.
 */
export class ArchivalMediaEngine {
  /**
   * Generates deterministic Ken Burns pan and zoom parameters for a photo or archival clip.
   */
  public static calculateKenBurns(params: {
    isStillPhoto: boolean;
    durationSeconds: number;
    motionDirection?: "ZOOM_IN" | "ZOOM_OUT" | "PAN_LEFT" | "PAN_RIGHT" | "STATIC";
    seed?: number;
  }): KenBurnsParams {
    const direction = params.motionDirection ?? (params.isStillPhoto ? "ZOOM_IN" : "STATIC");

    switch (direction) {
      case "ZOOM_IN":
        return {
          scaleStart: 1.0,
          scaleEnd: 1.15,
          panStartX: 0.5,
          panStartY: 0.5,
          panEndX: 0.48,
          panEndY: 0.52,
          easing: "EASE_IN_OUT",
        };
      case "ZOOM_OUT":
        return {
          scaleStart: 1.15,
          scaleEnd: 1.0,
          panStartX: 0.52,
          panStartY: 0.48,
          panEndX: 0.5,
          panEndY: 0.5,
          easing: "EASE_IN_OUT",
        };
      case "PAN_LEFT":
        return {
          scaleStart: 1.1,
          scaleEnd: 1.1,
          panStartX: 0.55,
          panStartY: 0.5,
          panEndX: 0.45,
          panEndY: 0.5,
          easing: "LINEAR",
        };
      case "PAN_RIGHT":
        return {
          scaleStart: 1.1,
          scaleEnd: 1.1,
          panStartX: 0.45,
          panStartY: 0.5,
          panEndX: 0.55,
          panEndY: 0.5,
          easing: "LINEAR",
        };
      case "STATIC":
      default:
        return {
          scaleStart: 1.0,
          scaleEnd: 1.0,
          panStartX: 0.5,
          panStartY: 0.5,
          panEndX: 0.5,
          panEndY: 0.5,
          easing: "LINEAR",
        };
    }
  }

  /**
   * Formats a formal, publication-ready archival date stamp.
   */
  public static formatDateStamp(asset: ArchivalAsset): string {
    if (asset.dateExact) {
      return `FILE FOOTAGE // ${asset.dateExact.toUpperCase()}`;
    }
    if (asset.year) {
      return `FILE FOOTAGE // ${asset.year}`;
    }
    return `ARCHIVE MATERIAL // ${asset.sourceArchive.toUpperCase()}`;
  }

  /**
   * Builds an ArchivalMediaPlan auditing all archival assets and treatments for a production.
   */
  public static buildArchivalPlan(params: {
    projectId: string;
    assets: ArchivalAsset[];
    clipPlacements: { clipId: string; assetId: string; startSeconds: number; endSeconds: number }[];
    grainOverlayDefault?: boolean;
  }): ArchivalMediaPlan {
    const { projectId, assets, clipPlacements } = params;
    const assetMap = new Map<string, ArchivalAsset>();
    for (const a of assets) {
      assetMap.set(a.id, a);
    }

    const treatments: ArchivalTreatment[] = [];
    const issues: string[] = [];
    let licenseCompliant = true;

    for (const placement of clipPlacements) {
      const asset = assetMap.get(placement.assetId);
      if (!asset) {
        issues.push(`Placement references missing archival asset '${placement.assetId}'`);
        licenseCompliant = false;
        continue;
      }

      // Check license
      if (asset.licenseStatus === "EXPIRED") {
        issues.push(`Asset '${asset.id}' (${asset.title}) has EXPIRED license (${asset.licenseExpiryDate ?? "unknown"}).`);
        licenseCompliant = false;
      } else if (asset.licenseStatus === "RESTRICTED") {
        issues.push(`Asset '${asset.id}' (${asset.title}) has RESTRICTED distribution conditions.`);
      }

      const duration = placement.endSeconds - placement.startSeconds;
      const kenBurns = asset.isStillPhoto
        ? this.calculateKenBurns({ isStillPhoto: true, durationSeconds: duration })
        : undefined;

      const dateStampText = this.formatDateStamp(asset);
      const sourceAttributionText = `Source: ${asset.sourceArchive}${asset.creator ? ` / ${asset.creator}` : ""}`;

      treatments.push(
        ArchivalTreatmentSchema.parse({
          clipId: placement.clipId,
          assetId: asset.id,
          kenBurns,
          dateStampText,
          sourceAttributionText,
          grainOverlay: params.grainOverlayDefault ?? false,
          monochromeFilter: false,
          timelineStartSeconds: placement.startSeconds,
          timelineEndSeconds: placement.endSeconds,
        })
      );
    }

    const payloadForHash = JSON.stringify({
      projectId,
      treatments: treatments.map((t) => ({ clip: t.clipId, asset: t.assetId, start: t.timelineStartSeconds })),
      licenseCompliant,
      issues,
    });

    const checksumSha256 = crypto
      .createHash("sha256")
      .update(payloadForHash)
      .digest("hex");

    return ArchivalMediaPlanSchema.parse({
      projectId,
      treatments,
      licenseCompliant,
      issues,
      checksumSha256,
    });
  }
}
