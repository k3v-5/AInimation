import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { AEExpressionBuilder } from "../../exporters/ae/expressions/AEExpressionBuilder.js";
import { AEShapeCompiler, AEShapeDefinition } from "../../exporters/ae/shapes/AEShapeCompiler.js";
import { AEJSXParser } from "../../exporters/ae/importer/AEJSXParser.js";

describe("Fase 26 — Capa 6: After Effects Performance & Benchmarks Suite", () => {
  it("benchmarks building 5,000 expressions, compiling 500 shape layers and parsing 500 JSX scripts in < 250ms", () => {
    const t0 = performance.now();

    // 1. 5,000 expresiones
    for (let i = 0; i < 5000; i++) {
      AEExpressionBuilder.wiggle(i % 10, i * 2);
      AEExpressionBuilder.linear("time", 0, 10, 0, 100);
      AEExpressionBuilder.loopOut("cycle", 0);
    }

    // 2. 500 Shape Layers
    const shapeDefs: AEShapeDefinition[] = [
      {
        name: "BenchmarkShape",
        contents: [
          { type: "rect", size: [100, 100] },
          { type: "trim_paths", start: 0, end: 50 },
          { type: "repeater", copies: 3 },
        ],
        fillColor: [1, 1, 0],
      },
    ];

    for (let i = 0; i < 500; i++) {
      AEShapeCompiler.compileShapeLayer("comp", `Shape_${i}`, shapeDefs);
    }

    // 3. 500 JSX Script parses
    const sampleJSX = `app.project.items.addComp("BenchComp", 1920, 1080, 1.0, 10.0, 30.0);`;
    for (let i = 0; i < 500; i++) {
      AEJSXParser.parse(sampleJSX);
    }

    const elapsed = performance.now() - t0;
    assert.ok(elapsed < 250, `AE compiler benchmark took ${elapsed.toFixed(2)}ms (budget < 250ms)`);
  });
});
