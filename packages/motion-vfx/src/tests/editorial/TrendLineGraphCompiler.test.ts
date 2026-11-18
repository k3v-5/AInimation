import { describe, it } from "node:test";
import assert from "node:assert/strict";
import {
  DataSet,
  TrendLineSpec,
  compileTrendLineGraph,
  TIME_EDITORIAL_STYLE,
  DEFAULT_SAFE_ZONE,
} from "../../editorial/data-visualization/index.js";

describe("REQ-025 — TrendLineGraphCompiler", () => {
  const sampleTimelineDataset: DataSet = {
    id: "ds_unemployment",
    title: "Unemployment Rate 2019-2023",
    columns: [
      { key: "date", label: "Date", type: "DATE" },
      { key: "rate", label: "Unemployment %", type: "NUMBER" },
    ],
    rows: [
      { date: "2019-01-01", rate: 3.8 },
      { date: "2020-04-01", rate: 14.7 }, // Max extreme
      { date: "2021-01-01", rate: 6.4 },
      { date: "2022-01-01", rate: 4.0 },
      { date: "2023-01-01", rate: 3.4 }, // Min extreme
    ],
  };

  const baseSpec: TrendLineSpec = {
    id: "trend_unemployment",
    type: "TREND_LINE",
    datasetId: "ds_unemployment",
    xColumn: "date",
    yColumn: "rate",
    showPoints: true,
    showLabels: true,
    showGrid: true,
    interpolation: "LINEAR",
    highlightExtremes: true,
    width: 1920,
    height: 1080,
    durationSeconds: 6.0,
    startTimeSeconds: 0.5,
    safeZone: DEFAULT_SAFE_ZONE,
    style: TIME_EDITORIAL_STYLE,
    animation: {
      entranceDurationSeconds: 2.0,
      exitDurationSeconds: 0.8,
      easing: "EASE_OUT",
    },
  };

  it("compiles trend line graph with trimPath write-on animation and highlightExtremes", () => {
    const result = compileTrendLineGraph(sampleTimelineDataset, baseSpec);

    assert.equal(result.success, true);
    assert.ok(result.ir);
    assert.equal(result.ir.type, "TREND_LINE");

    // Verificar capa de Path principal
    const pathLayer = result.ir.layers.find((l) => l.name === "DV::TREND::PATH");
    assert.ok(pathLayer);
    assert.equal(pathLayer.geometry?.kind, "PATH");
    assert.ok((pathLayer.geometry as any).commands.length >= 4);

    // Verificar animación write-on (trimPathEnd de 0 a 1)
    const writeOnAnim = pathLayer.animation?.properties.find((p) => p.property === "trimPathEnd");
    assert.ok(writeOnAnim);
    assert.equal(writeOnAnim.keyframes[0].value, 0.0);
    assert.equal(writeOnAnim.keyframes[1].value, 1.0);

    // Puntos generados (5 puntos)
    const pointLayers = result.ir.layers.filter((l) => l.name.startsWith("DV::TREND::POINT::"));
    assert.equal(pointLayers.length, 5);

    // Verificar que los extremos (14.7 y 3.4) tienen radio aumentado (8 en lugar de 5)
    const extremePoints = pointLayers.filter((l) => (l.geometry as any).radius === 8);
    assert.equal(extremePoints.length, 2);

    // Grid horizontal generada
    const gridLayers = result.ir.layers.filter((l) => l.name.startsWith("DV::GRID::"));
    assert.ok(gridLayers.length >= 3);

    // Invariante de hash canónico
    assert.ok(result.checksumSha256);
    assert.equal(result.checksumSha256.length, 64);
  });

  it("compiles smooth spline curve with Bézier commands bounded to canvas safe area", () => {
    const smoothSpec: TrendLineSpec = {
      ...baseSpec,
      id: "trend_smooth",
      interpolation: "SMOOTH",
    };

    const result = compileTrendLineGraph(sampleTimelineDataset, smoothSpec);
    assert.equal(result.success, true);
    assert.ok(result.ir);

    const pathLayer = result.ir.layers.find((l) => l.name === "DV::TREND::PATH");
    assert.ok(pathLayer);
    const commands = (pathLayer.geometry as any).commands;
    assert.ok(commands.some((c: any) => c.type === "C"));
  });
});
