import { CaptionPlan } from "../../ai-planner/types/index.js";
import { AgentContext, AgentProposal, EditingAgent } from "../types/index.js";

/**
 * Agente especialista en subtítulos cinemáticos, ritmo y resaltado de palabras (Fase 8).
 */
export class CaptionAgent implements EditingAgent {
  public readonly id = "agent_caption_01";
  public readonly role = "caption" as const;

  public async analyze(context: AgentContext): Promise<AgentProposal> {
    const captionPlan: CaptionPlan = {
      style: context.style.captionStyle || "word-pop",
      segments: [
        {
          text: context.brief.objective,
          start: 0.0,
          end: Math.min(4.0, context.brief.targetDuration),
          isEmphasized: true,
        },
      ],
    };

    return {
      agentId: this.id,
      role: this.role,
      confidence: 0.94,
      recommendations: [
        {
          type: "define_captions",
          priority: 3,
          reasoning: "Generated kinetic captions styled for social media engagement.",
          parameters: { captions: captionPlan },
        },
      ],
    };
  }
}
