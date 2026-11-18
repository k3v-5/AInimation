import crypto from "crypto";
import { EditorialIR } from "../ir/editorial-ir.types.js";
import {
  QAIssue,
  QAIssueSchema,
  QAReport,
  QAReportSchema,
} from "./editorial-qa.types.js";

/**
 * REQ-036, REQ-037 & REQ-038: Editorial Quality Assurance (QA 2.0) Engine.
 * Scans the Editorial IR prior to export or rendering, detecting inadvertent black frames,
 * flash frames, track gaps, volume overloads, and media reference anomalies.
 */
export class EditorialQAEngine {
  public static auditIR(ir: EditorialIR, deterministicDate?: string): QAReport {
    const issues: QAIssue[] = [];
    let checksRun = 0;

    // 1. Audit Primary Video Track Gaps & Continuity
    const primaryTrack = ir.tracks.find((t) => t.type === "VIDEO_PRIMARY");
    if (primaryTrack) {
      checksRun++;
      const clips = [...primaryTrack.clips].sort(
        (a, b) => a.timelineRange.startSeconds - b.timelineRange.startSeconds
      );

      // Check gap before first clip
      if (clips.length > 0 && clips[0].timelineRange.startSeconds > 0.05) {
        const gapId = `qa_gap_0_${crypto.createHash("sha256").update(`gap_0_${primaryTrack.id}_${clips[0].id}`).digest("hex").slice(0, 8)}`;
        issues.push(
          QAIssueSchema.parse({
            id: gapId,
            checkType: "TRACK_GAP",
            severity: "BLOCKING",
            trackId: primaryTrack.id,
            timestampSeconds: 0,
            description: `Black frame gap of ${clips[0].timelineRange.startSeconds.toFixed(3)}s at timeline start.`,
            suggestedFix: "Shift first clip to 0.000s or insert an opening slug.",
          })
        );
      }

      // Check gaps between consecutive primary clips
      for (let i = 0; i < clips.length - 1; i++) {
        checksRun++;
        const currEnd = clips[i].timelineRange.startSeconds + clips[i].timelineRange.durationSeconds;
        const nextStart = clips[i + 1].timelineRange.startSeconds;
        const gap = nextStart - currEnd;

        if (gap > 0.04) {
          // More than 1 frame at 24/30fps
          const gapId = `qa_gap_${i}_${crypto.createHash("sha256").update(`gap_${i}_${clips[i].id}_${clips[i + 1].id}`).digest("hex").slice(0, 8)}`;
          issues.push(
            QAIssueSchema.parse({
              id: gapId,
              checkType: "TRACK_GAP",
              severity: "BLOCKING",
              trackId: primaryTrack.id,
              clipId: clips[i].id,
              timestampSeconds: currEnd,
              description: `Unintended black frame gap (${gap.toFixed(3)}s) between clips '${clips[i].label}' and '${clips[i + 1].label}'.`,
              suggestedFix: "Snap clips together or extend outgoing clip tail.",
            })
          );
        }
      }
    }

    // 2. Audit Flash Frames & Asset Validity across all tracks
    for (const track of ir.tracks) {
      for (const clip of track.clips) {
        checksRun += 2;

        // Check empty asset ID
        if (!clip.assetId || clip.assetId.trim() === "") {
          const missId = `qa_missing_${clip.id}_${crypto.createHash("sha256").update(`missing_${clip.id}_${track.id}`).digest("hex").slice(0, 8)}`;
          issues.push(
            QAIssueSchema.parse({
              id: missId,
              checkType: "MISSING_MEDIA_SOURCE",
              severity: "BLOCKING",
              trackId: track.id,
              clipId: clip.id,
              timestampSeconds: clip.timelineRange.startSeconds,
              description: `Clip '${clip.label}' has missing or empty assetId.`,
              suggestedFix: "Link clip to a valid media file URI.",
            })
          );
        }

        // Check flash frames on video tracks (< 0.10s / 3 frames)
        if (track.type.startsWith("VIDEO") && clip.timelineRange.durationSeconds < 0.10) {
          const flashId = `qa_flash_${clip.id}_${crypto.createHash("sha256").update(`flash_${clip.id}_${track.id}`).digest("hex").slice(0, 8)}`;
          issues.push(
            QAIssueSchema.parse({
              id: flashId,
              checkType: "FLASH_FRAME",
              severity: "WARNING",
              trackId: track.id,
              clipId: clip.id,
              timestampSeconds: clip.timelineRange.startSeconds,
              description: `Sub-perceptual flash frame detected (${clip.timelineRange.durationSeconds.toFixed(3)}s) on clip '${clip.label}'.`,
              suggestedFix: "Prune or extend clip duration to at least 0.150s.",
            })
          );
        }

        // Check Audio Volume clipping
        if (track.type.startsWith("AUDIO") && clip.volumeDb > 0.0) {
          const clipVolId = `qa_clip_${clip.id}_${crypto.createHash("sha256").update(`clipvol_${clip.id}_${clip.volumeDb}`).digest("hex").slice(0, 8)}`;
          issues.push(
            QAIssueSchema.parse({
              id: clipVolId,
              checkType: "AUDIO_CLIPPING",
              severity: "WARNING",
              trackId: track.id,
              clipId: clip.id,
              timestampSeconds: clip.timelineRange.startSeconds,
              description: `Audio volume level of +${clip.volumeDb.toFixed(1)}dB exceeds 0.0dB headroom threshold.`,
              suggestedFix: "Attenuate volume level to <= 0.0dB to prevent digital clipping.",
            })
          );
        }
      }
    }

    // Compute Overall QA Score
    let deduction = 0;
    let hasBlocking = false;

    for (const issue of issues) {
      if (issue.severity === "BLOCKING") {
        deduction += 25;
        hasBlocking = true;
      } else if (issue.severity === "WARNING") {
        deduction += 10;
      } else {
        deduction += 3;
      }
    }

    const qaScore = Math.max(0.0, Math.min(100.0, 100.0 - deduction));
    const isReadyForExport = qaScore >= 75.0 && !hasBlocking;

    return QAReportSchema.parse({
      projectId: ir.projectId,
      qaScore: Number(qaScore.toFixed(2)),
      totalChecksRun: checksRun,
      issues,
      isReadyForExport,
      auditedAt: deterministicDate ?? ir.createdAt,
    });
  }
}
