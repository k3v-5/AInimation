import {
  VisualizationDataset,
  ValidationResult,
  ValidationIssue,
  DataPoint,
} from "./types.js";

/**
 * REQ-025 §6: Validador determinista y estricto de datasets para visualización.
 */
export function validateVisualizationDataset(
  dataset: VisualizationDataset
): ValidationResult {
  const issues: ValidationIssue[] = [];

  // 1. Dataset existente y estructura base
  if (!dataset || typeof dataset !== "object") {
    return {
      valid: false,
      issues: [
        {
          code: "EMPTY_DATASET",
          severity: "ERROR",
          path: "dataset",
          message: "El dataset no existe o no es un objeto válido.",
        },
      ],
    };
  }

  // 2. ID obligatorio y no vacío
  if (!dataset.id || typeof dataset.id !== "string" || dataset.id.trim() === "") {
    issues.push({
      code: "INVALID_CONFIGURATION",
      severity: "ERROR",
      path: "dataset.id",
      message: "El dataset debe contener un 'id' no vacío.",
    });
  }

  // 3. Array de puntos y mínimo un punto (§6 & §40, §41)
  if (!Array.isArray(dataset.points)) {
    issues.push({
      code: "EMPTY_DATASET",
      severity: "ERROR",
      path: "dataset.points",
      message: "El dataset debe incluir un array 'points'.",
    });
    return { valid: false, issues };
  }

  if (dataset.points.length === 0) {
    issues.push({
      code: "EMPTY_DATASET",
      severity: "ERROR",
      path: "dataset.points",
      message: "El dataset no puede estar vacío (mínimo 1 punto requerido).",
    });
    return { valid: false, issues };
  }

  // 4. Verificación de precisión
  if (dataset.precision !== undefined) {
    if (
      !Number.isInteger(dataset.precision) ||
      dataset.precision < 0 ||
      dataset.precision > 10
    ) {
      issues.push({
        code: "INVALID_CONFIGURATION",
        severity: "ERROR",
        path: "dataset.precision",
        message: "La precisión debe ser un número entero entre 0 y 10.",
      });
    }
  }

  // 5. Verificación de puntos individuales
  const seenIds = new Set<string>();

  for (let i = 0; i < dataset.points.length; i++) {
    const p: DataPoint = dataset.points[i];
    const basePath = `dataset.points[${i}]`;

    if (!p || typeof p !== "object") {
      issues.push({
        code: "INVALID_VALUE",
        severity: "ERROR",
        path: basePath,
        message: `El elemento en el índice ${i} no es un objeto válido.`,
      });
      continue;
    }

    // ID obligatorio y único
    if (!p.id || typeof p.id !== "string" || p.id.trim() === "") {
      issues.push({
        code: "INVALID_CONFIGURATION",
        severity: "ERROR",
        path: `${basePath}.id`,
        message: `El punto en el índice ${i} tiene un ID inválido o vacío.`,
      });
    } else {
      if (seenIds.has(p.id)) {
        issues.push({
          code: "DUPLICATE_ID",
          severity: "ERROR",
          path: `${basePath}.id`,
          message: `ID duplicado detectado: '${p.id}'.`,
        });
      }
      seenIds.add(p.id);
    }

    // Label obligatorio
    if (p.label === undefined || p.label === null || typeof p.label !== "string") {
      issues.push({
        code: "INVALID_VALUE",
        severity: "ERROR",
        path: `${basePath}.label`,
        message: `El punto en el índice ${i} debe tener un 'label' de tipo string.`,
      });
    }

    // Value obligatorio y finito (§4)
    if (p.value === undefined || p.value === null || typeof p.value !== "number") {
      issues.push({
        code: "INVALID_VALUE",
        severity: "ERROR",
        path: `${basePath}.value`,
        message: `El punto en el índice ${i} debe tener un 'value' numérico.`,
      });
    } else if (!Number.isFinite(p.value)) {
      issues.push({
        code: "NON_FINITE_VALUE",
        severity: "ERROR",
        path: `${basePath}.value`,
        message: `El valor no es finito (detectado NaN o Infinity) en el índice ${i}.`,
      });
    }

    // Timestamp cuando exista debe ser finito
    if (p.timestamp !== undefined) {
      if (typeof p.timestamp !== "number" || !Number.isFinite(p.timestamp)) {
        issues.push({
          code: "INVALID_TIMESTAMP",
          severity: "ERROR",
          path: `${basePath}.timestamp`,
          message: `El timestamp en el índice ${i} debe ser un número finito.`,
        });
      }
    }

    // Comprobar ausencia de undefined en campos serializables
    if (p.unit !== undefined && typeof p.unit !== "string") {
      issues.push({
        code: "INVALID_VALUE",
        severity: "ERROR",
        path: `${basePath}.unit`,
        message: `El campo 'unit' debe ser string si se especifica.`,
      });
    }
  }

  // 6. Comprobar circularidad y serialización de metadata (§6 & §35)
  try {
    const seen = new WeakSet();
    const detectCircular = (obj: any) => {
      if (obj && typeof obj === "object") {
        if (seen.has(obj)) {
          throw new Error("Estructura circular detectada");
        }
        seen.add(obj);
        for (const k of Object.keys(obj)) {
          if (typeof obj[k] === "function") {
            throw new Error(`Función detectada en propiedad '${k}'`);
          }
          detectCircular(obj[k]);
        }
      }
    };
    detectCircular(dataset);
  } catch (err: any) {
    issues.push({
      code: "INVALID_CONFIGURATION",
      severity: "ERROR",
      path: "dataset.metadata",
      message: err.message || "Metadata no serializable o circular.",
    });
  }

  return {
    valid: issues.filter((iss) => iss.severity === "ERROR").length === 0,
    issues,
  };
}
