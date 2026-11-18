/**
 * REQ-025: Sistema estructurado de errores y diagnósticos para Data Visualization Engine.
 */

export type DataVisualizationErrorCode =
  | "DATASET_EMPTY"
  | "COLUMN_NOT_FOUND"
  | "COLUMN_TYPE_MISMATCH"
  | "INVALID_NUMBER"
  | "INVALID_DATE"
  | "NULL_VALUE"
  | "DUPLICATE_DATA"
  | "ZERO_RANGE"
  | "INVALID_SCALE"
  | "INVALID_DURATION"
  | "UNSUPPORTED_CHART"
  | "LAYOUT_OVERFLOW"
  | "SAFE_ZONE_VIOLATION";

export class DataVisualizationError extends Error {
  public readonly code: DataVisualizationErrorCode;
  public readonly path?: string;
  public readonly rowIndex?: number;
  public readonly column?: string;

  constructor(params: {
    code: DataVisualizationErrorCode;
    message: string;
    path?: string;
    rowIndex?: number;
    column?: string;
  }) {
    super(`[${params.code}] ${params.message}`);
    this.name = "DataVisualizationError";
    this.code = params.code;
    this.path = params.path;
    this.rowIndex = params.rowIndex;
    this.column = params.column;
    Object.setPrototypeOf(this, DataVisualizationError.prototype);
  }

  public toJSON() {
    return {
      code: this.code,
      message: this.message,
      path: this.path,
      rowIndex: this.rowIndex,
      column: this.column,
    };
  }
}
