import { TakeCandidate, BestTakeSelection } from "./performance-types.js";
import { PerformanceScoring } from "./performance-scoring.js";

/**
 * RF-056: BestTakeSelector
 * Selecciona la mejor toma de una misma intervención asegurando integridad semántica y naturalidad.
 */
export class BestTakeSelector {
  public static readonly BEST_TAKE_AUTO_SELECT_THRESHOLD = 0.8;
  public static readonly MIN_SCORE_DIFFERENCE_FOR_AUTO = 0.05;

  public static select(takeGroupId: string, takes: TakeCandidate[]): BestTakeSelection {
    if (takes.length === 0) {
      throw new Error(`BestTakeSelector: cannot select take from empty candidates list for group '${takeGroupId}'`);
    }

    if (takes.length === 1) {
      const take = takes[0];
      const score = PerformanceScoring.calculateTakeScore(take);
      return {
        takeGroupId,
        selectedTakeId: take.id,
        winnerScore: score,
        isAutoSelected: score >= this.BEST_TAKE_AUTO_SELECT_THRESHOLD,
        recommendation: score >= this.BEST_TAKE_AUTO_SELECT_THRESHOLD ? "SELECT" : "REVIEW",
      };
    }

    // Calcular score para todos los candidatos
    const scored = takes.map((t) => ({
      candidate: t,
      score: PerformanceScoring.calculateTakeScore(t),
    }));

    // Ordenar preliminarmente por score descendente
    scored.sort((a, b) => b.score - a.score || a.candidate.id.localeCompare(b.candidate.id));

    let winner = scored[0].candidate;
    let winnerScore = scored[0].score;
    const runnerUp = scored[1].candidate;
    const runnerUpScore = scored[1].score;
    const scoreDiff = Number(Math.max(0.0, winnerScore - runnerUpScore).toFixed(4));
    let tieBreakerApplied: string | undefined = undefined;

    // Comprobar empate determinista (diferencia < 0.02)
    if (scoreDiff < 0.02) {
      const tieResult = PerformanceScoring.breakTakeTie(winner, runnerUp);
      winner = tieResult.winner;
      tieBreakerApplied = tieResult.reason;
      winnerScore = PerformanceScoring.calculateTakeScore(winner);
    }

    // Auto-select solo si supera 0.80 y saca al menos 0.05 de ventaja
    const canAutoSelect =
      winnerScore >= this.BEST_TAKE_AUTO_SELECT_THRESHOLD && scoreDiff >= this.MIN_SCORE_DIFFERENCE_FOR_AUTO;

    return {
      takeGroupId,
      selectedTakeId: winner.id,
      winnerScore,
      runnerUpScore,
      scoreDifference: scoreDiff,
      isAutoSelected: canAutoSelect,
      desempateApplied: tieBreakerApplied,
      recommendation: canAutoSelect ? "SELECT" : "REVIEW",
    };
  }
}
