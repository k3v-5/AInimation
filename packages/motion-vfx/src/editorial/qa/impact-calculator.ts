import { EditorialDiff, EditorialImpact, EditorialRegression } from "./editorial-diff-types.js";
import { EditorialIR } from "../ir/editorial-ir.types.js";

/**
 * REQ-QA-032 to REQ-QA-039: Calculador de impacto editorial y detector de regresiones.
 */
export class ImpactCalculator {
  /**
   * REQ-QA-033: Diferencia temporal neta.
   */
  public static calculateDurationDelta(beforeSec: number, afterSec: number): number {
    return Number((afterSec - beforeSec).toFixed(4));
  }

  /**
   * REQ-QA-034: Impacto en Pacing.
   */
  public static calculatePacingImpact(
    beforeScore = 0.5,
    afterScore = 0.5
  ): { pacingDelta: number; trend: "IMPROVES" | "WORSENS" | "NEUTRAL" } {
    const delta = Number((afterScore - beforeScore).toFixed(4));
    const trend = delta > 0.05 ? "IMPROVES" : delta < -0.05 ? "WORSENS" : "NEUTRAL";
    return { pacingDelta: delta, trend };
  }

  /**
   * REQ-QA-032: Calcula overallImpactScore normalizado [0, 100].
   */
  public static computeOverallScore(impact: Partial<EditorialImpact>): number {
    const durWeight = Math.min(1.0, Math.abs(impact.durationDeltaSeconds ?? 0) / 10.0) * 20;
    const paceWeight = Math.abs(impact.pacingDelta ?? 0) * 15;
    const attnWeight = Math.abs(impact.attentionDelta ?? 0) * 15;
    const loadWeight = Math.abs(impact.cognitiveLoadDelta ?? 0) * 15;
    const narrWeight = (impact.narrativeImpactScore ?? 0) * 20;
    const evidWeight = (impact.evidenceImpactScore ?? 0) * 15;

    const raw = durWeight + paceWeight + attnWeight + loadWeight + narrWeight + evidWeight;
    return Number(Math.max(0.0, Math.min(100.0, raw)).toFixed(2));
  }

  /**
   * REQ-QA-043: Detección formal de regresiones editoriales (BLOCKING, WARNING, SUGGESTION).
   */
  public static detectRegressions(
    diffs: EditorialDiff[],
    beforeIR: EditorialIR,
    afterIR: EditorialIR
  ): EditorialRegression[] {
    const regressions: EditorialRegression[] = [];

    // Check evidence loss
    const beforeClaims = ((beforeIR as any).claims ?? []) as any[];
    const afterClaims = ((afterIR as any).claims ?? []) as any[];
    if (beforeClaims.length > afterClaims.length) {
      regressions.push({
        id: `reg_evidence_lost_${beforeClaims.length - afterClaims.length}`,
        severity: "BLOCKING",
        sourceDiffId: diffs.find((d) => d.category === "EVIDENCE")?.id ?? "diff_unknown",
        ruleId: "QA-EVID-001",
        description: `Regresión crítica: Se eliminaron ${beforeClaims.length - afterClaims.length} afirmación(es) con evidencia verificada.`,
        beforeState: beforeClaims.length,
        afterState: afterClaims.length,
      });
    }

    // Check narrative revelation displacement
    const beforeRevelation = ((beforeIR as any).beats ?? []).find((b: any) => b.type === "REVELATION");
    const afterRevelation = ((afterIR as any).beats ?? []).find((b: any) => b.type === "REVELATION");
    if (beforeRevelation && !afterRevelation) {
      regressions.push({
        id: "reg_narr_revelation_removed",
        severity: "BLOCKING",
        sourceDiffId: diffs.find((d) => d.category === "NARRATIVE")?.id ?? "diff_unknown",
        ruleId: "QA-NARR-003",
        description: "Regresión narrativa crítica: Se eliminó el beat esencial de REVELATION.",
        beforeState: beforeRevelation,
        afterState: null,
      });
    }

    return regressions;
  }
}
