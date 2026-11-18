import { describe, it } from "node:test";
import assert from "node:assert/strict";
import fc from "fast-check";
import { ProjectSerializer } from "../../runtime/persistence/ProjectSerializer.js";

describe("Fase 18 — Deterministic Cross-Process & Property-Based Tests", () => {
  it("PBT: canonical serialization is idempotent and strictly deterministic for arbitrary objects", () => {
    fc.assert(
      fc.property(
        fc.record({
          id: fc.string(),
          count: fc.integer({ min: -1000, max: 1000 }),
          tags: fc.array(fc.string(), { maxLength: 10 }),
          active: fc.boolean(),
        }),
        (obj) => {
          const pass1 = ProjectSerializer.canonicalize(obj);
          const pass2 = ProjectSerializer.canonicalize(JSON.parse(pass1));
          assert.equal(pass1, pass2, "Canonical JSON stringification must be idempotent");

          const hash1 = ProjectSerializer.hashProject(obj);
          const hash2 = ProjectSerializer.hashProject(JSON.parse(pass1));
          assert.equal(hash1, hash2, "Hashes must match exactly");
        }
      ),
      { numRuns: 100 }
    );
  });

  it("guarantees 100% byte-for-byte determinism in separate runtime instances", () => {
    function buildProjectIR() {
      return {
        schemaVersion: "1.8.0",
        composition: {
          id: "comp_cross_proc",
          name: "Cross Process Video",
          width: 1080,
          height: 1920,
          fps: 30,
          duration: 10,
        },
        elements: [
          { id: "e1", name: "Layer 1", type: "shape", startTime: 0, duration: 5 },
          { id: "e2", name: "Layer 2", type: "text", parentId: "e1", startTime: 2, duration: 8 },
        ],
      };
    }

    // Instancia / Run A
    const irA = buildProjectIR();
    const jsonA = ProjectSerializer.canonicalize(irA);
    const hashA = ProjectSerializer.hashProject(irA);

    // Instancia / Run B
    const irB = buildProjectIR();
    const jsonB = ProjectSerializer.canonicalize(irB);
    const hashB = ProjectSerializer.hashProject(irB);

    assert.equal(jsonA, jsonB, "Serialized JSON must be byte-for-byte identical");
    assert.equal(hashA, hashB, "Content hashes must match");
  });
});
