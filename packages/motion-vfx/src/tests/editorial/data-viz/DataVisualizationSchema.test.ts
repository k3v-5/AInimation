import { describe, it } from "node:test";
import assert from "node:assert/strict";
import {
  DataVisualizationDatasetSchema,
  BarChartSpecSchema,
  TrendLineSpecSchema,
  BigStatSpecSchema,
  ChronologyTimelineSpecSchema,
} from "../../../editorial/data-viz/schema.js";

describe("DataVisualizationSchema Tests (Zod Contracts)", () => {
  it("validates a complete valid dataset structure", () => {
    const raw = {
      id: "ds_valid_01",
      title: "Global GDP",
      unit: "CURRENCY",
      source: {
        id: "src_imf",
        title: "IMF World Economic Outlook",
      },
      columns: [
        { key: "country", label: "Country", type: "STRING" },
        { key: "gdp", label: "GDP (B$)", type: "NUMBER" },
      ],
      rows: [
        { country: "USA", gdp: 28780 },
        { country: "China", gdp: 18530 },
      ],
    };

    const parsed = DataVisualizationDatasetSchema.parse(raw);
    assert.equal(parsed.id, "ds_valid_01");
    assert.equal(parsed.columns.length, 2);
    assert.equal(parsed.rows.length, 2);
  });

  it("rejects dataset with invalid column type", () => {
    const raw = {
      id: "ds_invalid",
      columns: [{ key: "val", label: "Value", type: "INVALID_TYPE" }],
      rows: [],
    };
    assert.throws(() => DataVisualizationDatasetSchema.parse(raw));
  });

  it("validates bar chart and trend line specs", () => {
    const barSpec = {
      categoryColumn: "country",
      valueColumns: ["gdp"],
      orientation: "VERTICAL",
      sort: "DESCENDING",
      showValues: true,
      showLabels: true,
      showAxis: true,
      animationDurationSeconds: 2.0,
    };
    assert.doesNotThrow(() => BarChartSpecSchema.parse(barSpec));

    const trendSpec = {
      xColumn: "year",
      yColumn: "temp",
      showPoints: true,
      showLabels: false,
      showAxis: true,
      showGrid: true,
      highlightExtrema: true,
      animationDurationSeconds: 1.5,
    };
    assert.doesNotThrow(() => TrendLineSpecSchema.parse(trendSpec));
  });

  it("validates big stat and chronology specs", () => {
    const bigStat = {
      staticValue: 1200000,
      label: "Active Users",
      unit: "COUNT",
      animationDurationSeconds: 1.8,
    };
    assert.doesNotThrow(() => BigStatSpecSchema.parse(bigStat));

    const timeline = {
      orientation: "HORIZONTAL",
      animationDurationSeconds: 3.0,
      events: [
        { date: "2024-01-01", title: "Project Kickoff" },
        { date: "2024-06-01", title: "Alpha Release" },
      ],
    };
    assert.doesNotThrow(() => ChronologyTimelineSpecSchema.parse(timeline));
  });
});
