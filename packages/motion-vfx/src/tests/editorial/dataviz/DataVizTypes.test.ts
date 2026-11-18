import { describe, it } from "node:test";
import assert from "node:assert/strict";
import {
  validateDataSet,
  validateTimelineEvents,
  validateBigStatData,
} from "../../../editorial/dataviz/validators.js";
import {
  DatasetValidationError,
  DatasetTooLargeError,
} from "../../../editorial/dataviz/errors.js";

describe("Fase 5A — DataViz Types & Validators Suite", () => {
  it("validates a compliant DataSet with unique points", () => {
    const valid = validateDataSet({
      id: "ds_01",
      title: "Quarterly Revenue",
      points: [
        { id: "p1", label: "Q1", value: 120.5 },
        { id: "p2", label: "Q2", value: 145.2 },
      ],
    });
    assert.equal(valid.id, "ds_01");
    assert.equal(valid.points.length, 2);
  });

  it("rejects empty points array with DatasetValidationError", () => {
    assert.throws(
      () => validateDataSet({ id: "ds_empty", points: [] }),
      (err: unknown) => err instanceof DatasetValidationError
    );
  });

  it("rejects duplicate point IDs with DUPLICATE_POINT_ID", () => {
    assert.throws(
      () =>
        validateDataSet({
          id: "ds_dupe",
          points: [
            { id: "p1", label: "Item 1", value: 10 },
            { id: "p1", label: "Item 2", value: 20 },
          ],
        }),
      (err: unknown) =>
        err instanceof DatasetValidationError && (err as DatasetValidationError).code === "DUPLICATE_POINT_ID"
    );
  });

  it("rejects NaN values in data points", () => {
    assert.throws(
      () =>
        validateDataSet({
          id: "ds_nan",
          points: [{ id: "p1", label: "Bad", value: NaN }],
        }),
      (err: unknown) => err instanceof DatasetValidationError
    );
  });

  it("rejects Infinity values in data points", () => {
    assert.throws(
      () =>
        validateDataSet({
          id: "ds_inf",
          points: [{ id: "p1", label: "Bad", value: Infinity }],
        }),
      (err: unknown) => err instanceof DatasetValidationError
    );
  });

  it("rejects empty labels in data points", () => {
    assert.throws(
      () =>
        validateDataSet({
          id: "ds_nolabel",
          points: [{ id: "p1", label: "", value: 50 }],
        }),
      (err: unknown) => err instanceof DatasetValidationError
    );
  });

  it("enforces MAX_DATA_POINTS limit by throwing DatasetTooLargeError", () => {
    const hugePoints = Array.from({ length: 1001 }, (_, i) => ({
      id: `pt_${i}`,
      label: `L_${i}`,
      value: i,
    }));

    assert.throws(
      () => validateDataSet({ id: "ds_huge", points: hugePoints }),
      (err: unknown) => err instanceof DatasetTooLargeError
    );
  });

  it("validates timeline events and detects duplicate event IDs", () => {
    const validEvents = validateTimelineEvents([
      { id: "ev1", date: "1969-07-20", label: "Moon Landing" },
      { id: "ev2", date: "1989-11-09", label: "Fall of Berlin Wall" },
    ]);
    assert.equal(validEvents.length, 2);

    assert.throws(
      () =>
        validateTimelineEvents([
          { id: "ev1", date: "1969-07-20", label: "Moon Landing" },
          { id: "ev1", date: "1989-11-09", label: "Conflict" },
        ]),
      (err: unknown) => err instanceof DatasetValidationError
    );
  });

  it("validates BigStat data and rejects empty label", () => {
    const stat = validateBigStatData({
      value: 1800000,
      label: "Affected People",
      unit: "COUNT",
    });
    assert.equal(stat.value, 1800000);

    assert.throws(
      () => validateBigStatData({ value: 100, label: "" }),
      (err: unknown) => err instanceof DatasetValidationError
    );
  });
});
