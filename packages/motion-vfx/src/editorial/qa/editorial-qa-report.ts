import { EditorialQAFinding } from "./editorial-qa-finding.js";
import { HumanReviewItem } from "./human-review-queue.js";
import { QAHash } from "./qa-hash.js";

/**
 * REQ-030 / REQ-081 §17: Contrato de Scores Multidimensionales (0.00 - 100.00)
 */
export interface EditorialQAScore {
  overall: number;
  technical: number;
  narrative: number;
  visual: number;
  audio: number;
  evidence: number;
  pacing: number;
  attention: number;
  cognitiveLoad: number;
}

/**
 * REQ-030 §18: Estados Finales de Certificación Editorial
 */
export type EditorialQAStatus =
  | "BLOCKED"
  | "REVIEW_REQUIRED"
  | "PASS_WITH_WARNINGS"
  | "PASS";

/**
 * REQ-030 §29: Propuestas Declarativas de Mitigación
 */
export interface EditorialQAProposal {
  id: string;
  type:
    | "SHIFT_GRAPHIC"
    | "DUCK_AUDIO"
    | "SPLIT_SEGMENT"
    | "INSERT_RELEASE"
    | "REDUCE_CUT_DENSITY"
    | "REORDER_BROLL"
    | "REQUEST_EVIDENCE"
    | "HUMAN_REVIEW";
  timestampSeconds?: number;
  reason: string;
  expectedImpact: string;
  confidence: number;
  requiresHumanApproval: boolean;
}

/**
 * REQ-030 §30: Reporte Formal de Auditoría Editorial Pre-Render
 */
export interface EditorialQAReport {
  schemaVersion: string;
  engineVersion: string;
  generatedAt: string;
  inputChecksumSha256: string;
  status: EditorialQAStatus;
  score: EditorialQAScore;
  findings: EditorialQAFinding[];
  reviewQueue: HumanReviewItem[];
  proposals: EditorialQAProposal[];
  statistics: {
    blockingCount: number;
    warningCount: number;
    suggestionCount: number;
    humanReviewCount: number;
  };
  checksumSha256: string;
}

export class EditorialQAReportBuilder {
  public static readonly SCHEMA_VERSION = "4.0.0";
  public static readonly ENGINE_VERSION = "v4.0.0-editorial-master";

  /**
   * REQ-030 §18: Determina el status formal de QA.
   */
  public static determineStatus(params: {
    blockingCount: number;
    warningCount: number;
    pendingReviewsCount: number;
  }): EditorialQAStatus {
    if (params.blockingCount > 0) {
      return "BLOCKED";
    }
    if (params.pendingReviewsCount > 0) {
      return "REVIEW_REQUIRED";
    }
    if (params.warningCount > 0) {
      return "PASS_WITH_WARNINGS";
    }
    return "PASS";
  }

  /**
   * REQ-030 §17: Calcula los scores matemáticos acotados estrictamente a [0.00, 100.00].
   */
  public static calculateScores(findings: EditorialQAFinding[]): EditorialQAScore {
    const clamp = (val: number) => Math.max(0, Math.min(100, Math.round(val * 100) / 100));

    let technicalPenalties = 0;
    let narrativePenalties = 0;
    let visualPenalties = 0;
    let audioPenalties = 0;
    let evidencePenalties = 0;
    let pacingPenalties = 0;
    let attentionPenalties = 0;
    let cognitivePenalties = 0;

    for (const f of findings) {
      const p = f.severity === "BLOCKING" ? 25 : f.severity === "WARNING" ? 5 : 1;
      switch (f.category) {
        case "STRUCTURAL":
        case "TEMPORAL":
        case "EXPORT":
        case "SECURITY":
          technicalPenalties += p;
          break;
        case "NARRATIVE":
          narrativePenalties += p;
          break;
        case "VISUAL":
        case "CONTINUITY":
          visualPenalties += p;
          break;
        case "AUDIO":
          audioPenalties += p;
          break;
        case "EVIDENCE":
          evidencePenalties += p;
          break;
        case "PACING":
          pacingPenalties += p;
          break;
        case "ATTENTION":
          attentionPenalties += p;
          break;
        case "COGNITIVE_LOAD":
          cognitivePenalties += p;
          break;
        case "CONTRAST":
          narrativePenalties += p * 0.5;
          pacingPenalties += p * 0.5;
          break;
      }
    }

    const technical = clamp(100 - technicalPenalties);
    const narrative = clamp(100 - narrativePenalties);
    const visual = clamp(100 - visualPenalties);
    const audio = clamp(100 - audioPenalties);
    const evidence = clamp(100 - evidencePenalties);
    const pacing = clamp(100 - pacingPenalties);
    const attention = clamp(100 - attentionPenalties);
    const cognitiveLoad = clamp(100 - cognitivePenalties);

    // Overall ponderado determinista
    const overall = clamp(
      0.25 * technical +
      0.15 * narrative +
      0.10 * visual +
      0.10 * audio +
      0.15 * evidence +
      0.10 * pacing +
      0.075 * attention +
      0.075 * cognitiveLoad
    );

    return {
      overall,
      technical,
      narrative,
      visual,
      audio,
      evidence,
      pacing,
      attention,
      cognitiveLoad,
    };
  }

  /**
   * REQ-030 §30 & §31: Construye y sella criptográficamente el reporte mediante SHA-256 Canónico.
   */
  public static buildReport(params: {
    inputChecksumSha256: string;
    findings: EditorialQAFinding[];
    reviewQueue: HumanReviewItem[];
    proposals?: EditorialQAProposal[];
  }): EditorialQAReport {
    const blockingCount = params.findings.filter((f) => f.severity === "BLOCKING").length;
    const warningCount = params.findings.filter((f) => f.severity === "WARNING").length;
    const suggestionCount = params.findings.filter((f) => f.severity === "SUGGESTION").length;
    const pendingReviewsCount = params.reviewQueue.filter((r) => r.status === "PENDING").length;

    const status = this.determineStatus({
      blockingCount,
      warningCount,
      pendingReviewsCount,
    });

    const score = this.calculateScores(params.findings);

    // Estructura base para firma determinista
    const reportBase = {
      schemaVersion: this.SCHEMA_VERSION,
      engineVersion: this.ENGINE_VERSION,
      generatedAt: "1970-01-01T00:00:00.000Z", // Timestamp normalizado para canonización (§30)
      inputChecksumSha256: params.inputChecksumSha256,
      status,
      score,
      findings: params.findings,
      reviewQueue: params.reviewQueue,
      proposals: params.proposals || [],
      statistics: {
        blockingCount,
        warningCount,
        suggestionCount,
        humanReviewCount: params.reviewQueue.length,
      },
    };

    const checksumSha256 = QAHash.computeCanonicalSha256(reportBase);

    return {
      ...reportBase,
      generatedAt: new Date().toISOString(),
      checksumSha256,
    };
  }
}
