import { Manifest, ManifestSchema } from "./schemas/manifest.schema.js";

/**
 * Almacén y validador de manifiestos finales de producción y exportación (Fase 18).
 */
export class ManifestStore {
  private manifests = new Map<string, Manifest>(); // projectId -> Manifest

  public save(manifest: Manifest): void {
    ManifestSchema.parse(manifest);
    this.manifests.set(manifest.projectId, manifest);
  }

  public get(projectId: string): Manifest | undefined {
    return this.manifests.get(projectId);
  }

  public has(projectId: string): boolean {
    return this.manifests.has(projectId);
  }
}
