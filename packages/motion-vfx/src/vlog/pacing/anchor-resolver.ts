import { SYNC_TOLERANCES } from "../contracts/vlog.constants.js";

export type NarrativeAnchorType =
  | "HOOK"
  | "TOPIC_START"
  | "TOPIC_END"
  | "LOCATION_REVEAL"
  | "EMOTIONAL_PEAK"
  | "VISUAL_REVEAL"
  | "PUNCHLINE"
  | "CTA"
  | "ENDING"
  | "MANUAL";

export type AnchorDriftStatus = "OK" | "WARNING" | "ERROR" | "FATAL";

export interface NarrativeAnchor {
  id: string;
  type: NarrativeAnchorType;
  sourceTimeSeconds: number;
  targetTimeSeconds: number;
  priority: number; // 1 (baja) a 5 (crítica)
  locked: boolean; // Si es locked, no puede desplazarse fuera de tolerancia
  toleranceSeconds?: number; // default: 0.040s (40ms)
}

export interface AnchorResolutionResult {
  anchorId: string;
  type: NarrativeAnchorType;
  targetTimeSeconds: number;
  actualTimeSeconds: number;
  driftSeconds: number;
  status: AnchorDriftStatus;
  isCompliant: boolean;
  message: string;
}

/**
 * Resolutor de Anclas Narrativas y Verificador de Deriva Temporal (Milestone 5-07 & 5-08).
 * Comprueba que eventos clave (ganchos, remates, revelaciones de ubicación) mantengan
 * su sincronía dentro de las tolerancias canónicas (40ms OK, 100ms WARNING, 250ms ERROR, >250ms FATAL).
 */
export class AnchorResolver {
  public static evaluateAnchor(
    anchor: NarrativeAnchor,
    actualTimeSeconds: number
  ): AnchorResolutionResult {
    const driftSeconds = Number((actualTimeSeconds - anchor.targetTimeSeconds).toFixed(4));
    const absDrift = Math.abs(driftSeconds);

    const okLimit = anchor.toleranceSeconds ?? SYNC_TOLERANCES.SUBTITLE_WORD_DRIFT_SECONDS; // 0.040s (40ms)
    const warnLimit = SYNC_TOLERANCES.SEGMENT_ALIGNMENT_WARN_SECONDS; // 0.100s (100ms)
    const errorLimit = SYNC_TOLERANCES.SEGMENT_ALIGNMENT_FAIL_SECONDS; // 0.250s (250ms)

    let status: AnchorDriftStatus = "OK";
    let isCompliant = true;

    if (absDrift <= okLimit) {
      status = "OK";
      isCompliant = true;
    } else if (absDrift <= warnLimit) {
      status = "WARNING";
      isCompliant = !anchor.locked;
    } else if (absDrift <= errorLimit) {
      status = "ERROR";
      isCompliant = false;
    } else {
      status = "FATAL";
      isCompliant = false;
    }

    const message = `Anchor '${anchor.id}' [${anchor.type}] target: ${anchor.targetTimeSeconds.toFixed(3)}s, actual: ${actualTimeSeconds.toFixed(3)}s, drift: ${(driftSeconds * 1000).toFixed(1)}ms (${status})`;

    return {
      anchorId: anchor.id,
      type: anchor.type,
      targetTimeSeconds: anchor.targetTimeSeconds,
      actualTimeSeconds,
      driftSeconds,
      status,
      isCompliant,
      message,
    };
  }
}
