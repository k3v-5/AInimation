import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { PropertyBindingEngine } from "../../tracking/core/PropertyBindingEngine.js";
import { PropertyBinding, TransformSample } from "../../tracking/types/index.js";

describe("Fase 5G — Property Binding & Target Transform Mapping Tests", () => {
  it("binds tracker transform to target property with spatial offset and scale multiplier", () => {
    const binding: PropertyBinding = {
      id: "bind_title_to_head",
      sourceTrackerId: "tracker_head",
      targetElementId: "element_caption",
      targetProperty: "transform",
      offset: { x: 0, y: -150 }, // 150px por encima de la cabeza
      scaleMultiplier: { x: 1.2, y: 1.2 },
      rotationOffset: 5,
    };

    const trackedTransform: TransformSample = {
      position: { x: 500, y: 800 },
      scale: { x: 1.0, y: 1.0 },
      rotation: 10,
    };

    const mapped = PropertyBindingEngine.applyBinding(binding, trackedTransform);

    // Posición resultante: (500, 800 - 150) = (500, 650)
    assert.strictEqual(mapped.position?.x, 500);
    assert.strictEqual(mapped.position?.y, 650);

    // Escala: 1.0 * 1.2 = 1.2
    assert.strictEqual(mapped.scale?.x, 1.2);
    assert.strictEqual(mapped.scale?.y, 1.2);

    // Rotación: 10 + 5 = 15
    assert.strictEqual(mapped.rotation, 15);
  });
});
