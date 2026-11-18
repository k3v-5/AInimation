import { MigrationError, UnsupportedProjectVersionError } from "../../errors/runtime-errors.js";
import { Migration, MigrationPlan } from "./MigrationPlan.js";
import { Migration_010_to_020, Migration_020_to_180 } from "./migrations/v1_to_v2.js";

/**
 * Registro y ejecutor de migraciones de esquemas entre versiones del Motion Engine (Fase 18).
 */
export class MigrationRegistry {
  private static migrations: Migration[] = [Migration_010_to_020, Migration_020_to_180];

  public static register(migration: Migration): void {
    this.migrations.push(migration);
  }

  public static getMigration(fromVersion: string, toVersion: string): Migration | undefined {
    return this.migrations.find((m) => m.fromVersion === fromVersion && m.toVersion === toVersion);
  }

  public static planMigration(sourceVersion: string, targetVersion = "1.8.0"): MigrationPlan {
    if (sourceVersion === targetVersion) {
      return { sourceVersion, targetVersion, steps: [], canMigrate: true };
    }

    const steps = [];
    let current = sourceVersion;

    while (current !== targetVersion) {
      const step = this.migrations.find((m) => m.fromVersion === current);
      if (!step) {
        return { sourceVersion, targetVersion, steps: [], canMigrate: false };
      }
      steps.push({
        fromVersion: step.fromVersion,
        toVersion: step.toVersion,
        description: step.description,
      });
      current = step.toVersion;
    }

    return { sourceVersion, targetVersion, steps, canMigrate: true };
  }

  /**
   * Ejecuta la cadena completa de migraciones de forma atómica e idempotente.
   */
  public static migrate(projectData: any, targetVersion = "1.8.0"): { project: any; migratedSteps: string[] } {
    const sourceVersion = projectData.schemaVersion ?? "0.1.0";
    if (sourceVersion === targetVersion) {
      return { project: JSON.parse(JSON.stringify(projectData)), migratedSteps: [] };
    }

    const plan = this.planMigration(sourceVersion, targetVersion);
    if (!plan.canMigrate) {
      throw new UnsupportedProjectVersionError(sourceVersion, { targetVersion });
    }

    let currentData = JSON.parse(JSON.stringify(projectData));
    const executedSteps: string[] = [];

    for (const stepInfo of plan.steps) {
      const migration = this.getMigration(stepInfo.fromVersion, stepInfo.toVersion);
      if (!migration) {
        throw new MigrationError(stepInfo.fromVersion, stepInfo.toVersion, "Migration handler not found.");
      }

      try {
        currentData = migration.migrate(currentData);
        executedSteps.push(`${stepInfo.fromVersion}->${stepInfo.toVersion}`);
      } catch (err: any) {
        throw new MigrationError(stepInfo.fromVersion, stepInfo.toVersion, err.message);
      }
    }

    return { project: currentData, migratedSteps: executedSteps };
  }
}
