import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { GeometryFactory } from "../../graphics/geometry/GeometryFactory.js";
import { LayoutEngine } from "../../graphics/layout/LayoutEngine.js";
import { ProceduralMotion } from "../../graphics/motion/ProceduralMotion.js";

describe("Fase 5J — Shapes, Graphics & Procedural Motion Benchmark Suite", () => {
  it("benchmarks creating 1,000 arrow geometries, laying out 500 stacks and evaluating 1,000 trim paths", () => {
    // 1. Benchmark 1,000 Arrow polygons
    const t0 = performance.now();
    for (let i = 0; i < 1000; i++) {
      GeometryFactory.createArrowPolygon({
        type: "arrow",
        start: { x: 0, y: 0 },
        end: { x: 100 + i, y: 50 + i },
        headLength: 20,
        headWidth: 30,
        shaftWidth: 10,
      });
    }
    const arrowElapsed = performance.now() - t0;

    // 2. Benchmark 500 Stack layouts con 10 elementos cada uno
    const elements = Array.from({ length: 10 }, () => ({ width: 100, height: 40 }));
    const t1 = performance.now();
    for (let i = 0; i < 500; i++) {
      LayoutEngine.layoutStack(elements, { direction: "horizontal", gap: 12, alignment: "start" });
    }
    const layoutElapsed = performance.now() - t1;

    // 3. Benchmark 1,000 TrimPaths
    const trim = { start: 0.1, end: 0.9, offset: 0.05 };
    const t2 = performance.now();
    for (let i = 0; i < 1000; i++) {
      ProceduralMotion.evaluateTrimPaths(i / 1000, trim);
    }
    const trimElapsed = performance.now() - t2;

    // Presupuesto: < 100ms para cada tarea
    assert.ok(arrowElapsed < 100, `Arrow generation took ${arrowElapsed.toFixed(2)}ms (budget: <100ms)`);
    assert.ok(layoutElapsed < 100, `Stack layout took ${layoutElapsed.toFixed(2)}ms (budget: <100ms)`);
    assert.ok(trimElapsed < 100, `TrimPaths took ${trimElapsed.toFixed(2)}ms (budget: <100ms)`);
  });
});
