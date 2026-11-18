import { describe, it } from "node:test";
import assert from "node:assert/strict";
import { performance } from "node:perf_hooks";
import { Composition } from "../../core/composition.js";
import { ShapeElement } from "../../elements/ShapeElement.js";
import { AfterEffectsJSXCompiler } from "../../exporters/ae/AfterEffectsJSXCompiler.js";
import { FCPXMLExporter } from "../../exporters/fcpxml/FCPXMLExporter.js";
import { EDLExporter } from "../../exporters/edl/EDLExporter.js";

describe("Fase 17 — Multi-Target Exporters Performance Benchmark", () => {
  it("benchmarks 10, 100 and 500 layers export pipeline with latency metrics", () => {
    const scales = [10, 100, 500];

    for (const count of scales) {
      const comp = new Composition({
        name: `BenchmarkComp_${count}`,
        width: 1920,
        height: 1080,
        fps: 30,
        duration: 30.0,
      });

      for (let i = 0; i < count; i++) {
        const l = new ShapeElement({
          id: `layer_${i}`,
          name: `Layer_${i}`,
          shapeType: "rectangle",
          shapeData: { width: 100, height: 100 },
          startTime: (i * 0.1) % 25,
          duration: 5,
        });
        l.transform.position.setValue({ x: (i * 20) % 1920, y: (i * 10) % 1080 });
        l.transform.opacity.setValue(0.9);
        comp.addElement(l);
      }

      // 1. Benchmark AE JSX
      const t0 = performance.now();
      const jsxResult = AfterEffectsJSXCompiler.compile(comp, { projectId: `proj_${count}`, revisionId: "rev_1" });
      const jsxTime = performance.now() - t0;

      // 2. Benchmark FCPXML
      const t1 = performance.now();
      const fcpxmlResult = FCPXMLExporter.export(comp, { projectId: `proj_${count}`, revisionId: "rev_1" });
      const fcpxmlTime = performance.now() - t1;

      // 3. Benchmark EDL
      const t2 = performance.now();
      const edlResult = EDLExporter.export(comp, { projectId: `proj_${count}`, revisionId: "rev_1" });
      const edlTime = performance.now() - t2;

      assert.ok(jsxResult.jsxContent.length > 0);
      assert.ok(fcpxmlResult.xmlContent.length > 0);
      assert.ok(edlResult.edlContent.length > 0);

      assert.ok(
        jsxTime < 250,
        `JSX export for ${count} layers took ${jsxTime.toFixed(2)}ms (expected < 250ms)`
      );
      assert.ok(
        fcpxmlTime < 250,
        `FCPXML export for ${count} layers took ${fcpxmlTime.toFixed(2)}ms (expected < 250ms)`
      );
      assert.ok(
        edlTime < 250,
        `EDL export for ${count} layers took ${edlTime.toFixed(2)}ms (expected < 250ms)`
      );
    }
  });
});
