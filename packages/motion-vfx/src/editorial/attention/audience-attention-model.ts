import {
  AttentionDipAlert,
  AttentionPoint,
  AttentionProfile,
  AttentionProfileSchema,
  AudienceAttentionReport,
  AudienceAttentionReportSchema,
} from "../contracts/attention.types.js";
import { MathUtils } from "./math-utils.js";

export interface TimelineStimulusEvent {
  timestampSeconds: number;
  visualCut?: boolean;
  audioHitOrRiser?: boolean;
  narrativeBeatTransition?: boolean;
  dataOrEvidenceReveal?: boolean;
  customStimulusBoost?: number;
}

export interface AttentionSimulationInput {
  totalDurationSeconds: number;
  events: TimelineStimulusEvent[];
  profile?: Partial<AttentionProfile>;
}

/**
 * REQ-046: Audience Attention Model.
 * Deterministic parametric simulation of audience attention dynamics with explicit baseline decay
 * and order-independent stimulus composition.
 */
export class AudienceAttentionModel {
  public static readonly DEFAULT_PROFILE: AttentionProfile = {
    initialAttention: 0.85,
    baselineAttention: 0.40,
    decayLambda: 0.035,
    simulationStepSeconds: 0.1,
    reportingStepSeconds: 1.0,
  };

  public static simulate(input: AttentionSimulationInput): AudienceAttentionReport {
    const profile = AttentionProfileSchema.parse({
      ...this.DEFAULT_PROFILE,
      ...input.profile,
    });

    const totalDuration = MathUtils.clamp(input.totalDurationSeconds, 1.0, 86400.0);
    const simStep = profile.simulationStepSeconds;
    const reportStep = profile.reportingStepSeconds;

    // Index events by step bucket
    const eventsByStep = new Map<number, TimelineStimulusEvent[]>();
    for (const ev of input.events) {
      if (ev.timestampSeconds >= 0 && ev.timestampSeconds <= totalDuration) {
        const stepIdx = Math.floor(ev.timestampSeconds / simStep);
        const list = eventsByStep.get(stepIdx) ?? [];
        list.push(ev);
        eventsByStep.set(stepIdx, list);
      }
    }

    let currentAttention = profile.initialAttention;
    const attentionPoints: AttentionPoint[] = [];
    let nextReportingTime = 0.0;

    const totalSteps = Math.ceil(totalDuration / simStep);

    for (let s = 0; s <= totalSteps; s++) {
      const currentTime = Number((s * simStep).toFixed(2));

      // 1. Apply decay step
      if (s > 0) {
        currentAttention = MathUtils.exponentialDecay(
          currentAttention,
          profile.baselineAttention,
          profile.decayLambda,
          simStep
        );
      }

      // 2. Check for events in current simulation step
      const stepEvents = eventsByStep.get(s);
      if (stepEvents && stepEvents.length > 0) {
        const stimuli: number[] = [];
        for (const ev of stepEvents) {
          if (ev.visualCut) stimuli.push(0.15);
          if (ev.audioHitOrRiser) stimuli.push(0.10);
          if (ev.narrativeBeatTransition) stimuli.push(0.22);
          if (ev.dataOrEvidenceReveal) stimuli.push(0.12);
          if (ev.customStimulusBoost !== undefined) {
            stimuli.push(MathUtils.clamp(ev.customStimulusBoost, 0.0, 0.99));
          }
        }

        if (stimuli.length > 0) {
          currentAttention = MathUtils.composeStimuli(currentAttention, stimuli);
        }
      }

      // 3. Record reporting sample
      if (currentTime >= nextReportingTime - 1e-4 || s === totalSteps) {
        attentionPoints.push({
          timestampSeconds: currentTime,
          attentionScore: Number(currentAttention.toFixed(4)),
        });
        nextReportingTime += reportStep;
      }
    }

    // 4. Compute metrics and detect attention dips
    let sumAttention = 0.0;
    let minAttention = 1.0;
    const dipAlerts: AttentionDipAlert[] = [];
    let dipStartTime: number | null = null;
    let dipMinScore = 1.0;

    for (let i = 0; i < attentionPoints.length; i++) {
      const pt = attentionPoints[i];
      sumAttention += pt.attentionScore;
      if (pt.attentionScore < minAttention) {
        minAttention = pt.attentionScore;
      }

      if (pt.attentionScore < 0.40) {
        if (dipStartTime === null) {
          dipStartTime = pt.timestampSeconds;
          dipMinScore = pt.attentionScore;
        } else {
          if (pt.attentionScore < dipMinScore) {
            dipMinScore = pt.attentionScore;
          }
        }
      } else {
        if (dipStartTime !== null) {
          const dipDuration = pt.timestampSeconds - dipStartTime;
          if (dipDuration >= 4.0) {
            dipAlerts.push({
              startTimeSeconds: dipStartTime,
              endTimeSeconds: pt.timestampSeconds,
              minScore: Number(dipMinScore.toFixed(4)),
              recommendedFix: `Attention dropped to ${dipMinScore.toFixed(2)} for ${dipDuration.toFixed(1)}s; insert visual cut, B-Roll, or audio riser near ${dipStartTime.toFixed(1)}s.`,
            });
          }
          dipStartTime = null;
          dipMinScore = 1.0;
        }
      }
    }

    // Check dip extending to the end
    if (dipStartTime !== null) {
      const lastPt = attentionPoints[attentionPoints.length - 1];
      const dipDuration = lastPt.timestampSeconds - dipStartTime;
      if (dipDuration >= 4.0) {
        dipAlerts.push({
          startTimeSeconds: dipStartTime,
          endTimeSeconds: lastPt.timestampSeconds,
          minScore: Number(dipMinScore.toFixed(4)),
          recommendedFix: `Attention dropped to ${dipMinScore.toFixed(2)} for ${dipDuration.toFixed(1)}s; insert visual cut, B-Roll, or audio riser near ${dipStartTime.toFixed(1)}s.`,
        });
      }
    }

    const averageAttention = Number((sumAttention / Math.max(1, attentionPoints.length)).toFixed(4));
    minAttention = Number(minAttention.toFixed(4));

    const draftReport = {
      averageAttention,
      minAttention,
      dipAlerts,
      attentionPoints,
    };

    const checksumSha256 = MathUtils.computeCanonicalSha256(draftReport);

    const report: AudienceAttentionReport = {
      ...draftReport,
      checksumSha256,
    };

    return AudienceAttentionReportSchema.parse(report);
  }
}
