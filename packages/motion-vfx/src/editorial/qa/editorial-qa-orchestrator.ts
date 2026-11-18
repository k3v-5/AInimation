import { EditorialQAFinding, EditorialSeverity } from "./editorial-qa-finding.js";
import { EditorialQAProfile, DEFAULT_EDITORIAL_QA_PROFILE } from "./editorial-qa-profile.js";
import { EditorialQAReport, EditorialQAReportBuilder } from "./editorial-qa-report.js";
import { HumanReviewQueue } from "./human-review-queue.js";
import { EditorialRulesRegistry } from "./editorial-rules.js";
import { QAHash } from "./qa-hash.js";

/**
 * REQ-030 §3, §32: EditorialQAOrchestrator
 * Orquesta los linters técnico, editorial y narrativo en un pipeline determinista no destructivo.
 */
export class EditorialQAOrchestrator {
  /**
   * REQ-030 §32: Ordena de forma estable los hallazgos.
   * Severidad -> Timestamp -> RuleId -> Entity IDs -> Finding ID.
   */
  public static sortFindings(findings: EditorialQAFinding[]): EditorialQAFinding[] {
    const severityWeight: Record<EditorialSeverity, number> = {
      BLOCKING: 3,
      WARNING: 2,
      SUGGESTION: 1,
    };

    return [...findings].sort((a, b) => {
      // 1. Severidad (descendente)
      const diffSev = severityWeight[b.severity] - severityWeight[a.severity];
      if (diffSev !== 0) return diffSev;

      // 2. Timestamp (ascendente)
      const tA = a.timestampSeconds ?? 0;
      const tB = b.timestampSeconds ?? 0;
      if (tA !== tB) return tA - tB;

      // 3. Rule ID (lexicográfico)
      const diffRule = a.ruleId.localeCompare(b.ruleId);
      if (diffRule !== 0) return diffRule;

      // 4. Entity IDs (lexicográfico)
      const eA = (a.affectedEntityIds || []).join(",");
      const eB = (b.affectedEntityIds || []).join(",");
      const diffEntity = eA.localeCompare(eB);
      if (diffEntity !== 0) return diffEntity;

      // 5. Finding ID (lexicográfico)
      return a.id.localeCompare(b.id);
    });
  }

  /**
   * Ejecuta la auditoría integral desacoplada sobre una IR Editorial.
   */
  public static audit(params: {
    ir: any;
    profile?: Partial<EditorialQAProfile>;
    evidenceReport?: any;
    cognitiveAnalysis?: any;
    pacingAnalysis?: any;
    continuityReport?: any;
  }): EditorialQAReport {
    const profile = { ...DEFAULT_EDITORIAL_QA_PROFILE, ...params.profile };
    const ir = params.ir;

    // Calcular inputChecksumSha256
    const inputChecksumSha256 = ir.checksum || QAHash.computeCanonicalSha256(ir);

    // Contexto unificado
    const context = {
      ir,
      profile,
      evidenceReport: params.evidenceReport || ir.evidenceReport,
      cognitiveAnalysis: params.cognitiveAnalysis || ir.cognitiveAnalysis,
      pacingAnalysis: params.pacingAnalysis || ir.pacingAnalysis,
      continuityReport: params.continuityReport || ir.continuityReport,
      config: {
        thresholds: {
          humanReviewConfidence: profile.humanReviewConfidenceThreshold,
          maxCognitiveLoad: profile.cognitiveLoadThreshold,
        },
      },
    };

    // 1. Ejecutar linters mediante el registro canónico de reglas
    const rawFindings = EditorialRulesRegistry.evaluateAll(context);

    // 2. Ordenamiento determinista (§32)
    const sortedFindings = this.sortFindings(rawFindings);

    // 3. Evaluar HumanReviewQueue con umbral configurable (§19, §20)
    const reviewQueue = HumanReviewQueue.evaluateFindings(sortedFindings, {
      confidenceThreshold: profile.humanReviewConfidenceThreshold,
    });

    // 4. Construir reporte final y sellar mediante SHA-256
    return EditorialQAReportBuilder.buildReport({
      inputChecksumSha256,
      findings: sortedFindings,
      reviewQueue,
    });
  }
}
