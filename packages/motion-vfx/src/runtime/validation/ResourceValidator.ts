import { ProjectResourceLimitError } from "../../errors/runtime-errors.js";
import { RuntimeLimits } from "../../schemas/runtime.schema.js";
import { Diagnostic } from "../types.js";

/**
 * Validador de límites de recursos para prevenir proyectos patológicos o ataques DoS (Fase 18).
 */
export class ResourceValidator {
  public static validate(projectData: any): Diagnostic[] {
    const diagnostics: Diagnostic[] = [];

    const layers = projectData.layers ?? projectData.composition?.layers ?? [];
    if (layers.length > RuntimeLimits.MAX_LAYERS) {
      throw new ProjectResourceLimitError("layers", layers.length, RuntimeLimits.MAX_LAYERS);
    }

    const elements = projectData.elements ?? projectData.composition?.elements ?? [];
    if (elements.length > RuntimeLimits.MAX_ELEMENTS) {
      throw new ProjectResourceLimitError("elements", elements.length, RuntimeLimits.MAX_ELEMENTS);
    }

    const assets = projectData.assets ?? [];
    if (assets.length > RuntimeLimits.MAX_ASSETS) {
      throw new ProjectResourceLimitError("assets", assets.length, RuntimeLimits.MAX_ASSETS);
    }

    // Contar keyframes totales
    let totalKeyframes = 0;
    for (const elem of elements) {
      if (elem.transform) {
        for (const propName of ["position", "scale", "rotation", "opacity", "anchorPoint"]) {
          const prop = elem.transform[propName];
          if (prop?.keyframes) {
            const kfCount = prop.keyframes.length;
            totalKeyframes += kfCount;
            if (kfCount > RuntimeLimits.MAX_KEYFRAMES_PER_PROPERTY) {
              diagnostics.push({
                severity: "warning",
                code: "EXCESSIVE_KEYFRAMES_IN_PROPERTY",
                message: `Element '${elem.id}' property '${propName}' has ${kfCount} keyframes.`,
                path: `elements.${elem.id}.transform.${propName}`,
              });
            }
          }
        }
      }
    }

    if (totalKeyframes > RuntimeLimits.MAX_TOTAL_KEYFRAMES) {
      throw new ProjectResourceLimitError("totalKeyframes", totalKeyframes, RuntimeLimits.MAX_TOTAL_KEYFRAMES);
    }

    return diagnostics;
  }
}
