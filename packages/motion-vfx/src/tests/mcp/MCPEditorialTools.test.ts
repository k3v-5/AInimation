import test from "node:test";
import assert from "node:assert/strict";
import {
  editorial_compile_data_visualization,
  editorial_dataviz_to_jsx,
  editorial_parse_dataset,
} from "../../mcp/tools/dataviz-tools.js";
import {
  editorial_detect_redundancy,
  editorial_generate_trim_plan,
} from "../../mcp/tools/performance-tools.js";

test("MCP Editorial Tools Suite — DataViz, Performance & QA", async (t) => {
  await t.test("editorial_parse_dataset parses CSV into structured DataSet", async () => {
    const csvContent = "label,value\nCentro Histórico,40\nHospicio Cabañas,30\nVida Nocturna,20\nGastronomía,10";
    const result = await editorial_parse_dataset({
      format: "CSV",
      content: csvContent,
      title: "Puntos Visitados GDL",
    });

    assert.equal(result.success, true);
    assert.ok(result.dataset);
    assert.equal(result.dataset.rows.length, 4);
    assert.equal(result.dataset.rows[0]["label"], "Centro Histórico");
    assert.equal(result.dataset.rows[0]["value"], 40);
  });

  await t.test("editorial_compile_data_visualization compiles dataset into DataViz IR", async () => {
    const dataset = {
      id: "ds_test",
      title: "Horas de Actividad",
      unit: "h",
      points: [
        { id: "p1", label: "Día 1", value: 12 },
        { id: "p2", label: "Día 2", value: 14 },
      ],
    };

    const result = await editorial_compile_data_visualization({
      dataset: dataset as any,
      spec: {
        id: "viz_bar",
        type: "ANIMATED_BAR_CHART",
        theme: "TIME_EDITORIAL",
        orientation: "VERTICAL",
      } as any,
    });

    assert.ok(result);
    assert.equal(result.success, true);
    assert.ok(result.ir);
    assert.equal(result.ir.type, "BAR_CHART");
  });

  await t.test("editorial_dataviz_to_jsx transpiles DataViz IR to After Effects ExtendScript", async () => {
    const mockIR: any = {
      id: "viz_stat_72",
      type: "BIG_STAT",
      checksumSha256: "a".repeat(64),
      width: 1080,
      height: 1920,
      durationSeconds: 5.0,
      fps: 30,
      layers: [],
    };

    const result = await editorial_dataviz_to_jsx({ ir: mockIR });
    assert.equal(result.success, true);
    assert.match(result.jsxScript, /app\.beginUndoGroup/);
    assert.match(result.jsxScript, /comp\.motionBlur = true/);
  });

  await t.test("editorial_detect_redundancy flags duplicate arguments across speech segments", async () => {
    const segments: any[] = [
      { id: "s1", sourceClipId: "c1", startSeconds: 0, endSeconds: 4, transcript: "El Hospicio Cabañas tiene murales de Orozco extraordinarios.", confidence: 1.0, markers: [] },
      { id: "s2", sourceClipId: "c2", startSeconds: 10, endSeconds: 14, transcript: "Orozco pintó murales increíbles en el Hospicio Cabañas.", confidence: 1.0, markers: [] },
      { id: "s3", sourceClipId: "c3", startSeconds: 20, endSeconds: 24, transcript: "La gastronomía tapatía incluye tortas ahogadas y birria.", confidence: 1.0, markers: [] },
    ];

    const result = await editorial_detect_redundancy({ segments });
    assert.ok(result.redundancy);
  });

  await t.test("editorial_generate_trim_plan produces valid semantic trim report", async () => {
    const segments: any[] = [
      { id: "seg_1", sourceClipId: "c1", startSeconds: 0, endSeconds: 15, transcript: "Introducción a Guadalajara", confidence: 0.9, markers: [] },
      { id: "seg_2", sourceClipId: "c2", startSeconds: 15, endSeconds: 30, transcript: "Esperando en el semáforo", confidence: 0.4, markers: [] },
      { id: "seg_3", sourceClipId: "c3", startSeconds: 30, endSeconds: 50, transcript: "Llegada al Hospicio Cabañas", confidence: 0.95, markers: [] },
    ];

    const result = await editorial_generate_trim_plan({
      segments,
      sourceDurationSeconds: 50,
      profile: "DOCUMENTARY",
    });

    assert.ok(result.report);
  });
});
