import { EditorialConstraintSolver } from "./constraint-solver.js";

export interface EditorialLossMetrics {
  narrativeLoss: number; // [0.0, 1.0]
  attentionLoss: number; // [0.0, 1.0]
  pacingLoss: number; // [0.0, 1.0]
  evidenceLoss: number; // [0.0, 1.0]
  continuityLoss: number; // [0.0, 1.0]
  audioLoss: number; // [0.0, 1.0]
  styleLoss: number; // [0.0, 1.0]
  durationLoss: number; // [0.0, 1.0]
}

export interface OptimizationWeights {
  wNarrative: number;
  wAttention: number;
  wPacing: number;
  wEvidence: number;
  wContinuity: number;
  wAudio: number;
  wStyle: number;
  wDuration: number;
}

export interface CandidateProposal {
  id: string;
  name: string;
  durationSeconds: number;
  metrics: EditorialLossMetrics;
  candidatePayload: any;
}

export interface ParetoSolution {
  proposal: CandidateProposal;
  compositeLoss: number;
  isParetoOptimal: boolean;
  explanation: {
    whatChanged: string;
    whatWasPreserved: string;
    whatWasSacrificed: string;
    dominantDimensions: string[];
  };
}

/**
 * REQ-078 & REQ-079: Master Multi-Objective & Pareto Editorial Optimizer
 * Genera el frente de soluciones de compromiso no dominadas respetando estrictamente
 * las restricciones duras y justificando los sacrificios editoriales.
 */
export class ParetoEditorialOptimizer {
  public static readonly DEFAULT_WEIGHTS: OptimizationWeights = {
    wNarrative: 0.20,
    wAttention: 0.15,
    wPacing: 0.15,
    wEvidence: 0.20,
    wContinuity: 0.10,
    wAudio: 0.05,
    wStyle: 0.05,
    wDuration: 0.10,
  };

  /**
   * REQ-078: Calcula la función de pérdida combinada normalizada
   */
  public static calculateCompositeLoss(
    m: EditorialLossMetrics,
    weights: OptimizationWeights = ParetoEditorialOptimizer.DEFAULT_WEIGHTS
  ): number {
    const raw =
      weights.wNarrative * m.narrativeLoss +
      weights.wAttention * m.attentionLoss +
      weights.wPacing * m.pacingLoss +
      weights.wEvidence * m.evidenceLoss +
      weights.wContinuity * m.continuityLoss +
      weights.wAudio * m.audioLoss +
      weights.wStyle * m.styleLoss +
      weights.wDuration * m.durationLoss;

    return Number(Math.max(0.0, Math.min(1.0, raw)).toFixed(4));
  }

  /**
   * Determina si la propuesta A domina a la propuesta B (en minimización de pérdidas).
   * A domina a B si A <= B en todas las métricas y A < B en al menos una.
   */
  public static dominates(a: EditorialLossMetrics, b: EditorialLossMetrics): boolean {
    const keys: (keyof EditorialLossMetrics)[] = [
      "narrativeLoss",
      "attentionLoss",
      "pacingLoss",
      "evidenceLoss",
      "continuityLoss",
      "audioLoss",
      "styleLoss",
      "durationLoss",
    ];

    let strictlyBetterInAtLeastOne = false;

    for (const k of keys) {
      if (a[k] > b[k] + 1e-6) {
        return false; // A es peor en esta dimensión
      }
      if (a[k] < b[k] - 1e-6) {
        strictlyBetterInAtLeastOne = true;
      }
    }

    return strictlyBetterInAtLeastOne;
  }

  /**
   * REQ-079: Genera el conjunto de soluciones no dominadas (Frente de Pareto)
   */
  public static computeParetoFront(
    candidates: CandidateProposal[],
    constraintSolver?: EditorialConstraintSolver,
    weights: OptimizationWeights = ParetoEditorialOptimizer.DEFAULT_WEIGHTS
  ): ParetoSolution[] {
    // 1. Filtrado de factibilidad estricta
    const feasibleCandidates: CandidateProposal[] = [];
    for (const cand of candidates) {
      if (constraintSolver) {
        const check = constraintSolver.solve(cand.candidatePayload);
        if (!check.isFeasible) continue; // Descartar propuestas que violen restricciones duras
      }
      feasibleCandidates.push(cand);
    }

    if (feasibleCandidates.length === 0) return [];

    // 2. Identificar candidatos no dominados
    const paretoSet: CandidateProposal[] = [];

    for (let i = 0; i < feasibleCandidates.length; i++) {
      const a = feasibleCandidates[i];
      let isDominated = false;

      for (let j = 0; j < feasibleCandidates.length; j++) {
        if (i === j) continue;
        const b = feasibleCandidates[j];
        if (this.dominates(b.metrics, a.metrics)) {
          isDominated = true;
          break;
        }
      }

      if (!isDominated) {
        paretoSet.push(a);
      }
    }

    // 3. Estructurar soluciones y explicabilidad
    return paretoSet
      .map((prop) => {
        const compositeLoss = this.calculateCompositeLoss(prop.metrics, weights);

        return {
          proposal: prop,
          compositeLoss,
          isParetoOptimal: true,
          explanation: {
            whatChanged: `Ajuste de duración a ${prop.durationSeconds.toFixed(1)}s`,
            whatWasPreserved: `Evidencia narrativa (pérdida: ${(prop.metrics.evidenceLoss * 100).toFixed(1)}%)`,
            whatWasSacrificed: `Ritmo secundario (pérdida: ${(prop.metrics.pacingLoss * 100).toFixed(1)}%)`,
            dominantDimensions: ["EVIDENCE_INTEGRITY", "NARRATIVE_CONTINUITY"],
          },
        };
      })
      .sort((a, b) => a.compositeLoss - b.compositeLoss || a.proposal.id.localeCompare(b.proposal.id));
  }
}
