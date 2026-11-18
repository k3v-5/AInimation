import { DataSet } from "./types.js";
import { DataVisualizationError } from "./errors.js";

/**
 * REQ-025 §36, §37: Validador exhaustivo de Datasets.
 */

export interface DatasetValidationOptions {
  requiredColumns?: string[];
  allowEmptyRows?: boolean;
}

export function validateDataset(
  dataset: DataSet | null | undefined,
  options: DatasetValidationOptions = {}
): DataVisualizationError[] {
  const errors: DataVisualizationError[] = [];

  if (!dataset) {
    errors.push({
      code: "DATASET_NULL",
      message: "El dataset proporcionado es nulo o indefinido.",
      severity: "BLOCKING",
    });
    return errors;
  }

  if (!dataset.id || typeof dataset.id !== "string" || dataset.id.trim() === "") {
    errors.push({
      code: "DATASET_ID_MISSING",
      message: "El dataset debe tener un identificador 'id' no vacío.",
      severity: "BLOCKING",
    });
  }

  if (!Array.isArray(dataset.columns) || dataset.columns.length === 0) {
    errors.push({
      code: "DATASET_COLUMNS_EMPTY",
      message: "El dataset no tiene columnas declaradas.",
      severity: "BLOCKING",
    });
    return errors;
  }

  const columnKeys = new Set<string>();
  for (let i = 0; i < dataset.columns.length; i++) {
    const col = dataset.columns[i];
    if (!col.key || col.key.trim() === "") {
      errors.push({
        code: "COLUMN_KEY_EMPTY",
        message: `La columna en índice ${i} carece de 'key'.`,
        severity: "BLOCKING",
      });
      continue;
    }
    if (columnKeys.has(col.key)) {
      errors.push({
        code: "COLUMN_KEY_DUPLICATE",
        message: `Columna duplicada con key '${col.key}'.`,
        severity: "BLOCKING",
        column: col.key,
      });
    }
    columnKeys.add(col.key);

    if (!["STRING", "NUMBER", "DATE", "BOOLEAN"].includes(col.type)) {
      errors.push({
        code: "COLUMN_TYPE_INVALID",
        message: `Tipo de columna '${col.type}' no admitido en columna '${col.key}'.`,
        severity: "BLOCKING",
        column: col.key,
      });
    }
  }

  if (options.requiredColumns) {
    for (const reqCol of options.requiredColumns) {
      if (!columnKeys.has(reqCol)) {
        errors.push({
          code: "REQUIRED_COLUMN_MISSING",
          message: `La columna requerida '${reqCol}' no existe en el dataset.`,
          severity: "BLOCKING",
          column: reqCol,
        });
      }
    }
  }

  if (!Array.isArray(dataset.rows)) {
    errors.push({
      code: "DATASET_ROWS_INVALID",
      message: "La propiedad 'rows' del dataset debe ser un array.",
      severity: "BLOCKING",
    });
    return errors;
  }

  if (!options.allowEmptyRows && dataset.rows.length === 0) {
    errors.push({
      code: "DATASET_ROWS_EMPTY",
      message: "El dataset no contiene filas de datos.",
      severity: "BLOCKING",
    });
    return errors;
  }

  // Validar filas y tipos de datos
  for (let r = 0; r < dataset.rows.length; r++) {
    const row = dataset.rows[r];
    if (!row || typeof row !== "object") {
      errors.push({
        code: "ROW_NOT_OBJECT",
        message: `La fila en índice ${r} no es un objeto válido.`,
        severity: "BLOCKING",
        row: r,
      });
      continue;
    }

    for (const col of dataset.columns) {
      const val = row[col.key];
      if (val === undefined) {
        errors.push({
          code: "ROW_VALUE_UNDEFINED",
          message: `La fila ${r} no tiene definida la clave '${col.key}'.`,
          severity: "WARNING",
          column: col.key,
          row: r,
        });
        continue;
      }

      if (val === null) continue; // Los nulos se gestionan según la NullValuePolicy

      if (col.type === "NUMBER") {
        if (typeof val !== "number" || Number.isNaN(val) || !Number.isFinite(val)) {
          errors.push({
            code: "VALUE_NOT_FINITE_NUMBER",
            message: `Valor numérico no finito o NaN en fila ${r}, columna '${col.key}'.`,
            severity: "BLOCKING",
            column: col.key,
            row: r,
          });
        }
      } else if (col.type === "DATE") {
        if (typeof val === "string") {
          const parsedDate = Date.parse(val);
          if (isNaN(parsedDate)) {
            errors.push({
              code: "VALUE_INVALID_DATE",
              message: `Fecha inválida '${val}' en fila ${r}, columna '${col.key}'.`,
              severity: "BLOCKING",
              column: col.key,
              row: r,
            });
          }
        }
      }
    }
  }

  return errors;
}
