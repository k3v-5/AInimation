import { SupportedLocale } from "../contracts/language.types.js";
import { PacingConflict } from "../contracts/pacing.types.js";

export type PacingConflictType =
  | "VOICE_TOO_LONG"
  | "VOICE_TOO_SHORT"
  | "ANCHOR_DRIFT"
  | "BROLL_TOO_SHORT"
  | "BROLL_TOO_LONG"
  | "HOLD_LIMIT_EXCEEDED"
  | "STRETCH_LIMIT_EXCEEDED"
  | "TRANSITION_COLLISION"
  | "SUBTITLE_DRIFT"
  | "NO_VALID_SOLUTION";

export interface DetailedPacingConflict extends PacingConflict {
  conflictType: PacingConflictType;
  description: string;
  measuredValue: number;
  allowedValue: number;
}

/**
 * Gestor y Clasificador de Conflictos Temporales de Pacing (Milestone 5-22).
 * Cataloga inconsistencias que no pueden resolverse automáticamente sin romper
 * anclas locked o exceder las cotas de stretch [0.95, 1.05].
 */
export class PacingConflictResolver {
  public static createConflict(params: {
    segmentId: string;
    locale: SupportedLocale;
    conflictType: PacingConflictType;
    severity: "WARNING" | "BLOCKING";
    unresolvedDeltaSeconds: number;
    requiredVoiceStretch: number;
    measuredValue: number;
    allowedValue: number;
    suggestedAction: "EXTEND_BROLL_FURTHER" | "ADD_PAUSE" | "MANUAL_SCRIPT_EDIT";
    description: string;
  }): DetailedPacingConflict {
    return {
      segmentId: params.segmentId,
      locale: params.locale,
      conflictType: params.conflictType,
      severity: params.severity,
      unresolvedDeltaSeconds: Number(params.unresolvedDeltaSeconds.toFixed(4)),
      requiredVoiceStretch: Number(params.requiredVoiceStretch.toFixed(4)),
      measuredValue: Number(params.measuredValue.toFixed(4)),
      allowedValue: Number(params.allowedValue.toFixed(4)),
      suggestedAction: params.suggestedAction,
      description: params.description,
    };
  }
}
