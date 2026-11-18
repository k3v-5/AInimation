import { describe, it } from "node:test";
import assert from "node:assert/strict";
import {
  DataSet,
  BarChartSpec,
  compileAnimatedBarChart,
  TIME_EDITORIAL_STYLE,
  DEFAULT_SAFE_ZONE,
} from "../../editorial/data-visualization/index.js";

describe("REQ-025 — AnimatedBarChartCompiler", () => {
  const sampleDataset: DataSet = {
    id: "ds_gdp_growth",
    title: "GDP Growth 2024",
    columns: [
      { key: "country", label: "Country", type: "STRING" },
      { key: "gdp", label: "GDP Growth %", type: "NUMBER" },
    ],
    rows: [
      { country: "Germany", gdp: 0.2 },
      { country: "USA", gdp: 2.8 },
      { country: "India", gdp: 6.8 },
      { country: "Japan", gdp: 0.7 },
      { country: "Brazil", gdp: 2.1 },
    ],
  };

  const baseSpec: BarChartSpec = {
    id: "chart_gdp_2024",
    type: "ANIMATED_BAR_CHART",
    datasetId: "ds_gdp_growth",
    categoryColumn: "country",
    valueColumn: "gdp",
    orientation: "VERTICAL",
    sort: "DESCENDING",
    showValues: true,
    showLabels: true,
    showAxis: true,
    showGrid: true,
    animateCounters: true,
    width: 1920,
    height: 1080,
    durationSeconds: 5.0,
    startTimeSeconds: 0.5,
    safeZone: DEFAULT_SAFE_ZONE,
    style: TIME_EDITORIAL_STYLE,
    animation: {
      entranceDurationSeconds: 1.2,
      exitDurationSeconds: 0.5,
      easing: "EASE_OUT",
      staggerSeconds: 0.1,
    },
  };

  it("compiles vertical bar chart with descending sort and counter animations", () => {
    const result = compileAnimatedBarChart(sampleDataset, baseSpec);

    assert.equal(result.success, true);
    assert.ok(result.ir);
    assert.equal(result.ir.type, "ANIMATED_BAR_CHART");
    assert.equal(result.ir.width, 1920);
    assert.equal(result.ir.height, 1080);
    assert.equal(result.ir.durationSeconds, 5.0);

    // Debe contener capas de fondo, barra, label y value para cada barra
    const barLayers = result.ir.layers.filter((l) => l.name.startsWith("DV::BAR::"));
    const labelLayers = result.ir.layers.filter((l) => l.name.startsWith("DV::LABEL::"));
    const valueLayers = result.ir.layers.filter((l) => l.name.startsWith("DV::VALUE::"));

    assert.equal(barLayers.length, 5);
    assert.equal(labelLayers.length, 5);
    assert.equal(valueLayers.length, 5);

    // Al ordenar descendente, la primera barra debe ser India (6.8)
    const firstLabel = labelLayers[0].text?.content;
    assert.equal(firstLabel, "India");

    // Verificar animación de contador en valores
    const firstValAnim = valueLayers[0].animation?.properties.find((p) => p.property === "counterValue");
    assert.ok(firstValAnim);
    assert.equal(firstValAnim.keyframes[1].value, 6.8);

    // Verificar SHA-256 no vacío y métricas
    assert.ok(result.checksumSha256);
    assert.equal(result.checksumSha256.length, 64);
    assert.equal(result.metrics?.dataPointCount, 5);
    assert.ok(result.metrics.layerCount >= 15);
  });

  it("compiles horizontal bar chart respecting maxBars constraint", () => {
    const horizontalSpec: BarChartSpec = {
      ...baseSpec,
      id: "chart_gdp_horiz",
      orientation: "HORIZONTAL",
      maxBars: 3,
    };

    const result = compileAnimatedBarChart(sampleDataset, horizontalSpec);
    assert.equal(result.success, true);
    assert.ok(result.ir);

    const barLayers = result.ir.layers.filter((l) => l.name.startsWith("DV::BAR::"));
    assert.equal(barLayers.length, 3);
  });

  it("rejects compilation if required category or value column is missing", () => {
    const invalidSpec: BarChartSpec = {
      ...baseSpec,
      categoryColumn: "non_existent_column",
    };

    const result = compileAnimatedBarChart(sampleDataset, invalidSpec);
    assert.equal(result.success, false);
    assert.equal(result.errors.some((e) => e.code === "REQUIRED_COLUMN_MISSING"), true);
  });
});
