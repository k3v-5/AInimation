import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { AEShapeCompiler, AEShapeDefinition } from "../../exporters/ae/shapes/AEShapeCompiler.js";

describe("Fase 26 — Capa 2: After Effects Shape Layer Compiler Tests", () => {
  it("compiles a vector shape layer with Rect, Fill, Stroke, Trim Paths and Repeater", () => {
    const shapeDefs: AEShapeDefinition[] = [
      {
        name: "BoxGroup",
        contents: [
          { type: "rect", size: [400, 200], roundness: 20 },
          { type: "trim_paths", start: 0, end: 75, offset: 90 },
          {
            type: "repeater",
            copies: 5,
            offset: 1,
            transform: { position: [100, 0], scale: [100, 100], rotation: 15 },
          },
        ],
        fillColor: [1, 0, 0], // Rojo
        strokeColor: [1, 1, 1], // Blanco
        strokeWidth: 4,
      },
    ];

    const lines = AEShapeCompiler.compileShapeLayer("comp", "Accent_Graphics", shapeDefs);
    const code = lines.join("\n");

    assert.ok(code.includes('comp.layers.addShape()'));
    assert.ok(code.includes('shapeLayer_Accent_Graphics.name = "Accent_Graphics"'));
    assert.ok(code.includes('"ADBE Vector Group"'));
    assert.ok(code.includes('"ADBE Vector Shape - Rect"'));
    assert.ok(code.includes('"ADBE Vector Filter - Trim"'));
    assert.ok(code.includes('"ADBE Vector Filter - Repeater"'));
    assert.ok(code.includes('"ADBE Vector Graphic - Fill"'));
    assert.ok(code.includes('"ADBE Vector Graphic - Stroke"'));
    assert.ok(code.includes('.setValue([400, 200])'));
    assert.ok(code.includes('.setValue(5)')); // copies
  });
});
