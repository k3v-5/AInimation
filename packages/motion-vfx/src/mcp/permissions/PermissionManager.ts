import { MCPToolCategory, MCPStructuredError } from "../types/index.js";
import { MCPErrorCatalog } from "../errors/MCPErrorCatalog.js";

/**
 * Gestor de permisos y sandbox de seguridad del MCP (Fase 3 Kernel MCP / REQ-014, REQ-030).
 * Impide ejecución arbitraria de eval(), scripts no sanitizados o comandos shell fuera del compilador formal.
 */
export class PermissionManager {
  private static readonly AUTHORIZED_CATEGORIES: Set<MCPToolCategory> = new Set([
    "discovery",
    "inspection",
    "planning",
    "mutation",
    "intelligence",
    "production",
  ]);

  private static readonly FORBIDDEN_TOKENS = [
    "eval(",
    "Function(",
    "child_process",
    "exec(",
    "spawn(",
    "__proto__",
    "constructor.prototype",
  ];

  /**
   * Valida si una categoría y payload cumplen las políticas de seguridad.
   */
  public static validate(
    category: MCPToolCategory,
    toolName: string,
    payload: unknown
  ): { valid: boolean; error?: MCPStructuredError } {
    if (!this.AUTHORIZED_CATEGORIES.has(category)) {
      return {
        valid: false,
        error: MCPErrorCatalog.create(
          "UNAUTHORIZED_CAPABILITY",
          `Category '${category}' is not an authorized MCP capability.`
        ),
      };
    }

    const payloadString = JSON.stringify(payload);
    for (const token of this.FORBIDDEN_TOKENS) {
      if (payloadString.includes(token)) {
        return {
          valid: false,
          error: MCPErrorCatalog.create(
            "UNAUTHORIZED_CAPABILITY",
            `Security violation: forbidden token '${token}' detected in tool call payload.`,
            { severity: "fatal", recoverable: false }
          ),
        };
      }
    }

    return { valid: true };
  }
}
