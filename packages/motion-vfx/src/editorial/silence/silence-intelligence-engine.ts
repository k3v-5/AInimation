import crypto from "crypto";
import { EditorialProfile } from "../contracts/content-profile.types.js";
import {
  ClassifiedSilence,
  ClassifiedSilenceSchema,
  SilenceDecisionAction,
  SilenceType,
} from "../contracts/silence-intelligence.types.js";

export interface RawSilenceInterval {
  startSeconds: number;
  endSeconds: number;
  precedingWord?: string;
  followingWord?: string;
  rmsLevelDb?: number;
  hasInhaleAcousticProfile?: boolean;
  isAfterSentenceTerminal?: boolean; // Follows '.', '?', '!'
  isAfterComma?: boolean;            // Follows ','
  isEmotionalPeakProximity?: boolean;
}

/**
 * REQ-006 & REQ-068: Silence Intelligence Engine.
 * Evaluates silences semantically, categorizing dead pauses vs dramatic pauses,
 * and applying profile-specific editorial pruning rules.
 */
export class SilenceIntelligenceEngine {
  /**
   * Classifies a collection of raw audio pauses and derives editorial decisions.
   */
  public static classifySilences(
    rawIntervals: RawSilenceInterval[],
    profile: EditorialProfile,
    sourceAudioTrackId?: string
  ): ClassifiedSilence[] {
    return rawIntervals.map((interval, index) => {
      const durationSeconds = Math.max(0, interval.endSeconds - interval.startSeconds);
      const classification = this.inferSilenceType(interval, durationSeconds);
      const decision = this.determineDecision(classification.type, durationSeconds, profile);

      const id = `silence_${index}_${crypto
        .createHash("sha256")
        .update(`${interval.startSeconds}_${interval.endSeconds}_${classification.type}`)
        .digest("hex")
        .substring(0, 12)}`;

      const result: ClassifiedSilence = {
        id,
        startSeconds: interval.startSeconds,
        endSeconds: interval.endSeconds,
        durationSeconds,
        type: classification.type,
        confidence: classification.confidence,
        decision: decision.action,
        targetDurationSeconds: decision.targetDurationSeconds,
        reasoning: decision.reasoning,
        sourceAudioTrackId,
      };

      return ClassifiedSilenceSchema.parse(result);
    });
  }

  /**
   * Infers the semantic nature of a silence pause.
   */
  private static inferSilenceType(
    interval: RawSilenceInterval,
    durationSeconds: number
  ): { type: SilenceType; confidence: number } {
    // 1. Respiratory Inhale detection
    if (interval.hasInhaleAcousticProfile || (durationSeconds >= 0.15 && durationSeconds <= 0.45 && interval.rmsLevelDb && interval.rmsLevelDb > -42)) {
      return { type: "BREATH", confidence: 0.88 };
    }

    // 2. High emotional proximity or post-question hesitation -> Dramatic Pause
    if (interval.isEmotionalPeakProximity && durationSeconds >= 0.6) {
      return { type: "DRAMATIC_PAUSE", confidence: 0.94 };
    }

    // 3. Sentence terminal pause
    if (interval.isAfterSentenceTerminal) {
      if (durationSeconds > 1.2) {
        return { type: "DRAMATIC_PAUSE", confidence: 0.85 };
      }
      return { type: "NATURAL_PAUSE", confidence: 0.92 };
    }

    // 4. Comma / clause pause
    if (interval.isAfterComma && durationSeconds <= 0.8) {
      return { type: "NATURAL_PAUSE", confidence: 0.90 };
    }

    // 5. Mid-sentence thinking pause (between words, 0.6s to 1.5s)
    if (
      durationSeconds >= 0.60 &&
      durationSeconds <= 1.50 &&
      interval.precedingWord &&
      interval.followingWord &&
      !interval.isAfterSentenceTerminal &&
      !interval.isAfterComma
    ) {
      return { type: "THINKING_PAUSE", confidence: 0.82 };
    }

    // 6. Default short or dead air pause -> Filler Silence
    return { type: "FILLER_SILENCE", confidence: 0.89 };
  }

  /**
   * Derives the editorial action for a silence based on profile rules.
   */
  private static determineDecision(
    type: SilenceType,
    durationSeconds: number,
    profile: EditorialProfile
  ): { action: SilenceDecisionAction; targetDurationSeconds: number; reasoning: string } {
    const { maxFillerSilenceSeconds, preserveDramaticPauses, preserveBreaths, roomToneReplacement } =
      profile.silencePolicy;

    switch (type) {
      case "DRAMATIC_PAUSE":
        if (preserveDramaticPauses) {
          return {
            action: roomToneReplacement ? "REPLACE_WITH_ROOM_TONE" : "KEEP",
            targetDurationSeconds: durationSeconds,
            reasoning: `Preserving ${durationSeconds.toFixed(2)}s dramatic pause to maintain narrative tension per ${profile.name}.`,
          };
        }
        return {
          action: "TRIM",
          targetDurationSeconds: Math.min(durationSeconds, maxFillerSilenceSeconds),
          reasoning: `Trimming dramatic pause to ${maxFillerSilenceSeconds}s as genre ${profile.genre} mandates rapid pacing.`,
        };

      case "THINKING_PAUSE":
        if (preserveDramaticPauses) {
          return {
            action: roomToneReplacement ? "REPLACE_WITH_ROOM_TONE" : "KEEP",
            targetDurationSeconds: durationSeconds,
            reasoning: `Preserving contemplative pause (${durationSeconds.toFixed(2)}s) for interviewee authenticity.`,
          };
        }
        return {
          action: "TRIM",
          targetDurationSeconds: Math.min(durationSeconds, maxFillerSilenceSeconds),
          reasoning: `Shortening thinking pause to ${maxFillerSilenceSeconds}s for rhythm retention.`,
        };

      case "BREATH":
        if (preserveBreaths) {
          return {
            action: "KEEP",
            targetDurationSeconds: durationSeconds,
            reasoning: `Preserving natural respiratory breath to avoid synthetic dialogue feel.`,
          };
        }
        return {
          action: "ATTENUATE",
          targetDurationSeconds: durationSeconds,
          reasoning: `Attenuating breath intake volume to keep dialogue clean.`,
        };

      case "NATURAL_PAUSE":
        if (durationSeconds > maxFillerSilenceSeconds * 1.5) {
          return {
            action: "TRIM",
            targetDurationSeconds: maxFillerSilenceSeconds,
            reasoning: `Capping natural pause at ${maxFillerSilenceSeconds}s.`,
          };
        }
        return {
          action: "KEEP",
          targetDurationSeconds: durationSeconds,
          reasoning: `Preserving normal syntactical punctuation pause.`,
        };

      case "FILLER_SILENCE":
      default:
        if (durationSeconds > maxFillerSilenceSeconds) {
          return {
            action: "TRIM",
            targetDurationSeconds: Math.min(durationSeconds, maxFillerSilenceSeconds * 0.5),
            reasoning: `Pruning dead air silence (${durationSeconds.toFixed(2)}s -> ${(maxFillerSilenceSeconds * 0.5).toFixed(2)}s).`,
          };
        }
        return {
          action: "KEEP",
          targetDurationSeconds: durationSeconds,
          reasoning: `Silence within permissible filler threshold (${durationSeconds.toFixed(2)}s <= ${maxFillerSilenceSeconds}s).`,
        };
    }
  }
}
