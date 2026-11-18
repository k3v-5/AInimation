import { describe, it } from "node:test";
import assert from "node:assert/strict";
import { MemoryStorageAdapter } from "../../runtime/persistence/MemoryStorageAdapter.js";
import { ProjectSerializer } from "../../runtime/persistence/ProjectSerializer.js";
import { ProjectDiffEngine } from "../../runtime/ProjectDiff.js";
import { ProjectRuntime } from "../../runtime/ProjectRuntime.js";

describe("Fase 18 — Runtime Performance Benchmarks", () => {
  it("benchmarks create, save, hash, and diff pipelines for 10, 100, and 1000 elements", async () => {
    const scales = [10, 100, 1000];

    for (const count of scales) {
      const storage = new MemoryStorageAdapter();
      const runtime = new ProjectRuntime({ storageRoot: ":memory:" }, storage);

      const elements = Array.from({ length: count }, (_, i) => ({
        id: `elem_${i}`,
        name: `Layer_${i}`,
        type: "shape",
        startTime: (i * 0.1) % 25,
        duration: 5,
        transform: {
          position: { baseValue: { x: (i * 10) % 1920, y: (i * 5) % 1080 }, keyframes: [] },
          opacity: { baseValue: 0.9, keyframes: [] },
        },
      }));

      const projectData = {
        schemaVersion: "1.8.0",
        composition: {
          id: `comp_bench_${count}`,
          name: `Benchmark Comp ${count}`,
          width: 1920,
          height: 1080,
          fps: 30,
          duration: 30,
        },
        elements,
        assets: [],
      };

      // 1. Benchmark Hash & Canonicalization
      const t0 = performance.now();
      const hash = ProjectSerializer.hashProject(projectData);
      const hashDuration = performance.now() - t0;
      assert.equal(hash.length, 64);

      // 2. Benchmark Create Session
      const t1 = performance.now();
      const session = await runtime.createProject({
        projectId: `proj_bench_${count}`,
        project: projectData,
        metadata: { name: `Benchmark ${count}` },
      });
      const createDuration = performance.now() - t1;
      assert.equal(session.projectId, `proj_bench_${count}`);

      // 3. Benchmark Diff
      const modElements = [...elements];
      modElements[0] = { ...modElements[0], name: "Modified Name" };
      const modifiedProject = { ...projectData, elements: modElements };

      const t2 = performance.now();
      const diff = ProjectDiffEngine.diff(projectData, modifiedProject);
      const diffDuration = performance.now() - t2;
      assert.equal(diff.summary.layersModified, 1);

      // Latency thresholds
      assert.ok(hashDuration < 250, `Hashing ${count} elements took ${hashDuration.toFixed(2)}ms (< 250ms)`);
      assert.ok(createDuration < 250, `Creating project with ${count} elements took ${createDuration.toFixed(2)}ms (< 250ms)`);
      assert.ok(diffDuration < 250, `Diffing ${count} elements took ${diffDuration.toFixed(2)}ms (< 250ms)`);
    }
  });
});
