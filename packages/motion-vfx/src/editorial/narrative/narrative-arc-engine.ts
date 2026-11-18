import crypto from "crypto";
import {
  CANONICAL_BEAT_ENERGY_TARGETS,
  DocumentaryBeatType,
  NarrativeArcPlan,
  NarrativeArcPlanSchema,
  NarrativeBeatNode,
  NarrativeCausalityEdge,
  RevealConstraint,
} from "../contracts/narrative.types.js";
import { SceneEntity } from "../contracts/knowledge-graph.types.js";

/**
 * REQ-008, REQ-044 & REQ-045: Documentary Narrative Arc Engine.
 * Structures the narrative into 10 canonical beats, enforces causality constraints,
 * prevents premature information reveals, and computes continuous energy curves.
 */
export class NarrativeArcEngine {
  private static readonly CANONICAL_ORDER: DocumentaryBeatType[] = [
    "HOOK",
    "CONTEXT",
    "QUESTION",
    "EVIDENCE",
    "TESTIMONY",
    "CONFLICT",
    "ESCALATION",
    "REVELATION",
    "RESOLUTION",
    "REFLECTION",
  ];

  /**
   * Builds a complete NarrativeArcPlan from project scenes and narrative constraints.
   */
  public static buildPlan(params: {
    projectId: string;
    scenes: SceneEntity[];
    totalDurationSeconds?: number;
    causalityEdges?: NarrativeCausalityEdge[];
    revealConstraints?: RevealConstraint[];
    customBeats?: NarrativeBeatNode[];
  }): NarrativeArcPlan {
    const { projectId, scenes } = params;
    const causalityEdges = params.causalityEdges ?? [];
    const revealConstraints = params.revealConstraints ?? [];

    let beats: NarrativeBeatNode[] = [];

    if (params.customBeats && params.customBeats.length > 0) {
      beats = [...params.customBeats].sort(
        (a, b) => a.timelineStartSeconds - b.timelineStartSeconds
      );
    } else {
      // Automatically distribute scenes into canonical 10 beats or map scenes
      const totalScenes = Math.max(1, scenes.length);
      const totalDuration =
        params.totalDurationSeconds ??
        (scenes.reduce((acc, s) => acc + (s.estimatedDurationSeconds ?? 60.0), 0) || 300.0);

      let currentTime = 0.0;
      beats = this.CANONICAL_ORDER.map((beatType, idx) => {
        const sceneIndex = Math.min(idx, totalScenes - 1);
        const scene = scenes[sceneIndex];
        const sceneId = scene ? scene.id : `scene_${idx + 1}`;
        const sceneTitle = scene ? scene.name : `Beat ${beatType}`;

        // Allocate proportional duration
        const beatDuration = totalDuration / this.CANONICAL_ORDER.length;
        const start = currentTime;
        const end = currentTime + beatDuration;
        currentTime = end;

        const targetEnergy = CANONICAL_BEAT_ENERGY_TARGETS[beatType];
        // actual energy adapts slightly based on scene importance
        const sceneImportance = scene?.narrativeImportance ?? 0.5;
        const actualEnergy = Math.max(
          0.0,
          Math.min(1.0, targetEnergy * 0.8 + sceneImportance * 0.2)
        );

        return {
          id: `beat_${beatType.toLowerCase()}_${idx + 1}`,
          beat: beatType,
          sceneId,
          title: sceneTitle,
          targetDurationSeconds: beatDuration,
          actualDurationSeconds: beatDuration,
          timelineStartSeconds: start,
          timelineEndSeconds: end,
          targetEnergyLevel: targetEnergy,
          actualEnergyLevel: Number(actualEnergy.toFixed(4)),
          claimIds: [],
          causalDependencies: idx > 0 ? [`beat_${this.CANONICAL_ORDER[idx - 1].toLowerCase()}_${idx}`] : [],
          prohibitedRevealItemIds: [],
        };
      });
    }

    const computedTotalDuration =
      beats.length > 0 ? beats[beats.length - 1].timelineEndSeconds : 0.0;

    // Generate discrete energy sample points (every 2 seconds)
    const energyPoints: { timestampSeconds: number; energy: number }[] = [];
    const step = 2.0;
    for (let t = 0.0; t <= computedTotalDuration; t += step) {
      energyPoints.push({
        timestampSeconds: Number(t.toFixed(2)),
        energy: this.evaluateEnergyAtTime(beats, t),
      });
    }

    const payloadForHash = JSON.stringify({
      projectId,
      totalDuration: computedTotalDuration,
      beats: beats.map((b) => ({ id: b.id, beat: b.beat, start: b.timelineStartSeconds, end: b.timelineEndSeconds })),
      causalityEdges,
      revealConstraints,
    });

    const checksumSha256 = crypto
      .createHash("sha256")
      .update(payloadForHash)
      .digest("hex");

    return NarrativeArcPlanSchema.parse({
      projectId,
      totalDurationSeconds: computedTotalDuration,
      beats,
      causalityEdges,
      revealConstraints,
      energyPoints,
      checksumSha256,
    });
  }

  /**
   * Evaluates interpolated narrative energy at timestamp t.
   */
  public static evaluateEnergyAtTime(beats: NarrativeBeatNode[], timestampSeconds: number): number {
    if (beats.length === 0) return 0.5;
    if (timestampSeconds <= beats[0].timelineStartSeconds) return beats[0].actualEnergyLevel;
    if (timestampSeconds >= beats[beats.length - 1].timelineEndSeconds) {
      return beats[beats.length - 1].actualEnergyLevel;
    }

    // Find active beat or interpolate between adjacent beats
    for (let i = 0; i < beats.length; i++) {
      const beat = beats[i];
      if (timestampSeconds >= beat.timelineStartSeconds && timestampSeconds < beat.timelineEndSeconds) {
        const beatProgress =
          (timestampSeconds - beat.timelineStartSeconds) /
          Math.max(0.001, beat.timelineEndSeconds - beat.timelineStartSeconds);

        const nextEnergy =
          i < beats.length - 1 ? beats[i + 1].actualEnergyLevel : beat.actualEnergyLevel;

        // Smooth cosine interpolation between current and next beat energy
        const blend = 0.5 * (1 - Math.cos(beatProgress * Math.PI));
        const val = beat.actualEnergyLevel * (1 - blend) + nextEnergy * blend;
        return Number(Math.max(0.0, Math.min(1.0, val)).toFixed(4));
      }
    }

    return beats[beats.length - 1].actualEnergyLevel;
  }

  /**
   * REQ-044: Validates causal dependencies. Ensures predecessor beats precede successor beats.
   */
  public static validateCausality(plan: NarrativeArcPlan): {
    valid: boolean;
    violations: string[];
  } {
    const violations: string[] = [];
    const beatMap = new Map<string, NarrativeBeatNode>();
    for (const b of plan.beats) {
      beatMap.set(b.id, b);
    }

    for (const edge of plan.causalityEdges) {
      const fromBeat = beatMap.get(edge.fromBeatId);
      const toBeat = beatMap.get(edge.toBeatId);

      if (!fromBeat) {
        violations.push(`Causality edge from non-existent beat: '${edge.fromBeatId}'`);
        continue;
      }
      if (!toBeat) {
        violations.push(`Causality edge to non-existent beat: '${edge.toBeatId}'`);
        continue;
      }

      if (edge.strict && fromBeat.timelineEndSeconds > toBeat.timelineStartSeconds) {
        violations.push(
          `Causality inversion: '${fromBeat.title}' (${fromBeat.timelineEndSeconds.toFixed(1)}s) ` +
          `must strictly precede '${toBeat.title}' (${toBeat.timelineStartSeconds.toFixed(1)}s). Reason: ${edge.reason}`
        );
      }
    }

    return {
      valid: violations.length === 0,
      violations,
    };
  }

  /**
   * REQ-045: Validates reveal constraints against clip timeline placements.
   * Ensures critical elements are not revealed prematurely before their allowed beat.
   */
  public static validateRevealConstraints(
    plan: NarrativeArcPlan,
    occurrences: { clipId: string; itemId: string; timestampSeconds: number }[]
  ): { valid: boolean; violations: string[] } {
    const violations: string[] = [];
    const beatTypeOrder = this.CANONICAL_ORDER;

    for (const constraint of plan.revealConstraints) {
      const allowedBeatIndex = beatTypeOrder.indexOf(constraint.prohibitedBeforeBeat);
      if (allowedBeatIndex === -1) continue;

      // Find the earliest beat where this beatType begins
      const matchingBeat = plan.beats.find((b) => b.beat === constraint.prohibitedBeforeBeat);
      const earliestAllowedTimestamp = matchingBeat ? matchingBeat.timelineStartSeconds : 0.0;

      for (const occ of occurrences) {
        if (occ.itemId === constraint.itemId && occ.timestampSeconds < earliestAllowedTimestamp - 0.001) {
          violations.push(
            `Premature reveal: Item '${constraint.itemId}' (${constraint.description}) ` +
            `appears at ${occ.timestampSeconds.toFixed(1)}s before allowed beat '${constraint.prohibitedBeforeBeat}' ` +
            `which starts at ${earliestAllowedTimestamp.toFixed(1)}s`
          );
        }
      }
    }

    return {
      valid: violations.length === 0,
      violations,
    };
  }
}
