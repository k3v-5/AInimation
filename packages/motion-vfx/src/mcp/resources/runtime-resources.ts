import { ProjectRuntime } from "../../runtime/ProjectRuntime.js";
import { RuntimeMetrics } from "../../runtime/diagnostics/RuntimeMetrics.js";

/**
 * Endpoints declarativos de lectura de recursos para el Runtime de Producción (Fase 18).
 */
export class RuntimeMCPResources {
  public static async getResourceContent(runtime: ProjectRuntime, uri: string): Promise<string> {
    if (uri === "runtime://health") {
      const projects = await runtime.listProjects();
      const metrics = RuntimeMetrics.getAllSummaries();
      return JSON.stringify(
        {
          status: "healthy",
          uptimeSeconds: process.uptime(),
          totalProjects: projects.length,
          metrics,
        },
        null,
        2
      );
    }

    if (uri === "runtime://projects") {
      const projects = await runtime.listProjects();
      return JSON.stringify({ projects }, null, 2);
    }

    if (uri === "capabilities://runtime") {
      return JSON.stringify(
        {
          persistence: true,
          revisions: true,
          transactions: true,
          recovery: true,
          migrations: true,
          locking: true,
          deterministicHashing: true,
          maxLayers: 5000,
          maxKeyframes: 100000,
        },
        null,
        2
      );
    }

    const projectMatch = uri.match(/^project:\/\/([^/]+)$/);
    if (projectMatch) {
      const projectId = projectMatch[1];
      const status = await runtime.getStatus(projectId);
      return JSON.stringify(status, null, 2);
    }

    const revisionsMatch = uri.match(/^project:\/\/([^/]+)\/revisions$/);
    if (revisionsMatch) {
      const projectId = revisionsMatch[1];
      const revisions = await runtime.listRevisions(projectId);
      return JSON.stringify({ projectId, revisions }, null, 2);
    }

    const diagsMatch = uri.match(/^project:\/\/([^/]+)\/diagnostics$/);
    if (diagsMatch) {
      const projectId = diagsMatch[1];
      const health = await runtime.validateProject(projectId, false);
      return JSON.stringify(health, null, 2);
    }

    throw new Error(`Resource URI not found: ${uri}`);
  }
}
