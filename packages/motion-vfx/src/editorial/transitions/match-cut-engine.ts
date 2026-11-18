import crypto from "node:crypto";
import {
  FormalVisualFeatures,
  MatchCutCandidate,
  MatchCutCandidateSchema,
  MatchCutReport,
  MatchCutReportSchema,
  MatchCutType,
  SpatialOffsetCorrection,
} from "../contracts/match-cut.types.js";

export interface ShotWithFeatures {
  id: string;
  name?: string;
  features: FormalVisualFeatures;
}

/**
 * REQ-060 & REQ-061: Cinematic Match Cut Engine.
 * Detects formal geometric, chromatic, kinetic, and auditory similarities across shot transitions.
 */
export class MatchCutEngine {
  public static readonly VIABILITY_THRESHOLD = 70.0;

  /**
   * Evaluates geometric affinity based on shape type and spatial proximity.
   */
  public static calculateGeometricAffinity(
    a: FormalVisualFeatures,
    b: FormalVisualFeatures
  ): number {
    if (!a.primaryShape || !b.primaryShape) {
      return 0.0;
    }

    if (a.primaryShape !== b.primaryShape) {
      return 20.0;
    }

    let score = 85.0;

    // Evaluate spatial center distance
    if (a.shapeCenter && b.shapeCenter) {
      const dx = a.shapeCenter.x - b.shapeCenter.x;
      const dy = a.shapeCenter.y - b.shapeCenter.y;
      const dist = Math.sqrt(dx * dx + dy * dy);
      // Perfect alignment adds up to 15 points
      const proximity = Math.max(0.0, 15.0 * (1.0 - Math.min(1.0, dist / 0.5)));
      score += proximity;
    }

    return Number(Math.min(100.0, Math.max(0.0, score)).toFixed(2));
  }

  /**
   * Evaluates chromatic affinity by circular angular distance on the 0-360 color wheel.
   */
  public static calculateChromaticAffinity(
    a: FormalVisualFeatures,
    b: FormalVisualFeatures
  ): number {
    if (a.dominantColorHue === undefined || b.dominantColorHue === undefined) {
      return 0.0;
    }

    const diff = Math.abs(a.dominantColorHue - b.dominantColorHue);
    const circularDiff = Math.min(diff, 360.0 - diff); // [0, 180] degrees

    // Tolerance window: within 45 degrees yields strong match
    const affinity = Math.max(0.0, 100.0 - (circularDiff / 45.0) * 100.0);
    return Number(Math.min(100.0, affinity).toFixed(2));
  }

  /**
   * Evaluates kinetic affinity based on camera or subject motion vectors and speeds.
   */
  public static calculateKineticAffinity(
    a: FormalVisualFeatures,
    b: FormalVisualFeatures
  ): number {
    if (a.motionVectorDegrees === undefined || b.motionVectorDegrees === undefined) {
      return 0.0;
    }

    const diff = Math.abs(a.motionVectorDegrees - b.motionVectorDegrees);
    const circularDiff = Math.min(diff, 360.0 - diff); // [0, 180] degrees

    // Directional coherence within 35 degrees
    const dirScore = Math.max(0.0, 100.0 - (circularDiff / 35.0) * 100.0);

    let totalKinetic = dirScore;
    if (a.motionSpeed !== undefined && b.motionSpeed !== undefined) {
      const speedDiff = Math.abs(a.motionSpeed - b.motionSpeed);
      const speedScore = Math.max(0.0, 100.0 - speedDiff * 100.0);
      totalKinetic = dirScore * 0.70 + speedScore * 0.30;
    }

    return Number(Math.min(100.0, Math.max(0.0, totalKinetic)).toFixed(2));
  }

  /**
   * Evaluates auditory or sound motif affinity.
   */
  public static calculateSoundAffinity(
    a: FormalVisualFeatures,
    b: FormalVisualFeatures
  ): number {
    if (!a.acousticMotif || !b.acousticMotif) {
      return 0.0;
    }

    const normA = a.acousticMotif.toLowerCase().trim();
    const normB = b.acousticMotif.toLowerCase().trim();

    if (normA === normB) {
      return 95.0;
    }

    const wordsA = normA.split(/\s+/);
    const wordsB = normB.split(/\s+/);
    const hasOverlap = wordsA.some((w) => wordsB.includes(w));

    return hasOverlap ? 75.0 : 15.0;
  }

  /**
   * Computes spatial offset and scale correction factor to align centers of attention at cut point.
   */
  public static calculateSpatialOffset(
    a: FormalVisualFeatures,
    b: FormalVisualFeatures
  ): SpatialOffsetCorrection {
    const centerA = a.shapeCenter ?? { x: 0.5, y: 0.5 };
    const centerB = b.shapeCenter ?? { x: 0.5, y: 0.5 };

    const deltaX = Number((centerA.x - centerB.x).toFixed(4));
    const deltaY = Number((centerA.y - centerB.y).toFixed(4));

    let scaleCorrection = 1.0;
    if (a.shapeRadius && b.shapeRadius && b.shapeRadius > 0.001) {
      scaleCorrection = Number((a.shapeRadius / b.shapeRadius).toFixed(4));
    }

    return {
      deltaX,
      deltaY,
      scaleCorrectionFactor: Math.max(0.1, Math.min(5.0, scaleCorrection)),
    };
  }

  /**
   * Evaluates a potential match cut between two adjacent shots.
   */
  public static evaluateMatchCut(
    outgoingShot: ShotWithFeatures,
    incomingShot: ShotWithFeatures
  ): MatchCutCandidate {
    const geoAffinity = this.calculateGeometricAffinity(outgoingShot.features, incomingShot.features);
    const chromAffinity = this.calculateChromaticAffinity(outgoingShot.features, incomingShot.features);
    const kinAffinity = this.calculateKineticAffinity(outgoingShot.features, incomingShot.features);
    const sndAffinity = this.calculateSoundAffinity(outgoingShot.features, incomingShot.features);

    // Identify primary type and composite score
    const affinities = [
      { type: "GEOMETRIC" as MatchCutType, score: geoAffinity },
      { type: "CHROMATIC" as MatchCutType, score: chromAffinity },
      { type: "KINETIC" as MatchCutType, score: kinAffinity },
      { type: "AUDIO_SEMANTIC" as MatchCutType, score: sndAffinity },
    ].sort((a, b) => b.score - a.score);

    const primary = affinities[0];
    const secondary = affinities[1];

    let matchType: MatchCutType = primary.type;
    let matchScore = primary.score;

    // Composite match if both primary and secondary criteria are high (>= 60)
    if (primary.score >= 60.0 && secondary.score >= 60.0) {
      matchType = "COMPOSITE";
      matchScore = Number((primary.score * 0.60 + secondary.score * 0.40).toFixed(2));
    }

    const isViable = matchScore >= this.VIABILITY_THRESHOLD;
    const spatialOffset = this.calculateSpatialOffset(outgoingShot.features, incomingShot.features);

    let explanation: string;
    if (isViable) {
      explanation = `Viable ${matchType} match cut detected (${matchScore}/100) between '${outgoingShot.id}' and '${incomingShot.id}'.`;
      if (spatialOffset.deltaX !== 0 || spatialOffset.deltaY !== 0) {
        explanation += ` Align incoming shot by [dx: ${spatialOffset.deltaX}, dy: ${spatialOffset.deltaY}].`;
      }
    } else {
      explanation = `Transition between '${outgoingShot.id}' and '${incomingShot.id}' is below match cut threshold (${matchScore} < ${this.VIABILITY_THRESHOLD}). Recommend standard hard cut or L-cut.`;
    }

    const candidate: MatchCutCandidate = {
      id: `match_${outgoingShot.id}_to_${incomingShot.id}`,
      outgoingShotId: outgoingShot.id,
      incomingShotId: incomingShot.id,
      type: matchType,
      matchScore,
      geometricAffinity: geoAffinity,
      chromaticAffinity: chromAffinity,
      kineticAffinity: kinAffinity,
      soundAffinity: sndAffinity,
      spatialOffset,
      explanation,
      isViableMatchCut: isViable,
    };

    return MatchCutCandidateSchema.parse(candidate);
  }

  /**
   * Scans a sequence of contiguous shots for viable match cut opportunities.
   */
  public static scanSequenceForMatchCuts(
    sequenceId: string,
    shots: ShotWithFeatures[]
  ): MatchCutReport {
    const candidates: MatchCutCandidate[] = [];

    for (let i = 0; i < shots.length - 1; i++) {
      const candidate = this.evaluateMatchCut(shots[i], shots[i + 1]);
      candidates.push(candidate);
    }

    const viableMatchesCount = candidates.filter((c) => c.isViableMatchCut).length;

    const hashPayload = JSON.stringify({
      sequenceId,
      totalPairsEvaluated: candidates.length,
      viableMatchesCount,
      candidates: candidates.map((c) => ({
        id: c.id,
        score: c.matchScore,
        viable: c.isViableMatchCut,
      })),
    });

    const checksumSha256 = crypto.createHash("sha256").update(hashPayload).digest("hex");

    const report: MatchCutReport = {
      sequenceId,
      totalPairsEvaluated: candidates.length,
      viableMatchesCount,
      candidates,
      checksumSha256,
    };

    return MatchCutReportSchema.parse(report);
  }
}
