import { describe, it } from "node:test";
import assert from "node:assert/strict";
import { normalizeDataset } from "../../../editorial/data-viz/normalization.js";
import { DataVisualizationDataset } from "../../../editorial/data-viz/types.js";

describe("DataVisualizationNormalization Tests", () => {
  it("normalizes numeric values bounded strictly in [0.0, 1.0]", () => {
    const ds: DataVisualizationDataset = {
      id: "norm_test",
      columns: [{ key: "val", label: "Val", type: "NUMBER" }],
      rows: [{ val: 10 }, { val: 20 }, { val: 30 }],
    };

    const norm = normalizeDataset(ds);
    assert.equal(norm.rows[0].val.normalized, 0.0);
    assert.equal(norm.rows[1].val.normalized, 0.5);
    assert.equal(norm.rows[2].val.normalized, 1.0);
  });

  it("handles constant datasets by assigning exactly 0.5 without division by zero", () => {
    const ds: DataVisualizationDataset = {
      id: "constant_test",
      columns: [
        { key: "item", label: "Item", type: "STRING" },
        { key: "score", label: "Score", type: "NUMBER" },
      ],
      rows: [
        { item: "A", score: 100 },
        { item: "B", score: 100 },
        { item: "C", score: 100 },
      ],
    };

    const norm = normalizeDataset(ds);
    assert.equal(norm.rows[0].score.normalized, 0.5);
    assert.equal(norm.rows[1].score.normalized, 0.5);
    assert.equal(norm.rows[2].score.normalized, 0.5);
  });

  it("preserves dataset immutability without mutating input rows", () => {
    const ds: DataVisualizationDataset = {
      id: "immutability_test",
      columns: [{ key: "v", label: "V", type: "NUMBER" }],
      rows: [{ v: 42 }],
    };

    const clone = JSON.parse(JSON.stringify(ds));
    const norm = normalizeDataset(ds);

    assert.deepEqual(ds, clone);
    assert.notEqual(norm.rows, ds.rows);
  });

  it("extracts and sorts category domains deterministically", () => {
    const ds: DataVisualizationDataset = {
      id: "domains_test",
      columns: [{ key: "tag", label: "Tag", type: "STRING" }],
      rows: [{ tag: "Zebra" }, { tag: "Apple" }, { tag: "Mango" }],
    };

    const norm = normalizeDataset(ds);
    assert.deepEqual(norm.categoryDomains.tag, ["Apple", "Mango", "Zebra"]);
  });
});
