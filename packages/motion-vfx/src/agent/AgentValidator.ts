import { AgentAction } from "./AgentAction.js";
import { AgentPolicy } from "./AgentPolicy.js";

/**
 * Validador de permisos y conformidad de acciones ejecutadas por agentes (Fase 18).
 */
export class AgentValidator {
  public static validateAction(action: AgentAction, policy: AgentPolicy): { allowed: boolean; reason?: string } {
    if (!policy.allowedActionTypes.includes(action.type)) {
      return {
        allowed: false,
        reason: `Action type '${action.type}' is not allowed by current agent policy`,
      };
    }

    if (!policy.allowDestructiveDeletions && (action.type === "remove_layer" || action.type === "delete_project")) {
      return {
        allowed: false,
        reason: `Destructive operation '${action.type}' is forbidden by policy`,
      };
    }

    return { allowed: true };
  }
}
