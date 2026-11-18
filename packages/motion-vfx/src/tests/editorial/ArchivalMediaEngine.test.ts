import { describe, it } from "node:test";
import assert from "node:assert/strict";
import fc from "fast-check";
import { ArchivalMediaEngine } from "../../editorial/archive/archival-media-engine.js";
import { ArchivalAsset } from "../../editorial/contracts/archive.types.js";

describe("Fase 4C — Archival Media Engine Suite", () => {
  const sampleAssets: ArchivalAsset[] = [
    {
      id: "archive_photo_1974",
      sourcePath: "/media/archive/protest_1974.png",
      title: "Student March in Downtown",
      year: 1974,
      sourceArchive: "National Historical Archives",
      creator: "Jane Doe",
      licenseStatus: "PUBLIC_DOMAIN",
      isStillPhoto: true,
      aspectRatio: "4:3",
    },
    {
      id: "archive_broadcast_1989",
      sourcePath: "/media/archive/news_1989.mp4",
      title: "Evening Broadcast on Treaty",
      dateExact: "November 9, 1989",
      sourceArchive: "BBC Archive",
      licenseStatus: "EDITORIAL_USE_ONLY",
      isStillPhoto: false,
      aspectRatio: "4:3",
    },
    {
      id: "archive_expired_license",
      sourcePath: "/media/archive/restricted_doc.png",
      title: "Classified Memorandum",
      year: 1962,
      sourceArchive: "Private Collection",
      licenseStatus: "EXPIRED",
      licenseExpiryDate: "2023-12-31",
      isStillPhoto: true,
      aspectRatio: "1:1",
    },
  ];

  it("calculates smooth Ken Burns parameters for historical still photos", () => {
    const kb = ArchivalMediaEngine.calculateKenBurns({
      isStillPhoto: true,
      durationSeconds: 6.0,
      motionDirection: "ZOOM_IN",
    });

    assert.equal(kb.scaleStart, 1.0);
    assert.equal(kb.scaleEnd, 1.15);
    assert.equal(kb.panStartX, 0.5);
    assert.equal(kb.panStartY, 0.5);
    assert.equal(kb.easing, "EASE_IN_OUT");
  });

  it("formats standard archival date stamps for historical footage and still imagery", () => {
    const stamp1 = ArchivalMediaEngine.formatDateStamp(sampleAssets[0]);
    assert.equal(stamp1, "FILE FOOTAGE // 1974");

    const stamp2 = ArchivalMediaEngine.formatDateStamp(sampleAssets[1]);
    assert.equal(stamp2, "FILE FOOTAGE // NOVEMBER 9, 1989");
  });

  it("audits license status and flags expired archival licenses as compliance blockers (REQ-087)", () => {
    const placements = [
      { clipId: "clip_01", assetId: "archive_photo_1974", startSeconds: 0.0, endSeconds: 5.0 },
      { clipId: "clip_02", assetId: "archive_expired_license", startSeconds: 5.0, endSeconds: 10.0 },
    ];

    const plan = ArchivalMediaEngine.buildArchivalPlan({
      projectId: "doc_archive_license_test",
      assets: sampleAssets,
      clipPlacements: placements,
    });

    assert.equal(plan.treatments.length, 2);
    assert.equal(plan.licenseCompliant, false);
    assert.ok(plan.issues.length > 0);
    assert.ok(plan.issues[0].includes("EXPIRED"));
  });

  it("guarantees 100% deterministic SHA-256 archival plan checksum", () => {
    const placements = [
      { clipId: "clip_01", assetId: "archive_photo_1974", startSeconds: 0.0, endSeconds: 5.0 },
    ];

    const plan1 = ArchivalMediaEngine.buildArchivalPlan({
      projectId: "det_archive_01",
      assets: sampleAssets,
      clipPlacements: placements,
    });
    const plan2 = ArchivalMediaEngine.buildArchivalPlan({
      projectId: "det_archive_01",
      assets: sampleAssets,
      clipPlacements: placements,
    });

    assert.equal(plan1.checksumSha256.length, 64);
    assert.equal(plan1.checksumSha256, plan2.checksumSha256);
  });

  it("PBT: Ken Burns parameters are always bounded within valid scale [0.5, 3.0] and pan [0.0, 1.0]", () => {
    fc.assert(
      fc.property(
        fc.constantFrom("ZOOM_IN", "ZOOM_OUT", "PAN_LEFT", "PAN_RIGHT", "STATIC"),
        fc.float({ min: 1.0, max: 60.0, noNaN: true }),
        fc.boolean(),
        (direction, duration, isStill) => {
          const kb = ArchivalMediaEngine.calculateKenBurns({
            motionDirection: direction,
            durationSeconds: duration,
            isStillPhoto: isStill,
          });

          return (
            kb.scaleStart >= 0.5 &&
            kb.scaleStart <= 3.0 &&
            kb.scaleEnd >= 0.5 &&
            kb.scaleEnd <= 3.0 &&
            kb.panStartX >= 0.0 &&
            kb.panStartX <= 1.0 &&
            kb.panStartY >= 0.0 &&
            kb.panStartY <= 1.0 &&
            kb.panEndX >= 0.0 &&
            kb.panEndX <= 1.0 &&
            kb.panEndY >= 0.0 &&
            kb.panEndY <= 1.0
          );
        }
      ),
      { numRuns: 100 }
    );
  });
});
