import { ProjectRuntime } from "../../runtime/ProjectRuntime.js";
import { DiffProjectRevisionsInputSchema } from "../../schemas/runtime.schema.js";
import { McpValidationError } from "../errors/mcp-errors.js";

/**
 * Handler de la herramienta MCP `diff_project_revisions` (Fase 18).
 */
export async function handleDiffProjectRevisions(runtime: ProjectRuntime, rawArgs: unknown) {
  const parseResult = DiffProjectRevisionsInputSchema.safeParse(rawArgs);
  if (!parseResult.success) {
    throw new McpValidationError("Invalid arguments for diff_project_revisions", {
      issues: parseResult.error.issues,
    });
  }

  const { projectId, fromRevisionId, toRevisionId } = parseResult.data;
  const diff = await runtime.diffRevisions(projectId, fromRevisionId, toRevisionId);

  return diff;
}
