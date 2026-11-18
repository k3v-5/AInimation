/**
 * Estado de fidelidad de exportación de una característica o entidad.
 */
export type CapabilityStatus = "exact" | "approximate" | "lossy" | "unsupported";

/**
 * Estrategia de degradación o adaptación aplicada cuando una característica no es exact.
 */
export type FallbackStrategy =
  | "none"
  | "convert-to-keyframes"
  | "flatten-text"
  | "drop-effect"
  | "closest-framerate"
  | "rasterize-vector"
  | "split-layers"
  | "approximate-bezier";

export interface CapabilityEntry {
  feature: string;
  status: CapabilityStatus;
  fallback: FallbackStrategy;
  description: string;
  notes?: string;
}

export interface CapabilityReport {
  target: "after-effects" | "fcpxml" | "edl";
  version: string;
  totalFeatures: number;
  exactCount: number;
  approximateCount: number;
  lossyCount: number;
  unsupportedCount: number;
  entries: CapabilityEntry[];
  warnings: string[];
}

export interface ExportPlanItem {
  entityId: string;
  entityType: string;
  feature: string;
  status: CapabilityStatus;
  fallback: FallbackStrategy;
  actionSummary: string;
}

export interface ExportPlan {
  target: "after-effects" | "fcpxml" | "edl";
  strict: boolean;
  dryRun: boolean;
  canProceed: boolean;
  items: ExportPlanItem[];
  warnings: string[];
  errors: string[];
  summary: {
    exact: number;
    approximate: number;
    lossy: number;
    unsupported: number;
  };
}
