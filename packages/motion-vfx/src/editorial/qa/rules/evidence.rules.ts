import { QARule, QAIssue, EditorialDocument, QARuleContext } from "../../contracts/editorial-qa.types.js";
import { QAId } from "../qa-id.js";

export const EvidenceRules: QARule[] = [
  {
    id: "QA-EVID-001",
    description: "Verifies that all factual claims have backed evidence",
    severity: "BLOCKING",
    evaluate(doc: EditorialDocument, _ctx: QARuleContext): QAIssue[] {
      const issues: QAIssue[] = [];
      const claims = (doc as any).claims as
        | Array<{ id: string; statement?: string; evidenceId?: string; isVerified?: boolean }>
        | undefined;

      if (claims) {
        for (const claim of claims) {
          if (!claim.evidenceId && !claim.isVerified) {
            issues.push({
              id: QAId.createIssueId({
                ruleId: "QA-EVID-001",
                entityIds: [claim.id],
                severity: "BLOCKING",
                fingerprint: `unsupported_claim_${claim.id}`,
              }),
              ruleId: "QA-EVID-001",
              severity: "BLOCKING",
              title: "Factual Claim Missing Supporting Evidence",
              message: `Factual claim '${claim.id}' is declared without verified backing evidence.`,
              entityIds: [claim.id],
              actualValue: "unsupported",
              expectedValue: "verified",
              confidence: 1.0,
              autoFixAvailable: false,
              fingerprint: `unsupported_claim_${claim.id}`,
            });
          }
        }
      }
      return issues;
    },
  },
];
