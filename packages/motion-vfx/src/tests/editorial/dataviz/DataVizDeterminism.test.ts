import { describe, it } from "node:test";
import assert from "node:assert/strict";
import { DataVizHash } from "../../../editorial/dataviz/dataviz-hash.js";
import { DataVizIR } from "../../../editorial/dataviz/types.js";

describe("Fase 5A — DataVizDeterminism & Hash Suite", () => {
  const baseIRPayload = {
    schemaVersion: "1.0.0" as const,
    engineVersion: "v4.0.0-editorial-master",
    id: "dtv_test_01",
    type: "BAR_CHART" as const,
    composition: { width: 1920, height: 1080, fps: 30, durationSeconds: 2.0 },
    dataset: {
      id: "ds_rev",
      points: [
        { id: "p1", label: "2023", value: 120.5, normalizedValue: 0.0 },
        { id: "p2", label: "2024", value: 180.2, normalizedValue: 1.0 },
      ],
    },
    layout: {
      bounds: { x: 0, y: 0, width: 1920, height: 1080 },
      margins: { top: 108, right: 192, bottom: 108, left: 192 },
      safeZone: { x: 192, y: 108, width: 1536, height: 864 },
      contentBounds: { x: 192, y: 108, width: 1536, height: 864 },
    },
    scales: [],
    elements: [],
    animations: [],
    style: {
      primaryColor: "#111111",
      accentColor: "#FF1424",
      backgroundColor: "#FFFFFF",
      textColor: "#000000",
      mutedColor: "#666666",
      positiveColor: "#00C853",
      negativeColor: "#D50000",
      titleFontFamily: "Impact",
      titleFontWeight: 900,
      labelFontFamily: "Arial Black",
      labelFontWeight: 800,
      titleSize: 64,
      labelSize: 24,
      valueSize: 36,
      tracking: 2,
      cornerRadius: 4,
      motionPreset: "EDITORIAL" as const,
    },
    metadata: {
      datasetId: "ds_rev",
      visualizationType: "BAR_CHART" as const,
      generatedAtDeterministic: true,
      engineVersion: "v4.0.0-editorial-master",
    },
  };

  it("reordering object keys produces identical canonical string and SHA-256 (REQ-025 §54)", () => {
    const objA = { z: 1, a: 2, m: { y: "hello", b: "world" } };
    const objB = { a: 2, m: { b: "world", y: "hello" }, z: 1 };

    assert.equal(DataVizHash.canonicalStringify(objA), DataVizHash.canonicalStringify(objB));
    assert.equal(
      DataVizHash.computeSha256(objA as any),
      DataVizHash.computeSha256(objB as any)
    );
  });

  it("converts -0 to 0 in canonical JSON serialization", () => {
    const obj1 = { val: -0 };
    const obj2 = { val: 0 };
    assert.equal(DataVizHash.canonicalStringify(obj1), DataVizHash.canonicalStringify(obj2));
  });

  it("produces strictly byte-identical checksum across repeated runs", () => {
    const hash1 = DataVizHash.computeSha256(baseIRPayload);
    const hash2 = DataVizHash.computeSha256(baseIRPayload);
    assert.equal(hash1, hash2);
    assert.equal(hash1.length, 64);
  });

  it("modifying a single value changes the resulting SHA-256 hash (REQ-025 §72)", () => {
    const hash1 = DataVizHash.computeSha256(baseIRPayload);

    const perturbed = JSON.parse(JSON.stringify(baseIRPayload));
    perturbed.dataset.points[0].value = 120.6; // Small perturbation

    const hash2 = DataVizHash.computeSha256(perturbed);
    assert.notEqual(hash1, hash2);
  });

  it("strips undefined values cleanly from canonical representation", () => {
    const withUndef = { a: 1, b: undefined, c: 3 };
    const withoutUndef = { a: 1, c: 3 };
    assert.equal(DataVizHash.canonicalStringify(withUndef), DataVizHash.canonicalStringify(withoutUndef));
  });

  it("excludes checksumSha256 from participating in its own calculation (REQ-025 §53)", () => {
    const hashWithout = DataVizHash.computeSha256(baseIRPayload);
    const withChecksum: DataVizIR = {
      ...baseIRPayload,
      checksumSha256: hashWithout,
    };
    const hashWith = DataVizHash.computeSha256(withChecksum);
    assert.equal(hashWith, hashWithout);
  });
});
