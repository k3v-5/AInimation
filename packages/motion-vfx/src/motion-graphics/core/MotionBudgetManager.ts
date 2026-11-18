import { MotionBudgetType, MotionComplexityResult } from "../types/index.js";

/**
 * Gestor de presupuesto cinético y medidor de complejidad visual (Fase 11).
 */
export class MotionBudgetManager {
  /**
   * Calcula la puntuación de complejidad de una escena y valida si respeta el presupuesto asignado.
   */
  public static evaluateComplexity(
    elementsCount: number,
    animatedPropertiesCount: number,
    hasCameraDynamics: boolean,
    hasParticles: boolean,
    budget: MotionBudgetType = "medium"
  ): MotionComplexityResult {
    let rawScore =
      elementsCount * 0.05 +
      animatedPropertiesCount * 0.03 +
      (hasCameraDynamics ? 0.2 : 0) +
      (hasParticles ? 0.25 : 0);

    const score = Math.max(0, Math.min(1.0, Math.round(rawScore * 100) / 100));

    let maxAllowed = 0.7;
    if (budget === "low") maxAllowed = 0.4;
    if (budget === "high") maxAllowed = 1.0;

    return {
      score,
      budget,
      isWithinBudget: score <= maxAllowed,
      activeElementsCount: elementsCount,
    };
  }
}
