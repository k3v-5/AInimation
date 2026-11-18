import { ProjectRuntime } from "../../runtime/ProjectRuntime.js";
import { McpValidationError } from "../errors/mcp-errors.js";

/**
 * Handler de la herramienta MCP `list_project_revisions` (Fase 18).
 */
export async function handleListProjectRevisions(runtime: ProjectRuntime, rawArgs: unknown) {
  const projectId = (rawArgs as any)?.projectId;
  if (!projectId || typeof projectId !== "string") {
    throw new McpValidationError("projectId is required for list_project_revisions");
  }

  const revisions = await runtime.listRevisions(projectId);
  return {
    projectId,
    totalRevisions: revisions.length,
    revisions,
  };
}
