/**
 * REQ-QA-026: Política de confianza y umbral de revisión humana.
 */
export const DEFAULT_HUMAN_REVIEW_CONFIDENCE_THRESHOLD = 0.7;

export interface HumanReviewPolicy {
  confidenceThreshold: number;
  autoApproveHighConfidence: boolean;
}

export class ConfidencePolicy {
  /**
   * REQ-QA-044: Valida que la confianza sea un número finito en [0, 1].
   */
  public static validateConfidence(confidence: number): void {
    if (!Number.isFinite(confidence) || confidence < 0.0 || confidence > 1.0) {
      throw new Error(
        `ConfidencePolicy: Invalid confidence value (${confidence}). Must be a finite number in [0.0, 1.0].`
      );
    }
  }

  /**
   * REQ-QA-026, REQ-QA-057: Determina si una decisión debe entrar en HumanReviewQueue.
   * Por defecto: confidence < 0.70.
   * 0.6999 entra.
   * 0.70 no entra por sí solo.
   * 0.7001 no entra.
   */
  public static shouldRouteToHumanReview(
    confidence: number,
    threshold = DEFAULT_HUMAN_REVIEW_CONFIDENCE_THRESHOLD
  ): boolean {
    this.validateConfidence(confidence);
    const clampedThreshold = Math.max(0.0, Math.min(1.0, threshold));
    return confidence < clampedThreshold;
  }

  /**
   * REQ-QA-045: Regla de no invención.
   * Si faltan datos requeridos, reduce la confianza automáticamente.
   */
  public static penalizeMissingData(baseConfidence: number, missingFieldsCount: number): number {
    this.validateConfidence(baseConfidence);
    const penalty = missingFieldsCount * 0.25;
    return Math.max(0.0, Number((baseConfidence - penalty).toFixed(4)));
  }
}
