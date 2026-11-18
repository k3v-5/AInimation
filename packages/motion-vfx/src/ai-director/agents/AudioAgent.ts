import { AudioPlan, SFXPlan } from "../../ai-planner/types/index.js";
import { AgentContext, AgentProposal, EditingAgent } from "../types/index.js";

/**
 * Agente especialista en audio, selección de música, auto-ducking y efectos de sonido (Fase 8).
 */
export class AudioAgent implements EditingAgent {
  public readonly id = "agent_audio_01";
  public readonly role = "audio" as const;

  public async analyze(context: AgentContext): Promise<AgentProposal> {
    const sfx: SFXPlan[] = [
      { id: "sfx_hook", type: "impact", time: 0.1, volume: 0.8 },
      { id: "sfx_trans_1", type: "whoosh", time: 3.0, volume: 0.6 },
    ];

    const audioPlan: AudioPlan = {
      musicAssetId: "audio_bg_music_track",
      musicVolume: 0.35,
      enableDucking: true,
      soundEffects: sfx,
    };

    return {
      agentId: this.id,
      role: this.role,
      confidence: 0.9,
      recommendations: [
        {
          type: "define_audio",
          priority: 2,
          reasoning: "Selected upbeat background music and inserted transition sound effects.",
          parameters: { audio: audioPlan },
        },
      ],
    };
  }
}
