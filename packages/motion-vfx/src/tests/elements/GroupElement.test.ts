import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { GroupElement } from "../../elements/GroupElement.js";
import { TextElement } from "../../elements/TextElement.js";
import { HierarchyCycleError } from "../../errors/index.js";

describe("Fase 2B — GroupElement Hierarchy & Container Tests", () => {
  it("adds, retrieves and removes child elements cleanly", () => {
    const group = new GroupElement({ id: "main_group" });
    const textChild = new TextElement({ id: "text_child", text: "Child" });

    group.addChild(textChild);
    assert.strictEqual(textChild.parentId, "main_group");
    assert.strictEqual(group.getChildren().length, 1);
    assert.strictEqual(group.getChild("text_child")?.id, "text_child");

    assert.strictEqual(group.removeChild("text_child"), true);
    assert.strictEqual(textChild.parentId, undefined);
    assert.strictEqual(group.getChildren().length, 0);
  });

  it("propagates group world transform to nested children during evaluation", () => {
    const group = new GroupElement({ id: "group_parent" });
    group.transform.position.setValue({ x: 100, y: 200 });

    const text = new TextElement({ id: "text_elem" });
    text.transform.position.setValue({ x: 50, y: 50 });

    group.addChild(text);

    const evaluatedGroup = group.evaluate(0);
    assert.strictEqual(evaluatedGroup.children.length, 1);

    const evaluatedChild = evaluatedGroup.children[0];
    assert.ok(evaluatedChild.transform);

    // Traslación compuesta: 100 + 50 = 150, 200 + 50 = 250
    assert.strictEqual(evaluatedChild.transform.matrix.tx, 150);
    assert.strictEqual(evaluatedChild.transform.matrix.ty, 250);
  });

  it("rejects adding group as child of itself with HierarchyCycleError", () => {
    const group = new GroupElement({ id: "self_group" });

    assert.throws(() => {
      group.addChild(group);
    }, HierarchyCycleError);
  });
});
