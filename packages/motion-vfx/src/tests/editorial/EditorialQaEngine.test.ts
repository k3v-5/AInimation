import test from "node:test";
import assert from "node:assert/strict";
import {
  EditorialIRBuilder,
  EditorialQAEngine,
} from "../../editorial/index.js";

test("Fase 4C — Editorial QA Engine 2.0 Suite", async (t) => {
  const baseMetadata = {
    title: "QA Test Sequence",
    profile: "VLOG",
    frameRate: 30,
    width: 1080,
    height: 1920,
    sampleRate: 44100,
    targetDialogueLufs: -14,
  };

  await t.test("approves clean IR with 100 QA score and isReadyForExport = true", () => {
    const builder = new EditorialIRBuilder("proj_clean", baseMetadata);
    builder.createTrack({ id: "v1", name: "Primary", type: "VIDEO_PRIMARY", index: 0 });
    builder.addClip("v1", {
      id: "clip_1",
      assetId: "media/good_clip.mp4",
      sourceRange: { startSeconds: 0, durationSeconds: 5 },
      timelineRange: { startSeconds: 0, durationSeconds: 5 },
    });

    const ir = builder.build();
    const report = EditorialQAEngine.auditIR(ir);

    assert.equal(report.isReadyForExport, true);
    assert.equal(report.qaScore, 100);
    assert.equal(report.issues.length, 0);
  });

  await t.test("detects unintended black frame gaps on primary video track (BLOCKING)", () => {
    const builder = new EditorialIRBuilder("proj_gap", baseMetadata);
    builder.createTrack({ id: "v1", name: "Primary", type: "VIDEO_PRIMARY", index: 0 });

    // Clip 1 ends at 3.0s, Clip 2 starts at 3.5s -> 0.5s gap!
    builder.addClip("v1", {
      id: "clip_1",
      assetId: "media/clip1.mp4",
      sourceRange: { startSeconds: 0, durationSeconds: 3 },
      timelineRange: { startSeconds: 0, durationSeconds: 3 },
    });
    builder.addClip("v1", {
      id: "clip_2",
      assetId: "media/clip2.mp4",
      sourceRange: { startSeconds: 0, durationSeconds: 3 },
      timelineRange: { startSeconds: 3.5, durationSeconds: 3 },
    });

    const ir = builder.build();
    const report = EditorialQAEngine.auditIR(ir);

    assert.equal(report.isReadyForExport, false);
    const gapIssue = report.issues.find((i) => i.checkType === "TRACK_GAP");
    assert.ok(gapIssue);
    assert.equal(gapIssue.severity, "BLOCKING");
  });

  await t.test("detects flash frames (< 0.1s) and audio volume clipping (> 0 dB)", () => {
    const builder = new EditorialIRBuilder("proj_flash", baseMetadata);
    builder
      .createTrack({ id: "v1", name: "Primary", type: "VIDEO_PRIMARY", index: 0 })
      .createTrack({ id: "a1", name: "Audio", type: "AUDIO_DIALOGUE", index: 1 });

    // Flash frame: 0.05s
    builder.addClip("v1", {
      id: "clip_flash",
      assetId: "media/flash.mp4",
      sourceRange: { startSeconds: 0, durationSeconds: 0.05 },
      timelineRange: { startSeconds: 0, durationSeconds: 0.05 },
    });

    // Audio clipping: +3.0 dB
    builder.addClip("a1", {
      id: "clip_loud",
      assetId: "audio/loud.wav",
      volumeDb: 3.0,
      sourceRange: { startSeconds: 0, durationSeconds: 5 },
      timelineRange: { startSeconds: 0, durationSeconds: 5 },
    });

    const ir = builder.build();
    const report = EditorialQAEngine.auditIR(ir);

    const flashIssue = report.issues.find((i) => i.checkType === "FLASH_FRAME");
    assert.ok(flashIssue);
    assert.equal(flashIssue.severity, "WARNING");

    const clipIssue = report.issues.find((i) => i.checkType === "AUDIO_CLIPPING");
    assert.ok(clipIssue);
    assert.equal(clipIssue.severity, "WARNING");
  });
});
