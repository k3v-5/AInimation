import assert from "node:assert/strict";
import { describe, it } from "node:test";
import fc from "fast-check";
import { AspectRatioAdapter } from "../../delivery/adapter/AspectRatioAdapter.js";
import { parseAspectRatio, AspectRatio } from "../../delivery/core/AspectRatio.js";
import { Composition } from "../../core/composition.js";
import { TextElement } from "../../elements/TextElement.js";

describe("Fase 25 — Capa 7: Property-Based Testing (fast-check) Suite", () => {
  it("PBT: AspectRatioAdapter guarantees base composition is strictly immutable for any dimensions", () => {
    fc.assert(
      fc.property(
        fc.constantFrom<AspectRatio>("9:16", "16:9", "1:1", "4:5", "21:9"),
        fc.integer({ min: 100, max: 2000 }),
        fc.integer({ min: 100, max: 2000 }),
        (targetRatio, initialX, initialY) => {
          const comp = new Composition({
            id: "comp_pbt",
            width: 1080,
            height: 1920,
            fps: 30,
            duration: 5.0,
          });

          const elem = new TextElement({
            id: "elem_pbt",
            name: "PBT Element",
            text: "Testing Immutability",
          });
          elem.transform.position.setValue({ x: initialX, y: initialY });
          comp.addElement(elem);

          const adapted = AspectRatioAdapter.adapt(comp, targetRatio);
          const targetDim = parseAspectRatio(targetRatio);

          // Invariantes del resultado adaptado
          assert.equal(adapted.composition.width, targetDim.width);
          assert.equal(adapted.composition.height, targetDim.height);
          assert.equal(adapted.composition.getElements().length, 1);

          // Invariantes de no-mutación de la composición base
          assert.equal(comp.width, 1080);
          assert.equal(comp.height, 1920);
          assert.equal(comp.getElements()[0].transform.position.getValue().x, initialX);
          assert.equal(comp.getElements()[0].transform.position.getValue().y, initialY);

          return true;
        }
      ),
      { numRuns: 50 }
    );
  });
});
