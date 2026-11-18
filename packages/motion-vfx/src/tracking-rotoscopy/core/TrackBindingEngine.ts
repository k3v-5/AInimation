import { Vector2 } from "../../core/types.js";
import { RelativeBinding, Track } from "../types/index.js";
import { TrackProcessor } from "./TrackProcessor.js";

/**
 * Motor de vinculación de elementos a trayectorias de tracking y cálculo de flechas inteligentes (Fase 12).
 */
export class TrackBindingEngine {
  /**
   * Calcula la posición absoluta de una capa vinculada a una trayectoria con offset relativo.
   */
  public static calculateBoundPosition(
    track: Track,
    t: number,
    binding: RelativeBinding
  ): Vector2 | undefined {
    const trackPos = TrackProcessor.evaluatePosition(track, t);
    if (!trackPos) return undefined;

    return {
      x: trackPos.x + binding.offset.x,
      y: trackPos.y + binding.offset.y,
    };
  }

  /**
   * Calcula los parámetros de una flecha inteligente apuntando desde un origen a un objetivo en seguimiento.
   */
  public static calculateSmartArrow(
    sourcePos: Vector2,
    targetTrack: Track,
    t: number
  ): { targetPos: Vector2; length: number; angleRadians: number } | undefined {
    const targetPos = TrackProcessor.evaluatePosition(targetTrack, t);
    if (!targetPos) return undefined;

    const dx = targetPos.x - sourcePos.x;
    const dy = targetPos.y - sourcePos.y;
    const length = Math.sqrt(dx * dx + dy * dy);
    const angleRadians = Math.atan2(dy, dx);

    return {
      targetPos,
      length,
      angleRadians,
    };
  }
}
