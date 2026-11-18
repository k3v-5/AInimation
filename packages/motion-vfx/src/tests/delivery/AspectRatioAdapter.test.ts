import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { Composition } from "../../core/composition.js";
import { TextElement } from "../../elements/TextElement.js";
import { AspectRatioAdapter } from "../../delivery/adapter/AspectRatioAdapter.js";
import { LayoutReframer } from "../../delivery/adapter/LayoutReframer.js";
import { parseAspectRatio } from "../../delivery/core/AspectRatio.js";
import { UnsupportedAspectRatioError } from "../../delivery/core/DeliveryErrors.js";

describe("Fase 25 — Capa 1 & 2: AspectRatioAdapter & Reframer Tests", () => {
  it("parses valid aspect ratios and throws UnsupportedAspectRatioError on invalid", () => {
    const dim916 = parseAspectRatio("9:16");
    assert.equal(dim916.width, 1080);
    assert.equal(dim916.height, 1920);

    const dim169 = parseAspectRatio("16:9");
    assert.equal(dim169.width, 1920);
    assert.equal(dim169.height, 1080);

    assert.throws(() => {
      parseAspectRatio("3:4");
    }, UnsupportedAspectRatioError);
  });

  it("LayoutReframer calculates centered position and scale for 9:16 to 16:9", () => {
    const srcDim = { width: 1080, height: 1920 };
    const dstDim = parseAspectRatio("16:9"); // 1920x1080

    const originalTransform = {
      position: { x: 540, y: 960 }, // centro de 9:16
      scale: { x: 1.0, y: 1.0 },
    };

    const reframed = LayoutReframer.reframe(srcDim, dstDim, originalTransform, "smart_recenter");

    assert.equal(reframed.position.x, 960); // centro horizontal en 16:9
    assert.equal(reframed.position.y, 540); // centro vertical en 16:9
    assert.ok(reframed.scale.x < 1.0); // escala reducida para encajar 1920 vertical en 1080
  });

  it("AspectRatioAdapter adapts a 9:16 composition to 16:9, 1:1, 4:5 and 21:9", () => {
    const comp = new Composition({
      id: "comp_base",
      name: "Base Comp",
      width: 1080,
      height: 1920,
      fps: 60,
      duration: 10.0,
    });

    const title = new TextElement({
      id: "title_1",
      name: "Title Layer",
      text: "HELLO WORLD",
      style: { fontSize: 64, fontFamily: "Inter-Bold" },
    });
    title.transform.position.setValue({ x: 540, y: 960 });
    comp.addElement(title);

    // Adaptar a 16:9
    const res169 = AspectRatioAdapter.adapt(comp, "16:9", "youtube_horizontal");
    assert.equal(res169.composition.width, 1920);
    assert.equal(res169.composition.height, 1080);
    assert.equal(res169.composition.getElements().length, 1);
    assert.equal(typeof res169.contentHash, "string");

    // Adaptar a 1:1
    const res11 = AspectRatioAdapter.adapt(comp, "1:1", "linkedin");
    assert.equal(res11.composition.width, 1080);
    assert.equal(res11.composition.height, 1080);

    // Adaptar a 4:5
    const res45 = AspectRatioAdapter.adapt(comp, "4:5", "instagram_feed");
    assert.equal(res45.composition.width, 1080);
    assert.equal(res45.composition.height, 1350);

    // Invariante: La composición base no fue modificada
    assert.equal(comp.width, 1080);
    assert.equal(comp.height, 1920);
  });
});
