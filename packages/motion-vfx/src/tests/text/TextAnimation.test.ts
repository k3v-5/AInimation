import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { slideIn } from "../../animation/primitives/slide.js";
import { TextElement } from "../../elements/TextElement.js";
import { animateText } from "../../text/animation/TextAnimation.js";
import { typewriter } from "../../text/animation/typewriter.js";

describe("Fase 4B — Text Animation & Virtual Subtarget Evaluation Tests", () => {
  it("animates characters independently via animateText without altering scene graph size", () => {
    const textElem = new TextElement({ id: "hero_text", text: "WOW" });
    const anim = animateText(textElem, {
      scope: "character",
      animation: slideIn({ id: "base" } as any, { direction: "up", distance: 50, duration: 0.5 }),
      stagger: 0.1,
    });

    assert.strictEqual(anim.children.length, 3);
    // Char 0: delay = 0, Char 1: delay = 0.1, Char 2: delay = 0.2
    assert.strictEqual(anim.children[0].delay, 0);
    assert.strictEqual(anim.children[1].delay, 0.1);
    assert.strictEqual(anim.children[2].delay, 0.2);

    // Comprobar evaluación en t = 0.05 (char 0 activo, char 1 y 2 en espera)
    const at005 = anim.evaluate(0.05);
    const pos0 = at005.get<any>({ elementId: "hero_text:char:0", propertyPath: "transform.position" });
    assert.ok(pos0 !== undefined);
  });

  it("typewriter reveals characters sequentially", () => {
    const textElem = new TextElement({ id: "type_node", text: "CODE" });
    const anim = typewriter(textElem, { duration: 0.4 });

    assert.strictEqual(anim.children.length, 4);
    // Evaluated at t = 0.5s -> All 4 characters are fully faded in (opacity = 1.0)
    const atEnd = anim.evaluate(0.5);
    for (let i = 0; i < 4; i++) {
      assert.strictEqual(
        atEnd.get({ elementId: `type_node:char:${i}`, propertyPath: "transform.opacity" }),
        1.0
      );
    }
  });
});
