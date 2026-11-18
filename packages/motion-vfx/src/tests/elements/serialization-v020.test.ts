import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { Composition } from "../../core/composition.js";
import {
  AudioElement,
  GroupElement,
  ImageElement,
  ShapeElement,
  TextElement,
  VideoElement,
} from "../../elements/index.js";
import { SerializationError } from "../../errors/index.js";
import { deserializeComposition } from "../../serialization/deserializer.js";
import { serializeComposition } from "../../serialization/serializer.js";

describe("Fase 2C — Serialization & Round-Trip Tests (Schema v0.2.0)", () => {
  it("serializes and deserializes a multi-element composition (v0.2.0) with exact evaluation equality", () => {
    const comp = new Composition({
      id: "full_scene_comp",
      name: "Complete AV Composition",
      width: 1080,
      height: 1920,
      fps: 30,
      duration: 10,
    });

    // 1. Registrar Assets
    comp.assets.add({
      id: "logo_asset",
      type: "image",
      source: { path: "assets/logo.png" },
      metadata: { width: 512, height: 512 },
    });
    comp.assets.add({
      id: "video_asset",
      type: "video",
      source: { path: "assets/bg.mp4" },
      metadata: { duration: 15, width: 1920, height: 1080, fps: 30 },
    });
    comp.assets.add({
      id: "music_asset",
      type: "audio",
      source: { path: "assets/audio.mp3" },
      metadata: { duration: 120, sampleRate: 48000 },
    });

    // 2. Elementos
    const shape = new ShapeElement({
      id: "bg_shape",
      name: "Background Box",
      shapeType: "rectangle",
      shapeData: { width: 1080, height: 1920 },
      style: { fill: { r: 0.05, g: 0.05, b: 0.1, a: 1 } },
      startTime: 0,
      duration: 10,
    });

    const video = new VideoElement({
      id: "bg_video",
      name: "Background Video",
      assetId: "video_asset",
      startTime: 0,
      duration: 10,
    });

    const group = new GroupElement({
      id: "header_group",
      name: "Header UI",
      startTime: 0,
      duration: 8,
    });
    group.transform.position.setValue({ x: 540, y: 300 });

    const image = new ImageElement({
      id: "brand_logo",
      assetId: "logo_asset",
    });
    image.transform.position.setValue({ x: -200, y: 0 });
    image.transform.scale.setValue({ x: 0.5, y: 0.5 });

    const title = new TextElement({
      id: "brand_title",
      text: "Motion Graphics Engine",
      style: {
        fontFamily: "Inter",
        fontSize: 64,
        fontWeight: 800,
        color: { r: 1, g: 1, b: 1, a: 1 },
      },
    });
    title.transform.position.setValue({ x: 100, y: 0 });
    title.transform.opacity.addKeyframe(0, 0, "easeOut");
    title.transform.opacity.addKeyframe(1, 1);

    group.addChild(image);
    group.addChild(title);

    const audio = new AudioElement({
      id: "bg_music",
      name: "Soundtrack",
      assetId: "music_asset",
      startTime: 0,
      duration: 10,
    });

    comp.addElement(shape);
    comp.addElement(video);
    comp.addElement(group);
    comp.addElement(audio);

    // 3. Serializar a JSON v0.2.0
    const serialized = serializeComposition(comp);
    assert.strictEqual(serialized.schemaVersion, "0.2.0");
    assert.strictEqual(serialized.assets?.length, 3);
    assert.strictEqual(serialized.elements?.length, 4);

    // 4. Deserializar en una nueva composición
    const restored = deserializeComposition(serialized);
    assert.strictEqual(restored.id, comp.id);
    assert.strictEqual(restored.assets.list().length, 3);
    assert.strictEqual(restored.getElements().length, 4);

    // 5. Comprobar igualdad determinista en múltiples timestamps
    const timestamps = [0, 0.5, 1.0, 2.5, 5.0, 7.5, 9.0];
    for (const t of timestamps) {
      const origEval = comp.evaluate(t);
      const restEval = restored.evaluate(t);
      assert.deepStrictEqual(restEval, origEval, `Mismatch between original and restored composition at time t=${t}`);
    }
  });

  it("deserializes Schema v0.1.0 projects seamlessly (backward compatibility)", () => {
    const v010Json = {
      schemaVersion: "0.1.0",
      composition: {
        id: "comp_legacy",
        name: "Legacy Composition",
        width: 1920,
        height: 1080,
        fps: 30,
        duration: 5,
        layers: [
          {
            id: "legacy_layer",
            name: "Layer 1",
            startTime: 0,
            endTime: 5,
            properties: {
              opacity: {
                type: "number",
                baseValue: 1,
                keyframes: [],
              },
            },
          },
        ],
      },
    };

    const restored = deserializeComposition(v010Json);
    assert.strictEqual(restored.id, "comp_legacy");
    assert.strictEqual(restored.getLayers().length, 1);
    assert.strictEqual(restored.getLayer("legacy_layer")?.name, "Layer 1");
  });

  it("rejects unknown or incompatible schema versions", () => {
    const badJson = {
      schemaVersion: "999.0.0",
      composition: { width: 1920, height: 1080, fps: 30, duration: 5 },
    };
    assert.throws(() => {
      deserializeComposition(badJson);
    }, SerializationError);
  });
});
