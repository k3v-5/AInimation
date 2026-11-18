import crypto from "crypto";
import {
  CitationCard,
  CitationCardSchema,
  ClaimAuditResult,
  EvidenceAuditReport,
  EvidenceAuditReportSchema,
} from "../contracts/evidence.types.js";
import { ClaimEntity } from "../contracts/knowledge-graph.types.js";

/**
 * REQ-009 & REQ-010: Fact & Evidence Layer Engine.
 * Audits assertions, computes evidentiary integrity scores, and compiles on-screen citation cards.
 */
export class EvidenceEngine {
  /**
   * Audits all claims in a project, verifying source backing and generating citation cards.
   */
  public static auditEvidence(params: {
    projectId: string;
    claims: ClaimEntity[];
    claimTimings?: Record<string, { startSeconds: number; durationSeconds: number }>;
  }): EvidenceAuditReport {
    const { projectId, claims } = params;
    const claimTimings = params.claimTimings ?? {};

    const audits: ClaimAuditResult[] = [];
    const citationCards: CitationCard[] = [];

    let verifiedCount = 0;
    let unverifiedCount = 0;
    let missingSourceCount = 0;

    for (const claim of claims) {
      const hasEvidence = claim.evidenceAssetIds.length > 0;
      const hasCitation = Boolean(claim.sourceCitation && claim.sourceCitation.trim().length > 0);
      const requiresCitation = claim.requiresOnScreenCitation ?? false;

      let status = claim.status;
      let blockingIssue = false;
      let notes = "";

      if (requiresCitation && !hasCitation) {
        status = "MISSING_SOURCE";
        missingSourceCount++;
        blockingIssue = true;
        notes = "Claim marked as requiring on-screen citation, but sourceCitation is empty.";
      } else if (hasEvidence && hasCitation) {
        status = "VERIFIED";
        verifiedCount++;
        notes = "Claim is fully backed by evidence asset(s) and valid citation.";
      } else if (status === "CONTRADICTED") {
        blockingIssue = true;
        notes = "Claim is marked as contradicted by evidence.";
      } else {
        status = "UNVERIFIED";
        unverifiedCount++;
        notes = "Claim lacks supporting evidence assets or source citation.";
      }

      audits.push({
        claimId: claim.id,
        claimText: claim.text,
        status,
        hasEvidence,
        evidenceCount: claim.evidenceAssetIds.length,
        requiresCitation,
        hasCitation,
        confidence: claim.confidence ?? 1.0,
        blockingIssue,
        notes,
      });

      // Generate Citation Card if required and source exists
      if (requiresCitation && hasCitation) {
        const customTiming = Object.hasOwn(claimTimings, claim.id) ? claimTimings[claim.id] : undefined;
        const timing = customTiming ?? { startSeconds: 0.0, durationSeconds: 5.0 };
        const start = timing.startSeconds;
        const end = start + timing.durationSeconds;

        const card: CitationCard = {
          id: `citation_${claim.id}`,
          claimId: claim.id,
          sourceTitle: claim.sourceCitation!,
          sourceAuthorOrOrg: claim.sourceCitation!,
          timelineStartSeconds: start,
          timelineEndSeconds: end,
          speakerId: claim.speakerId,
          onScreenText: `SOURCE: ${claim.sourceCitation}`,
          style: "LOWER_THIRD",
        };

        citationCards.push(CitationCardSchema.parse(card));
      }
    }

    const totalClaims = claims.length;
    let integrityScore = 100.0;

    if (totalClaims > 0) {
      // Score calculation: verified adds up to 100, unverified reduces score, missing sources penalizes heavily
      const baseRatio = (verifiedCount / totalClaims) * 100.0;
      const missingPenalty = (missingSourceCount / totalClaims) * 30.0;
      integrityScore = Math.max(0.0, Math.min(100.0, baseRatio - missingPenalty));
    }

    integrityScore = Number(integrityScore.toFixed(2));

    const payloadForHash = JSON.stringify({
      projectId,
      totalClaims,
      audits: audits.map((a) => ({ id: a.claimId, status: a.status })),
      citationCards: citationCards.map((c) => ({ id: c.id, text: c.onScreenText })),
      integrityScore,
    });

    const checksumSha256 = crypto
      .createHash("sha256")
      .update(payloadForHash)
      .digest("hex");

    return EvidenceAuditReportSchema.parse({
      projectId,
      totalClaims,
      verifiedClaims: verifiedCount,
      unverifiedClaims: unverifiedCount,
      missingSourceClaims: missingSourceCount,
      evidenceIntegrityScore: integrityScore,
      audits,
      citationCards,
      checksumSha256,
    });
  }
}
