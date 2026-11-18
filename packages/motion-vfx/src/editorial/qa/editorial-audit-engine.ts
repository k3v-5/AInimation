import crypto from "node:crypto";
import { EditorialDocument, QALintOptions } from "../contracts/editorial-qa.types.js";
import { EditorialQAFinding, EditorialSeverity } from "./editorial-findings.js";
import { EditorialQAContext, EditorialRulesRegistry } from "./editorial-rules.js";
import { HumanReviewQueue } from "./human-review-queue.js";
import { QAHash } from "./qa-hash.js";

/**
 * REQ-030 §18: Contrato Formal de Auditoría Editorial
 */
export interface EditorialAuditReport {
  schemaVersion: string;
  engineVersion: string;

  inputChecksumSha256: string;

  status: "PASS" | "PASS_WITH_WARNINGS" | "BLOCKED";

  findings: EditorialQAFinding[];

  summary: {
    blockingCount: number;
    warningCount: number;
    suggestionCount: number;
  };

  categorySummary: Record<string, number>;

  qualityScore: number;

  generatedAtPolicy: "DETERMINISTIC";

  checksumSha256: string;

  // Compatibilidad con contratos y suites de pruebas existentes
  canExport?: boolean;
  score?: number;
  overallScore?: number;
  issues?: any[];
  categories?: Record<string, { score: number; issuesCount: number }>;
  humanReview?: any[];
  humanReviewCount?: number;
}

/**
 * REQ-030 §18 & §19: EditorialAuditEngine
 * Orquestador determinista y reproducible de la auditoría editorial pre-render.
 */
export class EditorialAuditEngine {
  public static audit(
    docOrContext: EditorialDocument | EditorialQAContext | { ir: EditorialDocument; [key: string]: any },
    options: QALintOptions = {}
  ): EditorialAuditReport {
    const isContext = docOrContext && "ir" in docOrContext;
    const ir: EditorialDocument = isContext ? (docOrContext as any).ir : (docOrContext as EditorialDocument);
    const context: EditorialQAContext = isContext
      ? (docOrContext as any)
      : {
          ir,
          evidenceReport: (ir as any).evidenceReport,
          cognitiveModel: (ir as any).cognitiveAnalysis,
          pacingCurve: (ir as any).pacingAnalysis,
          attentionModel: (ir as any).attentionAnalysis,
          continuityReport: (ir as any).continuityReport,
        };

    // 1. Evaluación canónica mediante el registro de reglas
    const findings = EditorialRulesRegistry.evaluateAll(context);

    // 2. Filtrar sugerencias si está configurado
    const filteredFindings =
      options.includeSuggestions === false
        ? findings.filter((f) => f.severity !== "SUGGESTION")
        : findings;

    // 3. Resumen de severidades y categorías
    let blockingCount = 0;
    let warningCount = 0;
    let suggestionCount = 0;
    const categorySummary: Record<string, number> = {};
    const legacyCategories: Record<string, { score: number; issuesCount: number }> = {
      AUDIO: { score: 100, issuesCount: 0 },
      TIMELINE: { score: 100, issuesCount: 0 },
      STRUCTURE: { score: 100, issuesCount: 0 },
      EVIDENCE: { score: 100, issuesCount: 0 },
      NARRATIVE: { score: 100, issuesCount: 0 },
      PACING: { score: 100, issuesCount: 0 },
      COGNITIVE: { score: 100, issuesCount: 0 },
    };

    for (const f of filteredFindings) {
      if (f.severity === "BLOCKING") blockingCount++;
      else if (f.severity === "WARNING") warningCount++;
      else if (f.severity === "SUGGESTION") suggestionCount++;

      categorySummary[f.category] = (categorySummary[f.category] || 0) + 1;

      // Adaptación de categorías legacy para tests que inspeccionan categories.AUDIO, etc.
      const catKey = f.category === "TEMPORAL" ? "TIMELINE" : f.category;
      if (!legacyCategories[catKey]) {
        legacyCategories[catKey] = { score: 100, issuesCount: 0 };
      }
      legacyCategories[catKey].issuesCount++;
      legacyCategories[catKey].score = Math.max(0, legacyCategories[catKey].score - (f.severity === "BLOCKING" ? 50 : 20));
    }

    // 4. Cálculo determinista de Quality Score (§19)
    // score = 100 - (25 * blocking + 5 * warning + 1 * suggestion), clamped en [0, 100]
    const penalties = 25 * blockingCount + 5 * warningCount + 1 * suggestionCount;
    const qualityScore = Number(Math.max(0, Math.min(100, 100 - penalties)).toFixed(2));

    // 5. Estado de certificación
    let status: "PASS" | "PASS_WITH_WARNINGS" | "BLOCKED" = "PASS";
    let canExport = true;

    if (blockingCount > 0) {
      status = "BLOCKED";
      canExport = false;
    } else if (warningCount > 0) {
      status = "PASS_WITH_WARNINGS";
      if (options.strict || options.failOnWarnings) {
        canExport = false;
      }
    }

    // 6. Cola de revisión humana (§20)
    const reviewQueue = new HumanReviewQueue();
    reviewQueue.enqueueFindings(filteredFindings);
    const humanReviewItems = reviewQueue.getItems();

    // 7. Input checksum
    const inputChecksumSha256 =
      ir.checksum ||
      crypto.createHash("sha256").update(QAHash.canonicalStringify(ir), "utf8").digest("hex");

    // 8. Construcción del reporte determinista
    const report: EditorialAuditReport = {
      schemaVersion: "4.0.0",
      engineVersion: "v4.0.0-editorial-master",
      inputChecksumSha256,
      status,
      findings: filteredFindings,
      summary: {
        blockingCount,
        warningCount,
        suggestionCount,
      },
      categorySummary,
      qualityScore,
      generatedAtPolicy: "DETERMINISTIC",
      checksumSha256: "",

      // Aliases para retrocompatibilidad
      canExport,
      score: qualityScore,
      overallScore: qualityScore,
      issues: filteredFindings,
      categories: legacyCategories,
      humanReview: humanReviewItems,
      humanReviewCount: humanReviewItems.length,
    };

    // 9. Sellado criptográfico canónico SHA-256 (sin el campo checksumSha256)
    const { checksumSha256: _, ...reportToHash } = report;
    report.checksumSha256 = crypto
      .createHash("sha256")
      .update(QAHash.canonicalStringify(reportToHash), "utf8")
      .digest("hex");

    return report;
  }
}
