import { OutputProfile, RenderValidationResult } from "../types/index.js";

/**
 * Validador de entrega y conformidad de especificaciones técnicas de exportación (Fase 9).
 */
export class RenderValidator {
  public static validateOutput(
    actual: {
      width: number;
      height: number;
      fps: number;
      duration: number;
      codec: string;
      framesRendered: number;
    },
    expectedProfile: OutputProfile,
    expectedDuration: number
  ): RenderValidationResult {
    const issues: string[] = [];

    if (actual.width !== expectedProfile.width) {
      issues.push(
        `Width mismatch: actual ${actual.width}px != expected ${expectedProfile.width}px.`
      );
    }
    if (actual.height !== expectedProfile.height) {
      issues.push(
        `Height mismatch: actual ${actual.height}px != expected ${expectedProfile.height}px.`
      );
    }
    if (actual.fps !== expectedProfile.fps) {
      issues.push(`FPS mismatch: actual ${actual.fps} != expected ${expectedProfile.fps}.`);
    }
    if (Math.abs(actual.duration - expectedDuration) > 0.05) {
      issues.push(
        `Duration deviation: actual ${actual.duration.toFixed(2)}s != expected ${expectedDuration.toFixed(2)}s.`
      );
    }

    return {
      valid: issues.length === 0,
      issues,
    };
  }
}
