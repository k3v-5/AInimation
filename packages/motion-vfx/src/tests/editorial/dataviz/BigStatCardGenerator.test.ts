import { describe, it } from "node:test";
import assert from "node:assert/strict";
import { BigStatCardGenerator } from "../../../editorial/dataviz/big-stat-card-generator.js";

describe("Fase 5A — BigStatCardGenerator Suite", () => {
  it("compiles Big Stat card with type BIG_STAT and valid checksum", () => {
    const ir = BigStatCardGenerator.compile({
      value: 1800000,
      label: "personas afectadas",
      unit: "COUNT",
    });

    assert.equal(ir.type, "BIG_STAT");
    assert.ok(ir.checksumSha256 !== undefined);
    assert.equal(ir.checksumSha256?.length, 64);
  });

  it("formats large numbers into compact editorial format (1800000 -> 1.8M) per REQ-025 §115", () => {
    const ir = BigStatCardGenerator.compile({
      value: 1800000,
      label: "personas afectadas",
      unit: "COUNT",
    });

    const dominant = ir.elements.find((e) => e.id === "stat_dominant_value");
    assert.ok(dominant !== undefined);
    assert.equal(dominant?.properties.displayValue, "1.8M");
  });

  it("generates vector accent divider line with carmesí color #FF1424 (REQ-025 §34)", () => {
    const ir = BigStatCardGenerator.compile({
      value: 42,
      label: "Answer",
    });

    const divider = ir.elements.find((e) => e.id === "stat_accent_divider");
    assert.ok(divider !== undefined);
    assert.equal(divider?.properties.color, "#FF1424");
    assert.equal(divider?.properties.thicknessPx, 4);
  });

  it("formats secondary label in uppercase with tracking (REQ-025 §31)", () => {
    const ir = BigStatCardGenerator.compile({
      value: 99.9,
      label: "uptime achieved",
    });

    const label = ir.elements.find((e) => e.id === "stat_secondary_label");
    assert.ok(label !== undefined);
    assert.equal(label?.properties.text, "UPTIME ACHIEVED");
  });

  it("includes optional context and source attribution elements", () => {
    const ir = BigStatCardGenerator.compile({
      value: 500,
      label: "New Jobs",
      context: "Created across renewable energy sector in Q3",
      source: "Bureau of Labor Statistics",
    });

    const ctx = ir.elements.find((e) => e.id === "stat_context");
    const src = ir.elements.find((e) => e.id === "stat_source");

    assert.ok(ctx !== undefined);
    assert.ok(src !== undefined);
    assert.equal(src?.properties.text, "Source: Bureau of Labor Statistics");
  });

  it("adjusts dominant font size for 9:16 vertical composition", () => {
    const landscapeIR = BigStatCardGenerator.compile({ value: 100, label: "Stat" }, { composition: "LANDSCAPE_16_9" });
    const verticalIR = BigStatCardGenerator.compile({ value: 100, label: "Stat" }, { composition: "VERTICAL_9_16" });

    const landVal = landscapeIR.elements.find((e) => e.id === "stat_dominant_value");
    const vertVal = verticalIR.elements.find((e) => e.id === "stat_dominant_value");

    assert.ok((vertVal?.properties.fontSize as number) < (landVal?.properties.fontSize as number));
  });
});
