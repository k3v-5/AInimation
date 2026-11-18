import { SubclipOptimizer } from "../../broll-retrieval/core/SubclipOptimizer.js";
import { IndexedAsset } from "../../broll-retrieval/types/index.js";
import {
  BRollCandidate,
  BRollMatch,
  BRollMatchScore,
  ClipRange,
  FootageClassification,
} from "../contracts/classification.types.js";
import { IngestedMediaFile } from "../contracts/ingestion.types.js";
import { VlogClipLock } from "../contracts/vlog-project.types.js";
import { BROLL_SCORING_WEIGHTS, EPSILON } from "../contracts/vlog.constants.js";

/** Solicitud de emparejamiento de B-Roll para un segmento narrativo */
export interface BRollMatchQuery {
  narrativeSegmentId: string;
  intentText: string;
  entities?: string[];
  location?: string;
  activity?: string;
  targetDurationSeconds: number;
  timelineStartSeconds: number;
  timelineEndSeconds: number;
  recentUsageMediaIds?: string[]; // IDs de activos utilizados recientemente para aplicar cooldown
  locks?: Record<string, VlogClipLock>;
}

/**
 * Emparejador Semántico de B-Roll (Milestone 2-C).
 * Asocia material visual contextual con el habla y la narrativa de forma determinista,
 * reutilizando el ranking multicriterio y optimizador de subclips sin dependencias de red.
 */
export class VlogBRollMatcher {
  /**
   * Resuelve el mejor candidato B-Roll y alternativas clasificadas para una unidad narrativa.
   */
  public static matchBRoll(
    query: BRollMatchQuery,
    availableMedia: IngestedMediaFile[],
    classifications: Map<string, FootageClassification>
  ): BRollMatch | null {
    if (!availableMedia || availableMedia.length === 0) {
      return null;
    }

    const intentWords = query.intentText
      .toLowerCase()
      .replace(/[.,/#!$%^&*;:{}=\-_`~()]/g, "")
      .split(/\s+/)
      .filter((w) => w.length > 2);

    const targetEntities = (query.entities ?? []).map((e) => e.toLowerCase());
    const targetLocation = query.location?.toLowerCase();
    const targetActivity = query.activity?.toLowerCase();
    const recentUsage = query.recentUsageMediaIds ?? [];

    const candidates: BRollCandidate[] = [];

    for (const media of availableMedia) {
      const classif = classifications.get(media.id);
      const lock = query.locks?.[media.id];

      // 1. Filtro estricto de exclusión manual
      if (lock?.lockType === "FORBIDDEN") {
        continue;
      }

      // 2. Filtro de tipo: No utilizar A-Roll puro como B-Roll si hay alternativa
      if (classif && classif.primaryType === "A_ROLL" && lock?.lockType !== "FORCE") {
        continue;
      }

      // 3. Duración total del activo
      const duration = media.videoStream?.durationSeconds ?? media.fingerprint.durationSeconds ?? 5.0;
      if (duration < query.targetDurationSeconds * 0.80 && lock?.lockType !== "FORCE") {
        // Descartar si el clip es excesivamente corto para cubrir la necesidad
        continue;
      }

      // 4. Calcular scores individuales (0 a 100)
      const mediaTags = classif?.tags ?? [];

      // Helper de normalización de cadenas para comparar sin tildes/acentos
      const normalize = (s: string) =>
        s
          .normalize("NFD")
          .replace(/[\u0300-\u036f]/g, "")
          .toLowerCase();

      // Semantic Relevance (0 a 100)
      const contextWords = [
        ...intentWords,
        ...targetEntities,
        ...(targetLocation ? [targetLocation] : []),
      ];

      let semanticMatches = 0;
      for (const tag of mediaTags) {
        const normTag = normalize(tag);
        if (contextWords.some((w) => {
          const normW = normalize(w);
          return normTag.includes(normW) || normW.includes(normTag);
        })) {
          semanticMatches++;
        }
      }

      // La relevancia semántica considera tanto el porcentaje de tags del clip satisfechos como el de palabras de intención
      const tagCoverage = mediaTags.length > 0 ? semanticMatches / mediaTags.length : 0;
      const intentCoverage = semanticMatches / Math.max(1, contextWords.length);
      const semanticRelevance = Math.min(100, Math.max(tagCoverage, intentCoverage) * 100);

      // Entity Match (0 a 100)
      let entityMatches = 0;
      for (const ent of targetEntities) {
        if (mediaTags.some((t) => t.includes(ent) || ent.includes(t)) || media.filename.toLowerCase().includes(ent)) {
          entityMatches++;
        }
      }
      const entityMatch = targetEntities.length > 0
        ? Math.min(100, (entityMatches / targetEntities.length) * 100)
        : (semanticMatches > 0 ? 60.0 : 40.0);

      // Visual Quality (0 a 100)
      const isHD = (media.videoStream?.width ?? 0) >= 1920;
      const visualQuality = isHD ? 95.0 : 75.0;

      // Location Relevance (0 a 100)
      let locationRelevance = 50.0;
      if (targetLocation) {
        if (mediaTags.some((t) => t.includes(targetLocation)) || media.filename.toLowerCase().includes(targetLocation)) {
          locationRelevance = 100.0;
        } else {
          locationRelevance = 20.0;
        }
      }

      // Activity Relevance (0 a 100)
      let activityRelevance = 50.0;
      if (targetActivity) {
        if (mediaTags.some((t) => t.includes(targetActivity))) {
          activityRelevance = 100.0;
        }
      }

      // Duration Fit (0 a 100)
      const durationDiff = Math.abs(duration - query.targetDurationSeconds);
      const durationFit = Math.max(0, 100 - (durationDiff / Math.max(duration, 10.0)) * 100);

      // Continuity / Visual Harmony (0 a 100)
      const continuity = 70.0;

      // Novelty / Cooldown Penalty (0 a 100)
      const usageIndex = recentUsage.indexOf(media.id);
      let noveltyPenalty = 0.0;
      if (usageIndex !== -1) {
        // Más penalización cuanto más reciente (índice menor)
        noveltyPenalty = Math.max(15.0, 70.0 - usageIndex * 15.0);
      }

      // Ponderación canónica de M1
      let rawTotal =
        semanticRelevance * BROLL_SCORING_WEIGHTS.SEMANTIC +
        entityMatch * BROLL_SCORING_WEIGHTS.ENTITY +
        visualQuality * BROLL_SCORING_WEIGHTS.VISUAL +
        locationRelevance * BROLL_SCORING_WEIGHTS.LOCATION +
        activityRelevance * BROLL_SCORING_WEIGHTS.ACTIVITY +
        visualQuality * BROLL_SCORING_WEIGHTS.QUALITY +
        durationFit * BROLL_SCORING_WEIGHTS.DURATION +
        continuity * BROLL_SCORING_WEIGHTS.CONTINUITY -
        noveltyPenalty;

      // Reglas de bloqueo manual
      if (lock?.lockType === "FORCE") {
        rawTotal = 100.0;
      } else if (lock?.lockType === "PREFERRED") {
        rawTotal = Math.min(100.0, rawTotal + 20.0);
      }

      const total = Number(Math.max(0, Math.min(100, rawTotal)).toFixed(2));

      const score: BRollMatchScore = {
        total,
        semanticRelevance: Number(semanticRelevance.toFixed(2)),
        entityMatch: Number(entityMatch.toFixed(2)),
        visualQuality: Number(visualQuality.toFixed(2)),
        locationRelevance: Number(locationRelevance.toFixed(2)),
        activityRelevance: Number(activityRelevance.toFixed(2)),
        durationFit: Number(durationFit.toFixed(2)),
        noveltyPenalty: Number(noveltyPenalty.toFixed(2)),
      };

      // 5. Calcular ventana de subclip óptima reutilizando SubclipOptimizer
      const indexedAssetMock: IndexedAsset = {
        id: media.id,
        uri: media.absolutePath,
        duration,
        orientation: media.videoStream?.orientation === "PORTRAIT" ? "portrait" : "landscape",
        tags: mediaTags,
        shots: [
          {
            id: `shot_${media.id}_0`,
            start: 0,
            end: duration,
            objects: [],
            hasFace: false,
            textSafeSide: "center",
            quality: visualQuality / 100,
            energy: 0.5,
          },
        ],
        license: {
          source: "user",
          attributionRequired: false,
          commercialUse: true,
        },
        usageCount: usageIndex !== -1 ? 1 : 0,
        fingerprint: media.fingerprint.checksumSha256,
      };

      const subclip = SubclipOptimizer.findBestSubclip(indexedAssetMock, query.targetDurationSeconds);
      const subclipRange: ClipRange = {
        assetId: media.id,
        startSeconds: subclip.start,
        endSeconds: subclip.end,
        durationSeconds: Number((subclip.end - subclip.start).toFixed(3)),
      };

      candidates.push({
        candidateId: `cand_${media.id}_${query.narrativeSegmentId}`,
        mediaId: media.id,
        subclipRange,
        score,
        matchedTags: mediaTags,
        rationale: `Asset '${media.filename}' total score: ${total} (semantic: ${score.semanticRelevance}, entity: ${score.entityMatch}, noveltyPenalty: -${noveltyPenalty})`,
      });
    }

    if (candidates.length === 0) {
      return null;
    }

    // Ordenamiento determinista: score descendente, desempate lexicográfico por mediaId
    candidates.sort((a, b) => {
      const diff = b.score.total - a.score.total;
      if (Math.abs(diff) > EPSILON) {
        return diff;
      }
      return a.mediaId.localeCompare(b.mediaId);
    });

    const selectedCandidate = candidates[0];
    const alternatives = candidates.slice(1);
    const isExclusiveCover = selectedCandidate.subclipRange.durationSeconds >= query.targetDurationSeconds;

    return {
      narrativeSegmentId: query.narrativeSegmentId,
      selectedCandidate,
      alternatives,
      timelineStartSeconds: query.timelineStartSeconds,
      timelineEndSeconds: query.timelineEndSeconds,
      isExclusiveCover,
    };
  }
}
