/**
 * REQ-025: Data Visualization Structured Errors & Classes.
 */

export type DataVizIssueSeverity = "BLOCKING" | "WARNING";

export interface DataVizIssue {
  code: string;
  path: string;
  message: string;
  severity: DataVizIssueSeverity;
}

export class DataVizError extends Error {
  public readonly code: string;
  public readonly path: string;
  public readonly severity: DataVizIssueSeverity;

  constructor(message: string, code = "DATAVIZ_ERROR", path = "", severity: DataVizIssueSeverity = "BLOCKING") {
    super(message);
    this.name = "DataVizError";
    this.code = code;
    this.path = path;
    this.severity = severity;
  }
}

export class DatasetValidationError extends DataVizError {
  constructor(message: string, code = "DATASET_VALIDATION_ERROR", path = "") {
    super(message, code, path, "BLOCKING");
    this.name = "DatasetValidationError";
  }
}

export class DatasetTooLargeError extends DataVizError {
  constructor(message: string, path = "") {
    super(message, "DATASET_TOO_LARGE", path, "BLOCKING");
    this.name = "DatasetTooLargeError";
  }
}

export class UnsupportedScaleError extends DataVizError {
  constructor(message: string, path = "scale") {
    super(message, "UNSUPPORTED_SCALE_TYPE", path, "BLOCKING");
    this.name = "UnsupportedScaleError";
  }
}

export class ScaleError extends DataVizError {
  constructor(message: string, code = "SCALE_ERROR", path = "scale") {
    super(message, code, path, "BLOCKING");
    this.name = "ScaleError";
  }
}

export class LayoutOverflowError extends DataVizError {
  constructor(message: string, code = "LAYOUT_OVERFLOW", path = "layout") {
    super(message, code, path, "BLOCKING");
    this.name = "LayoutOverflowError";
  }
}

export class LabelCollisionError extends DataVizError {
  constructor(message: string, code = "LABEL_COLLISION", path = "labels") {
    super(message, code, path, "BLOCKING");
    this.name = "LabelCollisionError";
  }
}

export class JsxCompilationError extends DataVizError {
  constructor(message: string, code = "JSX_COMPILATION_ERROR", path = "compiler") {
    super(message, code, path, "BLOCKING");
    this.name = "JsxCompilationError";
  }
}
