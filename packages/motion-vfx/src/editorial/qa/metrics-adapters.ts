import { EditorialIR } from "../ir/editorial-ir.types.js";
import { AudienceAttentionModel } from "../attention/audience-attention-model.js";
import { CognitiveLoadEngine } from "../attention/cognitive-load-engine.js";
import { EditorialContrast } from "../attention/editorial-contrast.js";
import { PacingCurveComposer } from "../attention/pacing-curve-composer.js";
import {
  AudienceAttentionReport,
  CognitiveLoadReport,
  EditorialContrastReport,
  PacingAlignmentReport,
} from "../contracts/attention.types.js";

export interface AttentionSummary {
  averageAttention: number;
  minAttention: number;
  report: AudienceAttentionReport;
}

export interface CognitiveLoadSummary {
  peakLoad: number;
  averageLoad: number;
  overloadsCount: number;
  report: CognitiveLoadReport;
}

export interface ContrastSummary {
  contrastScore: number;
  isValidContrast: boolean;
  report: EditorialContrastReport;
}

export interface PacingSummary {
  alignmentScore: number;
  meanL1Distance: number;
  report: PacingAlignmentReport;
}

/**
 * REQ-4I-042: 4H Metrics Adapters.
 * Decoupled interface bridge calculating Attention, Cognitive Load, Contrast, and Pacing summaries from Editorial IR.
 */
export class MetricsAdapters {
  public static getIRDuration(ir: EditorialIR): number {
    let maxEnd = 0.0;
    for (const track of ir.tracks) {
      for (const clip of track.clips) {
        const end = clip.timelineRange.startSeconds + clip.timelineRange.durationSeconds;
        if (end > maxEnd) maxEnd = end;
      }
    }
    return Math.max(1.0, Number(maxEnd.toFixed(3)));
  }

  public static evaluateAttention(ir: EditorialIR): AttentionSummary {
    const totalDuration = this.getIRDuration(ir);
    const cuts: number[] = [];

    for (const track of ir.tracks) {
      if (track.type.startsWith("VIDEO")) {
        for (const clip of track.clips) {
          cuts.push(clip.timelineRange.startSeconds);
        }
      }
    }

    const events = cuts.map((t) => ({ timestampSeconds: t, visualCut: true }));

    const report = AudienceAttentionModel.simulate({
      totalDurationSeconds: totalDuration,
      events,
    });

    return {
      averageAttention: report.averageAttention,
      minAttention: report.minAttention,
      report,
    };
  }

  public static evaluateCognitiveLoad(ir: EditorialIR): CognitiveLoadSummary {
    const totalDuration = this.getIRDuration(ir);
    const report = CognitiveLoadEngine.evaluate({
      totalDurationSeconds: totalDuration,
      states: [
        {
          timestampSeconds: 1.0,
          speechActive: true,
          speechWordsPerMinute: 150,
          onScreenDataElementsCount: 1,
        },
      ],
    });

    return {
      peakLoad: report.peakLoad,
      averageLoad: report.averageLoad,
      overloadsCount: report.detectedOverloadsCount,
      report,
    };
  }

  public static evaluateContrast(ir: EditorialIR): ContrastSummary {
    const primary = ir.tracks.find((t) => t.type === "VIDEO_PRIMARY");
    const beats = (primary?.clips ?? []).map((c, i) => ({
      beatIndex: i,
      name: c.label,
      tension: (i % 4 === 3 ? "PEAK" : i % 4 === 2 ? "HIGH" : i % 4 === 1 ? "MEDIUM" : "LOW") as
        | "LOW"
        | "MEDIUM"
        | "HIGH"
        | "PEAK"
        | "RELEASE",
      durationSeconds: c.timelineRange.durationSeconds,
    }));

    const report = EditorialContrast.evaluate({ beats });

    return {
      contrastScore: report.contrastScore,
      isValidContrast: report.isValidContrast,
      report,
    };
  }

  public static evaluatePacing(ir: EditorialIR): PacingSummary {
    const totalDuration = this.getIRDuration(ir);
    const primary = ir.tracks.find((t) => t.type === "VIDEO_PRIMARY");
    const cuts = (primary?.clips ?? []).map((c) => c.timelineRange.startSeconds);

    const report = PacingCurveComposer.evaluate({
      totalDurationSeconds: totalDuration,
      cutTimestampsSeconds: cuts,
      targetCurve: [{ startSeconds: 0, endSeconds: totalDuration, targetPacing: 0.5 }],
    });

    return {
      alignmentScore: report.alignmentScore,
      meanL1Distance: report.meanL1Distance,
      report,
    };
  }
}
