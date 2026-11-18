import { Migration } from "../MigrationPlan.js";

export const Migration_010_to_020: Migration = {
  fromVersion: "0.1.0",
  toVersion: "0.2.0",
  description: "Migra Schema v0.1.0 (Core Temporal) a v0.2.0 (Element Model y Assets)",
  canMigrate(projectData: any): boolean {
    return projectData.schemaVersion === "0.1.0";
  },
  migrate(projectData: any): any {
    return {
      schemaVersion: "0.2.0",
      composition: {
        id: projectData.composition?.id ?? "comp_migrated",
        name: projectData.composition?.name ?? "Migrated Comp",
        width: projectData.composition?.width ?? 1920,
        height: projectData.composition?.height ?? 1080,
        fps: projectData.composition?.fps ?? 30,
        duration: projectData.composition?.duration ?? 10,
        layers: projectData.composition?.layers ?? [],
      },
      assets: projectData.assets ?? [],
      elements: projectData.elements ?? [],
    };
  },
};

export const Migration_020_to_180: Migration = {
  fromVersion: "0.2.0",
  toVersion: "1.8.0",
  description: "Migra Schema v0.2.0 a v1.8.0 (Production Runtime Envelope Ready)",
  canMigrate(projectData: any): boolean {
    return projectData.schemaVersion === "0.2.0";
  },
  migrate(projectData: any): any {
    return {
      schemaVersion: "1.8.0",
      composition: projectData.composition,
      assets: projectData.assets ?? [],
      elements: projectData.elements ?? [],
    };
  },
};
