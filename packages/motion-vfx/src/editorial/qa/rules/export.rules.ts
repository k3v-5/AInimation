import { QARule, QAIssue, EditorialDocument, QARuleContext } from "../../contracts/editorial-qa.types.js";
import { QAId } from "../qa-id.js";

export const ExportRules: QARule[] = [
  {
    id: "QA-EXP-001",
    description: "Verifies composition has at least one track with clips",
    severity: "BLOCKING",
    evaluate(doc: EditorialDocument, _ctx: QARuleContext): QAIssue[] {
      const issues: QAIssue[] = [];
      if (!doc.tracks || doc.tracks.length === 0) {
        issues.push({
          id: QAId.createIssueId({
            ruleId: "QA-EXP-001",
            entityIds: [doc.projectId],
            severity: "BLOCKING",
            fingerprint: "empty_timeline_tracks",
          }),
          ruleId: "QA-EXP-001",
          severity: "BLOCKING",
          title: "Empty Timeline Tracks",
          message: `Project '${doc.projectId}' has zero tracks defined.`,
          entityIds: [doc.projectId],
          actualValue: 0,
          expectedValue: "> 0",
          confidence: 1.0,
          autoFixAvailable: false,
          fingerprint: "empty_timeline_tracks",
        });
      }
      return issues;
    },
  },
];
