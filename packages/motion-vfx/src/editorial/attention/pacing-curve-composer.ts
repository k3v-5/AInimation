import {
  PacingAlignmentReport,
  PacingAlignmentReportSchema,
  PacingDiscrepancy,
  PacingProfile,
  PacingProfileSchema,
} from "../contracts/attention.types.js";
import { MathUtils } from "./math-utils.js";

export interface TargetPacingSegment {
  startSeconds: number;
  endSeconds: number;
  targetPacing: number; // [0.0, 1.0]
}

export interface PacingEvaluationInput {
  totalDurationSeconds: number;
  cutTimestampsSeconds: number[];
  targetCurve: TargetPacingSegment[];
  profile?: Partial<PacingProfile>;
}

/**
 * REQ-049: Pacing Curve Composer.
 * Computes mean L1 distance between actual sliding-window cut density and profile target pacing.
 */
export class PacingCurveComposer {
  public static readonly DEFAULT_PROFILE: PacingProfile = {
    windowSeconds: 6.0,
    maxCutsPerWindow: 5.0,
  };

  public static evaluate(input: PacingEvaluationInput): PacingAlignmentReport {
    const profile = PacingProfileSchema.parse({
      ...this.DEFAULT_PROFILE,
      ...input.profile,
    });

    const totalDuration = MathUtils.clamp(input.totalDurationSeconds, 1.0, 86400.0);
    const cuts = input.cutTimestampsSeconds.filter((t) => t >= 0 && t <= totalDuration);
    const halfWindow = profile.windowSeconds / 2.0;

    const sampleStep = 1.0;
    const totalSamples = Math.floor(totalDuration / sampleStep) + 1;

    let totalL1Distance = 0.0;
    const discrepancies: PacingDiscrepancy[] = [];

    for (let i = 0; i < totalSamples; i++) {
      const t = Number((i * sampleStep).toFixed(2));

      // 1. Calculate P_actual(t) from sliding window
      const winStart = t - halfWindow;
      const winEnd = t + halfWindow;
      const cutsInWindow = cuts.filter((c) => c >= winStart && c <= winEnd).length;
      const pActual = MathUtils.clamp(cutsInWindow / profile.maxCutsPerWindow, 0.0, 1.0);

      // 2. Resolve P_target(t) from target curve segments
      let pTarget = 0.50; // default moderate pace
      for (const seg of input.targetCurve) {
        if (t >= seg.startSeconds && t <= seg.endSeconds) {
          pTarget = MathUtils.clamp(seg.targetPacing, 0.0, 1.0);
          break;
        }
      }

      // 3. Compute L1 distance at timestamp t
      const diff = Math.abs(pActual - pTarget);
      totalL1Distance += diff;

      // 4. Record significant discrepancy (> 0.35)
      if (diff > 0.35) {
        const delta = Number((pActual - pTarget).toFixed(4));
        const rec =
          pActual < pTarget
            ? `Pacing is too slow at t=${t}s (actual: ${pActual.toFixed(2)}, target: ${pTarget.toFixed(2)}); insert B-Roll or shorten shot duration.`
            : `Pacing is too frantic at t=${t}s (actual: ${pActual.toFixed(2)}, target: ${pTarget.toFixed(2)}); extend shot durations to let narrative breathe.`;

        discrepancies.push({
          timestampSeconds: t,
          delta,
          recommendation: rec,
        });
      }
    }

    const meanL1Distance = MathUtils.clamp(
      Number((totalL1Distance / totalSamples).toFixed(4)),
      0.0,
      1.0
    );

    const alignmentScore = MathUtils.clamp(
      Number((100.0 * (1.0 - meanL1Distance)).toFixed(2)),
      0.0,
      100.0
    );

    const draftReport = {
      alignmentScore,
      meanL1Distance,
      discrepancies,
    };

    const checksumSha256 = MathUtils.computeCanonicalSha256(draftReport);

    const report: PacingAlignmentReport = {
      ...draftReport,
      checksumSha256,
    };

    return PacingAlignmentReportSchema.parse(report);
  }
}
