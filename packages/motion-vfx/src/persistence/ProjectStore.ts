import { ProjectFile, ProjectSummary } from "./schemas/project.schema.js";
import { Revision, RevisionSummary } from "./schemas/revision.schema.js";

/**
 * Contrato de almacenamiento de proyectos y revisiones desacoplado del sistema de archivos (Fase 18).
 */
export interface ProjectStore {
  create(project: ProjectFile): Promise<void>;
  get(projectId: string): Promise<ProjectFile>;
  update(project: ProjectFile): Promise<void>;
  exists(projectId: string): Promise<boolean>;
  delete(projectId: string): Promise<void>;

  saveRevision(projectId: string, revision: Revision): Promise<void>;
  getRevision(projectId: string, revisionId: string): Promise<Revision>;
  listRevisions(projectId: string): Promise<RevisionSummary[]>;

  listProjects(): Promise<ProjectSummary[]>;
}
