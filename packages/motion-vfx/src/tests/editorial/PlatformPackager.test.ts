import test from "node:test";
import assert from "node:assert/strict";
import {
  EditorialIRBuilder,
  PlatformPackager,
  PlatformStandard,
} from "../../editorial/index.js";

test("Fase 4D — Platform Packager Suite", async (t) => {
  const createIr = (width: number, height: number) => {
    const builder = new EditorialIRBuilder("proj_pack_test", {
      title: "City Pulse",
      profile: "VLOG",
      frameRate: 30,
      width,
      height,
      sampleRate: 44100,
      targetDialogueLufs: -16,
    });
    builder.createTrack({ id: "v1", name: "Video", type: "VIDEO_PRIMARY", index: 0 });
    builder.addClip("v1", {
      id: "c1",
      assetId: "media/city.mp4",
      sourceRange: { startSeconds: 0, durationSeconds: 10 },
      timelineRange: { startSeconds: 0, durationSeconds: 10 },
    });
    return builder.build();
  };

  await t.test("packages for YouTube Long with -16 LUFS and 16:9 standard safe zones", () => {
    const ir16x9 = createIr(1920, 1080);
    const manifest = PlatformPackager.packageForPlatform(ir16x9, "YOUTUBE_LONG");

    assert.equal(manifest.platform, "YOUTUBE_LONG");
    assert.equal(manifest.targetDialogueLufs, -16);
    assert.equal(manifest.aspectRatio, "16:9");
    assert.equal(manifest.readyForDelivery, true);
    assert.equal(manifest.safeZone.socialUIExclusion, false);
  });

  await t.test("packages for TikTok/Reels with -14 LUFS and strict social UI exclusion", () => {
    const ir9x16 = createIr(1080, 1920);
    const manifest = PlatformPackager.packageForPlatform(ir9x16, "TIKTOK_REELS_SHORT");

    assert.equal(manifest.platform, "TIKTOK_REELS_SHORT");
    assert.equal(manifest.targetDialogueLufs, -14);
    assert.equal(manifest.aspectRatio, "9:16");
    assert.equal(manifest.readyForDelivery, true);
    assert.equal(manifest.safeZone.socialUIExclusion, true);
    assert.equal(manifest.safeZone.bottomMarginPercent, 22);
    assert.equal(manifest.safeZone.rightMarginPercent, 18);
  });

  await t.test("packages for Broadcast EBU R128 with -23 LUFS and -1.0 dBTP ceiling", () => {
    const irBroadcast = createIr(1920, 1080);
    const manifest = PlatformPackager.packageForPlatform(irBroadcast, "BROADCAST_EBU_R128");

    assert.equal(manifest.platform, "BROADCAST_EBU_R128");
    assert.equal(manifest.targetDialogueLufs, -23);
    assert.equal(manifest.truePeakMaxDb, -1.0);
    assert.equal(manifest.readyForDelivery, true);
  });
});
