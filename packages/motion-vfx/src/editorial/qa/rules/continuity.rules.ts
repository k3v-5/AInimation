import { QARule, QAIssue, EditorialDocument, QARuleContext } from "../../contracts/editorial-qa.types.js";
import { QAId } from "../qa-id.js";

export const ContinuityRules: QARule[] = [
  {
    id: "QA-CONT-001",
    description: "Detects rapid consecutive cuts under 0.8s on primary video track",
    severity: "WARNING",
    evaluate(doc: EditorialDocument, _ctx: QARuleContext): QAIssue[] {
      const issues: QAIssue[] = [];
      const primaryTrack = doc.tracks.find((t) => t.type === "VIDEO_PRIMARY");
      if (!primaryTrack) return issues;

      for (const clip of primaryTrack.clips) {
        if (clip.timelineRange.durationSeconds < 0.8) {
          issues.push({
            id: QAId.createIssueId({
              ruleId: "QA-CONT-001",
              entityIds: [clip.id],
              timestampSeconds: clip.timelineRange.startSeconds,
              severity: "WARNING",
              fingerprint: `rapid_cut_${clip.id}`,
            }),
            ruleId: "QA-CONT-001",
            severity: "WARNING",
            title: "Rapid Consecutive Cut Warning",
            message: `Primary clip '${clip.id}' duration is ${clip.timelineRange.durationSeconds}s (< 0.8s), risk of perceptual jarring.`,
            timestampSeconds: clip.timelineRange.startSeconds,
            durationSeconds: clip.timelineRange.durationSeconds,
            entityIds: [clip.id],
            threshold: 0.8,
            confidence: 0.85,
            autoFixAvailable: false,
            fingerprint: `rapid_cut_${clip.id}`,
          });
        }
      }
      return issues;
    },
  },
];
