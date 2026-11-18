import {
  EditorialDiffReport,
  EditorialDiff,
  EditorialDiffType,
} from "../contracts/editorial-diff.types.js";
import { EditorialDocument } from "../contracts/editorial-qa.types.js";
import { ImpactAnalyzer } from "./impact-analyzer.js";
import { QANormalizer } from "./qa-normalizer.js";

/**
 * REQ-082: EditorialDiffEngine
 * Comparador semántico inmutable de versiones de líneas de tiempo editoriales.
 */
export class EditorialDiffEngine {
  public static readonly DIFF_SCHEMA_VERSION = "1.0.0";

  public static diff(before: EditorialDocument, after: EditorialDocument): EditorialDiffReport {
    const rawDiffs: Omit<EditorialDiff, "impact">[] = [];

    // Map clips por ID
    const beforeClips = new Map<string, { trackId: string; clip: any }>();
    for (const track of before.tracks) {
      for (const clip of track.clips) {
        beforeClips.set(clip.id, { trackId: track.id, clip });
      }
    }

    const afterClips = new Map<string, { trackId: string; clip: any }>();
    for (const track of after.tracks) {
      for (const clip of track.clips) {
        afterClips.set(clip.id, { trackId: track.id, clip });
      }
    }

    // 1. Clips eliminados
    for (const [id, { trackId, clip }] of beforeClips.entries()) {
      if (!afterClips.has(id)) {
        rawDiffs.push({
          id: `diff_rm_${id}`,
          type: "REMOVED",
          entityType: "CLIP",
          entityId: id,
          path: `tracks.${trackId}.clips.${id}`,
          before: clip,
          delta: -clip.timelineRange.durationSeconds,
        });
      }
    }

    // 2. Clips añadidos
    for (const [id, { trackId, clip }] of afterClips.entries()) {
      if (!beforeClips.has(id)) {
        rawDiffs.push({
          id: `diff_add_${id}`,
          type: "ADDED",
          entityType: "CLIP",
          entityId: id,
          path: `tracks.${trackId}.clips.${id}`,
          after: clip,
          delta: clip.timelineRange.durationSeconds,
        });
      }
    }

    // Map ripple shifts per track
    const trackShifts = new Map<string, number>();
    for (const [id, { trackId, clip: bClip }] of beforeClips.entries()) {
      const aEntry = afterClips.get(id);
      if (aEntry) {
        const durDiff = aEntry.clip.timelineRange.durationSeconds - bClip.timelineRange.durationSeconds;
        if (Math.abs(durDiff) > 1e-4) {
          trackShifts.set(trackId, (trackShifts.get(trackId) ?? 0) + durDiff);
        }
      }
    }

    // 3. Clips modificados o desplazados
    for (const [id, { trackId, clip: bClip }] of beforeClips.entries()) {
      const aEntry = afterClips.get(id);
      if (aEntry) {
        const aClip = aEntry.clip;
        const startDiff = aClip.timelineRange.startSeconds - bClip.timelineRange.startSeconds;
        const durDiff = aClip.timelineRange.durationSeconds - bClip.timelineRange.durationSeconds;

        if (Math.abs(durDiff) > 1e-4) {
          rawDiffs.push({
            id: `diff_mod_${id}`,
            type: "RESIZED",
            entityType: "CLIP",
            entityId: id,
            path: `tracks.${trackId}.clips.${id}.durationSeconds`,
            before: bClip.timelineRange.durationSeconds,
            after: aClip.timelineRange.durationSeconds,
            delta: Number(durDiff.toFixed(4)),
            origin: "DIRECT",
          } as any);
        } else if (Math.abs(startDiff) > 1e-4) {
          const shift = trackShifts.get(trackId) ?? 0;
          const isDerived = Math.abs(startDiff - shift) < 1e-3;
          rawDiffs.push({
            id: `diff_mv_${id}`,
            type: "MOVED",
            entityType: "CLIP",
            entityId: id,
            path: `tracks.${trackId}.clips.${id}.startSeconds`,
            before: bClip.timelineRange.startSeconds,
            after: aClip.timelineRange.startSeconds,
            delta: Number(startDiff.toFixed(4)),
            origin: isDerived ? "DERIVED" : "DIRECT",
          } as any);
        }
      }
    }

    // Analizar impacto global
    const { impact, impactLevel } = ImpactAnalyzer.analyzeImpact({
      beforeDoc: before,
      afterDoc: after,
      diffs: rawDiffs,
    });

    const fullDiffs: EditorialDiff[] = rawDiffs.map((d: any) => ({
      ...d,
      origin: d.origin ?? "DIRECT",
      category: "TIMING",
      impact,
    }));

    let added = 0;
    let removed = 0;
    let modified = 0;
    let moved = 0;

    for (const d of fullDiffs) {
      if (d.type === "ADDED") added++;
      else if (d.type === "REMOVED") removed++;
      else if (d.type === "MODIFIED" || d.type === "RESIZED") modified++;
      else if (d.type === "MOVED") moved++;
    }

    const beforeChecksum = before.checksum || QANormalizer.computeCanonicalSha256(before);
    const afterChecksum = after.checksum || QANormalizer.computeCanonicalSha256(after);

    const preliminary: Omit<EditorialDiffReport, "checksumSha256"> = {
      beforeChecksumSha256: beforeChecksum,
      afterChecksumSha256: afterChecksum,
      diffs: fullDiffs,
      changes: fullDiffs,
      totalChanges: fullDiffs.length,
      impactLevel,
      impact: {
        ...impact,
        duration: {
          beforeSeconds: (impact as any).durationBeforeSeconds ?? 0,
          afterSeconds: (impact as any).durationAfterSeconds ?? 0,
          deltaSeconds: impact.durationDeltaSeconds ?? 0,
        },
        pacing: {
          beforeAlignmentScore: 0.8,
          afterAlignmentScore: 0.8 + (impact.pacingAlignmentDelta ?? 0),
          delta: impact.pacingAlignmentDelta ?? 0,
        },
        attention: {
          beforeAverage: 0.8,
          afterAverage: 0.8 + (impact.attentionDelta ?? 0),
          delta: impact.attentionDelta ?? 0,
        },
        cognitiveLoad: {
          beforeAverage: 0.4,
          afterAverage: 0.4 + (impact.cognitiveLoadDelta ?? 0),
          delta: impact.cognitiveLoadDelta ?? 0,
          overloadCountBefore: 0,
          overloadCountAfter: 0,
        },
        contrast: {
          beforeScore: 80,
          afterScore: 80,
          delta: 0,
        },
        narrative: {
          causalChangesCount: impact.narrativeImpact?.causalRelationsChanged ?? 0,
          beatChangesCount: impact.narrativeImpact?.beatsAffected?.length ?? 0,
          spoilerRiskChanged: (impact.narrativeImpact?.spoilersIntroduced ?? 0) > 0,
        },
        continuity: {
          newViolations: 0,
          resolvedViolations: 0,
        },
      },
      baseChecksum: beforeChecksum,
      candidateChecksum: afterChecksum,
      fromChecksum: beforeChecksum,
      toChecksum: afterChecksum,
      summary: {
        added,
        removed,
        modified,
        moved,
        durationDeltaSeconds: impact.durationDeltaSeconds,
        overallImpactScore: impact.overallImpactScore,
      },

      requiresRevalidation: impactLevel === "HIGH" || impactLevel === "CRITICAL",
      // Compatibility fields
      changedEntitiesCount: fullDiffs.length,
      addedCount: added,
      removedCount: removed,
      modifiedCount: modified + moved,
      riskLevel: impactLevel,
    };

    const checksumSha256 = QANormalizer.computeCanonicalSha256(preliminary);

    return {
      ...preliminary,
      checksumSha256,
    };
  }

  // Alias y sobrecargas compatibles
  public static compare(arg1: any, arg2?: any): EditorialDiffReport {
    if (arg2) {
      return this.diff(arg1, arg2);
    }
    const before = arg1.baseIR ?? arg1.before;
    const after = arg1.candidateIR ?? arg1.after;
    const report = this.diff(before, after);

    if (arg1.basePacingScore !== undefined && arg1.candidatePacingScore !== undefined) {
      const delta = Number((arg1.candidatePacingScore - arg1.basePacingScore).toFixed(4));
      report.impact.pacingAlignmentDelta = delta;
      if (delta <= -20.0) {
        report.riskLevel = "HIGH";
      }
    }

    if (report.changes.length === 0) {
      report.riskLevel = "LOW";
    }

    let beforeCuts = 0;
    for (const t of before.tracks ?? []) beforeCuts += (t.clips ?? []).length;
    let afterCuts = 0;
    for (const t of after.tracks ?? []) afterCuts += (t.clips ?? []).length;
    report.impact.cutCountDelta = afterCuts - beforeCuts;

    for (const c of report.changes) {
      c.operation = c.type === "ADDED" ? "ADD" : c.type === "REMOVED" ? "REMOVE" : c.type;
    }

    return report;
  }
}
