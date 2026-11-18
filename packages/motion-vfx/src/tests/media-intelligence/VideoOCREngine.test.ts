import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { VideoOCREngine, OCRBoundingBox, DetectedTextRegion } from "../../media-intelligence/ocr/VideoOCREngine.js";

describe("Media Intelligence — VideoOCREngine Tests", () => {
  it("calculates exact IoU between bounding boxes", () => {
    const boxA: OCRBoundingBox = { x: 100, y: 100, width: 200, height: 100 }; // area = 20000
    const boxB: OCRBoundingBox = { x: 200, y: 100, width: 200, height: 100 }; // overlap = 100x100 = 10000, union = 30000 -> IoU = 0.3333

    const iou = VideoOCREngine.calculateIoU(boxA, boxB);
    assert.ok(Math.abs(iou - 0.3333) < 0.01);

    // Non-overlapping boxes
    const boxC: OCRBoundingBox = { x: 500, y: 500, width: 100, height: 100 };
    assert.equal(VideoOCREngine.calculateIoU(boxA, boxC), 0.0);
  });

  it("detects text collisions and suggests safe non-colliding screen placement", () => {
    // Detected burned-in subtitle at the bottom
    const detectedRegions: DetectedTextRegion[] = [
      {
        id: "ocr_1",
        text: "ORIGINAL SUBTITLE",
        confidence: 0.98,
        boundingBox: { x: 240, y: 1400, width: 600, height: 150 },
        timestamp: 1.0,
      },
    ];

    const textDim = { width: 500, height: 120 };

    // Should suggest center or top because bottom has collision
    const suggestion = VideoOCREngine.suggestSafePlacement(detectedRegions, 1080, 1920, textDim);

    assert.equal(suggestion.hasCollisionRisk, false);
    assert.equal(suggestion.zone, "center");
    assert.equal(suggestion.position[0], 540);
    assert.equal(suggestion.position[1], 960);
  });
});
