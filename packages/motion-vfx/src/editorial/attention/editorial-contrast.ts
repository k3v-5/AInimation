import {
  EditorialContrastReport,
  EditorialContrastReportSchema,
  TensionLevel,
  TensionRun,
} from "../contracts/attention.types.js";
import { MathUtils } from "./math-utils.js";

export interface BeatTensionInput {
  beatIndex: number;
  name?: string;
  tension: TensionLevel;
  durationSeconds: number;
}

export interface ContrastEvaluationInput {
  beats: BeatTensionInput[];
}

/**
 * REQ-048: Dramatic Tension and Editorial Contrast Engine.
 * Evaluates narrative tension grammar with single-penalty monotony runs and decomposable scoring.
 */
export class EditorialContrast {
  public static evaluate(input: ContrastEvaluationInput): EditorialContrastReport {
    const beats = [...input.beats].sort((a, b) => a.beatIndex - b.beatIndex);

    let monotonyPenalty = 0.0;
    let stagnationPenalty = 0.0;
    let missingReleasePenalty = 0.0;
    let erraticPenalty = 0.0;

    const monotonyRuns: TensionRun[] = [];
    const violations: string[] = [];

    // 1. Detect contiguous runs of HIGH or PEAK (single penalty per run)
    let currentHighRunStart: number | null = null;
    let currentHighRunDuration = 0.0;
    let currentHighRunLevel: "HIGH" | "PEAK" = "HIGH";

    for (let i = 0; i < beats.length; i++) {
      const b = beats[i];
      const isHighOrPeak = b.tension === "HIGH" || b.tension === "PEAK";

      if (isHighOrPeak) {
        if (currentHighRunStart === null) {
          currentHighRunStart = i;
          currentHighRunDuration = b.durationSeconds;
          currentHighRunLevel = b.tension === "PEAK" ? "PEAK" : "HIGH";
        } else {
          currentHighRunDuration += b.durationSeconds;
          if (b.tension === "PEAK") {
            currentHighRunLevel = "PEAK";
          }
        }
      } else {
        if (currentHighRunStart !== null) {
          const runLength = i - currentHighRunStart;
          const isMonotony = (runLength >= 3 && currentHighRunDuration >= 20.0) || currentHighRunDuration >= 35.0;
          if (isMonotony) {
            monotonyRuns.push({
              level: currentHighRunLevel,
              startBeatIndex: currentHighRunStart,
              endBeatIndex: i - 1,
              durationSeconds: Number(currentHighRunDuration.toFixed(2)),
            });
            monotonyPenalty += 15.0;
            violations.push(
              `MONOTONOUS_HIGH_TENSION: Contiguous high/peak run of ${runLength} beats (${currentHighRunDuration.toFixed(1)}s) from beat ${currentHighRunStart} to ${i - 1} without release.`
            );
          }
          currentHighRunStart = null;
          currentHighRunDuration = 0.0;
        }
      }
    }

    // Check high run extending to end
    if (currentHighRunStart !== null) {
      const runLength = beats.length - currentHighRunStart;
      const isMonotony = (runLength >= 3 && currentHighRunDuration >= 20.0) || currentHighRunDuration >= 35.0;
      if (isMonotony) {
        monotonyRuns.push({
          level: currentHighRunLevel,
          startBeatIndex: currentHighRunStart,
          endBeatIndex: beats.length - 1,
          durationSeconds: Number(currentHighRunDuration.toFixed(2)),
        });
        monotonyPenalty += 15.0;
        violations.push(
          `MONOTONOUS_HIGH_TENSION: Contiguous high/peak run of ${runLength} beats (${currentHighRunDuration.toFixed(1)}s) ending timeline without release.`
        );
      }
    }

    // 2. Detect stagnation in LOW (> 35s)
    let currentLowStart = 0;
    let currentLowDuration = 0.0;
    for (let i = 0; i < beats.length; i++) {
      const b = beats[i];
      if (b.tension === "LOW") {
        currentLowDuration += b.durationSeconds;
        if (currentLowDuration > 35.0 && currentLowStart === 0) {
          stagnationPenalty += 12.0;
          violations.push(
            `BOREDOM_STAGNATION: Low tension sustained for ${currentLowDuration.toFixed(1)}s (> 35s) near beat ${i}.`
          );
          currentLowStart = 1; // Flag recorded
        }
      } else {
        currentLowDuration = 0.0;
        currentLowStart = 0;
      }
    }

    // 3. Detect missing release after PEAK & erratic transitions
    for (let i = 0; i < beats.length; i++) {
      const b = beats[i];
      const next = beats[i + 1];

      if (b.tension === "PEAK" && next) {
        if (next.tension !== "RELEASE" && next.tension !== "MEDIUM") {
          missingReleasePenalty += 10.0;
          violations.push(
            `MISSING_RELEASE: Peak tension at beat ${i} was followed by '${next.tension}' instead of RELEASE or MEDIUM.`
          );
        }
      }

      if (b.tension === "LOW" && next && next.tension === "PEAK" && next.durationSeconds < 4.0) {
        erraticPenalty += 8.0;
        violations.push(
          `ERRATIC_TENSION: Abrupt jump from LOW directly to PEAK at beat ${i + 1} without ramp.`
        );
      }
    }

    const totalPenalties = monotonyPenalty + stagnationPenalty + missingReleasePenalty + erraticPenalty;
    const contrastScore = MathUtils.clamp(Number((100.0 - totalPenalties).toFixed(2)), 0.0, 100.0);

    const draftReport = {
      contrastScore,
      penalties: {
        monotonyPenalty: Number(monotonyPenalty.toFixed(2)),
        stagnationPenalty: Number(stagnationPenalty.toFixed(2)),
        missingReleasePenalty: Number(missingReleasePenalty.toFixed(2)),
        erraticPenalty: Number(erraticPenalty.toFixed(2)),
      },
      monotonyRuns,
      violations,
      isValidContrast: contrastScore >= 70.0 && violations.length === 0,
    };

    const checksumSha256 = MathUtils.computeCanonicalSha256(draftReport);

    const report: EditorialContrastReport = {
      ...draftReport,
      checksumSha256,
    };

    return EditorialContrastReportSchema.parse(report);
  }
}
