import {
  EditorialImpact,
  ImpactLevel,
  EditorialDiff,
} from "../contracts/editorial-diff.types.js";
import { EditorialDocument } from "../contracts/editorial-qa.types.js";

/**
 * REQ-082 §28, §35: ImpactAnalyzer
 * Cuantifica con precisión matemática el impacto de intervenciones sobre duración, ritmo, narrativa y evidencia.
 */
export class ImpactAnalyzer {
  public static analyzeImpact(params: {
    beforeDoc: EditorialDocument;
    afterDoc: EditorialDocument;
    diffs: Omit<EditorialDiff, "impact">[];
  }): { impact: EditorialImpact; impactLevel: ImpactLevel } {
    const { beforeDoc, afterDoc, diffs } = params;

    // 1. Duración total
    const durBefore = this.calculateDocumentDuration(beforeDoc);
    const durAfter = this.calculateDocumentDuration(afterDoc);
    const durationDeltaSeconds = Number((durAfter - durBefore).toFixed(4));

    // 2. Pacing
    const pacingBefore = (beforeDoc as any).pacingScore ?? 0.7;
    const pacingAfter = (afterDoc as any).pacingScore ?? 0.7;
    const pacingDelta = Number((pacingAfter - pacingBefore).toFixed(4));

    // 3. Atención y Carga Cognitiva
    const attBefore = (beforeDoc as any).attentionScore ?? 0.8;
    const attAfter = (afterDoc as any).attentionScore ?? 0.8;
    const attentionDelta = Number((attAfter - attBefore).toFixed(4));

    const cogBefore = (beforeDoc as any).cognitiveScore ?? 0.4;
    const cogAfter = (afterDoc as any).cognitiveScore ?? 0.4;
    const cognitiveLoadDelta = Number((cogAfter - cogBefore).toFixed(4));

    // 4. Impacto Narrativo
    const beatsBefore = (beforeDoc as any).beats as Array<{ id: string; type: string }> | undefined;
    const beatsAfter = (afterDoc as any).beats as Array<{ id: string; type: string }> | undefined;
    const beatsAffected: string[] = [];
    let causalRelationsChanged = 0;
    let spoilersIntroduced = 0;

    if (beatsBefore && beatsAfter) {
      const idsBefore = new Set(beatsBefore.map((b) => b.id));
      const idsAfter = new Set(beatsAfter.map((b) => b.id));
      for (const b of beatsBefore) {
        if (!idsAfter.has(b.id)) beatsAffected.push(b.id);
      }
      for (const b of beatsAfter) {
        if (!idsBefore.has(b.id)) beatsAffected.push(b.id);
      }
      causalRelationsChanged = Math.abs(beatsBefore.length - beatsAfter.length);
    }

    // 5. Impacto en Evidencia
    const claimsBefore = (beforeDoc as any).claims as Array<{ id: string; isVerified?: boolean }> | undefined;
    const claimsAfter = (afterDoc as any).claims as Array<{ id: string; isVerified?: boolean }> | undefined;
    let claimsAffected = 0;
    let unsupportedClaimsDelta = 0;

    if (claimsBefore && claimsAfter) {
      const cAfterIds = new Set(claimsAfter.map((c) => c.id));
      for (const c of claimsBefore) {
        if (!cAfterIds.has(c.id)) claimsAffected++;
      }
      const unsuppBefore = claimsBefore.filter((c) => !c.isVerified).length;
      const unsuppAfter = claimsAfter.filter((c) => !c.isVerified).length;
      unsupportedClaimsDelta = unsuppAfter - unsuppBefore;
    }

    // 6. Impacto en Exportación
    const blockersAdded = unsupportedClaimsDelta > 0 ? unsupportedClaimsDelta : 0;
    const blockersRemoved = unsupportedClaimsDelta < 0 ? Math.abs(unsupportedClaimsDelta) : 0;

    // Cálculo del Overall Impact Score [0, 100]
    const magnitude =
      Math.abs(durationDeltaSeconds) * 2.0 +
      Math.abs(pacingDelta) * 30.0 +
      Math.abs(cognitiveLoadDelta) * 20.0 +
      beatsAffected.length * 15.0 +
      claimsAffected * 25.0 +
      diffs.length * 5.0;

    const overallImpactScore = Number(Math.max(0.0, Math.min(100.0, magnitude)).toFixed(4));

    const impact: EditorialImpact = {
      durationDeltaSeconds,
      pacingDelta,
      pacingScoreBefore: pacingBefore,
      pacingScoreAfter: pacingAfter,
      attentionDelta,
      cognitiveLoadDelta,
      contrastDelta: 0.0,
      narrativeImpact: {
        causalRelationsChanged,
        beatsAffected,
        spoilersIntroduced,
      },
      continuityImpact: {
        visualIssuesDelta: 0,
        audioIssuesDelta: 0,
      },
      evidenceImpact: {
        claimsAffected,
        unsupportedClaimsDelta,
      },
      exportImpact: {
        blockersAdded,
        blockersRemoved,
      },
      overallImpactScore,
    };

    // Clasificación de ImpactLevel
    let impactLevel: ImpactLevel = "NONE";
    if (diffs.length === 0 && Math.abs(durationDeltaSeconds) < 1e-4) {
      impactLevel = "NONE";
    } else if (claimsAffected > 0 || spoilersIntroduced > 0 || blockersAdded > 0) {
      impactLevel = "CRITICAL";
    } else if (beatsAffected.length > 0 || Math.abs(durationDeltaSeconds) > 10.0 || Math.abs(cognitiveLoadDelta) > 0.3) {
      impactLevel = "HIGH";
    } else if (Math.abs(durationDeltaSeconds) > 2.0 || Math.abs(pacingDelta) > 0.1) {
      impactLevel = "MEDIUM";
    } else {
      impactLevel = "LOW";
    }

    return { impact, impactLevel };
  }

  private static calculateDocumentDuration(doc: EditorialDocument): number {
    let maxEnd = 0;
    for (const track of doc.tracks) {
      for (const clip of track.clips) {
        const end = clip.timelineRange.startSeconds + clip.timelineRange.durationSeconds;
        if (end > maxEnd) maxEnd = end;
      }
    }
    return maxEnd;
  }
}
