import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { TimeRange } from "../../timeline/core/TimeRange.js";

describe("Fase 5B — TimeRange Semiclosed Interval [start, end) Tests", () => {
  it("strictly implements [start, end) semantics (start inclusive, end exclusive)", () => {
    const range = new TimeRange(5.0, 10.0);

    assert.strictEqual(range.duration, 5.0);
    assert.strictEqual(range.contains(5.0), true); // start inclusive
    assert.strictEqual(range.contains(7.5), true); // interior
    assert.strictEqual(range.contains(10.0), false); // end exclusive
    assert.strictEqual(range.contains(4.999), false);
    assert.strictEqual(range.contains(10.001), false);
  });

  it("checks overlap between ranges accurately", () => {
    const r1 = new TimeRange(0, 5);
    const r2 = new TimeRange(3, 8);
    const r3 = new TimeRange(5, 10);

    assert.strictEqual(r1.overlaps(r2), true); // [0,5) overlaps [3,8) in [3,5)
    assert.strictEqual(r1.overlaps(r3), false); // [0,5) and [5,10) touch at 5 but do not overlap
  });

  it("throws ValidationError when end is smaller than start", () => {
    assert.throws(() => new TimeRange(10, 5), /cannot be smaller than 'start'/);
  });
});
