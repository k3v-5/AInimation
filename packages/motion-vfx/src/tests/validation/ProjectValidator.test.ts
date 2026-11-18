import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { Composition } from "../../core/composition.js";
import { GroupElement, TextElement, VideoElement } from "../../elements/index.js";
import { ValidationError } from "../../errors/index.js";
import { ProjectValidator } from "../../validation/ProjectValidator.js";

describe("Fase 2C — ProjectValidator & AI Robustness Suite", () => {
  it("validates a healthy composition without issues", () => {
    const comp = new Composition({ width: 1080, height: 1920, fps: 30, duration: 10 });
    comp.assets.add({ id: "vid_1", type: "video", source: { path: "video.mp4" } });
    comp.addElement(new VideoElement({ id: "video_node", assetId: "vid_1" }));

    const report = ProjectValidator.validate(comp);
    assert.strictEqual(report.isValid, true);
    assert.strictEqual(report.issues.length, 0);
  });

  it("detects MISSING_ASSET when element references unknown asset ID", () => {
    const comp = new Composition({ width: 1080, height: 1920, fps: 30, duration: 10 });
    // Elemento que referencia asset no registrado
    comp.addElement(new VideoElement({ id: "video_orphan", assetId: "ghost_asset" }));

    const report = ProjectValidator.validate(comp);
    assert.strictEqual(report.isValid, false);
    const issue = report.issues.find((i) => i.code === "MISSING_ASSET");
    assert.ok(issue, "Expected MISSING_ASSET issue");
    assert.strictEqual(issue?.elementId, "video_orphan");
    assert.strictEqual(issue?.assetId, "ghost_asset");
  });

  it("detects MISSING_PARENT when element points to non-existent parentId", () => {
    const comp = new Composition({ width: 1080, height: 1920, fps: 30, duration: 10 });
    const text = new TextElement({ id: "text_node" });
    text.parentId = "missing_parent_id";
    comp.addElement(text);

    const report = ProjectValidator.validate(comp);
    assert.strictEqual(report.isValid, false);
    const issue = report.issues.find((i) => i.code === "MISSING_PARENT");
    assert.ok(issue, "Expected MISSING_PARENT issue");
    assert.strictEqual(issue?.elementId, "text_node");
  });

  it("detects INVALID_TRANSFORM when AI injects NaN or Infinity", () => {
    const comp = new Composition({ width: 1080, height: 1920, fps: 30, duration: 10 });
    const text = new TextElement({ id: "bad_transform_text" });
    text.transform.position.setValue({ x: NaN, y: Infinity });
    comp.addElement(text);

    const report = ProjectValidator.validate(comp);
    assert.strictEqual(report.isValid, false);
    const issue = report.issues.find((i) => i.code === "INVALID_TRANSFORM");
    assert.ok(issue, "Expected INVALID_TRANSFORM issue");
  });

  it("assertValid() throws ValidationError with diagnostic summary on invalid project", () => {
    const comp = new Composition({ width: 1080, height: 1920, fps: 30, duration: 10 });
    comp.addElement(new VideoElement({ id: "bad_elem", assetId: "missing" }));

    assert.throws(() => {
      ProjectValidator.assertValid(comp);
    }, ValidationError);
  });
});
