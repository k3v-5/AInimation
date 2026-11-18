import crypto from "node:crypto";
import { NarrativeArcPlan, DocumentaryBeatType } from "../contracts/narrative.types.js";
import {
  TrailerCutSegment,
  TrailerFormat,
  TrailerPlan,
  TrailerPlanSchema,
  TrailerPurpose,
  MusicCueType,
} from "../contracts/trailer.types.js";
import { SocialHookScorer } from "./social-hook-scorer.js";

export interface CompileTrailerParams {
  projectId: string;
  narrativePlan: NarrativeArcPlan;
  format: TrailerFormat;
  callToActionText?: string;
  customDurationSeconds?: number;
  hookAudioVisualFeatures?: {
    cutsCount?: number;
    initialSilenceSeconds?: number;
    speechText?: string;
    hasAudioRiserOrImpact?: boolean;
    hasVisualPunchIn?: boolean;
  };
}

interface SegmentTemplate {
  beatType: DocumentaryBeatType;
  fallbackBeatType?: DocumentaryBeatType;
  purpose: TrailerPurpose;
  cue: MusicCueType;
  durationRatio: number;
}

/**
 * REQ-028: Generator of promotional teasers, promos, and cinematic trailers derived from the Narrative Arc Plan.
 */
export class TrailerGenerator {
  public static readonly FORMAT_DURATIONS: Record<TrailerFormat, number> = {
    "15s_teaser": 15.0,
    "30s_promo": 30.0,
    "60s_trailer": 60.0,
    "90s_epic": 90.0,
  };

  private static readonly TEASER_15S_TEMPLATES: SegmentTemplate[] = [
    { beatType: "HOOK", purpose: "HOOK_PUNCH", cue: "RISER", durationRatio: 0.25 },
    { beatType: "ESCALATION", fallbackBeatType: "CONFLICT", purpose: "INTRIGUE_BUILD", cue: "BED", durationRatio: 0.30 },
    { beatType: "REVELATION", purpose: "CLIMAX_DROP", cue: "DROP", durationRatio: 0.25 },
    { beatType: "RESOLUTION", fallbackBeatType: "HOOK", purpose: "TITLE_CALL_TO_ACTION", cue: "HIT", durationRatio: 0.20 },
  ];

  private static readonly PROMO_30S_TEMPLATES: SegmentTemplate[] = [
    { beatType: "HOOK", purpose: "HOOK_PUNCH", cue: "RISER", durationRatio: 0.20 },
    { beatType: "QUESTION", fallbackBeatType: "CONTEXT", purpose: "INTRIGUE_BUILD", cue: "BED", durationRatio: 0.20 },
    { beatType: "EVIDENCE", fallbackBeatType: "TESTIMONY", purpose: "EVIDENCE_FLASH", cue: "BED", durationRatio: 0.20 },
    { beatType: "ESCALATION", fallbackBeatType: "CONFLICT", purpose: "INTRIGUE_BUILD", cue: "SILENCE_BREAKER", durationRatio: 0.18 },
    { beatType: "REVELATION", purpose: "CLIMAX_DROP", cue: "DROP", durationRatio: 0.12 },
    { beatType: "RESOLUTION", fallbackBeatType: "HOOK", purpose: "TITLE_CALL_TO_ACTION", cue: "HIT", durationRatio: 0.10 },
  ];

  private static readonly TRAILER_60S_TEMPLATES: SegmentTemplate[] = [
    { beatType: "HOOK", purpose: "HOOK_PUNCH", cue: "RISER", durationRatio: 0.15 },
    { beatType: "CONTEXT", purpose: "INTRIGUE_BUILD", cue: "BED", durationRatio: 0.15 },
    { beatType: "QUESTION", purpose: "INTRIGUE_BUILD", cue: "BED", durationRatio: 0.15 },
    { beatType: "EVIDENCE", purpose: "EVIDENCE_FLASH", cue: "BED", durationRatio: 0.18 },
    { beatType: "CONFLICT", fallbackBeatType: "ESCALATION", purpose: "INTRIGUE_BUILD", cue: "SILENCE_BREAKER", durationRatio: 0.15 },
    { beatType: "REVELATION", purpose: "CLIMAX_DROP", cue: "DROP", durationRatio: 0.12 },
    { beatType: "RESOLUTION", fallbackBeatType: "REFLECTION", purpose: "TITLE_CALL_TO_ACTION", cue: "HIT", durationRatio: 0.10 },
  ];

  /**
   * Compiles an immutable, deterministic promotional trailer plan.
   */
  public static compileTrailer(params: CompileTrailerParams): TrailerPlan {
    const targetDuration = params.customDurationSeconds ?? this.FORMAT_DURATIONS[params.format];
    const ctaText = params.callToActionText ?? "COMING SOON // WATCH THE FULL DOCUMENTARY";

    const beatMap = new Map(params.narrativePlan.beats.map((b) => [b.beat, b]));

    let templates: SegmentTemplate[];
    if (params.format === "15s_teaser") {
      templates = this.TEASER_15S_TEMPLATES;
    } else if (params.format === "30s_promo") {
      templates = this.PROMO_30S_TEMPLATES;
    } else {
      templates = this.TRAILER_60S_TEMPLATES;
    }

    let currentTimeline = 0.0;
    const segments: TrailerCutSegment[] = [];

    for (let i = 0; i < templates.length; i++) {
      const tmpl = templates[i];
      let beat = beatMap.get(tmpl.beatType);
      if (!beat && tmpl.fallbackBeatType) {
        beat = beatMap.get(tmpl.fallbackBeatType);
      }
      if (!beat) {
        beat = params.narrativePlan.beats[i % params.narrativePlan.beats.length];
      }

      // Compute exact duration to ensure sum equals targetDuration
      let segDuration: number;
      if (i === templates.length - 1) {
        segDuration = Number((targetDuration - currentTimeline).toFixed(2));
      } else {
        segDuration = Number((targetDuration * tmpl.durationRatio).toFixed(2));
      }

      // Safeguard against rounding drift
      if (segDuration <= 0.0) {
        segDuration = 1.0;
      }

      const sourceStart = beat.timelineStartSeconds;
      const sourceEnd = Math.min(
        beat.timelineEndSeconds,
        sourceStart + segDuration
      );

      const segment: TrailerCutSegment = {
        id: `trailer_seg_${i + 1}_${tmpl.purpose.toLowerCase()}`,
        sourceBeatType: beat.beat,
        sceneId: beat.sceneId,
        sourceStartSeconds: sourceStart,
        sourceEndSeconds: sourceEnd,
        trailerStartSeconds: currentTimeline,
        trailerEndSeconds: currentTimeline + segDuration,
        durationSeconds: segDuration,
        purpose: tmpl.purpose,
        soundbiteText: `[SOUNDBITE] ${beat.title}`,
        musicCue: tmpl.cue,
      };

      segments.push(segment);
      currentTimeline = Number((currentTimeline + segDuration).toFixed(2));
    }

    const actualDuration = Number(currentTimeline.toFixed(2));

    // Evaluate social hook metrics on the first segment window
    const firstSeg = segments[0];
    const hookEval = SocialHookScorer.evaluateHook({
      windowDurationSeconds: Math.min(5.0, firstSeg?.durationSeconds ?? 5.0),
      cutsCount: params.hookAudioVisualFeatures?.cutsCount ?? 2,
      initialSilenceSeconds: params.hookAudioVisualFeatures?.initialSilenceSeconds ?? 0.05,
      hasVisualPunchIn: params.hookAudioVisualFeatures?.hasVisualPunchIn ?? true,
      hasAudioRiserOrImpact: params.hookAudioVisualFeatures?.hasAudioRiserOrImpact ?? true,
      speechText: params.hookAudioVisualFeatures?.speechText ?? firstSeg?.soundbiteText ?? "Why did nobody notice?",
    });

    const hashPayload = JSON.stringify({
      projectId: params.projectId,
      format: params.format,
      targetDuration,
      actualDuration,
      segments: segments.map((s) => ({
        id: s.id,
        beat: s.sourceBeatType,
        purpose: s.purpose,
        start: s.trailerStartSeconds,
        duration: s.durationSeconds,
      })),
      hookScore: hookEval.retentionPredictionScore,
    });

    const checksumSha256 = crypto.createHash("sha256").update(hashPayload).digest("hex");

    const plan: TrailerPlan = {
      id: `trailer_${params.format}_${params.projectId}`,
      projectId: params.projectId,
      format: params.format,
      targetDurationSeconds: targetDuration,
      actualDurationSeconds: actualDuration,
      segments,
      socialHookMetrics: hookEval,
      callToActionText: ctaText,
      checksumSha256,
    };

    return TrailerPlanSchema.parse(plan);
  }
}
