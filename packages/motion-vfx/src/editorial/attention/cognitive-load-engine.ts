import {
  CognitiveLoadReport,
  CognitiveLoadReportSchema,
  CognitiveMitigationProposal,
  CognitiveOverloadAlert,
} from "../contracts/attention.types.js";
import { MathUtils } from "./math-utils.js";

export interface InstantaneousCognitiveState {
  timestampSeconds: number;
  speechWordsPerMinute?: number;
  speechActive?: boolean;
  onScreenDataElementsCount?: number;
  subtitlesCharsPerSecond?: number;
  audioEnergyDbfs?: number; // dBFS: -60 to 0
  cameraMotionIntensity?: number; // [0, 1]
  cutsInRecent3Seconds?: number;
}

export interface CognitiveEvaluationInput {
  totalDurationSeconds: number;
  states: InstantaneousCognitiveState[];
}

/**
 * REQ-047: Cognitive Load Engine.
 * Deterministic multimodal cognitive saturation calculator with proposal-first mitigations.
 */
export class CognitiveLoadEngine {
  public static readonly WEIGHT_VOICE = 0.30;
  public static readonly WEIGHT_DATA = 0.25;
  public static readonly WEIGHT_SUBTITLES = 0.20;
  public static readonly WEIGHT_MUSIC = 0.15;
  public static readonly WEIGHT_KINETIC = 0.10;

  public static readonly CRITICAL_OVERLOAD_THRESHOLD = 0.85;
  public static readonly CRITICAL_OVERLOAD_MIN_DURATION = 3.0;

  /**
   * Normalizes vocal speech into [0, 1].
   */
  public static normalizeVoice(wpm?: number, active?: boolean): number {
    if (!active || wpm === undefined || wpm <= 0) {
      return 0.0;
    }
    return MathUtils.clamp(Number(((wpm - 100.0) / (220.0 - 100.0)).toFixed(4)), 0.0, 1.0);
  }

  /**
   * Normalizes on-screen data/graphics into [0, 1].
   */
  public static normalizeDataGraphics(elementCount?: number): number {
    if (!elementCount || elementCount <= 0) {
      return 0.0;
    }
    return MathUtils.clamp(Number((elementCount / 3.0).toFixed(4)), 0.0, 1.0);
  }

  /**
   * Normalizes subtitle reading rate into [0, 1].
   */
  public static normalizeSubtitles(charsPerSecond?: number): number {
    if (!charsPerSecond || charsPerSecond <= 0) {
      return 0.0;
    }
    return MathUtils.clamp(Number((charsPerSecond / 25.0).toFixed(4)), 0.0, 1.0);
  }

  /**
   * Normalizes audio energy in dBFS into [0, 1].
   */
  public static normalizeAudio(energyDbfs?: number): number {
    if (energyDbfs === undefined) {
      return 0.0;
    }
    return MathUtils.clamp(
      Number(((energyDbfs - -30.0) / (-6.0 - -30.0)).toFixed(4)),
      0.0,
      1.0
    );
  }

  /**
   * Normalizes visual kinetic motion into [0, 1].
   */
  public static normalizeKinetic(cutsIn3s?: number, cameraMotion?: number): number {
    const cutsTerm = (cutsIn3s ?? 0) / 4.0;
    const motionTerm = 0.30 * (cameraMotion ?? 0.0);
    return MathUtils.clamp(Number((cutsTerm + motionTerm).toFixed(4)), 0.0, 1.0);
  }

  /**
   * Evaluates instantaneous cognitive load across the editorial timeline.
   */
  public static evaluate(input: CognitiveEvaluationInput): CognitiveLoadReport {
    const totalDuration = MathUtils.clamp(input.totalDurationSeconds, 1.0, 86400.0);
    const sortedStates = [...input.states].sort((a, b) => a.timestampSeconds - b.timestampSeconds);

    let sumLoad = 0.0;
    let peakLoad = 0.0;

    const overloadAlerts: CognitiveOverloadAlert[] = [];
    const recommendedMitigations: CognitiveMitigationProposal[] = [];

    let currentOverloadStart: number | null = null;
    let maxOverloadInRun = 0.0;
    let dominantCauseInRun = "MULTIMODAL_CONCURRENCY";

    for (let i = 0; i < sortedStates.length; i++) {
      const state = sortedStates[i];
      if (state.timestampSeconds < 0 || state.timestampSeconds > totalDuration) {
        continue;
      }

      const v = this.normalizeVoice(state.speechWordsPerMinute, state.speechActive);
      const d = this.normalizeDataGraphics(state.onScreenDataElementsCount);
      const s = this.normalizeSubtitles(state.subtitlesCharsPerSecond);
      const m = this.normalizeAudio(state.audioEnergyDbfs);
      const k = this.normalizeKinetic(state.cutsInRecent3Seconds, state.cameraMotionIntensity);

      const instantaneousLoad = Number(
        (
          this.WEIGHT_VOICE * v +
          this.WEIGHT_DATA * d +
          this.WEIGHT_SUBTITLES * s +
          this.WEIGHT_MUSIC * m +
          this.WEIGHT_KINETIC * k
        ).toFixed(4)
      );

      sumLoad += instantaneousLoad;
      if (instantaneousLoad > peakLoad) {
        peakLoad = instantaneousLoad;
      }

      // Check for overload state
      if (instantaneousLoad >= this.CRITICAL_OVERLOAD_THRESHOLD) {
        if (currentOverloadStart === null) {
          currentOverloadStart = state.timestampSeconds;
          maxOverloadInRun = instantaneousLoad;
        } else {
          if (instantaneousLoad > maxOverloadInRun) {
            maxOverloadInRun = instantaneousLoad;
          }
        }

        // Determine dominant contributor
        const contributors = [
          { name: "SPEECH_VELOCITY", val: this.WEIGHT_VOICE * v },
          { name: "DATA_GRAPHICS_OVERLOAD", val: this.WEIGHT_DATA * d },
          { name: "SUBTITLE_READING_SATURATION", val: this.WEIGHT_SUBTITLES * s },
          { name: "AUDIO_DENSITY", val: this.WEIGHT_MUSIC * m },
          { name: "VISUAL_KINETIC_FRENZY", val: this.WEIGHT_KINETIC * k },
        ].sort((a, b) => b.val - a.val);

        dominantCauseInRun = contributors[0].name;
      } else {
        if (currentOverloadStart !== null) {
          const overloadDuration = state.timestampSeconds - currentOverloadStart;
          if (overloadDuration >= this.CRITICAL_OVERLOAD_MIN_DURATION) {
            this.recordOverload(
              currentOverloadStart,
              overloadDuration,
              maxOverloadInRun,
              dominantCauseInRun,
              overloadAlerts,
              recommendedMitigations
            );
          }
          currentOverloadStart = null;
          maxOverloadInRun = 0.0;
        }
      }
    }

    // Check overload extending to end of timeline
    if (currentOverloadStart !== null && sortedStates.length > 0) {
      const lastTime = sortedStates[sortedStates.length - 1].timestampSeconds;
      const overloadDuration = lastTime - currentOverloadStart;
      if (overloadDuration >= this.CRITICAL_OVERLOAD_MIN_DURATION) {
        this.recordOverload(
          currentOverloadStart,
          overloadDuration,
          maxOverloadInRun,
          dominantCauseInRun,
          overloadAlerts,
          recommendedMitigations
        );
      }
    }

    const stateCount = Math.max(1, sortedStates.length);
    const averageLoad = Number((sumLoad / stateCount).toFixed(4));
    peakLoad = Number(peakLoad.toFixed(4));

    const draftReport = {
      averageLoad,
      peakLoad,
      detectedOverloadsCount: overloadAlerts.length,
      overloadAlerts,
      recommendedMitigations,
    };

    const checksumSha256 = MathUtils.computeCanonicalSha256(draftReport);

    const report: CognitiveLoadReport = {
      ...draftReport,
      checksumSha256,
    };

    return CognitiveLoadReportSchema.parse(report);
  }

  private static recordOverload(
    startTime: number,
    duration: number,
    maxLoad: number,
    dominantCause: string,
    alerts: CognitiveOverloadAlert[],
    mitigations: CognitiveMitigationProposal[]
  ): void {
    alerts.push({
      timestampSeconds: Number(startTime.toFixed(2)),
      durationSeconds: Number(duration.toFixed(2)),
      loadIndex: Number(maxLoad.toFixed(4)),
      primaryCause: dominantCause,
    });

    if (dominantCause === "DATA_GRAPHICS_OVERLOAD") {
      mitigations.push({
        id: `mitig_shift_data_${alerts.length}`,
        timestampSeconds: Number(startTime.toFixed(2)),
        type: "SHIFT_GRAPHIC",
        offsetSeconds: 1.5,
        reason: "Delay on-screen graphic/citation display until speech pause to prevent cognitive overload.",
        confidence: 0.95,
      });
    } else if (dominantCause === "AUDIO_DENSITY") {
      mitigations.push({
        id: `mitig_duck_audio_${alerts.length}`,
        timestampSeconds: Number(startTime.toFixed(2)),
        type: "DUCK_AUDIO",
        gainDeltaDb: -4.0,
        reason: "Apply additional -4dB ducking on background music/SFX during dense speech delivery.",
        confidence: 0.90,
      });
    } else {
      mitigations.push({
        id: `mitig_split_dense_${alerts.length}`,
        timestampSeconds: Number(startTime.toFixed(2)),
        type: "SPLIT_DENSE_SEGMENT",
        reason: "Add a 1.0s breath or cutaway to space multimodal information delivery.",
        confidence: 0.85,
      });
    }
  }
}
