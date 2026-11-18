import { ProjectRuntime } from "../../runtime/ProjectRuntime.js";
import { McpValidationError } from "../errors/mcp-errors.js";

/**
 * Handler de la herramienta MCP `get_project_status` (Fase 18).
 */
export async function handleGetProjectStatus(runtime: ProjectRuntime, rawArgs: unknown) {
  const projectId = (rawArgs as any)?.projectId;
  if (!projectId || typeof projectId !== "string") {
    throw new McpValidationError("projectId is required for get_project_status");
  }

  const status = await runtime.getStatus(projectId);
  const health = await runtime.validateProject(projectId, false);

  return {
    ...status,
    healthStatus: health.status,
    errorsCount: health.errors.length,
    warningsCount: health.warnings.length,
  };
}
