import { describe, it } from "node:test";
import assert from "node:assert/strict";
import { Composition } from "../../core/composition.js";
import { ShapeElement } from "../../elements/ShapeElement.js";
import { TextElement } from "../../elements/TextElement.js";
import { AfterEffectsJSXCompiler } from "../../exporters/ae/AfterEffectsJSXCompiler.js";
import { AECapabilityAnalyzer } from "../../exporters/ae/AECapabilityMatrix.js";

describe("Fase 17 — AfterEffectsJSXCompiler Tests", () => {
  it("compiles a composition with elements, transforms, keyframes and parenting", () => {
    const comp = new Composition({
      name: "Comp_Test_AE",
      width: 1920,
      height: 1080,
      fps: 30,
      duration: 10.0,
    });

    const parentElem = new ShapeElement({
      id: "layer_parent",
      name: "ParentLayer",
      shapeType: "rectangle",
      shapeData: { width: 400, height: 300 },
      startTime: 0,
      duration: 10,
    });

    const childElem = new TextElement({
      id: "layer_child",
      name: "ChildLayer",
      text: "Subtítulo enlazado",
      parentId: "layer_parent",
      startTime: 1,
      duration: 8,
    });

    // Animar escala en childElem
    childElem.transform.scale.addKeyframe(1.0, { x: 0, y: 0 });
    childElem.transform.scale.addKeyframe(2.0, { x: 1.2, y: 1.2 });

    comp.addElement(parentElem);
    comp.addElement(childElem);

    const result = AfterEffectsJSXCompiler.compile(comp, {
      projectId: "proj_ae_test",
      revisionId: "rev_1",
    });

    assert.ok(result.jsxContent.includes('addComp("Comp_Test_AE", 1920, 1080, 1, 10, 30)'));
    assert.ok(result.jsxContent.includes("ParentLayer"));
    assert.ok(result.jsxContent.includes("ChildLayer"));
    assert.ok(result.jsxContent.includes("layer_2.parent = layer_1")); // Parenting check
    assert.ok(result.jsxContent.includes("setValueAtTime(1, [0, 0])")); // Keyframe check
    assert.ok(result.jsxContent.includes("setValueAtTime(2, [120, 120])")); // Scale percentage check

    assert.ok(result.manifest.deterministicHash.length === 64);
    assert.equal(result.manifest.projectId, "proj_ae_test");
    assert.equal(result.manifest.revisionId, "rev_1");
  });

  it("supports dryRun producing capability plan without raw execution code", () => {
    const comp = new Composition({ name: "DryRunComp", width: 1080, height: 1920, fps: 30, duration: 5.0 });
    comp.addElement(new ShapeElement({ id: "l1", name: "Layer1", shapeType: "rectangle", shapeData: { width: 100, height: 100 } }));

    const dryResult = AfterEffectsJSXCompiler.compile(comp, { dryRun: true });
    assert.ok(dryResult.plan.canProceed);
    assert.ok(dryResult.jsxContent.includes("DRY RUN"));
  });

  it("generates an accurate AECapabilityReport", () => {
    const report = AECapabilityAnalyzer.getCapabilityReport();
    assert.equal(report.target, "after-effects");
    assert.ok(report.exactCount > 0);
    assert.ok(report.entries.length > 0);
  });
});
