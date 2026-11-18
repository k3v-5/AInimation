import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { Composition } from "../../core/composition.js";
import { TextElement } from "../../elements/TextElement.js";
import { AEBridgeManager } from "../../exporters/ae/AEBridgeManager.js";

describe("Fase 26 — Capa 4: After Effects Bridge Integration Tests", () => {
  it("compiles a composition, validates expressions and provides unified bridge access", () => {
    const comp = new Composition({
      id: "comp_bridge",
      name: "Bridge Showcase",
      width: 1920,
      height: 1080,
      fps: 60,
      duration: 5.0,
    });

    const title = new TextElement({
      id: "t_bridge",
      name: "Hero Title",
      text: "HELLO AE BRIDGE",
      style: { fontSize: 72, fontFamily: "Inter-Bold" },
    });
    comp.addElement(title);

    const result = AEBridgeManager.compileProject(comp, {
      projectId: "proj_bridge",
      revisionId: "rev_bridge",
    });

    assert.ok(result.jsxContent.includes('addComp("Bridge Showcase"'));
    assert.ok(result.jsxContent.includes('Hero Title'));

    // Validar generador de expresiones a través del bridge
    const wiggleExpr = AEBridgeManager.expressions.wiggle(2, 30);
    assert.equal(AEBridgeManager.validateExpression(wiggleExpr).valid, true);

    // Compilar shape layer a través del bridge
    const shapeCode = AEBridgeManager.compileShapeLayers("comp", "Vector_Decor", [
      {
        name: "Circle",
        contents: [{ type: "ellipse", size: [200, 200] }],
        fillColor: [0, 1, 0],
      },
    ]);
    assert.ok(shapeCode.join("\n").includes('"ADBE Vector Shape - Ellipse"'));
  });
});
