import { GraphicsPlan } from "../../ai-planner/types/index.js";
import { AgentContext, AgentProposal, EditingAgent } from "../types/index.js";

/**
 * Agente especialista en gráficos procedurales, animaciones cinéticas y presupuesto de movimiento (Fase 8).
 */
export class MotionAgent implements EditingAgent {
  public readonly id = "agent_motion_01";
  public readonly role = "motion" as const;

  public async analyze(context: AgentContext): Promise<AgentProposal> {
    const graphicsPlan: GraphicsPlan = {
      elements: [
        {
          id: "callout_hook",
          type: "badge",
          purpose: "Emphasize key topic at start",
          start: 0.5,
          duration: 2.5,
          parameters: { text: "IMPORTANTE" },
        },
      ],
    };

    return {
      agentId: this.id,
      role: this.role,
      confidence: 0.88,
      recommendations: [
        {
          type: "define_graphics",
          priority: 3,
          reasoning: "Added attention badge graphic in the opening hook section.",
          parameters: { graphics: graphicsPlan },
        },
      ],
    };
  }
}
