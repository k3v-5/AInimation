import { ExportManifest, ExportManifestBuilder } from "../exporters/common/ExportManifest.js";

export interface ProjectIdentityInput {
  script: string;
  styleId?: string;
  durationTarget?: number;
  aspectRatio?: string;
  resolution?: { width: number; height: number };
  fps?: number;
  language?: string;
  captionConfig?: Record<string, any>;
  audioConfig?: Record<string, any>;
  seed?: number;
  schemaVersion?: string;
  engineVersion?: string;
}

export interface MCPProjectSnapshot {
  projectId: string;
  revisionId: string;
  parentRevisionId?: string;
  operation: string;
  createdAt: string;
  ir: any; // Instancia de CompiledProjectOutput / Composition
  summary: {
    duration: number;
    width: number;
    height: number;
    fps: number;
    layerCount: number;
  };
}

/**
 * Almacén determinista e inmutable de proyectos y revisiones en memoria para MCP (Fase 17).
 */
export class MCPProjectStore {
  private static projects = new Map<string, Map<string, MCPProjectSnapshot>>();

  /**
   * Genera un identificador de proyecto determinista a partir del input canónico.
   */
  public static computeProjectId(input: ProjectIdentityInput): string {
    const canonicalInput = ExportManifestBuilder.canonicalize({
      script: input.script,
      styleId: input.styleId ?? "fast-tiktok",
      durationTarget: input.durationTarget ?? 30,
      aspectRatio: input.aspectRatio ?? "9:16",
      fps: input.fps ?? 30,
      seed: input.seed ?? 42,
      schemaVersion: input.schemaVersion ?? "1.7.0",
      engineVersion: input.engineVersion ?? "1.7.0",
    });

    return "proj_" + ExportManifestBuilder.sha256(canonicalInput).slice(0, 16);
  }

  /**
   * Genera un revisionId determinista e inmutable.
   */
  public static computeRevisionId(parentRevisionId: string, operation: string, irData: any): string {
    const canonicalPayload = ExportManifestBuilder.canonicalize({
      parentRevisionId,
      operation,
      irSummary: {
        id: irData?.id,
        duration: irData?.duration,
        layerCount: irData?.composition?.layers?.length ?? irData?.layers?.length ?? 0,
      },
    });

    return "rev_" + ExportManifestBuilder.sha256(canonicalPayload).slice(0, 12);
  }

  /**
   * Guarda una revisión inmutable de proyecto.
   */
  public static saveRevision(snapshot: MCPProjectSnapshot): void {
    if (!this.projects.has(snapshot.projectId)) {
      this.projects.set(snapshot.projectId, new Map());
    }

    const revisionsMap = this.projects.get(snapshot.projectId)!;
    revisionsMap.set(snapshot.revisionId, snapshot);
  }

  /**
   * Obtiene una revisión específica o la última registrada.
   */
  public static getRevision(projectId: string, revisionId?: string): MCPProjectSnapshot | undefined {
    const revisionsMap = this.projects.get(projectId);
    if (!revisionsMap) return undefined;

    if (revisionId) {
      return revisionsMap.get(revisionId);
    }

    // Si no se especifica revisionId, devolver la última revisión insertada
    const allRevs = Array.from(revisionsMap.values());
    return allRevs[allRevs.length - 1];
  }

  /**
   * Lista todas las revisiones registradas de un proyecto.
   */
  public static listRevisions(projectId: string): MCPProjectSnapshot[] {
    const revisionsMap = this.projects.get(projectId);
    if (!revisionsMap) return [];
    return Array.from(revisionsMap.values());
  }

  /**
   * Limpia el almacén (útil para tests).
   */
  public static clear(): void {
    this.projects.clear();
  }
}
