import { ProjectRuntime } from "../../runtime/ProjectRuntime.js";
import { SaveProjectInputSchema } from "../../schemas/runtime.schema.js";
import { McpValidationError } from "../errors/mcp-errors.js";

/**
 * Handler de la herramienta MCP `save_project` (Fase 18).
 */
export async function handleSaveProject(runtime: ProjectRuntime, rawArgs: unknown) {
  const parseResult = SaveProjectInputSchema.safeParse(rawArgs);
  if (!parseResult.success) {
    throw new McpValidationError("Invalid arguments for save_project", {
      issues: parseResult.error.issues,
    });
  }

  const { projectId, description } = parseResult.data;
  const session = await runtime.openProject(projectId);

  const { newRevisionId } = await session.transact((draft) => draft, {
    description: description ?? "Manual save via MCP",
    operation: "save_project",
  });

  return {
    projectId,
    revisionId: newRevisionId,
    contentHash: session.contentHash,
    status: "saved",
  };
}
