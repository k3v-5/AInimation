import { ProjectRuntime } from "../../runtime/ProjectRuntime.js";
import { CloseProjectInputSchema } from "../../schemas/runtime.schema.js";
import { McpValidationError } from "../errors/mcp-errors.js";

/**
 * Handler de la herramienta MCP `close_project` (Fase 18).
 */
export async function handleCloseProject(runtime: ProjectRuntime, rawArgs: unknown) {
  const parseResult = CloseProjectInputSchema.safeParse(rawArgs);
  if (!parseResult.success) {
    throw new McpValidationError("Invalid arguments for close_project", {
      issues: parseResult.error.issues,
    });
  }

  const { projectId } = parseResult.data;
  await runtime.closeProject(projectId);

  return {
    projectId,
    status: "closed",
  };
}
