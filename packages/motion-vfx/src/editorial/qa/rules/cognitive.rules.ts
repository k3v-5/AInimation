import { QARule, QAIssue, EditorialDocument, QARuleContext } from "../../contracts/editorial-qa.types.js";
import { QAId } from "../qa-id.js";

export const CognitiveRules: QARule[] = [
  {
    id: "QA-COG-001",
    description: "Detects sustained high cognitive load above threshold (> 0.85)",
    severity: "WARNING",
    evaluate(doc: EditorialDocument, _ctx: QARuleContext): QAIssue[] {
      const issues: QAIssue[] = [];
      const cognitiveWindows = (doc as any).cognitiveWindows as
        | Array<{ windowStart: number; score: number }>
        | undefined;

      if (cognitiveWindows) {
        for (const w of cognitiveWindows) {
          if (w.score > 0.85) {
            issues.push({
              id: QAId.createIssueId({
                ruleId: "QA-COG-001",
                entityIds: [doc.projectId],
                timestampSeconds: w.windowStart,
                severity: "WARNING",
                fingerprint: `cognitive_overload_${w.windowStart}`,
              }),
              ruleId: "QA-COG-001",
              severity: "WARNING",
              title: "Sustained Cognitive Overload",
              message: `Cognitive load score ${w.score.toFixed(2)} exceeds threshold (0.85) at t=${w.windowStart}s.`,
              timestampSeconds: w.windowStart,
              entityIds: [doc.projectId],
              actualValue: w.score,
              threshold: 0.85,
              confidence: 0.88,
              autoFixAvailable: false,
              fingerprint: `cognitive_overload_${w.windowStart}`,
            });
          }
        }
      }
      return issues;
    },
  },
];
