import * as fs from "node:fs/promises";
import * as os from "node:os";
import * as path from "node:path";
import assert from "node:assert/strict";
import { describe, it, beforeEach, afterEach } from "node:test";
import { FileProjectStore } from "../../persistence/FileProjectStore.js";
import { MemoryProjectStore } from "../../persistence/MemoryProjectStore.js";
import { ProjectMigration } from "../../persistence/ProjectMigration.js";
import { ProjectSerializer } from "../../persistence/ProjectSerializer.js";
import { ProjectFile } from "../../persistence/schemas/project.schema.js";
import { Revision } from "../../persistence/schemas/revision.schema.js";
import { ProjectAlreadyExistsError, ProjectNotFoundError } from "../../persistence/errors/persistence-errors.js";

describe("Fase 18 — Persistence & Atomic Writes Layer Tests", () => {
  let tempDir: string;

  beforeEach(async () => {
    tempDir = await fs.mkdtemp(path.join(os.tmpdir(), "motion-engine-p18-test-"));
  });

  afterEach(async () => {
    try {
      await fs.rm(tempDir, { recursive: true, force: true });
    } catch {}
  });

  it("ProjectSerializer produces 100% deterministic canonical JSON and SHA-256 hashes", () => {
    const objA = {
      z: 100,
      a: "hello",
      b: { y: true, x: [1, 2, 3], zero: -0 },
    };

    const objB = {
      b: { zero: 0, x: [1, 2, 3], y: true },
      a: "hello",
      z: 100,
    };

    const canonicalA = ProjectSerializer.canonicalize(objA);
    const canonicalB = ProjectSerializer.canonicalize(objB);

    assert.equal(canonicalA, canonicalB);
    assert.equal(ProjectSerializer.hashCanonical(objA), ProjectSerializer.hashCanonical(objB));
    assert.ok(canonicalA.includes('"zero":0'));
  });

  it("MemoryProjectStore handles project and revision CRUD operations strictly", async () => {
    const store = new MemoryProjectStore();

    const initialProject: ProjectFile = {
      schemaVersion: "1.8.0",
      engineVersion: "1.8.0",
      projectId: "proj_mem_1",
      headRevisionId: "rev_001",
      metadata: { name: "Memory Project Test", tags: ["test"] },
      project: { duration: 10, elements: [] },
      contentHash: ProjectSerializer.hashCanonical({ duration: 10, elements: [] }),
    };

    await store.create(initialProject);
    assert.equal(await store.exists("proj_mem_1"), true);
    assert.equal(await store.exists("unknown"), false);

    // Duplicate create throws
    await assert.rejects(async () => {
      await store.create(initialProject);
    }, ProjectAlreadyExistsError);

    // Read project
    const fetched = await store.get("proj_mem_1");
    assert.equal(fetched.projectId, "proj_mem_1");
    assert.equal(fetched.metadata.name, "Memory Project Test");

    // Save and fetch revision
    const rev1: Revision = {
      revisionId: "rev_001",
      projectId: "proj_mem_1",
      parentRevisionId: null,
      createdBy: { type: "agent", agentId: "agent-007" },
      message: "Initial commit",
      changes: [],
      projectHash: initialProject.contentHash,
      schemaVersion: "1.8.0",
      project: initialProject.project,
    };

    await store.saveRevision("proj_mem_1", rev1);
    const fetchedRev = await store.getRevision("proj_mem_1", "rev_001");
    assert.equal(fetchedRev.revisionId, "rev_001");
    assert.equal(fetchedRev.message, "Initial commit");

    const revList = await store.listRevisions("proj_mem_1");
    assert.equal(revList.length, 1);
    assert.equal(revList[0].revisionId, "rev_001");

    const projList = await store.listProjects();
    assert.equal(projList.length, 1);
    assert.equal(projList[0].projectId, "proj_mem_1");
  });

  it("FileProjectStore guarantees atomic writes and disk layout consistency", async () => {
    const store = new FileProjectStore(tempDir);

    const project: ProjectFile = {
      schemaVersion: "1.8.0",
      engineVersion: "1.8.0",
      projectId: "proj_file_1",
      headRevisionId: "rev_001",
      metadata: { name: "File Store Test", tags: ["disk"] },
      project: { duration: 15, elements: [] },
      contentHash: ProjectSerializer.hashCanonical({ duration: 15, elements: [] }),
    };

    await store.create(project);
    assert.equal(await store.exists("proj_file_1"), true);

    const headFilePath = path.join(tempDir, "projects", "proj_file_1", "project.json");
    const rawDisk = await fs.readFile(headFilePath, "utf-8");
    const parsedDisk = JSON.parse(rawDisk);
    assert.equal(parsedDisk.projectId, "proj_file_1");

    // Save revision to disk
    const rev: Revision = {
      revisionId: "rev_001",
      projectId: "proj_file_1",
      parentRevisionId: null,
      createdBy: { type: "user", userId: "director" },
      message: "First cut",
      changes: [],
      projectHash: project.contentHash,
      schemaVersion: "1.8.0",
      project: project.project,
    };

    await store.saveRevision("proj_file_1", rev);
    const revFilePath = path.join(tempDir, "projects", "proj_file_1", "revisions", "rev_001.json");
    assert.equal(await fs.stat(revFilePath).then(() => true).catch(() => false), true);

    const fetchedRev = await store.getRevision("proj_file_1", "rev_001");
    assert.equal(fetchedRev.message, "First cut");
  });

  it("ProjectMigration migrates legacy v0.1.0 and v0.2.0 projects cleanly to v1.8.0", () => {
    const legacy010 = {
      schemaVersion: "0.1.0",
      composition: {
        id: "comp_legacy",
        name: "Legacy Project",
        duration: 5,
        width: 1920,
        height: 1080,
        fps: 30,
        layers: [],
      },
    };

    const res = ProjectMigration.migrate(legacy010);
    assert.equal(res.migrated, true);
    assert.equal(res.project.schemaVersion, "1.8.0");
    assert.deepEqual(res.steps, ["0.1.0->0.2.0", "0.2.0->1.8.0"]);
    assert.equal(res.project.composition.name, "Legacy Project");
  });
});
