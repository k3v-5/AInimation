import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { VlogJsxBuilder } from "../../../vlog/exporter/vlog-jsx-builder.js";

describe("Milestone 7 — Vlog JSX Builder Suite", () => {
  it("escapes strings safely for ExtendScript single quotes", () => {
    const raw = "Let's explore 'Guadalajara' & Jalisco\\Mexico\nNext line";
    const escaped = VlogJsxBuilder.escapeString(raw);

    assert.ok(!escaped.includes("\n"));
    assert.ok(escaped.includes("\\'"));
    assert.ok(escaped.includes("\\\\"));
  });

  it("converts hex colors to normalized [r, g, b] conforming to USER_DESIGN_PREFERENCES", () => {
    // Rojo Carmesí Editorial #FF1424 -> [1.0, 0.08, 0.14]
    const crimson = VlogJsxBuilder.hexToRgbNormalized("#FF1424");
    assert.equal(crimson[0], 1.0);
    assert.equal(crimson[1], 0.078);
    assert.equal(crimson[2], 0.141);

    // Blanco puro #FFFFFF
    const white = VlogJsxBuilder.hexToRgbNormalized("#FFFFFF");
    assert.deepEqual(white, [1.0, 1.0, 1.0]);
  });

  it("manages indentation cleanly", () => {
    const builder = new VlogJsxBuilder();
    builder.addLine("function test() {");
    builder.indent();
    builder.addLine("var x = 10;");
    builder.dedent();
    builder.addLine("}");

    const code = builder.toString();
    assert.ok(code.includes("  var x = 10;"));
  });
});
