import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { describe, it } from "node:test";
import { Composition } from "../../core/composition.js";
import { GroupElement, TextElement } from "../../elements/index.js";
import { deserializeComposition } from "../../serialization/deserializer.js";
import { serializeComposition } from "../../serialization/serializer.js";

const FIXTURES_DIR = path.resolve(process.cwd(), "src/tests/fixtures");

describe("Fase 2C — Core Integration & Stability Check Tests", () => {
  it("loads and evaluates all Golden Fixtures flawlessly", () => {
    const fixtureFiles = [
      "empty-project.json",
      "simple-text.json",
      "animated-text.json",
      "nested-groups.json",
      "video-project.json",
      "full-project.json",
    ];

    for (const filename of fixtureFiles) {
      const filePath = path.join(FIXTURES_DIR, filename);
      const rawJson = JSON.parse(fs.readFileSync(filePath, "utf-8"));

      const comp = deserializeComposition(rawJson);
      assert.ok(comp.id, `Fixture ${filename} failed to deserialize valid ID`);

      // Evaluar en múltiples timestamps (0s, mitad de duración, final)
      const eval0 = comp.evaluate(0);
      const evalMid = comp.evaluate(comp.duration / 2);
      const evalEnd = comp.evaluate(comp.duration - 0.01);

      assert.strictEqual(eval0.time, 0);
      assert.strictEqual(evalMid.time, comp.duration / 2);
      assert.strictEqual(evalEnd.time, comp.duration - 0.01);
    }
  });

  it("STRICT DETERMINISM: evaluate(t) produces deep identical snapshot every run", () => {
    const filePath = path.join(FIXTURES_DIR, "full-project.json");
    const comp = deserializeComposition(JSON.parse(fs.readFileSync(filePath, "utf-8")));

    const testTime = 3.14159;
    const snap1 = comp.evaluate(testTime);
    const snap2 = comp.evaluate(testTime);

    assert.deepStrictEqual(snap1, snap2, "Evaluation snapshot must be 100% deterministic and pure");
  });

  it("ROUND-TRIP STABILITY: A -> serialize -> B -> serialize -> C guarantees B == C", () => {
    const filePath = path.join(FIXTURES_DIR, "full-project.json");
    const originalJson = JSON.parse(fs.readFileSync(filePath, "utf-8"));

    const compA = deserializeComposition(originalJson);
    const jsonB = serializeComposition(compA);
    const compB = deserializeComposition(jsonB);
    const jsonC = serializeComposition(compB);

    assert.deepStrictEqual(jsonB, jsonC, "Round-trip serialization must be semantically lossless");
  });

  it("DEEP CLONE ZERO-ALIASING: modifying cloned transform does not mutate original", () => {
    const originalText = new TextElement({ id: "original_t", text: "Original" });
    originalText.transform.position.setValue({ x: 100, y: 100 });

    const clone = originalText.clone();
    assert.notStrictEqual(clone.id, originalText.id);

    // Mutar el clon
    clone.transform.position.setValue({ x: 999, y: 999 });

    // El original debe permanecer inalterado en (100, 100)
    assert.deepStrictEqual(originalText.transform.position.getValue(), { x: 100, y: 100 });
    assert.deepStrictEqual(clone.transform.position.getValue(), { x: 999, y: 999 });
  });

  it("compounds keyframed animation inside animated parent group", () => {
    const comp = new Composition({ width: 1080, height: 1920, fps: 30, duration: 5 });

    const group = new GroupElement({ id: "motion_group" });
    group.transform.position.addKeyframe(0, { x: 0, y: 0 }, "linear");
    group.transform.position.addKeyframe(1, { x: 100, y: 0 });

    const text = new TextElement({ id: "motion_text" });
    text.transform.position.addKeyframe(0, { x: 0, y: 0 }, "linear");
    text.transform.position.addKeyframe(1, { x: 100, y: 0 });

    group.addChild(text);
    comp.addElement(group);

    // En t = 0.5s:
    // group local pos = (50, 0)
    // text local pos = (50, 0)
    // text world pos = 50 + 50 = (100, 0)
    const snapshot = comp.evaluate(0.5);
    const groupEval = snapshot.elements?.find((e) => e.id === "motion_group") as any;
    const textEval = groupEval?.children?.[0];

    assert.strictEqual(textEval?.transform?.matrix?.tx, 100);
    assert.strictEqual(textEval?.transform?.matrix?.ty, 0);
  });
});
