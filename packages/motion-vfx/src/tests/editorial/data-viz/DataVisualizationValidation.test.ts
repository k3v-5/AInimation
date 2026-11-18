import { describe, it } from "node:test";
import assert from "node:assert/strict";
import { validateDataset, assertValidDataset } from "../../../editorial/data-viz/validation.js";
import { DataVisualizationDataset } from "../../../editorial/data-viz/types.js";

describe("DataVisualizationValidation Tests", () => {
  it("rejects empty datasets with DATASET_EMPTY", () => {
    const ds: DataVisualizationDataset = {
      id: "empty_ds",
      columns: [{ key: "c1", label: "Col 1", type: "STRING" }],
      rows: [],
    };
    const diags = validateDataset(ds);
    assert.equal(diags.some((d) => d.code === "DATASET_EMPTY"), true);
    assert.throws(() => assertValidDataset(ds));
  });

  it("rejects NaN and Infinity in numeric columns", () => {
    const ds: DataVisualizationDataset = {
      id: "bad_num_ds",
      columns: [{ key: "val", label: "Value", type: "NUMBER" }],
      rows: [
        { val: 10 },
        { val: NaN },
        { val: Infinity },
      ],
    };
    const diags = validateDataset(ds);
    const errors = diags.filter((d) => d.code === "INVALID_NUMBER");
    assert.equal(errors.length, 2);
    assert.throws(() => assertValidDataset(ds));
  });

  it("distinguishes null from 0 correctly", () => {
    const ds: DataVisualizationDataset = {
      id: "null_vs_zero",
      columns: [{ key: "val", label: "Value", type: "NUMBER" }],
      rows: [
        { val: 0 },
        { val: null },
      ],
    };
    const diags = validateDataset(ds);
    // null y 0 no generan errores bloqueantes
    assert.equal(diags.some((d) => d.severity === "ERROR"), false);
  });

  it("detects duplicate rows and applies duplicate policy", () => {
    const ds: DataVisualizationDataset = {
      id: "dup_ds",
      columns: [{ key: "cat", label: "Category", type: "STRING" }],
      rows: [{ cat: "A" }, { cat: "B" }, { cat: "A" }],
    };

    // Policy REJECT
    const rejectDiags = validateDataset(ds, { duplicatePolicy: "REJECT" });
    assert.equal(rejectDiags.some((d) => d.code === "DUPLICATE_DATA" && d.severity === "ERROR"), true);

    // Policy KEEP_LAST
    const keepDiags = validateDataset(ds, { duplicatePolicy: "KEEP_LAST" });
    assert.equal(keepDiags.some((d) => d.code === "DUPLICATE_DATA" && d.severity === "WARNING"), true);
  });
});
