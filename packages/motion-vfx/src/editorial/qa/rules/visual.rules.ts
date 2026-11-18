import { QARule, QAIssue, EditorialDocument, QARuleContext } from "../../contracts/editorial-qa.types.js";
import { QAId } from "../qa-id.js";

export const VisualRules: QARule[] = [
  {
    id: "QA-VIS-001",
    description: "Verifies composition dimensions are strictly positive",
    severity: "BLOCKING",
    evaluate(doc: EditorialDocument, _ctx: QARuleContext): QAIssue[] {
      const issues: QAIssue[] = [];
      const { width, height } = doc.metadata;
      if (!Number.isFinite(width) || width <= 0 || !Number.isFinite(height) || height <= 0) {
        issues.push({
          id: QAId.createIssueId({
            ruleId: "QA-VIS-001",
            entityIds: [doc.projectId],
            severity: "BLOCKING",
            fingerprint: `invalid_dimensions_${width}x${height}`,
          }),
          ruleId: "QA-VIS-001",
          severity: "BLOCKING",
          title: "Invalid Composition Dimensions",
          message: `Composition dimensions [${width}x${height}] are non-positive or invalid.`,
          entityIds: [doc.projectId],
          actualValue: `${width}x${height}`,
          expectedValue: "> 0",
          confidence: 1.0,
          autoFixAvailable: false,
          fingerprint: `invalid_dimensions_${width}x${height}`,
        });
      }
      return issues;
    },
  },
];
