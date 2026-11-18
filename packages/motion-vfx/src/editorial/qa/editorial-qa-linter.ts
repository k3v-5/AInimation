import {
  EditorialDocument,
  EditorialQAReport,
  QALintOptions,
  QARuleContext,
  QAIssue,
} from "../contracts/editorial-qa.types.js";
import { QASeverityCalculator } from "./qa-severity.js";
import { EditorialQARegistry } from "./editorial-qa-registry.js";
import { QARulesRegistry } from "./qa-rules.js";
import { HumanReviewQueue } from "./human-review-queue.js";
import { QAReportBuilder } from "./qa-report-builder.js";
import "./editorial-qa-rules.js";

/**
 * REQ-030 §4: EditorialQALinter
 * Punto de entrada principal determinista para linting editorial.
 */
export class EditorialQALinter {
  public static lint(
    target: EditorialDocument | { ir: EditorialDocument; config?: any; evidenceReport?: any; [key: string]: any },
    options: QALintOptions = {}
  ): EditorialQAReport {
    const isContextObj = (target as any).ir !== undefined;
    const doc = isContextObj ? (target as any).ir : (target as EditorialDocument);
    const context: any = isContextObj ? target : { ir: doc };

    if (!context.evidenceReport && (doc as any).evidenceReport) {
      context.evidenceReport = (doc as any).evidenceReport;
    }
    if (!context.cognitiveAnalysis && (doc as any).cognitiveAnalysis) {
      context.cognitiveAnalysis = (doc as any).cognitiveAnalysis;
    }
    if (!context.pacingAnalysis && (doc as any).pacingAnalysis) {
      context.pacingAnalysis = (doc as any).pacingAnalysis;
    }
    if (!context.continuityReport && (doc as any).continuityReport) {
      context.continuityReport = (doc as any).continuityReport;
    }

    // Evaluar reglas del registro de 17 categorías y del registro modular

    const registryIssues = EditorialQARegistry.evaluate(context);
    const domainIssues = QARulesRegistry.evaluateAll(doc, context);

    // Unir issues evitando duplicados
    const seen = new Set<string>();
    const allIssues: QAIssue[] = [];

    for (const issue of [...registryIssues, ...domainIssues]) {
      const key = `${issue.ruleId}_${issue.entityIds.join(",")}_${(issue as any).fingerprint ?? ""}`;
      if (!seen.has(key)) {
        seen.add(key);
        allIssues.push(issue as QAIssue);
      }
    }

    const filteredIssues =
      options.includeSuggestions === false
        ? allIssues.filter((i) => i.severity !== "SUGGESTION")
        : allIssues;

    const reviewQueue = new HumanReviewQueue();
    reviewQueue.enqueueIssues(filteredIssues);
    const humanSummary = reviewQueue.getSummary();

    const report = QAReportBuilder.buildReport({
      document: doc,
      issues: filteredIssues,
      humanReviewSummary: humanSummary,
    });

    (report as any).findings = filteredIssues;
    (report as any).blockingCount = report.summary.blocking;
    (report as any).warningCount = report.summary.warnings;
    (report as any).suggestionCount = report.summary.suggestions;

    if (isContextObj) {
      if (report.status === "PASSED") (report as any).status = "PASS";
    }

    // Ajuste en modo estricto: failOnWarnings
    if (options.strict || options.failOnWarnings) {
      if (report.status === "PASSED_WITH_WARNINGS" || (report as any).status === "PASS_WITH_WARNINGS") {
        return {
          ...report,
          canExport: false,
          exportReadiness: {
            ready: false,
            blockers: report.issues.filter((i) => i.severity === "BLOCKING" || i.severity === "WARNING"),
          },
        };
      }
    }

    return report;
  }

  // Compatibilidad con pruebas previas
  public static createDefaultConfig(): any {
    return {
      enabledRules: [],
      thresholds: {
        humanReviewConfidence: 0.7,
        maxCognitiveLoad: 0.85,
        minAttention: 0.5,
        minPacingAlignment: 0.65,
        maxLowTensionDuration: 15.0,
        maxHighTensionRun: 20.0,
      },
      failOnWarnings: false,
      requireEvidence: true,
      requireSafeZones: true,
      deterministic: true,
    };
  }

  public static calculateOverallScore(
    blockingCount: number,
    warningCount: number,
    suggestionCount: number
  ): number {
    return QASeverityCalculator.calculateScore(blockingCount, warningCount, suggestionCount);
  }
}
