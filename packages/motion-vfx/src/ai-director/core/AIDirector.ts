import { EditingPlan } from "../../ai-planner/types/index.js";
import { PlanRepairEngine } from "../../ai-planner/core/PlanRepairEngine.js";
import { PlanValidator } from "../../ai-planner/core/PlanValidator.js";
import { BuiltinStyleProfiles } from "../../ai-planner/presets/StyleProfiles.js";
import { AudioAgent } from "../agents/AudioAgent.js";
import { CaptionAgent } from "../agents/CaptionAgent.js";
import { MotionAgent } from "../agents/MotionAgent.js";
import { StoryAgent } from "../agents/StoryAgent.js";
import { VisualAgent } from "../agents/VisualAgent.js";
import {
  AgentContext,
  CreativeBrief,
  DecisionLogEntry,
  PlanningSession,
  PlanningState,
} from "../types/index.js";

/**
 * Director de Inteligencia Artificial que orquesta la colaboración multi-agente (Fase 8).
 */
export class AIDirector {
  private storyAgent = new StoryAgent();
  private visualAgent = new VisualAgent();
  private audioAgent = new AudioAgent();
  private captionAgent = new CaptionAgent();
  private motionAgent = new MotionAgent();

  /**
   * Ejecuta una sesión completa de dirección y planificación multi-agente.
   */
  public async directSession(
    brief: CreativeBrief,
    options: { sessionId?: string; availableAssets?: any[]; transcript?: any } = {}
  ): Promise<PlanningSession> {
    const sessionId = options.sessionId ?? `session_${Date.now()}`;
    const traceId = `trace_${sessionId}`;
    const style = BuiltinStyleProfiles[brief.styleId ?? "fast-tiktok"] ?? BuiltinStyleProfiles["fast-tiktok"];

    const decisions: DecisionLogEntry[] = [];
    const now = new Date().toISOString();

    const context: AgentContext = {
      brief,
      style,
      transcript: options.transcript,
      availableAssets: options.availableAssets,
    };

    // 1. Ronda 1: Story Agent define la estructura narrativa
    const storyProposal = await this.storyAgent.analyze(context);
    const sections = storyProposal.recommendations[0].parameters.sections as any;
    decisions.push({
      agentId: this.storyAgent.id,
      action: "define_sections",
      reasoning: storyProposal.recommendations[0].reasoning,
      timestamp: now,
    });

    context.existingPlan = { sections };

    // 2. Ronda 2: Visual, Audio, Caption y Motion Agents generan sus propuestas en paralelo
    const [visualProposal, audioProposal, captionProposal, motionProposal] = await Promise.all([
      this.visualAgent.analyze(context),
      this.audioAgent.analyze(context),
      this.captionAgent.analyze(context),
      this.motionAgent.analyze(context),
    ]);

    const scenes = visualProposal.recommendations[0].parameters.scenes as any;
    const audio = audioProposal.recommendations[0].parameters.audio as any;
    const captions = captionProposal.recommendations[0].parameters.captions as any;
    const graphics = motionProposal.recommendations[0].parameters.graphics as any;

    decisions.push({
      agentId: this.visualAgent.id,
      action: "define_scenes",
      reasoning: visualProposal.recommendations[0].reasoning,
      timestamp: now,
    });
    decisions.push({
      agentId: this.audioAgent.id,
      action: "define_audio",
      reasoning: audioProposal.recommendations[0].reasoning,
      timestamp: now,
    });

    // 3. Ensamblar EditingPlan provisional
    let rawPlan: EditingPlan = {
      id: `plan_${sessionId}`,
      version: 1,
      brief,
      style,
      sections,
      scenes,
      captions,
      graphics,
      audio,
    };

    // 4. Validar y Auto-Reparar deterministamente
    const validatedPlan = PlanRepairEngine.repair(rawPlan);
    PlanValidator.assertValid(validatedPlan);

    return {
      id: sessionId,
      traceId,
      state: "approved",
      brief,
      style,
      plan: validatedPlan,
      decisions,
      conflicts: [],
    };
  }
}
