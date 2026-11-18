import crypto from "crypto";
import { EditorialProfile } from "../contracts/content-profile.types.js";
import { ProductionIntent } from "../contracts/production-intent.types.js";
import {
  ControlLevel,
  EditorialAction,
  EditorialAlternative,
  EditorialDecisionGraph,
  EditorialDecisionGraphSchema,
  EditorialDecisionNode,
  EditorialDecisionNodeSchema,
  EditorialScore,
  EditorialScoreSchema,
} from "../contracts/decision-graph.types.js";
import { ProjectKnowledgeGraph } from "../contracts/knowledge-graph.types.js";
import { canOverrideRule, RulePriorityTier } from "../contracts/rule-precedence.types.js";

export interface EditorialCandidateSegment {
  assetId: string;
  startSeconds: number;
  durationSeconds: number;
  isTalkingHead: boolean;
  isDramaticPause?: boolean;
  hasClaimCitation?: boolean;
  claimId?: string;
  hasEditorLock?: boolean;
  lockedAction?: EditorialAction;
  rawConfidence?: number;
  proposedAction: EditorialAction;
  reason: string;
  narrativeEffect: string;
}

/**
 * REQ-003, REQ-031, REQ-032, REQ-033, REQ-076:
 * Master Editorial Director Engine.
 * Evaluates editorial candidates, computes multi-dimensional EditorialScores,
 * enforces rule precedence hierarchy, and produces auditable, explainable decision graphs.
 */
export class EditorialDirectorEngine {
  /**
   * Evaluates a candidate segment and computes its multidimensional EditorialScore.
   */
  public static computeScore(params: {
    narrativeValue: number;
    emotionalValue: number;
    informationValue: number;
    visualValue: number;
    audioValue: number;
    redundancyPenalty: number;
    continuityScore: number;
  }): EditorialScore {
    const n = Math.min(1.0, Math.max(0.0, params.narrativeValue));
    const e = Math.min(1.0, Math.max(0.0, params.emotionalValue));
    const i = Math.min(1.0, Math.max(0.0, params.informationValue));
    const v = Math.min(1.0, Math.max(0.0, params.visualValue));
    const a = Math.min(1.0, Math.max(0.0, params.audioValue));
    const r = Math.min(1.0, Math.max(0.0, params.redundancyPenalty));
    const c = Math.min(1.0, Math.max(0.0, params.continuityScore));

    const weightedSum =
      0.25 * n +
      0.20 * e +
      0.20 * i +
      0.15 * v +
      0.10 * a +
      0.10 * c -
      0.15 * r;

    const overallScore = Math.min(100.0, Math.max(0.0, weightedSum * 100.0));

    return EditorialScoreSchema.parse({
      narrativeValue: n,
      emotionalValue: e,
      informationValue: i,
      visualValue: v,
      audioValue: a,
      redundancyPenalty: r,
      continuityScore: c,
      overallScore: Number(overallScore.toFixed(2)),
    });
  }

  /**
   * Plans decisions for a sequence of candidates, producing an explainable EditorialDecisionGraph.
   */
  public static planDecisions(params: {
    projectId: string;
    intent: ProductionIntent;
    profile: EditorialProfile;
    candidates: EditorialCandidateSegment[];
    knowledgeGraph?: ProjectKnowledgeGraph;
    deterministicTimestamp?: string;
  }): EditorialDecisionGraph {
    const { projectId, profile, candidates } = params;
    const decisions: EditorialDecisionNode[] = [];

    for (let i = 0; i < candidates.length; i++) {
      const candidate = candidates[i];
      const decision = this.evaluateCandidate({
        candidate,
        profile,
        index: i,
        knowledgeGraph: params.knowledgeGraph,
      });
      decisions.push(decision);
    }

    const createdAt = params.deterministicTimestamp ?? "2026-09-02T00:00:00.000Z";
    const graphContent = JSON.stringify({
      projectId,
      profileName: profile.name,
      decisions,
      createdAt,
    });

    const checksum = crypto.createHash("sha256").update(graphContent).digest("hex");

    const graph: EditorialDecisionGraph = {
      projectId,
      profileName: profile.name,
      decisions,
      checksum,
      createdAt,
    };

    return EditorialDecisionGraphSchema.parse(graph);
  }

  /**
   * Evaluates a single candidate enforcing REQ-076 Rule Precedence.
   */
  private static evaluateCandidate(params: {
    candidate: EditorialCandidateSegment;
    profile: EditorialProfile;
    index: number;
    knowledgeGraph?: ProjectKnowledgeGraph;
  }): EditorialDecisionNode {
    const { candidate, profile, index } = params;

    let tier: RulePriorityTier = "OPTIMIZATION";
    let action = candidate.proposedAction;
    let controlLevel: ControlLevel = "AUTO";
    let reason = candidate.reason;
    let narrativeEffect = candidate.narrativeEffect;
    let confidence = candidate.rawConfidence ?? 0.95;
    const alternatives: EditorialAlternative[] = [];

    // 1. Check for Human EDITOR_LOCK (Tier 700)
    if (candidate.hasEditorLock) {
      tier = "EDITOR_LOCK";
      controlLevel = "LOCKED_BY_EDITOR";
      action = candidate.lockedAction ?? "KEEP";
      reason = "Protected by explicit human editor lock.";
      narrativeEffect = "Preserve human artistic intent.";
      confidence = 1.0;
      if (candidate.proposedAction !== action) {
        alternatives.push({
          action: candidate.proposedAction,
          score: 50,
          rejectionReason: "Blocked by EDITOR_LOCK precedence hierarchy (REQ-076).",
        });
      }
    }
    // 2. Check for LEGAL_FACTUAL claim protection (Tier 800)
    else if (candidate.hasClaimCitation || candidate.claimId) {
      tier = "LEGAL_FACTUAL";
      action = "KEEP";
      reason = "Verified factual claim requires on-screen presence.";
      narrativeEffect = "Ensure factual accuracy and journalistic integrity.";
      confidence = 0.98;
      if (candidate.proposedAction === "CUT") {
        alternatives.push({
          action: "CUT",
          score: 20,
          rejectionReason: "Factual evidence cannot be pruned per LEGAL_FACTUAL tier (REQ-076).",
        });
      }
    }
    // 3. Check for Dramatic Silence in Documentary Profile (Tier NARRATIVE 600)
    else if (candidate.isDramaticPause && profile.silencePolicy.preserveDramaticPauses) {
      tier = "NARRATIVE";
      action = profile.silencePolicy.roomToneReplacement ? "REPLACE_WITH_ROOM_TONE" : "HOLD_SILENCE";
      reason = `Preserving dramatic pause in ${profile.name} to allow narrative gravity.`;
      narrativeEffect = "Deepen audience reflection and emotional tension.";
      confidence = 0.92;
      alternatives.push({
        action: "TRIM_SILENCE",
        score: 60,
        rejectionReason: "Aggressive trim rejected to honor documentary pause policy.",
      });
    }
    // 4. Check for Dynamic Punch-in constraints in serious genres
    else if (candidate.proposedAction === "PUNCH_IN" && !profile.shotGrammarPolicy.allowDynamicPunchIn) {
      tier = "STYLE";
      action = "KEEP";
      reason = `Dynamic punch-in rejected: prohibited by ${profile.name} shot grammar.`;
      narrativeEffect = "Preserve sober framing stability.";
      confidence = 0.95;
      alternatives.push({
        action: "PUNCH_IN",
        score: 40,
        rejectionReason: "Punch-in not permitted for this genre.",
      });
    }

    // Confidence-aware control level adjustment (REQ-033)
    if (controlLevel !== "LOCKED_BY_EDITOR") {
      if (confidence < 0.70) {
        controlLevel = "SUGGEST";
      } else {
        controlLevel = "AUTO";
      }
    }

    const score = this.computeScore({
      narrativeValue: tier === "NARRATIVE" || tier === "EDITOR_LOCK" ? 0.95 : 0.80,
      emotionalValue: candidate.isDramaticPause ? 0.90 : 0.70,
      informationValue: candidate.hasClaimCitation ? 0.98 : 0.75,
      visualValue: 0.85,
      audioValue: 0.90,
      redundancyPenalty: 0.05,
      continuityScore: 0.92,
    });

    const decisionId = `dec_${index}_${crypto
      .createHash("sha256")
      .update(`${candidate.assetId}_${candidate.startSeconds}_${action}`)
      .digest("hex")
      .substring(0, 12)}`;

    const node: EditorialDecisionNode = {
      decisionId,
      timestampSeconds: candidate.startSeconds,
      durationSeconds: candidate.durationSeconds,
      action,
      targetAssetId: candidate.assetId,
      tier,
      reason,
      confidence,
      narrativeEffect,
      score,
      controlLevel,
      alternativesConsidered: alternatives,
    };

    return EditorialDecisionNodeSchema.parse(node);
  }
}
