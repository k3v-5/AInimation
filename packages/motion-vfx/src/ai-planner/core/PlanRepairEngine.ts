import { EditingPlan } from "../types/index.js";

/**
 * Motor de autoreparación determinista para planes generados por IA (Fase 7).
 */
export class PlanRepairEngine {
  /**
   * Aplica reparaciones y normalizaciones deterministas a un plan de edición.
   */
  public static repair(plan: EditingPlan): EditingPlan {
    const repaired: EditingPlan = JSON.parse(JSON.stringify(plan));

    // 1. Reparar targetDuration
    if (repaired.brief.targetDuration <= 0) {
      repaired.brief.targetDuration = 30.0;
    }

    // 2. Reparar secciones invertidas y asegurar orden temporal
    for (const section of repaired.sections) {
      if (section.start > section.end) {
        const tmp = section.start;
        section.start = section.end;
        section.end = tmp;
      }
      if (section.start < 0) section.start = 0;
      if (section.end === section.start) section.end = section.start + 1.0;
    }

    // 3. Reparar tomas de escenas
    for (const scene of repaired.scenes) {
      if (scene.start > scene.end) {
        const tmp = scene.start;
        scene.start = scene.end;
        scene.end = tmp;
      }

      for (const shot of scene.shots) {
        if (shot.duration <= 0) {
          shot.duration = 2.0; // Duración por defecto
        }
        if (!shot.transition) {
          shot.transition = {
            type: repaired.style.defaultTransition || "cut",
            duration: 0.3,
          };
        }
      }
    }

    return repaired;
  }
}
