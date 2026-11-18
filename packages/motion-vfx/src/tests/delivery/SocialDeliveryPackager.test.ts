import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { Composition } from "../../core/composition.js";
import { TextElement } from "../../elements/TextElement.js";
import { SocialDeliveryPackager } from "../../delivery/packaging/SocialDeliveryPackager.js";

describe("Fase 25 — Capa 6: Social Delivery Packager & Manifest Tests", () => {
  it("packages a base composition into 9:16, 16:9, 1:1 variants and generates platform manifest", () => {
    const comp = new Composition({
      id: "comp_pack_test",
      width: 1080,
      height: 1920,
      fps: 30,
      duration: 10.0,
    });

    const title = new TextElement({
      id: "t_pack",
      name: "Title",
      text: "COMPLETE DELIVERY",
      style: { fontSize: 72, fontFamily: "Inter-Bold" },
    });
    title.transform.position.setValue({ x: 540, y: 960 });
    comp.addElement(title);

    const { pkg, manifest } = SocialDeliveryPackager.package(
      comp,
      "proj_social_01",
      "rev_social_01",
      {
        targetAspectRatios: ["9:16", "16:9", "1:1"],
        thumbnailCount: 3,
      }
    );

    assert.equal(pkg.projectId, "proj_social_01");
    assert.equal(Object.keys(pkg.variants).length, 3);
    assert.ok(pkg.variants["9:16"]);
    assert.ok(pkg.variants["16:9"]);
    assert.ok(pkg.variants["1:1"]);

    assert.equal(pkg.thumbnails.length, 3);
    assert.equal(typeof pkg.manifestHash, "string");
    assert.equal(manifest.manifestVersion, "2.5.0");
    assert.equal(typeof manifest.manifestHash, "string");
  });
});
