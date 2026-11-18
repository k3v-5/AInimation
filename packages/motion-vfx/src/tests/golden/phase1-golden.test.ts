import assert from "node:assert/strict";
import * as fs from "node:fs";
import * as path from "node:path";
import { describe, it } from "node:test";
import { fileURLToPath } from "node:url";
import { Composition } from "../../core/composition.js";
import { Layer } from "../../core/layer.js";
import { Vector2 } from "../../core/types.js";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

describe("Nivel 7 — Golden Tests: Canonical Motion Engine Snapshot", () => {
  it("evaluates composition state exactly identical to golden snapshot across all key timestamps", () => {
    // 1. Cargar snapshot dorado
    const snapshotPath = path.join(__dirname, "phase1-golden.snapshot.json");
    const goldenData = JSON.parse(fs.readFileSync(snapshotPath, "utf8"));

    // 2. Construir la animación canónica
    const comp = new Composition({
      id: "comp_golden",
      name: "Golden Composition",
      width: 1080,
      height: 1920,
      fps: 30,
      duration: 5.0,
    });

    const title = new Layer({
      id: "title",
      name: "Main Title",
      startTime: 0,
      endTime: 4,
    });

    title.property<number>("opacity").addKeyframe(0, 0, "easeOut");
    title.property<number>("opacity").addKeyframe(0.5, 1);

    title.property<Vector2>("scale").addKeyframe(0, { x: 0.5, y: 0.5 }, "easeOut");
    title.property<Vector2>("scale").addKeyframe(0.5, { x: 1.0, y: 1.0 });

    title.property<Vector2>("position").addKeyframe(0, { x: 540, y: 1200 }, "easeInOut");
    title.property<Vector2>("position").addKeyframe(1.0, { x: 540, y: 960 });

    title.property<number>("rotation").addKeyframe(0, 0, "linear");
    title.property<number>("rotation").addKeyframe(2.0, 360);

    comp.addLayer(title);

    // 3. Comparar cada timestamp contra el snapshot dorado
    const timestamps = [0, 0.25, 0.5, 0.75, 1, 2, 4.5];
    for (const t of timestamps) {
      const actual = comp.evaluate(t);
      const expected = goldenData[String(t)];

      assert.ok(expected, `Missing golden expectation for timestamp t=${t}`);
      assert.deepStrictEqual(actual, expected, `Golden test mismatch at timestamp t=${t}`);
    }
  });
});
