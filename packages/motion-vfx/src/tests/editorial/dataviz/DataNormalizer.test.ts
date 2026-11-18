import { describe, it } from "node:test";
import assert from "node:assert/strict";
import {
  DataNormalizer,
  normalizeNumber,
} from "../../../editorial/dataviz/data-normalizer.js";
import { DataSet } from "../../../editorial/dataviz/types.js";

describe("Fase 5A — DataNormalizer Suite", () => {
  const sampleDs: DataSet = {
    id: "ds_test",
    points: [
      { id: "p1", label: "A", value: 10 },
      { id: "p2", label: "B", value: 50 },
      { id: "p3", label: "C", value: 90 },
    ],
  };

  it("normalizes numbers to 4 decimal places and eliminates -0", () => {
    assert.equal(normalizeNumber(1.234567), 1.2346);
    assert.equal(normalizeNumber(-0.00000001), 0);
    assert.equal(Object.is(normalizeNumber(-0), 0), true);
  });

  it("calculates min accurately", () => {
    assert.equal(DataNormalizer.calculateMin(sampleDs.points), 10);
  });

  it("calculates max accurately", () => {
    assert.equal(DataNormalizer.calculateMax(sampleDs.points), 90);
  });

  it("calculates range accurately", () => {
    assert.equal(DataNormalizer.calculateRange(sampleDs.points), 80);
  });

  it("normalizes values bounded between 0.0 and 1.0", () => {
    assert.equal(DataNormalizer.normalizeValue(10, 10, 90), 0.0);
    assert.equal(DataNormalizer.normalizeValue(50, 10, 90), 0.5);
    assert.equal(DataNormalizer.normalizeValue(90, 10, 90), 1.0);
  });

  it("handles constant dataset by returning 0.50 without division by zero (REQ-025 §15)", () => {
    assert.equal(DataNormalizer.normalizeValue(42, 42, 42), 0.5);

    const constDs: DataSet = {
      id: "ds_const",
      points: [
        { id: "c1", label: "C1", value: 100 },
        { id: "c2", label: "C2", value: 100 },
      ],
    };
    const norm = DataNormalizer.normalizeDataset(constDs);
    assert.equal(norm.scaleWarning, "CONSTANT_DOMAIN");
    assert.equal(norm.points[0].normalizedValue, 0.5);
    assert.equal(norm.points[1].normalizedValue, 0.5);
  });

  it("normalizes dataset non-destructively without mutating raw input", () => {
    const originalPoints = JSON.stringify(sampleDs.points);
    const result = DataNormalizer.normalizeDataset(sampleDs);
    assert.equal(JSON.stringify(sampleDs.points), originalPoints);
    assert.equal(result.minValue, 10);
    assert.equal(result.maxValue, 90);
    assert.equal(result.points.length, 3);
  });

  it("parses dates and years into timestampSeconds", () => {
    const temporalDs: DataSet = {
      id: "ds_temp",
      points: [
        { id: "t1", label: "1945", value: 100, date: "1945" },
        { id: "t2", label: "1989", value: 200, date: "1989" },
      ],
    };
    const res = DataNormalizer.normalizeDataset(temporalDs);
    assert.equal(res.points[0].timestampSeconds, 1945);
    assert.equal(res.points[1].timestampSeconds, 1989);
  });
});
