import { Composition } from "../core/composition.js";
import { ProjectDeserializer } from "../persistence/ProjectDeserializer.js";

/**
 * Snapshot inmutable y reproducible del estado de la IR de un proyecto (Fase 18).
 */
export class ProjectSnapshot {
  public readonly projectId: string;
  public readonly revisionId: string;
  public readonly projectHash: string;
  private readonly projectData: Record<string, unknown>;

  constructor(projectId: string, revisionId: string, projectHash: string, projectData: Record<string, unknown>) {
    this.projectId = projectId;
    this.revisionId = revisionId;
    this.projectHash = projectHash;
    this.projectData = JSON.parse(JSON.stringify(projectData));
  }

  public getRawData<T = Record<string, unknown>>(): T {
    return JSON.parse(JSON.stringify(this.projectData)) as T;
  }

  public toComposition(): Composition {
    return ProjectDeserializer.deserialize(this.projectData);
  }
}
