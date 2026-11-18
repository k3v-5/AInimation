import { describe, it } from "node:test";
import assert from "node:assert/strict";
import { Composition } from "../../core/composition.js";
import { ShapeElement } from "../../elements/ShapeElement.js";
import { TextElement } from "../../elements/TextElement.js";
import { MemoryStorageAdapter } from "../../runtime/persistence/MemoryStorageAdapter.js";
import { ProjectEnvelopeFactory } from "../../runtime/persistence/ProjectEnvelope.js";
import { ProjectSerializer } from "../../runtime/persistence/ProjectSerializer.js";
import { ProjectRepository } from "../../runtime/ProjectRepository.js";

describe("Fase 18 — Persistence & Canonical Serialization Unit Tests", () => {
  it("guarantees identical SHA-256 hash regardless of object key permutation", () => {
    const objA = {
      name: "Project A",
      width: 1080,
      height: 1920,
      fps: 30,
      settings: { color: "red", quality: 100, tags: ["viral", "tiktok"] },
    };

    const objB = {
      fps: 30,
      settings: { quality: 100, tags: ["viral", "tiktok"], color: "red" },
      height: 1920,
      name: "Project A",
      width: 1080,
    };

    const hashA = ProjectSerializer.hashProject(objA);
    const hashB = ProjectSerializer.hashProject(objB);

    assert.equal(hashA, hashB, "Permuted keys must produce identical hash");
    assert.equal(hashA.length, 64);
  });

  it("normalizes -0 to 0 and throws on NaN or Infinity", () => {
    const objNegativeZero = { x: -0, y: 0 };
    const canonical = ProjectSerializer.canonicalize(objNegativeZero);
    assert.equal(canonical, '{"x":0,"y":0}');

    assert.throws(
      () => ProjectSerializer.canonicalize({ x: NaN }),
      /Non-finite number/
    );
    assert.throws(
      () => ProjectSerializer.canonicalize({ x: Infinity }),
      /Non-finite number/
    );
  });

  it("performs full round-trip persistence and recovery via ProjectRepository", async () => {
    const storage = new MemoryStorageAdapter();
    const repo = new ProjectRepository(storage);

    const comp = new Composition({
      id: "comp_roundtrip",
      name: "RoundTrip Test",
      width: 1920,
      height: 1080,
      fps: 30,
      duration: 15.0,
    });

    const shape = new ShapeElement({
      id: "shape_1",
      name: "Box",
      shapeType: "rectangle",
      shapeData: { width: 400, height: 400 },
      startTime: 0,
      duration: 5,
    });

    const text = new TextElement({
      id: "text_1",
      name: "Title",
      text: "Hola Mundo Persistente",
      parentId: "shape_1",
      startTime: 1,
      duration: 10,
    });

    comp.addElement(shape);
    comp.addElement(text);

    const serialized = ProjectSerializer.serializeComposition(comp);

    const created = await repo.create({
      projectId: "proj_rt_1",
      project: serialized,
      metadata: { name: "RoundTrip Project", description: "Persistence test" },
    });

    assert.equal(created.projectId, "proj_rt_1");
    assert.equal(created.revisionId, "rev_000001");
    assert.ok(created.contentHash.length === 64);

    const loaded = await repo.load("proj_rt_1");
    assert.equal(loaded.projectId, created.projectId);
    assert.equal(loaded.contentHash, created.contentHash);
    assert.equal(loaded.metadata.name, "RoundTrip Project");
  });
});
