import { describe, it } from "node:test";
import assert from "node:assert/strict";
import { Composition } from "../../core/composition.js";
import { ShapeElement } from "../../elements/ShapeElement.js";
import { TextElement } from "../../elements/TextElement.js";
import { AfterEffectsJSXCompiler } from "../../exporters/ae/AfterEffectsJSXCompiler.js";
import { FCPXMLExporter } from "../../exporters/fcpxml/FCPXMLExporter.js";
import { EDLExporter } from "../../exporters/edl/EDLExporter.js";

describe("Fase 17 — Deterministic Cross-Process & Invariants Tests", () => {
  it("guarantees 100% byte-for-byte identical output across separate compilation runs", () => {
    function buildSampleComp(): Composition {
      const comp = new Composition({
        name: "Determinism_Comp",
        width: 1080,
        height: 1920,
        fps: 30,
        duration: 10.0,
      });

      const l1 = new ShapeElement({
        id: "layer_01",
        name: "Main Visual",
        shapeType: "rectangle",
        shapeData: { width: 500, height: 500 },
        startTime: 0,
        duration: 5,
      });
      l1.transform.position.setValue({ x: 540, y: 960 });
      l1.transform.scale.addKeyframe(0, { x: 1, y: 1 });
      l1.transform.scale.addKeyframe(2, { x: 1.5, y: 1.5 });

      const l2 = new TextElement({
        id: "layer_02",
        name: "Text Title",
        text: "Titulo Determinista",
        parentId: "layer_01",
        startTime: 2,
        duration: 6,
      });

      comp.addElement(l1);
      comp.addElement(l2);
      return comp;
    }

    // Proceso / Run A
    const compA = buildSampleComp();
    const jsxA = AfterEffectsJSXCompiler.compile(compA, { projectId: "proj_det", revisionId: "rev_1" });
    const fcpxmlA = FCPXMLExporter.export(compA, { projectId: "proj_det", revisionId: "rev_1" });
    const edlA = EDLExporter.export(compA, { projectId: "proj_det", revisionId: "rev_1" });

    // Proceso / Run B
    const compB = buildSampleComp();
    const jsxB = AfterEffectsJSXCompiler.compile(compB, { projectId: "proj_det", revisionId: "rev_1" });
    const fcpxmlB = FCPXMLExporter.export(compB, { projectId: "proj_det", revisionId: "rev_1" });
    const edlB = EDLExporter.export(compB, { projectId: "proj_det", revisionId: "rev_1" });

    // Verificación de determinismo estricto
    assert.equal(jsxA.jsxContent, jsxB.jsxContent, "JSX code must be byte-for-byte identical");
    assert.equal(
      jsxA.manifest.deterministicHash,
      jsxB.manifest.deterministicHash,
      "JSX manifest hash must match"
    );

    assert.equal(fcpxmlA.xmlContent, fcpxmlB.xmlContent, "FCPXML code must be byte-for-byte identical");
    assert.equal(
      fcpxmlA.manifest.deterministicHash,
      fcpxmlB.manifest.deterministicHash,
      "FCPXML manifest hash must match"
    );

    assert.equal(edlA.edlContent, edlB.edlContent, "EDL code must be byte-for-byte identical");
    assert.equal(
      edlA.manifest.deterministicHash,
      edlB.manifest.deterministicHash,
      "EDL manifest hash must match"
    );
  });
});
