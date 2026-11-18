import { ContentModel, DecisionLogEntry, PacingProfileType, PlannedScene, SemanticEditPlan } from "../types/index.js";
import { StoryAndPacingPlanner } from "./StoryAndPacingPlanner.js";

/**
 * Planificador editorial semántico de alto nivel (*AI Director Planner*) (Fase 14).
 */
export class SemanticEditPlanner {
  /**
   * Genera el plan de edición semántico a partir del ContentModel y el perfil de ritmo.
   */
  public static generatePlan(
    content: ContentModel,
    pacing: PacingProfileType = "fast_social"
  ): SemanticEditPlan {
    const shotDurations = StoryAndPacingPlanner.planShotDurations(content.totalDuration, pacing);
    const scenes: PlannedScene[] = [];
    const decisionLog: DecisionLogEntry[] = [];
    let currentTime = 0;

    const roles: PlannedScene["role"][] = ["hook", "context", "problem", "explanation", "reveal", "cta"];

    for (let i = 0; i < shotDurations.length; i++) {
      const dur = shotDurations[i];
      const role = roles[Math.min(i, roles.length - 1)];
      const isBRoll = i > 0 && i % 2 === 1;

      scenes.push({
        id: `scene_${i}`,
        role,
        start: currentTime,
        duration: dur,
        shotType: isBRoll ? "b_roll" : "talking_head",
        brollKeyword: isBRoll ? content.primaryTopic.toLowerCase() : undefined,
      });

      decisionLog.push({
        time: currentTime,
        action: `Assign shot #${i} as ${role} (${isBRoll ? "B-roll" : "Talking Head"})`,
        reason: `Pacing profile '${pacing}' allocated ${dur}s for narrative stage '${role}'.`,
        confidence: 0.92,
      });

      currentTime += dur;
    }

    return {
      id: `plan_${Date.now()}`,
      pacingProfile: pacing,
      scenes,
      decisionLog,
      parameters: { totalDuration: content.totalDuration },
    };
  }
}
