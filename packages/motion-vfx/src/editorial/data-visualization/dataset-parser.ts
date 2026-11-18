import { DataSet, DataColumn, DataColumnType, DataRow, DataValue } from "./types.js";
import { DatasetValidationError } from "./errors.js";

/**
 * REQ-025 §64-§68: Parser determinista de CSV y JSON datasets.
 * Cumple con RFC 4180, normalización de saltos de línea (CRLF/LF) y stripping de BOM.
 */

export interface CsvParseOptions {
  id?: string;
  title?: string;
  hasHeader?: boolean;
  delimiter?: string;
  columns?: DataColumn[];
}

export function parseCsv(source: string, options: CsvParseOptions = {}): DataSet {
  if (!source || typeof source !== "string") {
    throw new DatasetValidationError("El contenido CSV está vacío o no es una cadena válida.");
  }

  // 1. Quitar UTF-8 BOM si existe
  let cleanSource = source;
  if (cleanSource.charCodeAt(0) === 0xfeff) {
    cleanSource = cleanSource.slice(1);
  }

  // 2. Normalizar finales de línea (CRLF -> LF)
  cleanSource = cleanSource.replace(/\r\n/g, "\n").replace(/\r/g, "\n");

  const delimiter = options.delimiter ?? ",";
  const records = parseCsvRecords(cleanSource, delimiter);

  if (records.length === 0) {
    throw new DatasetValidationError("El archivo CSV no contiene registros.");
  }

  const hasHeader = options.hasHeader ?? true;
  let headers: string[] = [];
  let dataRowsRaw: string[][] = [];

  if (hasHeader) {
    headers = records[0].map((h) => h.trim());
    dataRowsRaw = records.slice(1);
  } else {
    headers = records[0].map((_, idx) => `col_${idx}`);
    dataRowsRaw = records;
  }

  // Verificar headers no duplicados ni vacíos
  const headerSet = new Set<string>();
  for (let i = 0; i < headers.length; i++) {
    const h = headers[i];
    if (!h || h.length === 0) {
      throw new DatasetValidationError(`Cabecera vacía en la columna ${i + 1}.`);
    }
    if (headerSet.has(h)) {
      throw new DatasetValidationError(`Columna duplicada '${h}' en el dataset.`);
    }
    headerSet.add(h);
  }

  // Inferencia o mapeo de columnas
  const columns: DataColumn[] = options.columns ?? headers.map((key, colIdx) => {
    const sampleValues = dataRowsRaw.map((r) => r[colIdx]).filter((v) => v !== undefined && v !== "");
    const type = inferColumnType(sampleValues);
    return {
      key,
      label: key,
      type,
    };
  });

  // Construir DataRows estructuradas
  const rows: DataRow[] = [];
  for (let rowIdx = 0; rowIdx < dataRowsRaw.length; rowIdx++) {
    const rawRow = dataRowsRaw[rowIdx];
    // Omitir filas totalmente vacías
    if (rawRow.length === 1 && rawRow[0] === "") continue;

    const rowObj: DataRow = {};
    for (let c = 0; c < columns.length; c++) {
      const col = columns[c];
      const rawVal = rawRow[c] !== undefined ? rawRow[c] : "";
      rowObj[col.key] = parseValue(rawVal, col.type);
    }
    rows.push(rowObj);
  }

  const datasetId = options.id ?? `ds_csv_${Math.abs(hashString(cleanSource)).toString(16)}`;

  return {
    id: datasetId,
    title: options.title,
    columns,
    rows,
    metadata: {
      sourceType: "CSV",
      rowCount: rows.length,
      columnCount: columns.length,
    },
  };
}

export function parseJsonDataset(source: string | object): DataSet {
  let parsed: any;
  if (typeof source === "string") {
    try {
      parsed = JSON.parse(source);
    } catch (err: any) {
      throw new DatasetValidationError(`JSON inválido: ${err.message}`);
    }
  } else {
    parsed = source;
  }

  if (!parsed || typeof parsed !== "object") {
    throw new DatasetValidationError("El contenido JSON no es un objeto o array válido.");
  }

  // Formato Canónico 1: { id, columns, rows }
  if (Array.isArray(parsed.columns) && Array.isArray(parsed.rows)) {
    return {
      id: parsed.id ?? `ds_json_${Date.now()}`,
      title: parsed.title,
      description: parsed.description,
      columns: parsed.columns,
      rows: parsed.rows,
      metadata: parsed.metadata,
    };
  }

  // Formato Canónico 2: Array de objetos [{ col1: v1, col2: v2 }, ...]
  const arrayData = Array.isArray(parsed) ? parsed : Array.isArray(parsed.data) ? parsed.data : null;
  if (arrayData) {
    if (arrayData.length === 0) {
      return {
        id: parsed.id ?? "ds_empty",
        columns: [],
        rows: [],
      };
    }

    const firstItem = arrayData[0];
    const keys = Object.keys(firstItem);
    const columns: DataColumn[] = keys.map((key) => {
      const samples = arrayData.map((r: any) => String(r[key] ?? "")).filter((v: any) => v !== "");
      return {
        key,
        label: key,
        type: inferColumnType(samples),
      };
    });

    const rows: DataRow[] = arrayData.map((item: any) => {
      const row: DataRow = {};
      for (const col of columns) {
        const val = item[col.key];
        if (val === undefined || val === null) {
          row[col.key] = null;
        } else if (col.type === "NUMBER") {
          const num = Number(val);
          row[col.key] = Number.isFinite(num) ? num : null;
        } else if (col.type === "BOOLEAN") {
          row[col.key] = Boolean(val);
        } else {
          row[col.key] = String(val);
        }
      }
      return row;
    });

    return {
      id: parsed.id ?? "ds_json_array",
      title: parsed.title,
      columns,
      rows,
      metadata: {
        sourceType: "JSON_ARRAY",
        rowCount: rows.length,
      },
    };
  }

  throw new DatasetValidationError("Estructura JSON no reconocida para DataSet tabular.");
}

/**
 * Algoritmo RFC 4180 puro para parsing de registros CSV con soporte para comillas y saltos.
 */
function parseCsvRecords(text: string, delimiter: string): string[][] {
  const rows: string[][] = [];
  let currentRow: string[] = [];
  let currentVal = "";
  let insideQuotes = false;

  for (let i = 0; i < text.length; i++) {
    const char = text[i];
    const nextChar = text[i + 1];

    if (char === '"') {
      if (insideQuotes && nextChar === '"') {
        currentVal += '"';
        i++; // Omitir comilla escapada ""
      } else {
        insideQuotes = !insideQuotes;
      }
    } else if (char === delimiter && !insideQuotes) {
      currentRow.push(currentVal);
      currentVal = "";
    } else if (char === "\n" && !insideQuotes) {
      currentRow.push(currentVal);
      rows.push(currentRow);
      currentRow = [];
      currentVal = "";
    } else {
      currentVal += char;
    }
  }

  if (currentVal !== "" || currentRow.length > 0) {
    currentRow.push(currentVal);
    rows.push(currentRow);
  }

  return rows;
}

export function inferColumnType(values: string[]): DataColumnType {
  if (values.length === 0) return "STRING";

  let isBool = true;
  let isNum = true;
  let isDate = true;

  for (const v of values) {
    const trimmed = v.trim();
    if (trimmed === "") continue;

    // Check bool
    const lower = trimmed.toLowerCase();
    if (lower !== "true" && lower !== "false" && lower !== "1" && lower !== "0") {
      isBool = false;
    }

    // Check num
    const num = Number(trimmed);
    if (Number.isNaN(num) || !Number.isFinite(num)) {
      isNum = false;
    }

    // Check date (YYYY-MM-DD o ISO o parseable válido con longitud >= 4)
    if (trimmed.length < 4 || isNaN(Date.parse(trimmed)) || /^\d+$/.test(trimmed)) {
      isDate = false;
    }
  }

  if (isBool && values.some((v) => ["true", "false"].includes(v.toLowerCase().trim()))) return "BOOLEAN";
  if (isNum) return "NUMBER";
  if (isDate) return "DATE";
  return "STRING";
}

function parseValue(val: string, type: DataColumnType): DataValue {
  const trimmed = val.trim();
  if (trimmed === "" || trimmed.toLowerCase() === "null") return null;

  switch (type) {
    case "NUMBER": {
      const num = Number(trimmed);
      return Number.isFinite(num) ? num : null;
    }
    case "BOOLEAN": {
      const lower = trimmed.toLowerCase();
      if (lower === "true" || lower === "1") return true;
      if (lower === "false" || lower === "0") return false;
      return null;
    }
    case "DATE":
    case "STRING":
    default:
      return val;
  }
}

function hashString(str: string): number {
  let hash = 0;
  for (let i = 0; i < str.length; i++) {
    hash = (hash << 5) - hash + str.charCodeAt(i);
    hash |= 0;
  }
  return hash;
}
