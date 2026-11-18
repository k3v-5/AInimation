import { QARule, QAIssue, EditorialDocument, QARuleContext } from "../../contracts/editorial-qa.types.js";
import { QAId } from "../qa-id.js";

/**
 * REQ-030 §14: Auditoría de Contraste Editorial (QA-CONTRAST-001)
 */
export const ContrastRules: QARule[] = [
  {
    id: "QA-CONTRAST-001",
    description: "Detecta estancamiento en tensión o ausencia prolongada de puntos de liberación (RELEASE)",
    severity: "WARNING",
    evaluate(doc: EditorialDocument, ctx: QARuleContext): QAIssue[] {
      const issues: QAIssue[] = [];
      const contrastMetrics = (ctx as any).contrastMetrics || (doc as any).contrastMetrics;

      if (contrastMetrics && contrastMetrics.highTensionStreakSeconds > 15.0) {
        issues.push({
          id: QAId.createIssueId({
            ruleId: "QA-CONTRAST-001",
            entityIds: [doc.projectId],
            timestampSeconds: contrastMetrics.streakStartSeconds ?? 0,
            severity: "WARNING",
            fingerprint: `tension_streak_${contrastMetrics.streakStartSeconds}`,
          }),
          ruleId: "QA-CONTRAST-001",
          severity: "WARNING",
          title: "Sustained High Tension Streak",
          message: `Racha de alta tensión prolongada (${contrastMetrics.highTensionStreakSeconds}s > 15.0s) sin punto de distensión (RELEASE).`,
          timestampSeconds: contrastMetrics.streakStartSeconds ?? 0,
          entityIds: [doc.projectId],
          confidence: 0.85,
          autoFixAvailable: true,
          fingerprint: `tension_streak_${contrastMetrics.streakStartSeconds}`,
        });
      }
      return issues;
    },
  },
];
