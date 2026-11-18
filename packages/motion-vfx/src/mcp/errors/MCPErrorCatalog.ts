import { MCPErrorCode, MCPStructuredError } from "../types/index.js";

/**
 * Catálogo estructurado de errores formales para agentes IA (Fase 3 Kernel MCP / REQ-016).
 * Todo error devuelto por el MCP contiene códigos normalizados, estado de recuperabilidad y acciones sugeridas.
 */
export class MCPErrorCatalog {
  public static create(
    code: MCPErrorCode,
    message: string,
    options: {
      objectId?: string;
      severity?: MCPStructuredError["severity"];
      recoverable?: boolean;
      suggestedActions?: string[];
      context?: Record<string, unknown>;
    } = {}
  ): MCPStructuredError {
    const defaultActions = this.getDefaultSuggestedActions(code);

    return {
      errorCode: code,
      severity: options.severity ?? this.getDefaultSeverity(code),
      recoverable: options.recoverable ?? this.isNaturallyRecoverable(code),
      objectId: options.objectId,
      message,
      suggestedActions: options.suggestedActions ?? defaultActions,
      context: options.context,
    };
  }

  private static getDefaultSeverity(code: MCPErrorCode): MCPStructuredError["severity"] {
    switch (code) {
      case "VERSION_CONFLICT":
      case "IDEMPOTENCY_COLLISION":
      case "RESOURCE_LIMIT_EXCEEDED":
      case "CONSTRAINT_FAILURE":
        return "warning";
      case "AE_DISCONNECTED":
      case "AE_TIMEOUT":
      case "TRANSACTION_ABORTED":
      case "COMPILATION_ERROR":
      case "RECONCILIATION_MISMATCH":
        return "critical";
      default:
        return "critical";
    }
  }

  private static isNaturallyRecoverable(code: MCPErrorCode): boolean {
    switch (code) {
      case "VERSION_CONFLICT":
      case "FONT_NOT_FOUND":
      case "CONSTRAINT_FAILURE":
      case "QA_FAILURE":
      case "RECONCILIATION_MISMATCH":
      case "IDEMPOTENCY_COLLISION":
        return true;
      default:
        return false;
    }
  }

  private static getDefaultSuggestedActions(code: MCPErrorCode): string[] {
    switch (code) {
      case "VERSION_CONFLICT":
        return ["inspect_project", "reapply_with_latest_version"];
      case "FONT_NOT_FOUND":
        return ["use_fallback_font", "register_font_variant"];
      case "CONSTRAINT_FAILURE":
        return ["auto_reframe", "adjust_safe_zones", "relocate_text"];
      case "QA_FAILURE":
        return ["fix_qa_issues", "adjust_timings", "remove_black_gaps"];
      case "RECONCILIATION_MISMATCH":
        return ["reinspect_ae_state", "resync_layer_transforms"];
      case "AE_DISCONNECTED":
        return ["reconnect_bridge", "restart_after_effects"];
      case "IDEMPOTENCY_COLLISION":
        return ["use_cached_result", "generate_new_operation_id"];
      default:
        return ["inspect_project_errors", "abort_transaction"];
    }
  }
}
