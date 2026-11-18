import { Composition } from "../../core/composition.js";

export type MCPToolCategory =
  | "discovery"
  | "inspection"
  | "planning"
  | "mutation"
  | "intelligence"
  | "production";

export type MCPErrorCode =
  | "INVALID_PROJECT"
  | "INVALID_OPERATION"
  | "VERSION_CONFLICT"
  | "OBJECT_NOT_FOUND"
  | "ASSET_NOT_FOUND"
  | "FONT_NOT_FOUND"
  | "UNAUTHORIZED_CAPABILITY"
  | "AE_DISCONNECTED"
  | "AE_TIMEOUT"
  | "COMPILATION_ERROR"
  | "RENDER_ERROR"
  | "QA_FAILURE"
  | "CONSTRAINT_FAILURE"
  | "RESOURCE_LIMIT_EXCEEDED"
  | "TRANSACTION_ABORTED"
  | "IDEMPOTENCY_COLLISION"
  | "RECONCILIATION_MISMATCH";

export interface MCPStructuredError {
  errorCode: MCPErrorCode;
  severity: "critical" | "warning" | "fatal";
  recoverable: boolean;
  objectId?: string;
  message: string;
  suggestedActions: string[];
  context?: Record<string, unknown>;
}

export interface MCPRequestEnvelope<T = Record<string, unknown>> {
  operationId: string; // UUID inmutable para idempotencia
  toolName: string;
  category: MCPToolCategory;
  expectedVersion?: number; // Versionado optimista
  transactionId?: string; // Transacción opcional
  dryRun?: boolean; // Simulación sin mutaciones
  params: T;
}

export interface MCPResponseEnvelope<T = unknown> {
  operationId: string;
  success: boolean;
  projectVersion: number;
  projectHash: string;
  result?: T;
  error?: MCPStructuredError;
  dryRunReport?: {
    plannedChanges: number;
    warnings: string[];
    estimatedRenderTimeSec: number;
  };
}

export interface TransactionSnapshot {
  transactionId: string;
  initialVersion: number;
  initialHash: string;
  compositionSnapshot: Composition;
  operationsLog: string[];
  status: "active" | "committed" | "rolled_back";
}
