import { ProjectValidationError } from "../../errors/runtime-errors.js";
import { ProjectEnvelope, ProjectEnvelopeFactory } from "../persistence/ProjectEnvelope.js";
import { StorageAdapter } from "../persistence/StorageAdapter.js";
import { Diagnostic, HealthReport } from "../types.js";
import { ProjectHealthValidator } from "./ProjectHealthValidator.js";
import { ReferentialIntegrityValidator } from "./ReferentialIntegrityValidator.js";
import { ResourceValidator } from "./ResourceValidator.js";

/**
 * Validador unificado de 6 capas para el Runtime de Producción (Fase 18).
 */
export class RuntimeValidator {
  /**
   * Valida integralmente un envelope de proyecto.
   */
  public static async validateEnvelope(
    rawEnvelope: unknown,
    options: { strict?: boolean; storage?: StorageAdapter } = {}
  ): Promise<{ envelope: ProjectEnvelope; health: HealthReport; diagnostics: Diagnostic[] }> {
    const strict = options.strict ?? true;
    const diagnostics: Diagnostic[] = [];

    // 1. Validar Envelope y checksum
    let envelope: ProjectEnvelope;
    try {
      envelope = ProjectEnvelopeFactory.validate(rawEnvelope);
    } catch (err: any) {
      if (strict) throw err;
      envelope = rawEnvelope as ProjectEnvelope;
      diagnostics.push({
        severity: "error",
        code: "ENVELOPE_VALIDATION_FAILED",
        message: err.message,
      });
    }

    const project = envelope.project as any;

    // 2. Validar Límites de Recursos
    try {
      const resDiags = ResourceValidator.validate(project);
      diagnostics.push(...resDiags);
    } catch (err: any) {
      if (strict) throw err;
      diagnostics.push({
        severity: "error",
        code: "RESOURCE_LIMIT_EXCEEDED",
        message: err.message,
      });
    }

    // 3. Validar Integridad Referencial
    const refDiags = ReferentialIntegrityValidator.validate(project);
    diagnostics.push(...refDiags);

    // 4. Validar Consistencia Temporal
    const comp = project.composition ?? project;
    if (comp) {
      if (comp.duration !== undefined && (typeof comp.duration !== "number" || comp.duration <= 0 || !Number.isFinite(comp.duration))) {
        diagnostics.push({
          severity: "error",
          code: "INVALID_DURATION",
          message: `Composition duration must be positive and finite, got ${comp.duration}`,
          path: "composition.duration",
        });
      }
      if (comp.fps !== undefined && (typeof comp.fps !== "number" || comp.fps <= 0 || !Number.isFinite(comp.fps))) {
        diagnostics.push({
          severity: "error",
          code: "INVALID_FPS",
          message: `Composition fps must be positive and finite, got ${comp.fps}`,
          path: "composition.fps",
        });
      }
    }

    // Generar Health Report
    const health = await ProjectHealthValidator.assessHealth(envelope, diagnostics, options.storage);

    if (strict && health.status === "invalid") {
      throw new ProjectValidationError(envelope.projectId, diagnostics.filter((d) => d.severity === "error"));
    }

    return { envelope, health, diagnostics };
  }
}
