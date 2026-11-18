import { describe, it } from "node:test";
import assert from "node:assert/strict";
import { Composition } from "../../core/composition.js";
import { ShapeElement } from "../../elements/ShapeElement.js";
import { EDLExporter } from "../../exporters/edl/EDLExporter.js";

describe("Fase 17 — CMX 3600 EDL Exporter Tests", () => {
  it("exports a composition to standard CMX 3600 EDL format", () => {
    const comp = new Composition({
      name: "EDL_Demo_Project",
      width: 1920,
      height: 1080,
      fps: 30,
      duration: 10.0,
    });

    comp.addElement(new ShapeElement({ id: "l1", name: "Shot A", shapeType: "rectangle", shapeData: { width: 100, height: 100 }, startTime: 0, duration: 4.0 }));
    comp.addElement(new ShapeElement({ id: "l2", name: "Shot B", shapeType: "rectangle", shapeData: { width: 100, height: 100 }, startTime: 4.0, duration: 6.0 }));

    const result = EDLExporter.export(comp, {
      projectId: "proj_edl",
      revisionId: "rev_1",
    });

    assert.ok(result.edlContent.includes("TITLE: EDL_DEMO_PROJECT"));
    assert.ok(result.edlContent.includes("FCM: NON-DROP FRAME"));
    assert.ok(result.edlContent.includes("001  AX       V     C"));
    assert.ok(result.edlContent.includes("* FROM CLIP NAME: Shot A"));
    assert.ok(result.edlContent.includes("002  AX       V     C"));
    assert.ok(result.edlContent.includes("* FROM CLIP NAME: Shot B"));

    assert.ok(result.warnings.length > 0); // Warning about lossy features
    assert.equal(result.manifest.exporter, "EDLExporter");
  });

  it("throws in strict mode because EDL is inherently lossy for transforms", () => {
    const comp = new Composition({ name: "StrictEDL", width: 1920, height: 1080, fps: 30, duration: 5.0 });
    comp.addElement(new ShapeElement({ id: "l1", name: "Layer1", shapeType: "rectangle", shapeData: { width: 100, height: 100 } }));

    assert.throws(
      () => {
        EDLExporter.export(comp, { strict: true });
      },
      /EDL_STRICT_EXPORT_FAILED/
    );
  });
});
