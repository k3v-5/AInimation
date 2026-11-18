import { QARule, QAIssue, EditorialDocument, QARuleContext } from "../../contracts/editorial-qa.types.js";
import { QAId } from "../qa-id.js";

export const SafetyRules: QARule[] = [
  {
    id: "QA-SAFE-001",
    description: "Detects unsafe code patterns or injection attempts in project metadata",
    severity: "BLOCKING",
    evaluate(doc: EditorialDocument, _ctx: QARuleContext): QAIssue[] {
      const issues: QAIssue[] = [];
      const unsafePatterns = [/<script>/i, /<\/script>/i, /eval\(/i, /app\.project\.close\(\)/i];
      const title = doc.metadata?.title ?? "";

      for (const pat of unsafePatterns) {
        if (pat.test(title)) {
          issues.push({
            id: QAId.createIssueId({
              ruleId: "QA-SAFE-001",
              entityIds: [doc.projectId],
              severity: "BLOCKING",
              fingerprint: "unsafe_script_injection",
            }),
            ruleId: "QA-SAFE-001",
            severity: "BLOCKING",
            title: "Security Sandbox Violation: Unsafe Metadata",
            message: `Project metadata title contains unsafe script injection pattern.`,
            entityIds: [doc.projectId],
            confidence: 1.0,
            autoFixAvailable: false,
            fingerprint: "unsafe_script_injection",
          });
          break;
        }
      }
      return issues;
    },
  },
];
