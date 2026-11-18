import { ProjectRuntime } from "../../runtime/ProjectRuntime.js";
import { RestoreProjectRevisionInputSchema } from "../../schemas/runtime.schema.js";
import { McpValidationError } from "../errors/mcp-errors.js";

/**
 * Handler de la herramienta MCP `restore_project_revision` (Fase 18).
 */
export async function handleRestoreProjectRevision(runtime: ProjectRuntime, rawArgs: unknown) {
  const parseResult = RestoreProjectRevisionInputSchema.safeParse(rawArgs);
  if (!parseResult.success) {
    throw new McpValidationError("Invalid arguments for restore_project_revision", {
      issues: parseResult.error.issues,
    });
  }

  const { projectId, targetRevisionId, description } = parseResult.data;
  const envelope = await runtime.restoreRevision(projectId, targetRevisionId, description);

  return {
    projectId,
    restoredFromRevisionId: targetRevisionId,
    newRevisionId: envelope.revisionId,
    contentHash: envelope.contentHash,
    status: "restored",
  };
}
