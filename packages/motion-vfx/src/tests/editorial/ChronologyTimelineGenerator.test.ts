import { describe, it } from "node:test";
import assert from "node:assert/strict";
import {
  DataSet,
  ChronologyTimelineSpec,
  generateChronologyTimeline,
  TIME_EDITORIAL_STYLE,
  DEFAULT_SAFE_ZONE,
} from "../../editorial/data-visualization/index.js";

describe("REQ-025 — ChronologyTimelineGenerator", () => {
  const sampleTimelineData: DataSet = {
    id: "ds_space_race",
    title: "Key Milestones of Space Exploration",
    columns: [
      { key: "date", label: "Date", type: "DATE" },
      { key: "event", label: "Mission Event", type: "STRING" },
      { key: "detail", label: "Description", type: "STRING" },
    ],
    rows: [
      { date: "1957-10-04", event: "Sputnik 1", detail: "First artificial satellite launched" },
      { date: "1961-04-12", event: "Vostok 1", detail: "Yuri Gagarin becomes first human in space" },
      { date: "1969-07-20", event: "Apollo 11", detail: "First crewed lunar landing" },
      { date: "1971-04-19", event: "Salyut 1", detail: "First space station launched into orbit" },
    ],
  };

  const baseSpec: ChronologyTimelineSpec = {
    id: "timeline_space",
    type: "CHRONOLOGY_TIMELINE",
    datasetId: "ds_space_race",
    dateColumn: "date",
    titleColumn: "event",
    descriptionColumn: "detail",
    orientation: "HORIZONTAL",
    showDates: true,
    showDescriptions: true,
    width: 1920,
    height: 1080,
    durationSeconds: 7.0,
    startTimeSeconds: 0.5,
    safeZone: DEFAULT_SAFE_ZONE,
    style: TIME_EDITORIAL_STYLE,
    animation: {
      entranceDurationSeconds: 1.5,
      exitDurationSeconds: 0.8,
      easing: "EASE_OUT",
    },
  };

  it("generates horizontal chronology timeline with alternating lanes and connector lines", () => {
    const result = generateChronologyTimeline(sampleTimelineData, baseSpec);

    assert.equal(result.success, true);
    assert.ok(result.ir);
    assert.equal(result.ir.type, "CHRONOLOGY_TIMELINE");

    // Eje principal de la línea de tiempo
    const axisLayer = result.ir.layers.find((l) => l.name === "DV::TIMELINE::AXIS");
    assert.ok(axisLayer);
    assert.equal(axisLayer.geometry?.kind, "LINE");

    // 4 nodos, 4 conectores, 4 títulos, 4 fechas, 4 descripciones
    const nodeLayers = result.ir.layers.filter((l) => l.name.startsWith("DV::TIMELINE::NODE::"));
    const connLayers = result.ir.layers.filter((l) => l.name.startsWith("DV::TIMELINE::CONN::"));
    const titleLayers = result.ir.layers.filter((l) => l.name.startsWith("DV::TIMELINE::TITLE::"));
    const dateLayers = result.ir.layers.filter((l) => l.name.startsWith("DV::TIMELINE::DATE::"));
    const descLayers = result.ir.layers.filter((l) => l.name.startsWith("DV::TIMELINE::DESC::"));

    assert.equal(nodeLayers.length, 4);
    assert.equal(connLayers.length, 4);
    assert.equal(titleLayers.length, 4);
    assert.equal(dateLayers.length, 4);
    assert.equal(descLayers.length, 4);

    // Verificar que los títulos son correctos y cronológicos
    assert.equal(titleLayers[0].text?.content, "Sputnik 1");
    assert.equal(titleLayers[2].text?.content, "Apollo 11");

    // Checksum determinista
    assert.ok(result.checksumSha256);
    assert.equal(result.checksumSha256.length, 64);
  });

  it("generates vertical chronology timeline orientation cleanly", () => {
    const verticalSpec: ChronologyTimelineSpec = {
      ...baseSpec,
      id: "timeline_vertical",
      orientation: "VERTICAL",
      width: 1080,
      height: 1920,
    };

    const result = generateChronologyTimeline(sampleTimelineData, verticalSpec);
    assert.equal(result.success, true);
    assert.ok(result.ir);
    assert.equal(result.ir.width, 1080);
    assert.equal(result.ir.height, 1920);

    const axisLayer = result.ir.layers.find((l) => l.name === "DV::TIMELINE::AXIS");
    assert.ok(axisLayer);
    // Eje vertical debe coincidir en X1 === X2
    const geo = axisLayer.geometry as any;
    assert.equal(geo.x1, geo.x2);
  });
});
