import { Time } from "../core/types.js";
import { ProjectMetadata, RuntimeConfig } from "../schemas/runtime.schema.js";

export type { ProjectMetadata, RuntimeConfig };

export interface RevisionInfo {
  revisionId: string;
  parentRevisionId?: string;
  operation: string;
  createdAt: string;
  contentHash: string;
  summary: {
    layerCount: number;
    elementCount: number;
    duration: number;
    fps: number;
    width: number;
    height: number;
  };
}

export type HealthStatus = "healthy" | "warning" | "degraded" | "invalid" | "corrupted";

export interface Diagnostic {
  severity: "error" | "warning" | "info";
  code: string;
  message: string;
  path?: string;
  context?: Record<string, unknown>;
}

export interface HealthReport {
  status: HealthStatus;
  projectId: string;
  revisionId: string;
  errors: Diagnostic[];
  warnings: Diagnostic[];
  determinism: {
    verified: boolean;
    hash?: string;
  };
  persistence: {
    readable: boolean;
    writable: boolean;
    checksumValid: boolean;
  };
}

export interface DiffEntry {
  path: string;
  type: "added" | "removed" | "modified";
  before?: unknown;
  after?: unknown;
  description: string;
}

export interface TimingChange {
  entityId: string;
  entityName: string;
  before: { startTime: Time; duration: Time };
  after: { startTime: Time; duration: Time };
}

export interface AssetChange {
  assetId: string;
  type: "added" | "removed" | "updated";
}

export interface ProjectDiff {
  projectId: string;
  fromRevisionId: string;
  toRevisionId: string;
  added: DiffEntry[];
  removed: DiffEntry[];
  modified: DiffEntry[];
  timingChanges: TimingChange[];
  assetChanges: AssetChange[];
  summary: {
    layersAdded: number;
    layersRemoved: number;
    layersModified: number;
    timingModifications: number;
    assetModifications: number;
  };
}

export interface JournalEntry {
  operationId: string;
  projectId: string;
  baseRevisionId: string;
  operation: string;
  startedAt: string;
  status: "started" | "committed" | "rolled_back" | "failed";
  payloadHash: string;
}

export interface RuntimeOperation {
  operationId: string;
  projectId: string;
  type: string;
  status: "queued" | "running" | "completed" | "failed" | "cancelled";
  progress: number;
  startedAt?: string;
  completedAt?: string;
  error?: Error;
}
