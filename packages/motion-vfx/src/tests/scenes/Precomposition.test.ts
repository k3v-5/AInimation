import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { Composition } from "../../core/composition.js";
import { CompositionElement } from "../../elements/CompositionElement.js";
import { TextElement } from "../../elements/TextElement.js";

describe("Fase 5C — Precomposition & Nested Scene Evaluation Tests", () => {
  it("evaluates nested CompositionElement cascading transforms and local timing", () => {
    // 1. Crear sub-composición interna
    const innerComp = new Composition({
      id: "inner_comp",
      width: 1920,
      height: 1080,
      fps: 30,
      duration: 10.0,
    });

    const innerText = new TextElement({
      id: "inner_title",
      text: "Nested Hello",
      startTime: 0,
      duration: 10,
    });
    innerText.transform.position.setValue({ x: 100, y: 100 });
    innerComp.addElement(innerText);

    // 2. Crear CompositionElement contenedor en tiempo global = 5s
    const precompElem = new CompositionElement({
      id: "precomp_hero",
      composition: innerComp,
      startTime: 5.0,
      duration: 10.0,
    });
    precompElem.transform.position.setValue({ x: 200, y: 300 });

    // En globalTime = 7.0s -> localTime = 2.0s
    const state = precompElem.evaluate(7.0);
    assert.strictEqual(state.active, true);
    assert.strictEqual(state.localTime, 2.0);
    assert.strictEqual(state.elements.length, 1);
    assert.strictEqual(state.elements[0].id, "inner_title");
  });
});
