import { Composition } from "../core/composition.js";
import { AudioElement, BaseElement, GroupElement, ImageElement, VideoElement } from "../elements/index.js";
import { ValidationError } from "../errors/index.js";
import { ValidationIssue, ValidationReport } from "./types.js";

/**
 * Validador estricto y diagnósticos completos de integridad para proyectos de Motion Graphics.
 */
export class ProjectValidator {
  /**
   * Valida un proyecto Composition produciendo un reporte exhaustivo con todos los problemas detectados.
   */
  public static validate(composition: Composition): ValidationReport {
    const issues: ValidationIssue[] = [];

    // 1. Validar Configuración de la Composición
    if (!composition.width || composition.width <= 0 || !Number.isFinite(composition.width)) {
      issues.push({
        severity: "error",
        code: "INVALID_SETTINGS",
        message: `Composition width must be a positive finite number, got ${composition.width}`,
        path: "composition.width",
      });
    }

    if (!composition.height || composition.height <= 0 || !Number.isFinite(composition.height)) {
      issues.push({
        severity: "error",
        code: "INVALID_SETTINGS",
        message: `Composition height must be a positive finite number, got ${composition.height}`,
        path: "composition.height",
      });
    }

    if (!composition.fps || composition.fps <= 0 || !Number.isFinite(composition.fps)) {
      issues.push({
        severity: "error",
        code: "INVALID_SETTINGS",
        message: `Composition fps must be a positive finite number, got ${composition.fps}`,
        path: "composition.fps",
      });
    }

    if (!composition.duration || composition.duration <= 0 || !Number.isFinite(composition.duration)) {
      issues.push({
        severity: "error",
        code: "INVALID_SETTINGS",
        message: `Composition duration must be a positive finite number, got ${composition.duration}`,
        path: "composition.duration",
      });
    }

    // 2. Validar Elementos y Referencias
    const allElements: BaseElement[] = [];
    const collectElements = (elems: BaseElement[]) => {
      for (const elem of elems) {
        allElements.push(elem);
        if (elem instanceof GroupElement) {
          collectElements(elem.getChildren());
        }
      }
    };
    collectElements(composition.getElements());

    const seenElementIds = new Set<string>();
    for (const elem of allElements) {
      // ID vacío o duplicado
      if (!elem.id || !elem.id.trim()) {
        issues.push({
          severity: "error",
          code: "INVALID_TIME",
          message: "Element has empty or invalid ID",
          elementId: elem.id,
        });
      } else if (seenElementIds.has(elem.id)) {
        issues.push({
          severity: "error",
          code: "DUPLICATE_ELEMENT_ID",
          message: `Duplicate element ID '${elem.id}' found in composition`,
          elementId: elem.id,
        });
      }
      seenElementIds.add(elem.id);

      // Timing
      if (elem.startTime === undefined || elem.startTime < 0 || !Number.isFinite(elem.startTime)) {
        issues.push({
          severity: "error",
          code: "INVALID_TIME",
          message: `Element '${elem.id}' has invalid startTime: ${elem.startTime}`,
          elementId: elem.id,
          path: `elements.${elem.id}.startTime`,
        });
      }

      if (elem.duration === undefined || elem.duration <= 0 || !Number.isFinite(elem.duration)) {
        issues.push({
          severity: "error",
          code: "INVALID_DURATION",
          message: `Element '${elem.id}' has invalid duration: ${elem.duration}`,
          elementId: elem.id,
          path: `elements.${elem.id}.duration`,
        });
      }

      // Referencias a Assets
      if (elem instanceof ImageElement || elem instanceof VideoElement || elem instanceof AudioElement) {
        const assetId = elem.assetId;
        if (!assetId || !composition.assets.has(assetId)) {
          issues.push({
            severity: "error",
            code: "MISSING_ASSET",
            message: `Element '${elem.id}' references missing asset '${assetId}'`,
            elementId: elem.id,
            assetId,
            path: `elements.${elem.id}.assetId`,
          });
        }
      }

      // Referencias a Parent
      if (elem.parentId) {
        if (!seenElementIds.has(elem.parentId) && !allElements.some((e) => e.id === elem.parentId)) {
          issues.push({
            severity: "error",
            code: "MISSING_PARENT",
            message: `Element '${elem.id}' references non-existent parent '${elem.parentId}'`,
            elementId: elem.id,
            path: `elements.${elem.id}.parentId`,
          });
        }
      }

      // Validar Transforms contra NaN / Infinity
      const checkTransformNumber = (val: number, name: string) => {
        if (typeof val !== "number" || !Number.isFinite(val)) {
          issues.push({
            severity: "error",
            code: "INVALID_TRANSFORM",
            message: `Element '${elem.id}' transform property '${name}' has invalid value: ${val}`,
            elementId: elem.id,
          });
        }
      };

      const pos = elem.transform.position.getValue();
      checkTransformNumber(pos.x, "position.x");
      checkTransformNumber(pos.y, "position.y");

      const scl = elem.transform.scale.getValue();
      checkTransformNumber(scl.x, "scale.x");
      checkTransformNumber(scl.y, "scale.y");

      checkTransformNumber(elem.transform.rotation.getValue(), "rotation");
      checkTransformNumber(elem.transform.opacity.getValue(), "opacity");
    }

    // 3. Validar Ciclos de Parenting
    for (const elem of allElements) {
      const visited = new Set<string>();
      let current: BaseElement | undefined = elem;
      while (current && current.parentId) {
        if (visited.has(current.id)) {
          issues.push({
            severity: "error",
            code: "PARENT_CYCLE",
            message: `Parent cycle detected involving element '${elem.id}'`,
            elementId: elem.id,
          });
          break;
        }
        visited.add(current.id);
        current = allElements.find((e) => e.id === current?.parentId);
      }
    }

    return {
      isValid: issues.filter((i) => i.severity === "error").length === 0,
      issues,
    };
  }

  /**
   * Asegura que el proyecto sea 100% válido o lanza ValidationError con el resumen de fallos.
   */
  public static assertValid(composition: Composition): void {
    const report = this.validate(composition);
    if (!report.isValid) {
      const errorSummaries = report.issues
        .filter((i) => i.severity === "error")
        .map((i) => `[${i.code}] ${i.message}`)
        .join("; ");
      throw new ValidationError(`Project validation failed: ${errorSummaries}`);
    }
  }
}
