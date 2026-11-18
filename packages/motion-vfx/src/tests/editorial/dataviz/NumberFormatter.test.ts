import { describe, it } from "node:test";
import assert from "node:assert/strict";
import { NumberFormatter } from "../../../editorial/dataviz/number-formatter.js";

describe("Fase 5A — NumberFormatter Suite", () => {
  it("formats small numbers without abbreviation (950 -> '950')", () => {
    assert.equal(NumberFormatter.format(950), "950");
  });

  it("formats thousands with K suffix (1250 -> '1.25K')", () => {
    assert.equal(NumberFormatter.format(1250), "1.25K");
  });

  it("formats millions with M suffix (1250000 -> '1.25M')", () => {
    assert.equal(NumberFormatter.format(1250000), "1.25M");
  });

  it("formats billions with B suffix (3200000000 -> '3.20B')", () => {
    assert.equal(NumberFormatter.format(3200000000), "3.20B");
  });

  it("preserves negative sign on abbreviated values (-1250000 -> '-1.25M')", () => {
    assert.equal(NumberFormatter.format(-1250000), "-1.25M");
  });

  it("disables abbreviation when abbreviate = false", () => {
    const formatted = NumberFormatter.format(1250000, { abbreviate: false, separator: "," });
    assert.equal(formatted, "1,250,000");
  });

  it("formats percentages without converting 25 to 0.25% (REQ-025 §93)", () => {
    assert.equal(NumberFormatter.format(25, { unit: "PERCENT" }), "25%");
    assert.equal(NumberFormatter.format(4.7, { unit: "%" }), "4.70%");
  });

  it("does NOT infer currency symbol unless explicitly configured (REQ-025 §92)", () => {
    // 100000 does NOT become $100K unless currencySymbol is passed
    assert.equal(NumberFormatter.format(100000), "100.00K");
    assert.equal(NumberFormatter.format(100000, { currencySymbol: "$" }), "$100.00K");
    assert.equal(NumberFormatter.format(-100000, { currencySymbol: "$" }), "-$100.00K");
  });

  it("supports custom unit labels (REQ-025 §94)", () => {
    const formatted = NumberFormatter.format(180, {
      unit: "CUSTOM",
      customUnitLabel: "km/h",
    });
    assert.equal(formatted, "180 km/h");
  });
});
