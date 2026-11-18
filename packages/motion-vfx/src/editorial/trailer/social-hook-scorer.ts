import { SocialHookMetrics, SocialHookMetricsSchema } from "../contracts/trailer.types.js";

export interface HookEvaluationInput {
  windowDurationSeconds?: number;
  cutsCount: number;
  initialSilenceSeconds?: number;
  hasVisualPunchIn?: boolean;
  firstSpokenWordTimestamp?: number;
  speechText?: string;
  hasAudioRiserOrImpact?: boolean;
}

/**
 * REQ-029: Quantitative evaluator and predictor for the first 3 to 6 seconds of audience retention.
 */
export class SocialHookScorer {
  private static readonly INTRIGUE_TRIGGERS = [
    "por qué",
    "por que",
    "cómo",
    "como",
    "why",
    "how",
    "what",
    "secreto",
    "secret",
    "nadie",
    "nobody",
    "nunca",
    "never",
    "verdad",
    "truth",
    "revelación",
    "revelation",
    "oculto",
    "hidden",
    "misterio",
    "mystery",
    "peligro",
    "danger",
    "error",
    "mentira",
    "lie",
    "descubrí",
    "discovered",
    "impacto",
    "shock",
  ];

  /**
   * Evaluates the opening hook window and produces a 0-100 retention prediction score.
   */
  public static evaluateHook(input: HookEvaluationInput): SocialHookMetrics {
    const windowDuration = input.windowDurationSeconds ?? 5.0;
    const initialSilence = Math.max(0.0, input.initialSilenceSeconds ?? 0.0);
    const cuts = Math.max(0, input.cutsCount);
    const hasPunchIn = input.hasVisualPunchIn ?? false;
    const speech = (input.speechText ?? "").toLowerCase();
    const hasImpact = input.hasAudioRiserOrImpact ?? false;
    const firstWordTime = Math.max(0.0, input.firstSpokenWordTimestamp ?? initialSilence);

    const recommendations: string[] = [];

    // 1. Visual Pace Score (0 - 100)
    // Ideal: 2 to 4 visual variations (cuts / punch-ins) in 5 seconds
    let visualPaceScore = 30.0;
    if (cuts >= 2 || (cuts >= 1 && hasPunchIn)) {
      visualPaceScore = Math.min(100.0, 70.0 + cuts * 10.0 + (hasPunchIn ? 10.0 : 0.0));
    } else if (cuts === 1 || hasPunchIn) {
      visualPaceScore = 60.0;
      recommendations.push("Add a secondary cut or B-roll insert before second 2.5 to increase visual tempo.");
    } else {
      visualPaceScore = 25.0;
      recommendations.push("Opening is a static single shot; add at least one dynamic cut or punch-in within 3s.");
    }

    // 2. Verbal Intrigue Score (0 - 100)
    let verbalIntrigueScore = 40.0;
    const detectedTriggers: string[] = [];

    for (const trigger of this.INTRIGUE_TRIGGERS) {
      if (speech.includes(trigger)) {
        detectedTriggers.push(trigger);
      }
    }

    if (speech.includes("?") || speech.includes("¿")) {
      detectedTriggers.push("question_mark");
    }

    if (detectedTriggers.length >= 2) {
      verbalIntrigueScore = Math.min(100.0, 65.0 + detectedTriggers.length * 10.0);
    } else if (detectedTriggers.length === 1) {
      verbalIntrigueScore = 70.0;
    } else if (speech.trim().length > 0) {
      verbalIntrigueScore = 45.0;
      recommendations.push("Lead with a provocative question or high-stakes keyword in the opening phrase.");
    } else {
      verbalIntrigueScore = 20.0;
      recommendations.push("No spoken words detected in the hook window.");
    }

    // Delay penalty if speech starts late (> 0.5s)
    if (firstWordTime > 0.5) {
      verbalIntrigueScore = Math.max(10.0, verbalIntrigueScore - (firstWordTime - 0.5) * 40.0);
    }

    // 3. Acoustic Impact Score (0 - 100)
    let acousticImpactScore = 50.0;
    if (hasImpact) {
      acousticImpactScore += 35.0;
    } else {
      recommendations.push("Add a subtle audio riser or sub-bass impact on the opening transition.");
    }

    if (initialSilence <= 0.15) {
      acousticImpactScore += 15.0;
    } else {
      const penalty = Math.min(40.0, (initialSilence - 0.15) * 80.0);
      acousticImpactScore = Math.max(10.0, acousticImpactScore - penalty);
      recommendations.push(`Trim ${initialSilence.toFixed(2)}s of initial silence to avoid immediate drop-off.`);
    }

    // Bound sub-scores
    visualPaceScore = Number(Math.max(0.0, Math.min(100.0, visualPaceScore)).toFixed(2));
    verbalIntrigueScore = Number(Math.max(0.0, Math.min(100.0, verbalIntrigueScore)).toFixed(2));
    acousticImpactScore = Number(Math.max(0.0, Math.min(100.0, acousticImpactScore)).toFixed(2));

    // 4. Combined Retention Prediction Score
    const retentionPrediction =
      visualPaceScore * 0.40 +
      verbalIntrigueScore * 0.35 +
      acousticImpactScore * 0.25;

    const retentionPredictionScore = Number(
      Math.max(0.0, Math.min(100.0, retentionPrediction)).toFixed(2)
    );

    // Mock cut timestamps
    const cutTimestamps: number[] = [];
    if (cuts > 0) {
      const step = windowDuration / (cuts + 1);
      for (let i = 1; i <= cuts; i++) {
        cutTimestamps.push(Number((i * step).toFixed(2)));
      }
    }

    const metrics: SocialHookMetrics = {
      windowDurationSeconds: windowDuration,
      visualPaceScore,
      verbalIntrigueScore,
      acousticImpactScore,
      retentionPredictionScore,
      cutTimestamps,
      intrigueWordsDetected: detectedTriggers,
      recommendations,
    };

    return SocialHookMetricsSchema.parse(metrics);
  }
}
