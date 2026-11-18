import { PlanPatch, SemanticEditPlan } from "../types/index.js";

/**
 * Aplicador de parches de edición iterativa (*Plan Patcher*) (Fase 14).
 */
export class IterativePlanPatcher {
  /**
   * Aplica un parche delta a un plan de edición existente.
   */
  public static applyPatch(plan: SemanticEditPlan, patch: PlanPatch): SemanticEditPlan {
    const updated = { ...plan };

    if (patch.target === "scenes" && typeof patch.changes.durationMultiplier === "number") {
      const mult = patch.changes.durationMultiplier;
      let currentStart = 0;
      updated.scenes = plan.scenes.map((s) => {
        const newDur = Math.round(s.duration * mult * 100) / 100;
        const scene = { ...s, start: currentStart, duration: newDur };
        currentStart += newDur;
        return scene;
      });
    }

    if (patch.target === "pacingProfile" && typeof patch.changes.pacingProfile === "string") {
      updated.pacingProfile = patch.changes.pacingProfile as any;
    }

    return updated;
  }
}
