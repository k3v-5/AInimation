import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { Composition } from "../../core/composition.js";
import { TextElement } from "../../elements/TextElement.js";
import { ThumbnailSelector } from "../../delivery/thumbnails/ThumbnailSelector.js";
import { ThumbnailScorer } from "../../delivery/thumbnails/ThumbnailScorer.js";

describe("Fase 25 — Capa 5: Thumbnail Selector & Scorer Tests", () => {
  it("scores frames based on presence of text and visual elements", () => {
    const comp = new Composition({
      id: "comp_thumb",
      width: 1080,
      height: 1920,
      fps: 30,
      duration: 5.0,
    });

    const title = new TextElement({
      id: "t_main",
      name: "Main Title",
      text: "CRAZY TRICK",
      style: { fontSize: 80, fontFamily: "Inter-Bold" },
    });
    title.transform.position.setValue({ x: 540, y: 960 });
    comp.addElement(title);

    const score = ThumbnailScorer.scoreFrame(comp, 1.0);
    assert.ok(score >= 0.5);
  });

  it("ThumbnailSelector extracts top 3 candidates ordered deterministically by score", () => {
    const comp = new Composition({
      id: "comp_thumb_extract",
      width: 1080,
      height: 1920,
      fps: 30,
      duration: 10.0,
    });

    const title = new TextElement({
      id: "t_main",
      name: "Main Title",
      text: "TOP 5 SECRETS",
      style: { fontSize: 80, fontFamily: "Inter-Bold" },
    });
    title.transform.position.setValue({ x: 540, y: 960 });
    comp.addElement(title);

    const thumbs = ThumbnailSelector.selectThumbnails(comp, "9:16", 3);
    assert.equal(thumbs.length, 3);

    // Invariante: orden descendente por score
    assert.ok(thumbs[0].score >= thumbs[1].score);
    assert.ok(thumbs[1].score >= thumbs[2].score);

    for (const t of thumbs) {
      assert.equal(typeof t.artifactHash, "string");
      assert.equal(t.aspectRatio, "9:16");
    }
  });
});
