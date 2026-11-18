import { ImpactAnalyzer } from "./impact-analyzer.js";
import { EditorialImpactReport } from "./editorial-diff-report.js";

export { ImpactAnalyzer };

/**
 * REQ-082 §26 & §27: EditorialImpactAnalyzer
 * Analizador semántico y multidimensional de impacto de revisiones.
 */
export class EditorialImpactAnalyzer {
  public static analyze(params: {
    beforeDoc: any;
    afterDoc: any;
    diffs?: any[];
  }): { impact: any; impactLevel: string; report: EditorialImpactReport } {
    const analysis = ImpactAnalyzer.analyzeImpact({
      beforeDoc: params.beforeDoc,
      afterDoc: params.afterDoc,
      diffs: params.diffs || [],
    });

    const narrativeChanges = (analysis.impact as any).narrativeImpact?.causalRelationsChanged ?? 0;
    const continuityChanges = (analysis.impact as any).continuityImpact?.visualIssuesDelta ?? 0;
    const evidenceScore = (analysis.impact as any).evidenceImpactScore ?? 0;

    const report: EditorialImpactReport = {
      attentionDelta: analysis.impact.attentionDelta,
      cognitiveLoadDelta: analysis.impact.cognitiveLoadDelta,
      contrastDelta: analysis.impact.contrastDelta,
      pacingAlignmentDelta: analysis.impact.pacingAlignmentDelta,
      narrativeImpact: narrativeChanges > 0 ? "HIGH" : "NONE",
      continuityImpact: continuityChanges > 0 ? "HIGH" : "NONE",
      evidenceImpact: evidenceScore > 0 ? "CRITICAL" : "NONE",
    };

    return {
      impact: analysis.impact,
      impactLevel: analysis.impactLevel,
      report,
    };
  }
}
