import { ProductionMCPContext } from "../tools/phase18-tools.js";

export interface Phase18ResourceDefinition {
  uri: string;
  name: string;
  mimeType: string;
  description: string;
  read: (params?: Record<string, string>) => Promise<{ contents: Array<{ uri: string; mimeType: string; text: string }> }>;
}

/**
 * Catálogo de recursos declarativos MCP para proyectos, revisiones y workflows (Fase 18).
 */
export class Phase18Resources {
  public static async listProjectsResource(): Promise<{ contents: Array<{ uri: string; mimeType: string; text: string }> }> {
    const service = ProductionMCPContext.getProjectService();
    const list = await service.listProjects();

    return {
      contents: [
        {
          uri: "projects://",
          mimeType: "application/json",
          text: JSON.stringify(list, null, 2),
        },
      ],
    };
  }

  public static async readProjectResource(projectId: string): Promise<{ contents: Array<{ uri: string; mimeType: string; text: string }> }> {
    const service = ProductionMCPContext.getProjectService();
    const snapshot = await service.getSnapshot(projectId);

    return {
      contents: [
        {
          uri: `projects://${projectId}`,
          mimeType: "application/json",
          text: JSON.stringify(snapshot.getRawData(), null, 2),
        },
      ],
    };
  }

  public static async listProjectRevisionsResource(projectId: string): Promise<{ contents: Array<{ uri: string; mimeType: string; text: string }> }> {
    const revManager = ProductionMCPContext.getRevisionManager();
    const list = await revManager.listRevisions(projectId);

    return {
      contents: [
        {
          uri: `projects://${projectId}/revisions`,
          mimeType: "application/json",
          text: JSON.stringify(list, null, 2),
        },
      ],
    };
  }

  public static async readRevisionResource(
    projectId: string,
    revisionId: string
  ): Promise<{ contents: Array<{ uri: string; mimeType: string; text: string }> }> {
    const revManager = ProductionMCPContext.getRevisionManager();
    const rev = await revManager.getRevision(projectId, revisionId);

    return {
      contents: [
        {
          uri: `projects://${projectId}/revisions/${revisionId}`,
          mimeType: "application/json",
          text: JSON.stringify(rev, null, 2),
        },
      ],
    };
  }
}
