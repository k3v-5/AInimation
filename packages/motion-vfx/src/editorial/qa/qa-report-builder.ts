import {
  EditorialDocument,
  EditorialQAReport,
  QAIssue,
  ExportReadiness,
} from "../contracts/editorial-qa.types.js";
import { HumanReviewSummary } from "../contracts/human-review.types.js";
import { QASeverityCalculator } from "./qa-severity.js";
import { QANormalizer } from "./qa-normalizer.js";

/**
 * REQ-030 §17: Deterministic QA Report Builder
 */
export class QAReportBuilder {
  public static readonly SCHEMA_VERSION = "1.0.0";
  public static readonly ENGINE_VERSION = "4.0.0";

  public static buildReport(params: {
    document: EditorialDocument;
    issues: QAIssue[];
    humanReviewSummary: HumanReviewSummary;
  }): EditorialQAReport {
    const { document, issues, humanReviewSummary } = params;

    let blocking = 0;
    let warnings = 0;
    let suggestions = 0;

    const categories: Record<string, { score: number; issuesCount: number }> = {
      TIMELINE: { score: 100, issuesCount: 0 },
      CONTINUITY: { score: 100, issuesCount: 0 },
      NARRATIVE: { score: 100, issuesCount: 0 },
      EVIDENCE: { score: 100, issuesCount: 0 },
      COGNITIVE: { score: 100, issuesCount: 0 },
      PACING: { score: 100, issuesCount: 0 },
      VISUAL: { score: 100, issuesCount: 0 },
      AUDIO: { score: 100, issuesCount: 0 },
      EXPORT: { score: 100, issuesCount: 0 },
      SAFETY: { score: 100, issuesCount: 0 },
    };

    const categorySummary: Record<string, number> = {
      STRUCTURE: 0,
      TIMING: 0,
      MEDIA: 0,
      AUDIO: 0,
      VISUAL_CONTINUITY: 0,
      SAFE_ZONE: 0,
      NARRATIVE: 0,
      EVIDENCE: 0,
      ATTENTION: 0,
      COGNITIVE_LOAD: 0,
      CONTRAST: 0,
      PACING: 0,
      STYLE: 0,
      EXPORT: 0,
      CONFIDENCE: 0,
      INTEGRITY: 0,
    };

    const blockers: QAIssue[] = [];
    let sumConf = 0;
    let minConf = 1.0;
    let belowHumanThreshold = 0;

    for (const issue of issues) {
      if (issue.severity === "BLOCKING") {
        blocking++;
        blockers.push(issue);
      } else if (issue.severity === "WARNING") {
        warnings++;
      } else {
        suggestions++;
      }

      sumConf += issue.confidence;
      if (issue.confidence < minConf) minConf = issue.confidence;
      if (issue.confidence < 0.7) belowHumanThreshold++;

      // Map rule prefix to category
      let cat = "TIMELINE";
      if (issue.ruleId.startsWith("QA-CONT")) {
        cat = "CONTINUITY";
        categorySummary.VISUAL_CONTINUITY++;
      } else if (issue.ruleId.startsWith("QA-NARR")) {
        cat = "NARRATIVE";
        categorySummary.NARRATIVE++;
      } else if (issue.ruleId.startsWith("QA-EVID")) {
        cat = "EVIDENCE";
        categorySummary.EVIDENCE++;
      } else if (issue.ruleId.startsWith("QA-COG")) {
        cat = "COGNITIVE";
        categorySummary.COGNITIVE_LOAD++;
      } else if (issue.ruleId.startsWith("QA-PACE")) {
        cat = "PACING";
        categorySummary.PACING++;
      } else if (issue.ruleId.startsWith("QA-VIS")) {
        cat = "VISUAL";
        categorySummary.SAFE_ZONE++;
      } else if (issue.ruleId.startsWith("QA-AUD")) {
        cat = "AUDIO";
        categorySummary.AUDIO++;
      } else if (issue.ruleId.startsWith("QA-EXP")) {
        cat = "EXPORT";
        categorySummary.EXPORT++;
      } else if (issue.ruleId.startsWith("QA-SAFE")) {
        cat = "SAFETY";
        categorySummary.INTEGRITY++;
      } else {
        categorySummary.TIMING++;
      }

      if (categories[cat]) {
        categories[cat].issuesCount++;
        const penalty = issue.severity === "BLOCKING" ? 40 : issue.severity === "WARNING" ? 15 : 5;
        categories[cat].score = Math.max(0, categories[cat].score - penalty);
      }
    }

    const avgConf = issues.length > 0 ? Number((sumConf / issues.length).toFixed(4)) : 1.0;
    if (issues.length === 0) minConf = 1.0;

    const score = QASeverityCalculator.calculateScore(blocking, warnings, suggestions);
    const status = QASeverityCalculator.determineStatus(
      blocking,
      warnings,
      humanReviewSummary.pendingCount
    );

    const exportReadiness: ExportReadiness = {
      ready: blocking === 0 && humanReviewSummary.pendingCount === 0,
      blockers,
    };

    const preliminary: Omit<EditorialQAReport, "checksumSha256"> = {
      schemaVersion: this.SCHEMA_VERSION,
      engineVersion: this.ENGINE_VERSION,
      documentId: document.projectId,
      projectId: document.projectId,
      inputChecksumSha256: document.checksum || "0".repeat(64),
      generatedAtDeterministic: "v4.0.0-editorial-master",
      status,
      score,
      overallScore: score,
      issues,
      summary: {
        blocking,
        warnings,
        suggestions,
        total: issues.length,
      },
      categories,
      categorySummary,
      confidenceSummary: {
        average: avgConf,
        minimum: Number(minConf.toFixed(4)),
        belowHumanReviewThreshold: belowHumanThreshold,
      },
      humanReviewRequired: humanReviewSummary.pendingCount > 0,
      humanReviewCount: humanReviewSummary.pendingCount,
      exportReadiness,
      humanReview: humanReviewSummary,
      integrity: {
        deterministic: true,
        algorithm: "SHA-256",
        canonicalizationVersion: "1.0.0",
        timestampDeterministic: true,
      },
      blockingCount: blocking,
      warningCount: warnings,
      suggestionCount: suggestions,
      canExport: exportReadiness.ready,
      confidenceScore: avgConf,
      findings: issues,
      reviewQueue: humanReviewSummary.items,
    };

    const checksumSha256 = QANormalizer.computeCanonicalSha256(preliminary);

    return {
      ...preliminary,
      checksumSha256,
    };
  }
}
