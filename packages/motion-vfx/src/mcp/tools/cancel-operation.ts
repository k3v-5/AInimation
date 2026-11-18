import { ProjectRuntime } from "../../runtime/ProjectRuntime.js";
import { CancelOperationInputSchema } from "../../schemas/runtime.schema.js";
import { McpValidationError } from "../errors/mcp-errors.js";

/**
 * Handler de la herramienta MCP `cancel_operation` (Fase 18).
 */
export async function handleCancelOperation(runtime: ProjectRuntime, rawArgs: unknown) {
  const parseResult = CancelOperationInputSchema.safeParse(rawArgs);
  if (!parseResult.success) {
    throw new McpValidationError("Invalid arguments for cancel_operation", {
      issues: parseResult.error.issues,
    });
  }

  const { operationId, reason } = parseResult.data;
  const success = runtime.getOperationManager().cancelOperation(operationId, reason);

  return {
    operationId,
    cancelled: success,
    reason,
  };
}
