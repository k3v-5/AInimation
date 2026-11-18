import crypto from "crypto";
import {
  AbstractNarrativeConcept,
  VisualMetaphorPattern,
  MetaphorCandidate,
} from "./visual-metaphor.types.js";
import { ShotIndexRecord } from "../perception/perception.types.js";

/**
 * REQ-015: Master Visual Metaphor Engine
 * Transforma abstracciones conceptuales y filosóficas en candidatos visuales justificados y verificables.
 */
export class VisualMetaphorEngine {
  public static readonly PATTERNS: Record<AbstractNarrativeConcept, VisualMetaphorPattern> = {
    ISOLATION: {
      concept: "ISOLATION",
      requiredFraming: ["WIDE", "EXTREME_CLOSE"],
      cameraMotion: ["STATIC", "SLOW" as any],
      requiredKeywords: ["solitary", "alone", "empty", "distance", "desert", "void", "single"],
      compositionHint: "High negative space, solitary subject in expansive framing",
    },
    CONFLICT: {
      concept: "CONFLICT",
      cameraMotion: ["HANDHELD", "PAN", "TRACKING"],
      lightingMood: ["DRAMATIC_LOW_KEY", "NIGHT"],
      requiredKeywords: ["opposing", "shadow", "tension", "fire", "confrontation", "sharp", "fracture"],
      compositionHint: "Opposing vector lines, harsh diagonal shadows",
    },
    LOSS: {
      concept: "LOSS",
      requiredFraming: ["MEDIUM", "CLOSE_UP"],
      lightingMood: ["DRAMATIC_LOW_KEY", "NIGHT"],
      requiredKeywords: ["rain", "empty", "abandoned", "decay", "falling", "shadow", "fading"],
      compositionHint: "Empty spaces formerly occupied, dimming luminescence",
    },
    HOPE: {
      concept: "HOPE",
      lightingMood: ["GOLDEN_HOUR", "DAYLIGHT"],
      cameraMotion: ["TILT", "DOLLY"],
      requiredKeywords: ["sunrise", "horizon", "dawn", "sky", "bloom", "light", "open"],
      compositionHint: "Upward camera tilt towards rising illumination",
    },
    BUREAUCRACY: {
      concept: "BUREAUCRACY",
      requiredFraming: ["WIDE", "MEDIUM"],
      requiredKeywords: ["grid", "repetitive", "hallway", "documents", "architecture", "uniform"],
      compositionHint: "Rigid geometric symmetry, repetitive architectural patterns",
    },
    POWER: {
      concept: "POWER",
      requiredFraming: ["WIDE", "CLOSE_UP"],
      requiredKeywords: ["monolithic", "tower", "elevation", "height", "shadow", "dominant"],
      compositionHint: "Extreme low angle looking upward at dominating structures",
    },
    UNCERTAINTY: {
      concept: "UNCERTAINTY",
      lightingMood: ["DRAMATIC_LOW_KEY", "NIGHT"],
      requiredKeywords: ["fog", "mist", "obscured", "reflection", "blur", "haze"],
      compositionHint: "Diffused boundaries, obscured horizon line",
    },
    FREEDOM: {
      concept: "FREEDOM",
      requiredFraming: ["WIDE"],
      cameraMotion: ["TRACKING", "DOLLY"],
      requiredKeywords: ["sky", "ocean", "unbounded", "wind", "flight", "drone"],
      compositionHint: "Expansive unconstrained horizontal perspective",
    },
    CONFINEMENT: {
      concept: "CONFINEMENT",
      requiredFraming: ["CLOSE_UP", "EXTREME_CLOSE"],
      requiredKeywords: ["bars", "corridor", "tight", "shadows", "cage", "wall"],
      compositionHint: "Obstructed foregrounds, compressed focal depth",
    },
    TRANSFORMATION: {
      concept: "TRANSFORMATION",
      requiredKeywords: ["season", "sunrise", "transition", "water", "flow", "mirror", "growth"],
      compositionHint: "Dynamic chromatic shift or organic state transition",
    },
  };

  /**
   * Evalúa y puntúa candidatos de metáforas visuales para un concepto abstracto dado
   */
  public static findMetaphorCandidates(params: {
    concept: AbstractNarrativeConcept;
    availableShots: ShotIndexRecord[];
    recentShotIds?: string[]; // Para penalizar clichés y repeticiones (REQ-014)
    confidenceThreshold?: number;
  }): MetaphorCandidate[] {
    const { concept, availableShots, recentShotIds = [], confidenceThreshold = 0.70 } = params;
    const pattern = this.PATTERNS[concept];
    const candidates: MetaphorCandidate[] = [];

    for (const shot of availableShots) {
      let visualFit = 0.5;
      let narrativeFit = 0.5;
      let continuityFit = 0.8;

      const text = `${shot.detectedSubjects.join(" ")} ${shot.transcriptText || ""}`.toLowerCase();

      // 1. Coincidencias de palabras clave de metáfora
      let keywordHits = 0;
      for (const kw of pattern.requiredKeywords) {
        if (text.includes(kw)) keywordHits++;
      }
      if (keywordHits > 0) {
        narrativeFit = Math.min(1.0, 0.5 + keywordHits * 0.25);
      }

      // 2. Coincidencia de encuadre y composición
      if (pattern.requiredFraming && pattern.requiredFraming.includes(shot.visualFeatures.composition.framing as any)) {
        visualFit += 0.25;
      }

      // 3. Coincidencia de atmósfera lumínica
      if (pattern.lightingMood && pattern.lightingMood.includes(shot.visualFeatures.lightingMood)) {
        visualFit += 0.25;
      }

      // 4. Penalización por repetición (REQ-014)
      if (recentShotIds.includes(shot.shotId)) {
        continuityFit -= 0.40;
      }

      visualFit = Math.min(1.0, visualFit);
      continuityFit = Math.max(0.0, continuityFit);

      const compositeScore = Number(
        (narrativeFit * 0.45 + visualFit * 0.35 + continuityFit * 0.20) * 100.0
      ).toFixed(2);

      const scoreNum = Number(compositeScore);
      const confidence = Number((narrativeFit * 0.6 + visualFit * 0.4).toFixed(3));

      if (scoreNum >= 50.0) {
        const id = `meta_${crypto
          .createHash("sha256")
          .update(`${concept}_${shot.shotId}`)
          .digest("hex")
          .slice(0, 10)}`;

        candidates.push({
          metaphorId: id,
          abstractConcept: concept,
          visualPattern: pattern.compositionHint,
          candidateShotId: shot.shotId,
          sourceAssetId: shot.sourceAssetId,
          semanticScore: scoreNum,
          narrativeFit,
          visualFit,
          continuityFit,
          compositeScore: scoreNum,
          confidence,
          requiresHumanReview: confidence < confidenceThreshold,
          explanation: `Metáfora de '${concept}' seleccionada con confianza ${(confidence * 100).toFixed(0)}%. Patrón: ${pattern.compositionHint}.`,
        });
      }
    }

    return candidates.sort((a, b) => b.compositeScore - a.compositeScore || a.metaphorId.localeCompare(b.metaphorId));
  }
}
