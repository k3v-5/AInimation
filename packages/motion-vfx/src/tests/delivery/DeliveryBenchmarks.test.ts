import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { Composition } from "../../core/composition.js";
import { TextElement } from "../../elements/TextElement.js";
import { SocialDeliveryPackager } from "../../delivery/packaging/SocialDeliveryPackager.js";

describe("Fase 25 — Capa 7: Delivery Performance & Benchmarks Suite", () => {
  it("benchmarks packaging 50 full multi-aspect social delivery packages in < 250ms", () => {
    const comp = new Composition({
      id: "comp_bench",
      width: 1080,
      height: 1920,
      fps: 30,
      duration: 10.0,
    });

    for (let i = 0; i < 5; i++) {
      const el = new TextElement({
        id: `t_bench_${i}`,
        name: `Layer ${i}`,
        text: `Title ${i}`,
        style: { fontSize: 60, fontFamily: "Inter-Bold" },
      });
      el.transform.position.setValue({ x: 540, y: 300 + i * 150 });
      comp.addElement(el);
    }

    const t0 = performance.now();
    const count = 50;

    for (let i = 0; i < count; i++) {
      const result = SocialDeliveryPackager.package(
        comp,
        `proj_bench_${i}`,
        `rev_bench_${i}`,
        {
          targetAspectRatios: ["9:16", "16:9", "1:1", "4:5"],
          thumbnailCount: 3,
        }
      );
      assert.equal(result.pkg.projectId, `proj_bench_${i}`);
    }

    const elapsed = performance.now() - t0;
    assert.ok(elapsed < 250, `Packaging ${count} social deliveries took ${elapsed.toFixed(2)}ms (budget < 250ms)`);
  });
});
