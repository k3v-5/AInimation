import crypto from "crypto";
import { DialogueRepairProposal, DialogueIssueType } from "./audio-ir.types.js";

/**
 * REQ-064: Dialogue Repair Intelligence
 * Diagnóstico declarativo y propuestas de mitigación no destructivas para defectos de diálogo.
 */
export class DialogueRepairEngine {
  /**
   * Genera un ID determinista para una propuesta de reparación
   */
  private static generateProposalId(clipId: string, issueType: string, time: number): string {
    const raw = `${clipId}_${issueType}_${time.toFixed(3)}`;
    return `rep_${crypto.createHash("sha256").update(raw, "utf8").digest("hex").slice(0, 12)}`;
  }

  /**
   * Analiza una pista o segmento de diálogo en busca de defectos acústicos conocidos
   */
  public static analyzeDialogue(params: {
    clipId: string;
    startSeconds: number;
    durationSeconds: number;
    peakLevelDb?: number;
    rmsDb?: number;
    detectedHumHz?: number;
    hasPlosiveTransient?: boolean;
    confidenceThreshold?: number;
  }): DialogueRepairProposal[] {
    const {
      clipId,
      startSeconds,
      durationSeconds,
      peakLevelDb = -6.0,
      detectedHumHz,
      hasPlosiveTransient,
      confidenceThreshold = 0.70,
    } = params;

    const proposals: DialogueRepairProposal[] = [];

    // 1. Detección de Clipping (> -0.1 dBTP)
    if (peakLevelDb >= -0.1) {
      const confidence = 0.95;
      proposals.push({
        id: this.generateProposalId(clipId, "CLIPPING", startSeconds),
        type: "CLIPPING",
        confidence,
        affectedRegion: { clipId, startSeconds, durationSeconds },
        suggestedParameters: {
          targetGainDb: -3.0,
        },
        rationale: `Pico acústico de ${peakLevelDb.toFixed(1)} dBFS excede el techo seguro; se recomienda atenuación de ganancia preventiva.`,
        reversible: true,
        requiresHumanReview: confidence < confidenceThreshold,
      });
    }

    // 2. Detección de Zumbido de Red (Hum a 50 Hz o 60 Hz)
    if (detectedHumHz && (Math.abs(detectedHumHz - 50) < 2 || Math.abs(detectedHumHz - 60) < 2)) {
      const confidence = 0.88;
      proposals.push({
        id: this.generateProposalId(clipId, "HUM", startSeconds),
        type: "HUM",
        confidence,
        affectedRegion: { clipId, startSeconds, durationSeconds },
        suggestedParameters: {
          notchFrequencyHz: detectedHumHz,
        },
        rationale: `Frecuencia fundamental de zumbido de línea eléctrica detectada a ${detectedHumHz} Hz; aplicar filtro notch estrecho.`,
        reversible: true,
        requiresHumanReview: confidence < confidenceThreshold,
      });
    }

    // 3. Detección de Golpe de Aire / Oclusiva (Plosive)
    if (hasPlosiveTransient) {
      const confidence = 0.65; // Menor certeza inicial -> entra en HumanReviewQueue (§20)
      proposals.push({
        id: this.generateProposalId(clipId, "PLOSIVE", startSeconds),
        type: "PLOSIVE",
        confidence,
        affectedRegion: { clipId, startSeconds, durationSeconds: Math.min(0.25, durationSeconds) },
        suggestedParameters: {
          highpassCutoffHz: 80,
          reductionDb: -6.0,
        },
        rationale: "Transitorio de baja frecuencia compatible con golpe de viento u oclusiva ('P'/'B').",
        reversible: true,
        requiresHumanReview: confidence < confidenceThreshold, // true
      });
    }

    return proposals;
  }
}
