import { describe, it } from "node:test";
import assert from "node:assert/strict";
import {
  formatCompactNumber,
  formatPercentage,
  formatCurrency,
  formatDate,
  formatDataValue,
} from "../../../editorial/data-viz/formatters.js";

describe("DataVisualizationFormatters Tests", () => {
  it("formats compact numbers with standard suffixes (K, M, B, T)", () => {
    assert.equal(formatCompactNumber(1250), "1.25K");
    assert.equal(formatCompactNumber(1250000), "1.25M");
    assert.equal(formatCompactNumber(2500000000), "2.50B");
    assert.equal(formatCompactNumber(1800000000000), "1.80T");
    assert.equal(formatCompactNumber(450), "450");
  });

  it("formats percentage and currency deterministically", () => {
    assert.equal(formatPercentage(42.5), "42.5%");
    assert.equal(formatCurrency(1250.75), "$1,250.75");
    assert.equal(formatCurrency(1000000, "€"), "€1,000,000.00");
  });

  it("formats dates without system timezone distortion", () => {
    const dStr = formatDate("2024-05-15T00:00:00Z");
    assert.equal(dStr, "2024-05-15");
  });

  it("formats generic data values with unit detection", () => {
    assert.equal(formatDataValue(null), "—");
    assert.equal(formatDataValue(true), "True");
    assert.equal(formatDataValue(18.4, "PERCENT"), "18.4%");
    assert.equal(formatDataValue(95000, "CURRENCY"), "$95,000.00");
  });

  it("never produces NaN or Infinity strings on finite inputs", () => {
    assert.equal(formatCompactNumber(0), "0");
    assert.equal(formatPercentage(0), "0.0%");
    assert.equal(formatCurrency(0), "$0.00");
  });
});
