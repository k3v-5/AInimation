import {
  EditorialDocument,
  EditorialQAReport,
  QARuleContext,
  QALintOptions,
} from "../contracts/editorial-qa.types.js";
import { QARulesRegistry } from "./qa-rules.js";
import { HumanReviewQueue } from "./human-review-queue.js";
import { QAReportBuilder } from "./qa-report-builder.js";

/**
 * REQ-030 §4: EditorialAuditEngine
 * Orquestador determinista del proceso de auditoría editorial.
 */
export class EditorialAuditEngine {
  public static audit(
    document: EditorialDocument,
    options: QALintOptions = {},
    context: QARuleContext = {}
  ): EditorialQAReport {
    // 1. Evaluar todas las reglas registradas
    const allIssues = QARulesRegistry.evaluateAll(document, context);

    // 2. Filtrar sugerencias si includeSuggestions === false
    const filteredIssues =
      options.includeSuggestions === false
        ? allIssues.filter((i) => i.severity !== "SUGGESTION")
        : allIssues;

    // 3. Alimentar la cola de revisión humana
    const reviewQueue = new HumanReviewQueue();
    reviewQueue.enqueueIssues(filteredIssues);
    const humanSummary = reviewQueue.getSummary();

    // 4. Construir y firmar reporte canónico
    return QAReportBuilder.buildReport({
      document,
      issues: filteredIssues,
      humanReviewSummary: humanSummary,
    });
  }
}
