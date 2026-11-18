import {
  DataVisualizationDataset,
  DuplicatePolicy,
  DataVisualizationDiagnostic,
} from "./types.js";
import { DataVisualizationError } from "./errors.js";

/**
 * REQ-025 §7 & §30: Validación matemática y de esquema estricta de datasets.
 */

export interface DatasetValidationOptions {
  duplicatePolicy?: DuplicatePolicy;
  strict?: boolean;
}

export function validateDataset(
  dataset: DataVisualizationDataset,
  options: DatasetValidationOptions = {}
): DataVisualizationDiagnostic[] {
  const diagnostics: DataVisualizationDiagnostic[] = [];
  const duplicatePolicy = options.duplicatePolicy ?? "REJECT";

  // 1. Dataset vacío
  if (!dataset || !dataset.rows || dataset.rows.length === 0) {
    diagnostics.push({
      severity: "ERROR",
      code: "DATASET_EMPTY",
      message: "El dataset no contiene filas de datos.",
      path: "rows",
    });
    if (options.strict) {
      throw new DataVisualizationError({
        code: "DATASET_EMPTY",
        message: "El dataset no contiene filas de datos.",
        path: "rows",
      });
    }
    return diagnostics;
  }

  // 2. Columnas válidas y únicas
  if (!dataset.columns || dataset.columns.length === 0) {
    diagnostics.push({
      severity: "ERROR",
      code: "COLUMN_NOT_FOUND",
      message: "El dataset debe declarar al menos una columna.",
      path: "columns",
    });
    if (options.strict) {
      throw new DataVisualizationError({
        code: "COLUMN_NOT_FOUND",
        message: "El dataset debe declarar al menos una columna.",
        path: "columns",
      });
    }
    return diagnostics;
  }

  const columnKeys = new Set<string>();
  const columnMap = new Map<string, string>();
  for (let c = 0; c < dataset.columns.length; c++) {
    const col = dataset.columns[c];
    if (columnKeys.has(col.key)) {
      diagnostics.push({
        severity: "ERROR",
        code: "DUPLICATE_DATA",
        message: `Columna duplicada con clave '${col.key}'.`,
        path: `columns[${c}].key`,
      });
    }
    columnKeys.add(col.key);
    columnMap.set(col.key, col.type);
  }

  // 3. Validación de filas y valores
  const seenRowKeys = new Set<string>();

  for (let r = 0; r < dataset.rows.length; r++) {
    const row = dataset.rows[r];

    // Detección de duplicados
    const rowSignature = JSON.stringify(row);
    if (seenRowKeys.has(rowSignature)) {
      if (duplicatePolicy === "REJECT") {
        diagnostics.push({
          severity: "ERROR",
          code: "DUPLICATE_DATA",
          message: `Fila duplicada detectada en el índice ${r}.`,
          path: `rows[${r}]`,
          rowIndex: r,
        });
      } else {
        diagnostics.push({
          severity: "WARNING",
          code: "DUPLICATE_DATA",
          message: `Fila duplicada en índice ${r} procesada bajo política ${duplicatePolicy}.`,
          path: `rows[${r}]`,
          rowIndex: r,
        });
      }
    }
    seenRowKeys.add(rowSignature);

    // Tipos de valores por columna
    for (const col of dataset.columns) {
      const val = row[col.key];

      if (val === undefined) {
        diagnostics.push({
          severity: "WARNING",
          code: "NULL_VALUE",
          message: `Valor indefinido en columna '${col.key}', fila ${r}.`,
          path: `rows[${r}].${col.key}`,
          rowIndex: r,
          column: col.key,
        });
        continue;
      }

      if (val === null) {
        // null es un valor ausente válido pero explícito, no un 0
        continue;
      }

      if (col.type === "NUMBER") {
        if (typeof val !== "number" || !Number.isFinite(val)) {
          diagnostics.push({
            severity: "ERROR",
            code: "INVALID_NUMBER",
            message: `Valor '${val}' en columna '${col.key}' (fila ${r}) no es un número finito válido.`,
            path: `rows[${r}].${col.key}`,
            rowIndex: r,
            column: col.key,
          });
        }
      } else if (col.type === "DATE") {
        const parsedTime = typeof val === "number" ? val : Date.parse(String(val));
        if (Number.isNaN(parsedTime)) {
          diagnostics.push({
            severity: "ERROR",
            code: "INVALID_DATE",
            message: `Valor '${val}' en columna '${col.key}' (fila ${r}) no es una fecha válida.`,
            path: `rows[${r}].${col.key}`,
            rowIndex: r,
            column: col.key,
          });
        }
      } else if (col.type === "BOOLEAN") {
        if (typeof val !== "boolean") {
          diagnostics.push({
            severity: "ERROR",
            code: "COLUMN_TYPE_MISMATCH",
            message: `Valor '${val}' en columna '${col.key}' (fila ${r}) no es un booleano.`,
            path: `rows[${r}].${col.key}`,
            rowIndex: r,
            column: col.key,
          });
        }
      } else if (col.type === "STRING") {
        if (typeof val !== "string") {
          diagnostics.push({
            severity: "WARNING",
            code: "COLUMN_TYPE_MISMATCH",
            message: `Valor no string en columna '${col.key}' (fila ${r}).`,
            path: `rows[${r}].${col.key}`,
            rowIndex: r,
            column: col.key,
          });
        }
      }
    }
  }

  if (options.strict) {
    const blocking = diagnostics.find((d) => d.severity === "ERROR");
    if (blocking) {
      throw new DataVisualizationError({
        code: blocking.code as any,
        message: blocking.message,
        path: blocking.path,
      });
    }
  }

  return diagnostics;
}

export function assertValidDataset(
  dataset: DataVisualizationDataset,
  options: DatasetValidationOptions = {}
): void {
  validateDataset(dataset, { ...options, strict: true });
}

import { Dataset, ValidationResult, DatasetValidationError } from "./contracts.js";

/**
 * REQ-025 §5: Validación estricta del Dataset canónico.
 * Rechaza NaN, Infinity, -Infinity, strings vacíos, datasets vacíos, y valida etiquetas y timestamps.
 */
export function validateCanonicalDataset(dataset: Dataset): ValidationResult {
  const errors: DatasetValidationError[] = [];

  if (!dataset || !dataset.id || dataset.id.trim() === "") {
    errors.push({
      code: "DATASET_ID_EMPTY",
      severity: "BLOCKING",
      field: "id",
      message: "El identificador del dataset no puede estar vacío.",
    });
  }

  if (!dataset.values || !Array.isArray(dataset.values) || dataset.values.length === 0) {
    errors.push({
      code: "DATASET_EMPTY",
      severity: "BLOCKING",
      field: "values",
      message: "El dataset debe contener al menos un valor.",
    });
    return { valid: false, errors };
  }

  const seenLabels = new Set<string>();

  for (let i = 0; i < dataset.values.length; i++) {
    const val = dataset.values[i];

    if (!val.label || typeof val.label !== "string" || val.label.trim() === "") {
      errors.push({
        code: "LABEL_REQUIRED",
        severity: "BLOCKING",
        field: "label",
        index: i,
        message: `El valor en el índice ${i} no contiene una etiqueta válida.`,
      });
    } else {
      if (seenLabels.has(val.label)) {
        errors.push({
          code: "DUPLICATE_LABEL",
          severity: "WARNING",
          field: "label",
          index: i,
          message: `Etiqueta duplicada '${val.label}' en el índice ${i}.`,
        });
      }
      seenLabels.add(val.label);
    }

    if (val.value === undefined || val.value === null || typeof val.value !== "number") {
      errors.push({
        code: "VALUE_NOT_NUMERIC",
        severity: "BLOCKING",
        field: "value",
        index: i,
        message: `El valor en el índice ${i} no es numérico.`,
      });
    } else if (Number.isNaN(val.value)) {
      errors.push({
        code: "VALUE_NAN",
        severity: "BLOCKING",
        field: "value",
        index: i,
        message: `El valor en el índice ${i} es NaN.`,
      });
    } else if (!Number.isFinite(val.value)) {
      errors.push({
        code: "VALUE_INFINITY",
        severity: "BLOCKING",
        field: "value",
        index: i,
        message: `El valor en el índice ${i} es infinito (${val.value}).`,
      });
    }

    if (val.timestamp !== undefined) {
      if (typeof val.timestamp !== "number" || isNaN(val.timestamp) || !Number.isFinite(val.timestamp) || val.timestamp < 0) {
        errors.push({
          code: "INVALID_TIMESTAMP",
          severity: "BLOCKING",
          field: "timestamp",
          index: i,
          message: `Timestamp inválido (${val.timestamp}) en el índice ${i}.`,
        });
      }
    }
  }

  return {
    valid: errors.filter((e) => e.severity === "BLOCKING").length === 0,
    errors,
  };
}

export function assertValidCanonicalDataset(dataset: Dataset): void {
  const result = validateCanonicalDataset(dataset);
  const blocking = result.errors.find((e) => e.severity === "BLOCKING");
  if (blocking) {
    throw new Error(`[DATA_VALIDATION_ERROR] ${blocking.code}: ${blocking.message}`);
  }
}
