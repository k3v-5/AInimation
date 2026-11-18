import { PlanValidationResult, SemanticEditPlan } from "../types/index.js";

/**
 * Validador de planes y motor de auto-reparación determinista (Fase 14).
 */
export class PlanValidatorAndRepair {
  /**
   * Valida un plan de edición y repara automáticamente pequeñas inconsistencias temporales.
   */
  public static validateAndRepair(plan: SemanticEditPlan): PlanValidationResult {
    const issues: string[] = [];
    const repairedScenes = [...plan.scenes];
    let needsRepair = false;

    for (let i = 0; i < repairedScenes.length; i++) {
      const scene = repairedScenes[i];
      if (scene.duration <= 0) {
        issues.push(`Scene #${i} '${scene.id}' has non-positive duration: ${scene.duration}`);
        repairedScenes[i] = { ...scene, duration: 1.5 };
        needsRepair = true;
      }
    }

    // Reajustar tiempos de inicio contiguos
    let currentStart = 0;
    for (let i = 0; i < repairedScenes.length; i++) {
      if (Math.abs(repairedScenes[i].start - currentStart) > 1e-6) {
        issues.push(`Scene #${i} start time misaligned (expected ${currentStart}, got ${repairedScenes[i].start})`);
        repairedScenes[i] = { ...repairedScenes[i], start: currentStart };
        needsRepair = true;
      }
      currentStart += repairedScenes[i].duration;
    }

    const isValid = issues.length === 0;

    return {
      isValid,
      issues,
      repairedPlan: needsRepair ? { ...plan, scenes: repairedScenes } : undefined,
    };
  }
}
