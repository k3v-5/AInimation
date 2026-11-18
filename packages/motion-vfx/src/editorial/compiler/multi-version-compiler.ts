import crypto from "crypto";
import { EditorialClipInput, EditorialIR } from "../ir/editorial-ir.types.js";
import { EditorialIRBuilder } from "../ir/editorial-ir-builder.js";
import {
  EDITORIAL_ASPECT_RATIO_DIMENSIONS,
  AspectRatioTarget,
  CutdownTarget,
  EditorialVariantPlan,
  EditorialVariantPlanSchema,
} from "./multi-version.types.js";

/**
 * REQ-026, REQ-027 & REQ-028: Multi-Version Editorial Compiler.
 * Compiles non-destructive derivatives (Full length, 60s, 30s, 15s, 6s)
 * across multiple aspect ratios (16:9, 9:16, 1:1, 4:5, 21:9) from a master Editorial IR.
 */
export class MultiVersionCompiler {
  private static readonly TARGET_DURATIONS: Record<CutdownTarget, number> = {
    FULL_LENGTH: Infinity,
    CUTDOWN_60S: 60.0,
    CUTDOWN_30S: 30.0,
    CUTDOWN_15S: 15.0,
    HOOK_TEASER_6S: 6.0,
  };

  /**
   * Compiles a specific derivative variant from the master Editorial IR.
   */
  public static compileVariant(params: {
    masterIR: EditorialIR;
    target: CutdownTarget;
    aspectRatio: AspectRatioTarget;
    deterministicTimestamp?: string;
  }): { variantIR: EditorialIR; plan: EditorialVariantPlan } {
    const { masterIR, target, aspectRatio } = params;
    const maxDurationSeconds = this.TARGET_DURATIONS[target];
    const dimensions = EDITORIAL_ASPECT_RATIO_DIMENSIONS[aspectRatio];

    const variantId = `${masterIR.projectId}_${target.toLowerCase()}_${aspectRatio.replace(":", "x")}`;
    const variantTitle = `${masterIR.metadata.title} [${target} - ${aspectRatio}]`;

    const builder = new EditorialIRBuilder(variantId, {
      ...masterIR.metadata,
      title: variantTitle,
      width: dimensions.width,
      height: dimensions.height,
    });

    const retainedClipIds: string[] = [];

    // Find Primary Video Track to determine cutoff time
    const primaryTrack = masterIR.tracks.find((t) => t.type === "VIDEO_PRIMARY") ?? masterIR.tracks[0];
    let effectiveDurationLimit = maxDurationSeconds;

    if (primaryTrack && isFinite(maxDurationSeconds)) {
      let accumulatedTime = 0.0;
      for (const clip of primaryTrack.clips) {
        if (accumulatedTime + clip.timelineRange.durationSeconds <= maxDurationSeconds) {
          accumulatedTime += clip.timelineRange.durationSeconds;
          retainedClipIds.push(clip.id);
        } else {
          // Add partial trim of this clip to reach target if headroom remains
          const remaining = maxDurationSeconds - accumulatedTime;
          if (remaining >= 1.0) {
            accumulatedTime += remaining;
            retainedClipIds.push(clip.id);
          }
          break;
        }
      }
      effectiveDurationLimit = Math.max(1.0, accumulatedTime);
    }

    // Clone & re-time tracks up to effectiveDurationLimit
    for (const track of masterIR.tracks) {
      builder.createTrack({
        id: track.id,
        name: track.name,
        type: track.type,
        index: track.index,
        isMuted: track.isMuted,
        isLocked: track.isLocked,
      });

      let timelineCursor = 0.0;

      for (const clip of track.clips) {
        if (clip.timelineRange.startSeconds >= effectiveDurationLimit) {
          continue; // Past cutdown limit
        }

        const clipDuration = clip.timelineRange.durationSeconds;
        const availableInCutdown = effectiveDurationLimit - clip.timelineRange.startSeconds;
        const effectiveClipDuration = Math.min(clipDuration, availableInCutdown);

        if (effectiveClipDuration > 0.1) {
          const adaptedClip: EditorialClipInput = {
            id: clip.id,
            assetId: clip.assetId,
            label: clip.label,
            sourceRange: {
              startSeconds: clip.sourceRange.startSeconds,
              durationSeconds: effectiveClipDuration,
            },
            timelineRange: {
              startSeconds: timelineCursor,
              durationSeconds: effectiveClipDuration,
            },
            speed: clip.speed,
            volumeDb: clip.volumeDb,
            pan: clip.pan,
            scale: clip.scale,
          };

          builder.addClip(track.id, adaptedClip);
          timelineCursor += effectiveClipDuration;
        }
      }
    }

    // Adapt markers within cutdown range
    for (const marker of masterIR.markers) {
      if (marker.timestampSeconds <= effectiveDurationLimit) {
        builder.addMarker(marker);
      }
    }

    const timestamp = params.deterministicTimestamp ?? masterIR.createdAt;
    const variantIR = builder.build(timestamp);

    // Calculate actual total duration
    let actualDurationSeconds = 0.0;
    for (const track of variantIR.tracks) {
      for (const clip of track.clips) {
        const end = clip.timelineRange.startSeconds + clip.timelineRange.durationSeconds;
        if (end > actualDurationSeconds) {
          actualDurationSeconds = end;
        }
      }
    }

    const planContent = JSON.stringify({
      variantId,
      masterProjectId: masterIR.projectId,
      cutdownTarget: target,
      aspectRatio,
      actualDurationSeconds,
      retainedClipIds,
      checksum: variantIR.checksum,
    });

    const planChecksum = crypto.createHash("sha256").update(planContent).digest("hex");

    const plan: EditorialVariantPlan = {
      variantId,
      masterProjectId: masterIR.projectId,
      cutdownTarget: target,
      aspectRatio,
      targetDurationSeconds: isFinite(maxDurationSeconds) ? maxDurationSeconds : actualDurationSeconds,
      actualDurationSeconds: Number(actualDurationSeconds.toFixed(3)),
      retainedClipIds,
      checksum: planChecksum,
    };

    return {
      variantIR,
      plan: EditorialVariantPlanSchema.parse(plan),
    };
  }
}
