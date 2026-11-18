import { describe, it } from "node:test";
import assert from "node:assert/strict";
import { Composition } from "../../core/composition.js";
import { Layer } from "../../core/layer.js";
import { FCPXMLExporter } from "../../exporters/fcpxml/FCPXMLExporter.js";

describe("Fase 17 — Apple FCPXML Exporter Tests", () => {
  it("exports a composition to well-formed FCPXML v1.9 format", () => {
    const comp = new Composition({
      name: "FCPXML_Demo",
      width: 1080,
      height: 1920,
      fps: 30,
      duration: 15.0,
    });

    comp.addLayer(new Layer({ id: "l1", name: "Intro Clip", startTime: 0, endTime: 5 }));
    comp.addLayer(new Layer({ id: "l2", name: "Main Section", startTime: 5, endTime: 15 }));

    const result = FCPXMLExporter.export(comp, {
      projectId: "proj_fcpxml",
      revisionId: "rev_1",
    });

    assert.ok(result.xmlContent.startsWith("<?xml version="));
    assert.ok(result.xmlContent.includes('<fcpxml version="1.9">'));
    assert.ok(result.xmlContent.includes('<format id="r1"'));
    assert.ok(result.xmlContent.includes('<project name="FCPXML_Demo">'));
    assert.ok(result.xmlContent.includes('<title name="Intro Clip"'));
    assert.ok(result.xmlContent.includes('<title name="Main Section"'));

    assert.equal(result.manifest.exporter, "FCPXMLExporter");
    assert.ok(result.manifest.deterministicHash.length === 64);
  });
});
