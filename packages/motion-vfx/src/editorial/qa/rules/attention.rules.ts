import { QARule, QAIssue, EditorialDocument, QARuleContext } from "../../contracts/editorial-qa.types.js";
import { QAId } from "../qa-id.js";

/**
 * REQ-030 §12: Auditoría de Atención (QA-ATTN-001)
 */
export const AttentionRules: QARule[] = [
  {
    id: "QA-ATTN-001",
    description: "Detecta caídas prolongadas de retención estimada o ausencia de estímulos",
    severity: "WARNING",
    evaluate(doc: EditorialDocument, ctx: QARuleContext): QAIssue[] {
      const issues: QAIssue[] = [];
      const attentionModel = (ctx as any).attentionModel || (doc as any).attentionModel;

      if (attentionModel && Array.isArray(attentionModel.points)) {
        for (const pt of attentionModel.points) {
          if (pt.retentionScore !== undefined && pt.retentionScore < 0.35) {
            issues.push({
              id: QAId.createIssueId({
                ruleId: "QA-ATTN-001",
                entityIds: [doc.projectId],
                timestampSeconds: pt.timestampSeconds ?? 0,
                severity: "WARNING",
                fingerprint: `retention_drop_${pt.timestampSeconds}`,
              }),
              ruleId: "QA-ATTN-001",
              severity: "WARNING",
              title: "Editorial Attention Estimate Drop",
              message: `Caída pronunciada en la estimación de retención editorial (${pt.retentionScore.toFixed(2)}) en t=${pt.timestampSeconds}s.`,
              timestampSeconds: pt.timestampSeconds,
              entityIds: [doc.projectId],
              confidence: 0.85,
              autoFixAvailable: true,
              fingerprint: `retention_drop_${pt.timestampSeconds}`,
            });
          }
        }
      }
      return issues;
    },
  },
];
