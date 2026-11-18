export type ValidationSeverity = "error" | "warning";

export type ValidationIssueCode =
  | "INVALID_SETTINGS"
  | "INVALID_DURATION"
  | "INVALID_TIME"
  | "DUPLICATE_ELEMENT_ID"
  | "DUPLICATE_ASSET_ID"
  | "MISSING_ASSET"
  | "MISSING_PARENT"
  | "PARENT_CYCLE"
  | "INVALID_TRANSFORM"
  | "INVALID_PROPERTY"
  | "UNSUPPORTED_ELEMENT_TYPE"
  | "INVALID_SCHEMA";

export interface ValidationIssue {
  severity: ValidationSeverity;
  code: ValidationIssueCode | string;
  message: string;
  path?: string;
  elementId?: string;
  assetId?: string;
}

export interface ValidationReport {
  isValid: boolean;
  issues: ValidationIssue[];
}
