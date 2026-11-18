import { ProjectRuntime } from "../../runtime/ProjectRuntime.js";
import { OpenProjectInputSchema } from "../../schemas/runtime.schema.js";
import { McpValidationError } from "../errors/mcp-errors.js";

/**
 * Handler de la herramienta MCP `open_project` (Fase 18).
 */
export async function handleOpenProject(runtime: ProjectRuntime, rawArgs: unknown) {
  const parseResult = OpenProjectInputSchema.safeParse(rawArgs);
  if (!parseResult.success) {
    throw new McpValidationError("Invalid arguments for open_project", {
      issues: parseResult.error.issues,
    });
  }

  const { projectId, readOnly } = parseResult.data;
  const session = await runtime.openProject(projectId, { readOnly });
  const health = await runtime.validateProject(projectId, false);

  return {
    projectId: session.projectId,
    revisionId: session.revisionId,
    contentHash: session.contentHash,
    status: "opened",
    healthStatus: health.status,
    readOnly,
  };
}
