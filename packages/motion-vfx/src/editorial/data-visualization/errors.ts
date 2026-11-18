/**
 * REQ-025 §36, §55: Errores tipados y estructurados del Data Visualization Engine.
 */

export interface DataVisualizationError {
  code: string;
  message: string;
  path?: string;
  severity: "BLOCKING" | "WARNING" | "SUGGESTION";
  column?: string;
  row?: number;
  field?: string;
  cause?: string;
}

export class DataVisualizationBaseException extends Error {
  public readonly details: DataVisualizationError;

  constructor(details: DataVisualizationError) {
    super(`[${details.code}] ${details.message}`);
    this.name = this.constructor.name;
    this.details = details;
  }
}

export class DataVisualizationValidationError extends DataVisualizationBaseException {
  constructor(message: string, details?: Partial<DataVisualizationError>) {
    super({
      code: details?.code ?? "DV_VALIDATION_ERROR",
      message,
      severity: details?.severity ?? "BLOCKING",
      ...details,
    });
  }
}

export class DatasetValidationError extends DataVisualizationBaseException {
  constructor(message: string, details?: Partial<DataVisualizationError>) {
    super({
      code: details?.code ?? "DV_DATASET_ERROR",
      message,
      severity: details?.severity ?? "BLOCKING",
      ...details,
    });
  }
}

export class VisualizationCompilationError extends DataVisualizationBaseException {
  constructor(message: string, details?: Partial<DataVisualizationError>) {
    super({
      code: details?.code ?? "DV_COMPILATION_ERROR",
      message,
      severity: details?.severity ?? "BLOCKING",
      ...details,
    });
  }
}

export class SafeZoneViolationError extends DataVisualizationBaseException {
  constructor(message: string, details?: Partial<DataVisualizationError>) {
    super({
      code: details?.code ?? "DV_SAFE_ZONE_VIOLATION",
      message,
      severity: details?.severity ?? "BLOCKING",
      ...details,
    });
  }
}

export class ScaleCalculationError extends DataVisualizationBaseException {
  constructor(message: string, details?: Partial<DataVisualizationError>) {
    super({
      code: details?.code ?? "DV_SCALE_CALCULATION_ERROR",
      message,
      severity: details?.severity ?? "BLOCKING",
      ...details,
    });
  }
}
