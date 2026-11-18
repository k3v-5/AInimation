import { SerializationError } from "../errors/index.js";
import { SerializedProject } from "./serializer.js";

export type SchemaVersion = "0.1.0" | "0.2.0";

export const SUPPORTED_SCHEMA_VERSIONS: readonly SchemaVersion[] = ["0.1.0", "0.2.0"];
export const LATEST_SCHEMA_VERSION: SchemaVersion = "0.2.0";

/**
 * Sistema de migración de proyectos serializados entre diferentes versiones de esquema.
 */
export class ProjectMigrator {
  /**
   * Migra un proyecto JSON a la versión de esquema destino.
   */
  public static migrate(data: any, targetVersion: SchemaVersion = LATEST_SCHEMA_VERSION): SerializedProject {
    if (!data || typeof data !== "object") {
      throw new SerializationError("Project JSON to migrate must be an object.");
    }

    const currentVersion = data.schemaVersion;
    if (!currentVersion || typeof currentVersion !== "string") {
      throw new SerializationError("Missing schemaVersion in project data.");
    }

    if (!SUPPORTED_SCHEMA_VERSIONS.includes(currentVersion as SchemaVersion)) {
      throw new SerializationError(`Unsupported source schemaVersion '${currentVersion}'.`);
    }

    if (currentVersion === targetVersion) {
      return JSON.parse(JSON.stringify(data));
    }

    let migrated = JSON.parse(JSON.stringify(data));

    // Pipeline secuencial de migraciones: 0.1.0 -> 0.2.0
    if (migrated.schemaVersion === "0.1.0" && targetVersion === "0.2.0") {
      migrated = this.migrate_010_to_020(migrated);
    }

    return migrated;
  }

  /**
   * Migración de Schema v0.1.0 (Core Temporal con Layers) a v0.2.0 (Element Model + Assets).
   */
  private static migrate_010_to_020(v010: any): SerializedProject {
    const assets: any[] = [];
    const elements: any[] = [];

    // En v0.1.0 las capas eran puras; las convertimos a BaseElements compatibles si es necesario
    return {
      schemaVersion: "0.2.0",
      composition: {
        id: v010.composition.id,
        name: v010.composition.name,
        width: v010.composition.width,
        height: v010.composition.height,
        fps: v010.composition.fps,
        duration: v010.composition.duration,
        layers: v010.composition.layers ?? [],
      },
      assets,
      elements,
    };
  }
}
