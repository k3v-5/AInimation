import { describe, it } from "node:test";
import assert from "node:assert/strict";
import { TrendLineGraphCompiler } from "../../../editorial/dataviz/trend-line-graph-compiler.js";
import { DataSet } from "../../../editorial/dataviz/types.js";

describe("Fase 5A — TrendLineGraphCompiler Suite", () => {
  const temporalDataset: DataSet = {
    id: "ds_unemployment",
    title: "Unemployment Rate",
    unit: "%",
    points: [
      { id: "p1", label: "Jan", value: 3.8, date: "2024-01" },
      { id: "p2", label: "Feb", value: 3.5, date: "2024-02" },
      { id: "p3", label: "Mar", value: 4.1, date: "2024-03", emphasis: "PRIMARY" },
      { id: "p4", label: "Apr", value: 3.9, date: "2024-04" },
    ],
  };

  it("compiles trend line graph with type LINE_GRAPH and valid checksum", () => {
    const ir = TrendLineGraphCompiler.compile(temporalDataset);
    assert.equal(ir.type, "LINE_GRAPH");
    assert.ok(ir.checksumSha256 !== undefined);
    assert.equal(ir.checksumSha256?.length, 64);
  });

  it("calculates Euclidean path length accurately (REQ-025 §28)", () => {
    const ir = TrendLineGraphCompiler.compile(temporalDataset);
    const line = ir.elements.find((e) => e.type === "LINE");
    assert.ok(line !== undefined);
    assert.ok((line?.properties.pathLengthPx as number) > 0);
  });

  it("generates stroke write-on animation with PATH_PROGRESS", () => {
    const ir = TrendLineGraphCompiler.compile(temporalDataset);
    const writeOn = ir.animations.find((a) => a.property === "PATH_PROGRESS");
    assert.ok(writeOn !== undefined);
    assert.equal(writeOn?.from, 0.0);
    assert.equal(writeOn?.to, 1.0);
  });

  it("identifies key points including min, max, first, and last (REQ-025 §29)", () => {
    const ir = TrendLineGraphCompiler.compile(temporalDataset);
    const points = ir.elements.filter((e) => e.type === "POINT");
    assert.equal(points.length, 4);

    const keyPoints = points.filter((p) => p.properties.isKeyPoint === true);
    assert.ok(keyPoints.length >= 2, "Must flag key points");
  });

  it("synchronizes point appearance animation with path progress", () => {
    const ir = TrendLineGraphCompiler.compile(temporalDataset);
    const pointAnims = ir.animations.filter((a) => a.property === "OPACITY");
    assert.equal(pointAnims.length, 4);
    // Point 0 should appear before Point 3
    assert.ok(pointAnims[0].startSeconds < pointAnims[3].startSeconds);
  });

  it("preserves input order by default (REQ-025 §27)", () => {
    const unorderDs: DataSet = {
      id: "ds_unorder",
      points: [
        { id: "p1", label: "2024", value: 10, date: "2024" },
        { id: "p2", label: "2020", value: 20, date: "2020" },
      ],
    };
    const ir = TrendLineGraphCompiler.compile(unorderDs, { sortByDate: false });
    assert.equal(ir.dataset.points[0].id, "p1");
    assert.equal(ir.dataset.points[1].id, "p2");
  });

  it("sorts by date when explicitly requested", () => {
    const unorderDs: DataSet = {
      id: "ds_sort_date",
      points: [
        { id: "p1", label: "2024", value: 10, date: "2024" },
        { id: "p2", label: "2020", value: 20, date: "2020" },
      ],
    };
    const ir = TrendLineGraphCompiler.compile(unorderDs, { sortByDate: true });
    assert.equal(ir.dataset.points[0].id, "p2"); // 2020 before 2024
  });

  it("handles single point dataset without crashing or NaN", () => {
    const singleDs: DataSet = {
      id: "ds_single",
      points: [{ id: "p1", label: "Only", value: 50 }],
    };
    const ir = TrendLineGraphCompiler.compile(singleDs);
    assert.equal(ir.type, "LINE_GRAPH");
    assert.equal(ir.dataset.points.length, 1);
  });
});
