import { UnsupportedSchemaVersionError } from "./errors/persistence-errors.js";

export interface MigrationPlan {
  sourceVersion: string;
  targetVersion: string;
  steps: string[];
}

/**
 * Gestor de migraciones de esquemas de proyectos persistidos (Fase 18).
 */
export class ProjectMigration {
  public static migrate(projectData: any, targetVersion = "1.8.0"): { project: any; migrated: boolean; steps: string[] } {
    const sourceVersion = projectData.schemaVersion ?? "0.1.0";

    if (sourceVersion === targetVersion) {
      return { project: JSON.parse(JSON.stringify(projectData)), migrated: false, steps: [] };
    }

    const steps: string[] = [];
    let current = JSON.parse(JSON.stringify(projectData));

    // 0.1.0 -> 0.2.0
    if (sourceVersion === "0.1.0") {
      current = {
        schemaVersion: "0.2.0",
        composition: current.composition ?? {
          id: "comp_migrated",
          name: "Migrated Composition",
          width: 1920,
          height: 1080,
          fps: 30,
          duration: 10,
          layers: [],
        },
        elements: current.elements ?? [],
        assets: current.assets ?? [],
      };
      steps.push("0.1.0->0.2.0");
    }

    // 0.2.0 -> 1.8.0
    if (current.schemaVersion === "0.2.0" && targetVersion === "1.8.0") {
      current = {
        schemaVersion: "1.8.0",
        composition: current.composition,
        elements: current.elements ?? [],
        assets: current.assets ?? [],
      };
      steps.push("0.2.0->1.8.0");
    }

    if (current.schemaVersion !== targetVersion) {
      throw new UnsupportedSchemaVersionError(sourceVersion, { targetVersion });
    }

    return { project: current, migrated: steps.length > 0, steps };
  }
}
