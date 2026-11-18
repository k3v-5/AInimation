import assert from "node:assert/strict";
import { describe, it } from "node:test";
import fc from "fast-check";
import { SafeZoneLayoutEngine } from "../../../vlog/overlays/safe-zone-layout-engine.js";

describe("Milestone 6-D — Safe Zone Layout & Social Collision Suite", () => {
  it("delivers exact canonical dimensions for all 5 aspect ratios", () => {
    assert.deepEqual(SafeZoneLayoutEngine.getDimensionsForAspectRatio("16:9"), { width: 1920, height: 1080 });
    assert.deepEqual(SafeZoneLayoutEngine.getDimensionsForAspectRatio("9:16"), { width: 1080, height: 1920 });
    assert.deepEqual(SafeZoneLayoutEngine.getDimensionsForAspectRatio("1:1"), { width: 1080, height: 1080 });
    assert.deepEqual(SafeZoneLayoutEngine.getDimensionsForAspectRatio("4:5"), { width: 1080, height: 1350 });
    assert.deepEqual(SafeZoneLayoutEngine.getDimensionsForAspectRatio("21:9"), { width: 2560, height: 1080 });
  });

  it("detects spatial overlap between bounding boxes", () => {
    const box1 = { x: 100, y: 100, width: 200, height: 100 };
    const box2 = { x: 250, y: 150, width: 200, height: 100 }; // Solapa
    const box3 = { x: 500, y: 500, width: 200, height: 100 }; // Lejos

    assert.equal(SafeZoneLayoutEngine.doBoxesOverlap(box1, box2), true);
    assert.equal(SafeZoneLayoutEngine.doBoxesOverlap(box1, box3), false);
  });

  it("avoids forbidden social UI regions in 9:16 (TikTok/Reels)", () => {
    const forbidden = SafeZoneLayoutEngine.getForbiddenRegions("9:16");
    assert.ok(forbidden.length >= 2);

    // Caja en la barra inferior (y = 1750 en canvas 1920) debe marcarse como prohibida
    const bottomBox = { x: 100, y: 1750, width: 300, height: 100 };
    assert.equal(SafeZoneLayoutEngine.intersectsForbiddenRegions(bottomBox, forbidden), true);
  });

  it("automatically resolves safe placement shifting to alternative slot upon conflict", () => {
    // Si TOP_LEFT ya tiene un obstáculo existente
    const existingObstacle = SafeZoneLayoutEngine.calculateSlotBoundingBox("TOP_LEFT", 300, 150, "16:9");

    const placement = SafeZoneLayoutEngine.resolveSafePlacement(
      "TOP_LEFT",
      300,
      150,
      [existingObstacle],
      "16:9"
    );

    assert.equal(placement.isSafe, true);
    // Debe haber seleccionado un slot alternativo (ej. TOP_RIGHT)
    assert.notEqual(placement.slot, "TOP_LEFT");
  });

  it("PBT: placement within safe boundaries never outputs negative coordinates", () => {
    fc.assert(
      fc.property(
        fc.integer({ min: 100, max: 400 }),
        fc.integer({ min: 50, max: 200 }),
        (w, h) => {
          const box = SafeZoneLayoutEngine.calculateSlotBoundingBox("TOP_LEFT", w, h, "16:9");
          assert.ok(box.x >= 0);
          assert.ok(box.y >= 0);
          assert.ok(box.width > 0);
          assert.ok(box.height > 0);
        }
      )
    );
  });
});
