import { QARule, QAIssue, EditorialDocument, QARuleContext } from "../../contracts/editorial-qa.types.js";
import { QAId } from "../qa-id.js";

export const TimelineRules: QARule[] = [
  {
    id: "QA-TIME-001",
    description: "Verifies all clips have strictly positive durations",
    severity: "BLOCKING",
    evaluate(doc: EditorialDocument, _ctx: QARuleContext): QAIssue[] {
      const issues: QAIssue[] = [];
      for (const track of doc.tracks) {
        for (const clip of track.clips) {
          if (clip.timelineRange.durationSeconds <= 0) {
            issues.push({
              id: QAId.createIssueId({
                ruleId: "QA-TIME-001",
                entityIds: [clip.id],
                timestampSeconds: clip.timelineRange.startSeconds,
                severity: "BLOCKING",
                fingerprint: `non_positive_dur_${clip.id}`,
              }),
              ruleId: "QA-TIME-001",
              severity: "BLOCKING",
              title: "Non-Positive Clip Duration",
              message: `Clip '${clip.id}' has duration ${clip.timelineRange.durationSeconds}s <= 0.`,
              timestampSeconds: clip.timelineRange.startSeconds,
              durationSeconds: clip.timelineRange.durationSeconds,
              entityIds: [clip.id],
              actualValue: clip.timelineRange.durationSeconds,
              expectedValue: "> 0",
              confidence: 1.0,
              autoFixAvailable: false,
              fingerprint: `non_positive_dur_${clip.id}`,
            });
          }
        }
      }
      return issues;
    },
  },
  {
    id: "QA-TIME-002",
    description: "Verifies clips do not start at negative timestamps",
    severity: "BLOCKING",
    evaluate(doc: EditorialDocument, _ctx: QARuleContext): QAIssue[] {
      const issues: QAIssue[] = [];
      for (const track of doc.tracks) {
        for (const clip of track.clips) {
          if (clip.timelineRange.startSeconds < 0) {
            issues.push({
              id: QAId.createIssueId({
                ruleId: "QA-TIME-002",
                entityIds: [clip.id],
                timestampSeconds: clip.timelineRange.startSeconds,
                severity: "BLOCKING",
                fingerprint: `negative_start_${clip.id}`,
              }),
              ruleId: "QA-TIME-002",
              severity: "BLOCKING",
              title: "Negative Clip Start Time",
              message: `Clip '${clip.id}' starts at negative time ${clip.timelineRange.startSeconds}s.`,
              timestampSeconds: clip.timelineRange.startSeconds,
              entityIds: [clip.id],
              actualValue: clip.timelineRange.startSeconds,
              expectedValue: ">= 0",
              confidence: 1.0,
              autoFixAvailable: false,
              fingerprint: `negative_start_${clip.id}`,
            });
          }
        }
      }
      return issues;
    },
  },
  {
    id: "QA-TIME-004",
    description: "Detects illegal overlapping clips on the same primary track",
    severity: "BLOCKING",
    evaluate(doc: EditorialDocument, _ctx: QARuleContext): QAIssue[] {
      const issues: QAIssue[] = [];
      for (const track of doc.tracks) {
        if (track.type !== "VIDEO_PRIMARY" && track.type !== "AUDIO_DIALOGUE") continue;
        const sorted = [...track.clips].sort(
          (a, b) => a.timelineRange.startSeconds - b.timelineRange.startSeconds
        );
        for (let i = 0; i < sorted.length - 1; i++) {
          const current = sorted[i];
          const next = sorted[i + 1];
          const currentEnd = current.timelineRange.startSeconds + current.timelineRange.durationSeconds;
          if (currentEnd > next.timelineRange.startSeconds + 0.001) {
            issues.push({
              id: QAId.createIssueId({
                ruleId: "QA-TIME-004",
                entityIds: [current.id, next.id],
                timestampSeconds: next.timelineRange.startSeconds,
                severity: "BLOCKING",
                fingerprint: `overlap_${current.id}_${next.id}`,
              }),
              ruleId: "QA-TIME-004",
              severity: "BLOCKING",
              title: "Illegal Clip Overlap on Same Track",
              message: `Clip '${current.id}' overlaps with '${next.id}' by ${(currentEnd - next.timelineRange.startSeconds).toFixed(3)}s.`,
              timestampSeconds: next.timelineRange.startSeconds,
              entityIds: [current.id, next.id],
              confidence: 1.0,
              autoFixAvailable: false,
              fingerprint: `overlap_${current.id}_${next.id}`,
            });
          }
        }
      }
      return issues;
    },
  },
];
