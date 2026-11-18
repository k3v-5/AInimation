import path from "node:path";
import {
  ClassificationEvidence,
  ClassificationScores,
  FootageClassification,
  FootageType,
} from "../contracts/classification.types.js";
import { IngestedMediaFile } from "../contracts/ingestion.types.js";

/** Entradas opcionales de análisis para mejorar la clasificación probabilística */
export interface ClassifierFeaturesInput {
  hasVoiceActivity?: boolean;
  voiceActivityRatio?: number; // [0.0, 1.0]
  hasDominantFace?: boolean;
  faceCoverageRatio?: number; // [0.0, 1.0]
  averageOpticalFlow?: number; // [0.0, 1.0]
  detectedTags?: string[];
  detectedObjects?: string[];
}

/**
 * Clasificador Probabilístico de Metraje Audiovisual (Milestone 2-B).
 * Separa A-Roll (hablante a cámara), B-Roll (recurso visual), Acción, Timelapse,
 * Fotos y Pantallas mediante un modelo multicriterio determinista y explicable.
 */
export class VlogFootageClassifier {
  /**
   * Clasifica un activo multimedia individual combinando metadatos técnicos y señales semánticas.
   */
  public static classify(
    media: IngestedMediaFile,
    features: ClassifierFeaturesInput = {}
  ): FootageClassification {
    const ext = media.extension.toLowerCase();
    const isStatic = [".png", ".jpg", ".jpeg", ".webp"].includes(ext);

    // Extraer o inferir features normalizadas
    const hasVoice = features.hasVoiceActivity ?? (media.audioStream !== undefined);
    const voiceRatio = this.clamp01(features.voiceActivityRatio ?? (hasVoice ? 0.65 : 0.0));
    const hasFace = features.hasDominantFace ?? false;
    const faceCoverage = this.clamp01(features.faceCoverageRatio ?? (hasFace ? 0.25 : 0.0));
    const opticalFlow = this.clamp01(features.averageOpticalFlow ?? 0.20);
    const tags = (features.detectedTags ?? []).map((t) => t.toLowerCase());
    const objects = (features.detectedObjects ?? []).map((o) => o.toLowerCase());

    const allTags = Array.from(new Set([...tags, ...objects]));

    // Inicializar scores probabilísticos
    let scoreARoll = 0.0;
    let scoreBRoll = 0.0;
    let scoreAction = 0.0;
    let scoreTimelapse = 0.0;
    let scoreScreen = 0.0;
    let scorePhoto = 0.0;
    let scoreOther = 0.0;

    // 1. Caso Fotografía
    if (isStatic) {
      scorePhoto = 0.95;
      scoreBRoll = 0.50;
    } else {
      // 2. Análisis A-Roll (Talking Head / Orador a cámara)
      if (hasFace && hasVoice) {
        // Rostro frontal sostenido + habla activa = fuerte candidato A-Roll
        scoreARoll += 0.50 * (faceCoverage > 0.10 ? 1.0 : 0.6);
        scoreARoll += 0.40 * voiceRatio;
      } else if (hasFace && !hasVoice) {
        // Rostro sin voz (ej. transeúnte en B-Roll)
        scoreARoll += 0.20;
        scoreBRoll += 0.60;
      } else if (!hasFace && hasVoice) {
        // Voz sin rostro visible (voiceover o metraje con audio)
        scoreARoll += 0.35 * voiceRatio;
        scoreBRoll += 0.45;
      }

      // 3. Análisis B-Roll (Planos de apoyo, arquitectura, paisaje, comida)
      const bRollKeywords = ["landscape", "food", "street", "building", "city", "nature", "car", "coffee", "monument", "market"];
      const bRollTagMatches = allTags.filter((t) => bRollKeywords.some((k) => t.includes(k))).length;
      if (bRollTagMatches > 0) {
        scoreBRoll += Math.min(0.50, bRollTagMatches * 0.20);
      }
      if (!hasFace) {
        scoreBRoll += 0.35;
      }

      // 4. Análisis Acción (Alto flujo óptico, deportes, drones)
      const actionKeywords = ["run", "sport", "action", "chase", "jump", "ride", "drone", "fast"];
      const actionTagMatches = allTags.filter((t) => actionKeywords.some((k) => t.includes(k))).length;
      if (opticalFlow > 0.60 || actionTagMatches > 0) {
        scoreAction += opticalFlow * 0.60 + Math.min(0.40, actionTagMatches * 0.20);
      }

      // 5. Análisis Timelapse
      const isTimelapseTag = allTags.some((t) => t.includes("timelapse") || t.includes("hyperlapse"));
      if (isTimelapseTag || (media.videoStream?.fps && media.videoStream.fps > 59 && opticalFlow > 0.50)) {
        scoreTimelapse += isTimelapseTag ? 0.90 : 0.65;
      }

      // 6. Análisis Pantalla / Screencast
      const screenKeywords = ["screen", "desktop", "ui", "code", "browser", "terminal", "app"];
      const screenTagMatches = allTags.filter((t) => screenKeywords.some((k) => t.includes(k))).length;
      if (screenTagMatches > 0) {
        scoreScreen += Math.min(0.90, screenTagMatches * 0.45);
      }
    }

    // Normalizar scores
    scoreARoll = this.clamp01(scoreARoll);
    scoreBRoll = this.clamp01(scoreBRoll);
    scoreAction = this.clamp01(scoreAction);
    scoreTimelapse = this.clamp01(scoreTimelapse);
    scoreScreen = this.clamp01(scoreScreen);
    scorePhoto = this.clamp01(scorePhoto);

    // Si ningún score es significativo, clasificar en OTHER
    const maxScore = Math.max(scoreARoll, scoreBRoll, scoreAction, scoreTimelapse, scoreScreen, scorePhoto);
    if (maxScore < 0.25) {
      scoreOther = 0.50;
    }

    const scores: ClassificationScores = {
      aRoll: Number(scoreARoll.toFixed(3)),
      bRoll: Number(scoreBRoll.toFixed(3)),
      action: Number(scoreAction.toFixed(3)),
      timelapse: Number(scoreTimelapse.toFixed(3)),
      screen: Number(scoreScreen.toFixed(3)),
      photo: Number(scorePhoto.toFixed(3)),
      other: Number(scoreOther.toFixed(3)),
    };

    // Determinar categoría primaria con mayor puntuación
    let primaryType: FootageType = "UNKNOWN";
    let highest = 0.0;

    const candidates: Array<{ type: FootageType; score: number }> = [
      { type: "PHOTO", score: scores.photo },
      { type: "SCREEN", score: scores.screen },
      { type: "A_ROLL", score: scores.aRoll },
      { type: "ACTION", score: scores.action },
      { type: "TIMELAPSE", score: scores.timelapse },
      { type: "B_ROLL", score: scores.bRoll },
      { type: "OTHER", score: scores.other },
    ];

    for (const c of candidates) {
      if (c.score > highest) {
        highest = c.score;
        primaryType = c.type;
      }
    }

    if (highest < 0.20) {
      primaryType = "UNKNOWN";
      highest = 0.10;
    }

    // Evidencia explicable
    const evidence: ClassificationEvidence = {
      hasVoiceActivity: hasVoice,
      voiceActivityRatio: voiceRatio,
      hasDominantFace: hasFace,
      faceCoverageRatio: faceCoverage,
      averageOpticalFlow: opticalFlow,
      isStaticImage: isStatic,
      aspectRatio: media.videoStream?.aspectRatio ?? "16:9",
      detectedTags: allTags,
    };

    let recommendedRole: "A_ROLL_PRIMARY" | "B_ROLL_CUTAWAY" | "TRANSITION_STINGER" | "UNKNOWN" = "UNKNOWN";
    if (primaryType === "A_ROLL") recommendedRole = "A_ROLL_PRIMARY";
    else if (["B_ROLL", "PHOTO", "SCREEN"].includes(primaryType)) recommendedRole = "B_ROLL_CUTAWAY";
    else if (["ACTION", "TIMELAPSE"].includes(primaryType)) recommendedRole = "TRANSITION_STINGER";

    return {
      mediaId: media.id,
      primaryType,
      confidence: Number(highest.toFixed(3)),
      scores,
      evidence,
      recommendedRole,
      tags: allTags,
    };
  }

  private static clamp01(val: number): number {
    if (isNaN(val) || !isFinite(val)) return 0.0;
    return Math.max(0.0, Math.min(1.0, val));
  }
}
