import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { Composition } from "../../core/composition.js";
import { ShapeElement } from "../../elements/ShapeElement.js";
import { TextElement } from "../../elements/TextElement.js";
import { VideoElement } from "../../elements/VideoElement.js";

describe("Fase 2B — Stacking Order Reordering Tests", () => {
  it("reorders elements with moveBefore, moveAfter, bringToFront and sendToBack", () => {
    const comp = new Composition({ width: 1080, height: 1920, fps: 30, duration: 10 });

    const bg = new ShapeElement({ id: "bg", shapeType: "rectangle" });
    const video = new VideoElement({ id: "video", assetId: "v1" });
    const text = new TextElement({ id: "text", text: "Title" });

    comp.addElement(bg);
    comp.addElement(video);
    comp.addElement(text);

    // Initial order: [bg, video, text]
    assert.deepStrictEqual(comp.getElements().map((e) => e.id), ["bg", "video", "text"]);

    // moveBefore(text, video) -> [bg, text, video]
    comp.moveBefore("text", "video");
    assert.deepStrictEqual(comp.getElements().map((e) => e.id), ["bg", "text", "video"]);

    // moveAfter(bg, text) -> [text, bg, video]
    comp.moveAfter("bg", "text");
    assert.deepStrictEqual(comp.getElements().map((e) => e.id), ["text", "bg", "video"]);

    // bringToFront(text) -> [bg, video, text]
    comp.bringToFront("text");
    assert.deepStrictEqual(comp.getElements().map((e) => e.id), ["bg", "video", "text"]);

    // sendToBack(text) -> [text, bg, video]
    comp.sendToBack("text");
    assert.deepStrictEqual(comp.getElements().map((e) => e.id), ["text", "bg", "video"]);
  });
});
