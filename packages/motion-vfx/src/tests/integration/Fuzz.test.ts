import assert from "node:assert/strict";
import { describe, it } from "node:test";
import fc from "fast-check";
import { Composition } from "../../core/composition.js";
import { ShapeElement, TextElement } from "../../elements/index.js";
import { deserializeComposition } from "../../serialization/deserializer.js";
import { serializeComposition } from "../../serialization/serializer.js";
import { ProjectValidator } from "../../validation/ProjectValidator.js";

describe("Fase 2C — Fuzz Testing & Resilience Suite (fast-check)", () => {
  it("generative fuzzing: randomized project trees evaluate and serialize safely", () => {
    fc.assert(
      fc.property(
        fc.integer({ min: 1, max: 10 }), // element count
        fc.double({ noNaN: true, noDefaultInfinity: true, min: 1, max: 20 }), // comp duration
        fc.double({ noNaN: true, noDefaultInfinity: true, min: 0, max: 20 }), // eval timestamp
        (elemCount, duration, evalTime) => {
          const comp = new Composition({
            width: 1080,
            height: 1920,
            fps: 30,
            duration,
          });

          for (let i = 0; i < elemCount; i++) {
            if (i % 2 === 0) {
              const text = new TextElement({
                id: `text_${i}`,
                text: `Fuzz Text ${i}`,
                startTime: 0,
                duration: duration / 2,
              });
              comp.addElement(text);
            } else {
              const shape = new ShapeElement({
                id: `shape_${i}`,
                shapeType: "rectangle",
                startTime: 0,
                duration,
              });
              comp.addElement(shape);
            }
          }

          // 1. Validar
          const report = ProjectValidator.validate(comp);
          assert.strictEqual(report.isValid, true);

          // 2. Serializar
          const json = serializeComposition(comp);
          assert.ok(json.schemaVersion);

          // 3. Deserializar
          const restored = deserializeComposition(json);

          // 4. Evaluar (clamped within [0, duration])
          const clampedTime = Math.min(evalTime, duration);
          const snapOriginal = comp.evaluate(clampedTime);
          const snapRestored = restored.evaluate(clampedTime);

          assert.deepStrictEqual(snapOriginal, snapRestored);
        }
      ),
      { numRuns: 100 }
    );
  });
});
