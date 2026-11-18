import { describe, it, before, after } from "node:test";
import assert from "node:assert/strict";
import * as fs from "node:fs/promises";
import * as os from "node:os";
import * as path from "node:path";
import { FileSystemStorageAdapter } from "../../runtime/persistence/FileSystemStorageAdapter.js";
import { ProjectEnvelopeFactory } from "../../runtime/persistence/ProjectEnvelope.js";
import { ProjectRecovery } from "../../runtime/ProjectRecovery.js";

describe("Fase 18 — Atomic Writes & Crash Recovery Tests", () => {
  const testRoot = path.join(os.tmpdir(), "motion_engine_test_recovery");

  before(async () => {
    await fs.mkdir(testRoot, { recursive: true });
  });

  after(async () => {
    try {
      await fs.rm(testRoot, { recursive: true, force: true });
    } catch {}
  });

  it("writes files atomically without leaving temporary files on success", async () => {
    const storage = new FileSystemStorageAdapter(testRoot);
    const key = "projects/test_proj/project.json";
    const data = new TextEncoder().encode(JSON.stringify({ test: true }));

    await storage.write(key, data);
    assert.ok(await storage.exists(key));

    const allFiles = await storage.list("projects/test_proj/");
    const tmpFiles = allFiles.filter((f) => f.includes(".tmp."));
    assert.equal(tmpFiles.length, 0, "No temporary files should linger after clean write");
  });

  it("recovers head file if a process crashed leaving a valid .tmp file and corrupted head", async () => {
    const storage = new FileSystemStorageAdapter(testRoot);
    const recovery = new ProjectRecovery(storage);

    const validEnvelope = ProjectEnvelopeFactory.create({
      projectId: "recovered_proj",
      project: { name: "Recovered IR", layers: [] },
      metadata: { name: "Recovered" },
    });

    const validBytes = new TextEncoder().encode(JSON.stringify(validEnvelope));
    const corruptBytes = new TextEncoder().encode("{ corrupted json ..");

    // Escribir head corrupto y archivo temporal válido
    await storage.write("projects/recovered_proj/project.json", corruptBytes);
    await storage.write("projects/recovered_proj/project.json.tmp.123_abc", validBytes);

    const report = await recovery.recoverProject("recovered_proj");
    assert.ok(report.recovered, "Recovery should succeed");
    assert.ok(report.recoveredFromTemp, "Should promote valid tmp file to head");

    const headData = await storage.read("projects/recovered_proj/project.json");
    assert.ok(headData);
    const parsed = JSON.parse(new TextDecoder().decode(headData));
    assert.equal(parsed.projectId, "recovered_proj");
  });
});
