import { EditingPlan } from "../../ai-planner/types/index.js";
import { UserFeedback } from "../types/index.js";

/**
 * Motor de revisión y replanificación parcial ante retroalimentación humana (Fase 8).
 */
export class RevisionEngine {
  /**
   * Aplica revisiones específicas a un plan de edición basándose en el feedback del usuario.
   */
  public static revise(plan: EditingPlan, feedback: UserFeedback): EditingPlan {
    const revised: EditingPlan = JSON.parse(JSON.stringify(plan));
    revised.version += 1;

    switch (feedback.category) {
      case "audio": {
        if (feedback.instruction.toLowerCase().includes("silence") || feedback.instruction.toLowerCase().includes("no music")) {
          delete revised.audio?.musicAssetId;
        } else if (feedback.instruction.toLowerCase().includes("ducking")) {
          if (revised.audio) revised.audio.enableDucking = true;
        }
        break;
      }
      case "caption": {
        if (feedback.instruction.toLowerCase().includes("karaoke")) {
          if (revised.captions) revised.captions.style = "karaoke";
        } else if (feedback.instruction.toLowerCase().includes("minimal")) {
          if (revised.captions) revised.captions.style = "minimal";
        }
        break;
      }
      case "motion": {
        if (feedback.instruction.toLowerCase().includes("high") || feedback.instruction.toLowerCase().includes("energetic")) {
          revised.style.motionIntensity = "high";
        } else if (feedback.instruction.toLowerCase().includes("low") || feedback.instruction.toLowerCase().includes("calm")) {
          revised.style.motionIntensity = "low";
        }
        break;
      }
      case "visual":
      case "style":
      case "story":
      default:
        // Mantener estructura
        break;
    }

    return revised;
  }
}
