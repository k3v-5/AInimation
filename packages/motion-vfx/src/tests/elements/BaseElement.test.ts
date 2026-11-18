import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { BaseElement } from "../../elements/BaseElement.js";
import { ElementType, EvaluatedElement } from "../../elements/types.js";
import { EvaluatedTransform } from "../../transform/types.js";

class DummyElement extends BaseElement {
  public readonly type: ElementType = "shape";

  public clone(): DummyElement {
    const cloned = new DummyElement({
      name: `${this.name}_copy`,
      startTime: this.startTime,
      duration: this.duration,
      visible: this.visible,
    });
    return cloned;
  }

  public evaluate(globalTime: number, parentTransform?: EvaluatedTransform): EvaluatedElement {
    return {
      id: this.id,
      name: this.name,
      type: this.type,
      active: this.isActive(globalTime),
      localTime: this.getLocalTime(globalTime),
      visible: this.visible,
      transform: this.transform.evaluate(globalTime),
    };
  }
}

describe("Fase 2B — BaseElement Lifecycle, Timing & Cloning Tests", () => {
  it("initializes with stable ID and decoupled human name", () => {
    const elem = new DummyElement({ id: "title-main", name: "Main Title" });

    assert.strictEqual(elem.id, "title-main");
    assert.strictEqual(elem.name, "Main Title");

    // Cambiar nombre no altera ID
    elem.name = "Updated Title";
    assert.strictEqual(elem.id, "title-main");
    assert.strictEqual(elem.name, "Updated Title");
  });

  it("calculates localTime accurately (globalTime - startTime)", () => {
    const elem = new DummyElement({ startTime: 10, duration: 5 });

    assert.strictEqual(elem.getLocalTime(10), 0);
    assert.strictEqual(elem.getLocalTime(12.5), 2.5);
    assert.strictEqual(elem.getLocalTime(15), 5);
  });

  it("determines active status strictly on half-open interval [startTime, startTime + duration)", () => {
    const elem = new DummyElement({ startTime: 5, duration: 3 });

    // Límites y dentro del intervalo
    assert.strictEqual(elem.isActive(4.9), false);
    assert.strictEqual(elem.isActive(5.0), true);
    assert.strictEqual(elem.isActive(5.5), true);
    assert.strictEqual(elem.isActive(7.999), true);
    assert.strictEqual(elem.isActive(8.0), false);
    assert.strictEqual(elem.isActive(10.0), false);
  });

  it("respects visibility flag (visible = false disables active status even in time range)", () => {
    const elem = new DummyElement({ startTime: 0, duration: 10, visible: false });

    assert.strictEqual(elem.isActive(5), false);
  });

  it("clone() produces a deep copy with a newly generated unique ID", () => {
    const original = new DummyElement({ id: "original_elem", name: "Original", startTime: 2, duration: 4 });
    const clone = original.clone();

    assert.notStrictEqual(clone.id, original.id);
    assert.strictEqual(clone.startTime, original.startTime);
    assert.strictEqual(clone.duration, original.duration);
    assert.strictEqual(clone.name, "Original_copy");
  });
});
