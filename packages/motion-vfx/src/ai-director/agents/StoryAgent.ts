import { EditorialSection } from "../../ai-planner/types/index.js";
import { AgentContext, AgentProposal, EditingAgent } from "../types/index.js";

/**
 * Agente especialista en narrativa, estructura, retención y ritmo editorial (Fase 8).
 */
export class StoryAgent implements EditingAgent {
  public readonly id = "agent_story_01";
  public readonly role = "story" as const;

  public async analyze(context: AgentContext): Promise<AgentProposal> {
    const duration = context.brief.targetDuration;
    const isShortForm = context.brief.platform === "tiktok" || context.brief.platform === "youtube-shorts";

    const hookDuration = isShortForm ? Math.min(3.0, duration * 0.1) : 5.0;
    const ctaDuration = Math.min(5.0, duration * 0.15);
    const mainDuration = duration - hookDuration - ctaDuration;

    const sections: EditorialSection[] = [
      {
        id: "sec_hook",
        type: "hook",
        start: 0,
        end: hookDuration,
        objective: "Capture viewer attention in first seconds",
        energy: 1.0,
      },
      {
        id: "sec_main",
        type: "main-point",
        start: hookDuration,
        end: hookDuration + mainDuration,
        objective: context.brief.objective,
        energy: 0.8,
      },
      {
        id: "sec_cta",
        type: "cta",
        start: hookDuration + mainDuration,
        end: duration,
        objective: "Encourage user action and subscription",
        energy: 0.9,
      },
    ];

    return {
      agentId: this.id,
      role: this.role,
      confidence: 0.95,
      recommendations: [
        {
          type: "define_sections",
          priority: 1,
          reasoning: "Established 3-act viral narrative structure optimized for platform retention.",
          parameters: { sections },
        },
      ],
    };
  }
}
