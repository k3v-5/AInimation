import { Framing, ScenePlan, ShotPlan } from "../../ai-planner/types/index.js";
import { BrollRanker } from "../../media-intelligence/core/BrollRanker.js";
import { AgentContext, AgentProposal, EditingAgent } from "../types/index.js";

/**
 * Agente especialista en tomas visuales, B-roll, encuadres y variedad visual (Fase 8).
 */
export class VisualAgent implements EditingAgent {
  public readonly id = "agent_visual_01";
  public readonly role = "visual" as const;

  public async analyze(context: AgentContext): Promise<AgentProposal> {
    const sections = (context.existingPlan?.sections as any[]) ?? [];
    const scenes: ScenePlan[] = [];
    const framings: Framing[] = ["close", "medium", "wide", "overhead"];

    let shotIdx = 0;

    for (const section of sections) {
      const sectionDuration = section.end - section.start;
      const shotCount = Math.max(1, Math.round(sectionDuration / 3.0));
      const shotDuration = sectionDuration / shotCount;

      const shots: ShotPlan[] = [];
      for (let i = 0; i < shotCount; i++) {
        const framing = framings[shotIdx % framings.length];
        const shotStart = section.start + i * shotDuration;

        let selectedAssetId = "broll_default";
        if (context.availableAssets && context.availableAssets.length > 0) {
          const ranked = BrollRanker.rankCandidates(context.availableAssets);
          if (ranked.length > 0) {
            selectedAssetId = ranked[shotIdx % ranked.length].assetId;
          }
        }

        shots.push({
          id: `shot_${section.id}_${i}`,
          assetId: selectedAssetId,
          purpose: `Visual for ${section.type} part ${i + 1}`,
          start: shotStart,
          duration: shotDuration,
          framing,
          transition: {
            type: context.style.defaultTransition || "cut",
            duration: 0.3,
          },
        });

        shotIdx++;
      }

      scenes.push({
        id: `sc_${section.id}`,
        sectionId: section.id,
        purpose: `Scene for ${section.type}`,
        start: section.start,
        end: section.end,
        shots,
      });
    }

    return {
      agentId: this.id,
      role: this.role,
      confidence: 0.92,
      recommendations: [
        {
          type: "define_scenes",
          priority: 2,
          reasoning: "Constructed visual scenes and shots with alternating framings for variety.",
          parameters: { scenes },
        },
      ],
    };
  }
}
