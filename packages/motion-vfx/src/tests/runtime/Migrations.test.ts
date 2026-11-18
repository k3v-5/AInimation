import { describe, it } from "node:test";
import assert from "node:assert/strict";
import { UnsupportedProjectVersionError } from "../../errors/runtime-errors.js";
import { MigrationRegistry } from "../../runtime/migration/MigrationRegistry.js";

describe("Fase 18 — Migration System & Idempotency Tests", () => {
  it("migrates Schema 0.1.0 to 1.8.0 sequentially and idempotently", () => {
    const v010Project = {
      schemaVersion: "0.1.0",
      composition: {
        id: "comp_old",
        name: "Old Comp",
        width: 1920,
        height: 1080,
        fps: 30,
        duration: 10,
        layers: [],
      },
    };

    // 1. Migrar 0.1.0 -> 1.8.0
    const { project: migrated, migratedSteps } = MigrationRegistry.migrate(v010Project, "1.8.0");

    assert.equal(migrated.schemaVersion, "1.8.0");
    assert.deepEqual(migratedSteps, ["0.1.0->0.2.0", "0.2.0->1.8.0"]);

    // 2. Idempotencia: Volver a migrar un proyecto ya en 1.8.0 no debe producir cambios
    const secondPass = MigrationRegistry.migrate(migrated, "1.8.0");
    assert.equal(secondPass.project.schemaVersion, "1.8.0");
    assert.equal(secondPass.migratedSteps.length, 0);
  });

  it("throws UnsupportedProjectVersionError when encountering unknown future versions", () => {
    const futureProject = {
      schemaVersion: "999.0.0",
      composition: { id: "comp_future" },
    };

    assert.throws(
      () => MigrationRegistry.migrate(futureProject, "1.8.0"),
      (err: any) => err instanceof UnsupportedProjectVersionError
    );
  });
});
