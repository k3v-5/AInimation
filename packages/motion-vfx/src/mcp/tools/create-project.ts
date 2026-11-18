import { Composition } from "../../core/composition.js";
import { ProjectRuntime } from "../../runtime/ProjectRuntime.js";
import { CreateProjectInputSchema } from "../../schemas/runtime.schema.js";
import { McpValidationError } from "../errors/mcp-errors.js";

/**
 * Handler de la herramienta MCP `create_project` (Fase 18).
 */
export async function handleCreateProject(runtime: ProjectRuntime, rawArgs: unknown) {
  const parseResult = CreateProjectInputSchema.safeParse(rawArgs);
  if (!parseResult.success) {
    throw new McpValidationError("Invalid arguments for create_project", {
      issues: parseResult.error.issues,
    });
  }

  const args = parseResult.data;
  const projectId = `proj_${Date.now().toString(36)}_${Math.random().toString(36).slice(2, 6)}`;

  const compData = args.projectIR ?? {
    schemaVersion: "1.8.0",
    composition: {
      id: `comp_${projectId}`,
      name: args.name,
      width: args.width,
      height: args.height,
      fps: args.fps,
      duration: args.duration,
      layers: [],
    },
    elements: [],
    assets: [],
  };

  const session = await runtime.createProject({
    projectId,
    project: compData,
    metadata: {
      name: args.name,
      description: args.description,
    },
  });

  return {
    projectId: session.projectId,
    revisionId: session.revisionId,
    contentHash: session.contentHash,
    status: "created",
    metadata: {
      name: args.name,
      width: args.width,
      height: args.height,
      fps: args.fps,
      duration: args.duration,
    },
  };
}
