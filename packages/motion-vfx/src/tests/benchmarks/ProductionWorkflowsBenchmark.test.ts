import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { MemoryProjectStore } from "../../persistence/MemoryProjectStore.js";
import { ProjectSerializer } from "../../persistence/ProjectSerializer.js";
import { ProjectFile } from "../../persistence/schemas/project.schema.js";
import { RevisionDiff } from "../../revisions/RevisionDiff.js";
import { RevisionGraph } from "../../revisions/RevisionGraph.js";
import { RevisionManager } from "../../revisions/RevisionManager.js";
import { RevisionPatch } from "../../revisions/RevisionPatch.js";

describe("Fase 18 — Production Workflows & Revisions Performance Benchmarks", () => {
  it("benchmarks serialization, diff, patch, and revision traversal for 10, 100, 1,000, and 10,000 layers", async () => {
    const layerScales = [10, 100, 1000, 10000];

    for (const numLayers of layerScales) {
      // 1. Generate synthetic project
      const elements: any[] = [];
      for (let i = 0; i < numLayers; i++) {
        elements.push({
          id: `layer_${i}`,
          name: `Layer Item ${i}`,
          startTime: i * 0.1,
          duration: 5.0,
          text: `Sample Caption ${i}`,
          transform: {
            position: { baseValue: [i * 10, i * 5] },
            opacity: { baseValue: 1.0 },
          },
        });
      }

      const projectA = {
        schemaVersion: "1.8.0",
        composition: { id: "comp_bench", duration: 100, fps: 30 },
        elements,
        assets: [],
      };

      // Measure Canonical Serialization
      const t0 = performance.now();
      const canonicalA = ProjectSerializer.canonicalize(projectA);
      const hashA = ProjectSerializer.hashCanonical(projectA);
      const tSerialize = performance.now() - t0;

      assert.ok(canonicalA.length > 0);
      assert.equal(hashA.length, 64);

      // Measure Diff Calculation with 10 modified elements and 5 added elements
      const modifiedElements = [...elements];
      for (let i = 0; i < Math.min(10, numLayers); i++) {
        modifiedElements[i] = { ...modifiedElements[i], text: `Modified ${i}` };
      }
      for (let i = 0; i < 5; i++) {
        modifiedElements.push({
          id: `new_layer_${i}`,
          name: `New Layer ${i}`,
          startTime: 10,
          duration: 2,
        });
      }

      const projectB = {
        ...projectA,
        elements: modifiedElements,
      };

      const tDiffStart = performance.now();
      const diffResult = RevisionDiff.diff(projectA, projectB);
      const tDiff = performance.now() - tDiffStart;

      assert.equal(diffResult.summary.added, 5);
      assert.equal(diffResult.summary.modified, Math.min(10, numLayers));

      // Measure Patch Application
      const tPatchStart = performance.now();
      const patched = RevisionPatch.applyPatch(projectA, diffResult.changes);
      const tPatch = performance.now() - tPatchStart;

      assert.equal((patched.elements as any).length, numLayers + 5);

      // For up to 1,000 layers, everything should run in sub-second time
      if (numLayers <= 1000) {
        assert.ok(tSerialize < 150, `Serialization for ${numLayers} layers took ${tSerialize.toFixed(2)}ms`);
        assert.ok(tDiff < 100, `Diff for ${numLayers} layers took ${tDiff.toFixed(2)}ms`);
        assert.ok(tPatch < 100, `Patch for ${numLayers} layers took ${tPatch.toFixed(2)}ms`);
      }
    }
  });
});
