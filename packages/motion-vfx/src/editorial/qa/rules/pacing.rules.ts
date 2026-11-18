import { QARule, QAIssue, EditorialDocument, QARuleContext } from "../../contracts/editorial-qa.types.js";
import { QAId } from "../qa-id.js";

export const PacingRules: QARule[] = [
  {
    id: "QA-PACE-001",
    description: "Detects pacing deviation from editorial target curve",
    severity: "WARNING",
    evaluate(doc: EditorialDocument, _ctx: QARuleContext): QAIssue[] {
      const issues: QAIssue[] = [];
      const pacingDeviation = (doc as any).pacingDeviation as number | undefined;

      if (pacingDeviation !== undefined && pacingDeviation > 0.35) {
        issues.push({
          id: QAId.createIssueId({
            ruleId: "QA-PACE-001",
            entityIds: [doc.projectId],
            severity: "WARNING",
            fingerprint: "severe_pacing_deviation",
          }),
          ruleId: "QA-PACE-001",
          severity: "WARNING",
          title: "Editorial Pacing Deviation",
          message: `Pacing curve deviates by ${(pacingDeviation * 100).toFixed(1)}% from target profile.`,
          entityIds: [doc.projectId],
          actualValue: pacingDeviation,
          threshold: 0.35,
          confidence: 0.82,
          autoFixAvailable: false,
          fingerprint: "severe_pacing_deviation",
        });
      }
      return issues;
    },
  },
];
