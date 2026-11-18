import { ProjectRuntime } from "../../runtime/ProjectRuntime.js";
import { ValidateProjectInputSchema } from "../../schemas/runtime.schema.js";
import { McpValidationError } from "../errors/mcp-errors.js";

/**
 * Handler de la herramienta MCP `validate_project` (Fase 18).
 */
export async function handleValidateProject(runtime: ProjectRuntime, rawArgs: unknown) {
  const parseResult = ValidateProjectInputSchema.safeParse(rawArgs);
  if (!parseResult.success) {
    throw new McpValidationError("Invalid arguments for validate_project", {
      issues: parseResult.error.issues,
    });
  }

  const { projectId, strict } = parseResult.data;
  const health = await runtime.validateProject(projectId, strict);

  return {
    projectId,
    status: health.status,
    errorsCount: health.errors.length,
    warningsCount: health.warnings.length,
    errors: health.errors,
    warnings: health.warnings,
    determinism: health.determinism,
    persistence: health.persistence,
  };
}
