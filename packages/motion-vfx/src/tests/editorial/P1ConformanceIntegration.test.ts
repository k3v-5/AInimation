import { describe, it } from "node:test";
import assert from "node:assert/strict";
import crypto from "crypto";
import { EditorialIRBuilder } from "../../editorial/ir/editorial-ir-builder.js";
import { MultiCameraDirector, CameraAngleDefinition, SpeechTurn } from "../../editorial/multicam/index.js";
import { OtioExporter, OtioImporter } from "../../editorial/exporters/index.js";
import { EditorialQAOrchestrator } from "../../editorial/qa/editorial-qa-orchestrator.js";

describe("P1 Final Conformance Audit & Integration Suite (REQ-036, REQ-011, REQ-012)", () => {
  const angles: CameraAngleDefinition[] = [
    {
      angleId: "cam_wide",
      name: "Wide Establishing",
      role: "WIDE",
      spatialSide: "NEUTRAL_CENTER",
      scale: "WIDE",
      cameraAzimuthDeg: 0,
    },
    {
      angleId: "cam_host",
      name: "Host Close-Up",
      role: "SPEAKER_PRIMARY",
      assignedSpeakerId: "host",
      spatialSide: "LEFT_OF_AXIS",
      scale: "MEDIUM_CLOSE",
      cameraAzimuthDeg: 40,
    },
    {
      angleId: "cam_guest",
      name: "Guest Close-Up",
      role: "SPEAKER_SECONDARY",
      assignedSpeakerId: "guest",
      spatialSide: "RIGHT_OF_AXIS",
      scale: "CLOSE_UP",
      cameraAzimuthDeg: 320,
    },
  ];

  it("executes full end-to-end pipeline: IR -> MultiCam -> QA -> OTIO Export -> OTIO Import -> IR", () => {
    // 1. Build initial IR
    const builder = new EditorialIRBuilder("proj_p1_e2e", {
      title: "Confession Interview Master",
      profile: "DOCUMENTARY",
      frameRate: 24,
      width: 1920,
      height: 1080,
      sampleRate: 48000,
      targetDialogueLufs: -16,
    });

    builder.createTrack({ id: "v1", name: "Master Video", type: "VIDEO_PRIMARY", index: 0 });
    builder.createTrack({ id: "a1", name: "Dialogue Audio", type: "AUDIO_DIALOGUE", index: 1 });

    builder.addClip("v1", {
      id: "clip_v1",
      assetId: "media/interview_host.mp4",
      label: "Host intro",
      sourceRange: { startSeconds: 0, durationSeconds: 6.0 },
      timelineRange: { startSeconds: 0, durationSeconds: 6.0 },
    });

    builder.addClip("v1", {
      id: "clip_v2",
      assetId: "media/interview_guest.mp4",
      label: "Guest confession",
      sourceRange: { startSeconds: 0, durationSeconds: 10.0 },
      timelineRange: { startSeconds: 6.0, durationSeconds: 10.0 },
    });

    builder.addClip("a1", {
      id: "clip_a1",
      assetId: "media/audio_sync.wav",
      label: "Sync Dialogue",
      sourceRange: { startSeconds: 0, durationSeconds: 16.0 },
      timelineRange: { startSeconds: 0, durationSeconds: 16.0 },
    });

    const initialIR = builder.build();

    // 2. MultiCam Director Planning
    const speechTurns: SpeechTurn[] = [
      { speakerId: "host", startSeconds: 0.0, endSeconds: 6.0 },
      { speakerId: "guest", startSeconds: 6.0, endSeconds: 16.0, emotionalState: "CONFESSION" },
    ];

    const cameraDecisions = MultiCameraDirector.planSwitching({
      angles,
      speechTurns,
    });

    assert.ok(cameraDecisions.length >= 2);
    const guestDecision = cameraDecisions.find((d) => d.timestampSeconds === 6.0);
    assert.ok(guestDecision);
    assert.equal(guestDecision.isEmotionalProtection, true);
    assert.equal(guestDecision.emotionalState, "CONFESSION");

    // 3. QA Orchestration
    const qaReport = EditorialQAOrchestrator.audit({
      ir: initialIR,
    });

    assert.ok(qaReport.status !== "BLOCKED");
    assert.ok(qaReport.score.overall > 80.0);

    // 4. OTIO Export
    const otioJson = OtioExporter.exportToOtioJson(initialIR, true);
    assert.ok(otioJson.includes('"OTIO_SCHEMA": "Timeline.1"'));
    assert.ok(otioJson.includes("Confession Interview Master"));

    // 5. OTIO Import & Re-normalization
    const { ir: reconstructedIR, warnings } = OtioImporter.importFromOtioJson(otioJson);
    assert.equal(warnings.length, 0);
    assert.equal(reconstructedIR.tracks.length, initialIR.tracks.length);
    assert.equal(reconstructedIR.tracks[0].clips.length, initialIR.tracks[0].clips.length);
    assert.equal(reconstructedIR.tracks[1].clips.length, initialIR.tracks[1].clips.length);
  });

  it("strictly validates Universal Rule Precedence: Emotional Protection holds camera regardless of pacing", () => {
    // A rapid speech turn during a breakdown must NOT cut away even if pacing would request a cut
    const turns: SpeechTurn[] = [
      { speakerId: "guest", startSeconds: 0.0, endSeconds: 5.0, emotionalState: "BREAKDOWN" },
      { speakerId: "host", startSeconds: 2.0, endSeconds: 3.0 }, // Host tries to interject
    ];

    const decisions = MultiCameraDirector.planSwitching({
      angles,
      speechTurns: turns,
      options: { minShotDurationSeconds: 1.0 }, // aggressive pacing
    });

    // Camera must stay on guest
    const firstDecision = decisions[1];
    assert.equal(firstDecision.activeAngleId, "cam_guest");
    assert.equal(firstDecision.isEmotionalProtection, true);
    assert.equal(firstDecision.emotionalState, "BREAKDOWN");
  });

  it("verifies byte-level determinism across repeated compilation runs", () => {
    const builder = new EditorialIRBuilder("proj_det", {
      title: "Determinism Test",
      profile: "JOURNALISM",
      frameRate: 29.97,
      width: 1920,
      height: 1080,
      sampleRate: 48000,
      targetDialogueLufs: -16,
    });

    builder.createTrack({ id: "v1", name: "V1", type: "VIDEO_PRIMARY", index: 0 });
    builder.addClip("v1", {
      id: "c1",
      assetId: "media/test.mov",
      label: "Test",
      sourceRange: { startSeconds: 0, durationSeconds: 5 },
      timelineRange: { startSeconds: 0, durationSeconds: 5 },
    });

    const ir = builder.build();

    const otio1 = OtioExporter.exportToOtioJson(ir);
    const otio2 = OtioExporter.exportToOtioJson(ir);
    assert.equal(otio1, otio2);

    const hash1 = crypto.createHash("sha256").update(otio1, "utf8").digest("hex");
    const hash2 = crypto.createHash("sha256").update(otio2, "utf8").digest("hex");
    assert.equal(hash1, hash2);
  });

  it("handles OTIO edge cases cleanly: empty timeline, single clip, multiple tracks and gaps", () => {
    // Empty timeline
    const emptyIR = new EditorialIRBuilder("empty_proj", {
      title: "Empty",
      profile: "VLOG",
      frameRate: 30,
      width: 1080,
      height: 1920,
      sampleRate: 48000,
      targetDialogueLufs: -16,
    }).build();

    const emptyOtio = OtioExporter.exportToOtioJson(emptyIR);
    const { ir: impEmpty } = OtioImporter.importFromOtioJson(emptyOtio);
    assert.equal(impEmpty.tracks.length, 0);

    // Multi-track with gaps
    const gapBuilder = new EditorialIRBuilder("gap_proj", {
      title: "Gaps",
      profile: "DOCUMENTARY",
      frameRate: 50,
      width: 3840,
      height: 2160,
      sampleRate: 48000,
      targetDialogueLufs: -23,
    });
    gapBuilder.createTrack({ id: "v1", name: "V1", type: "VIDEO_PRIMARY", index: 0 });
    gapBuilder.addClip("v1", {
      id: "c1",
      assetId: "m1.mov",
      label: "C1",
      sourceRange: { startSeconds: 0, durationSeconds: 2 },
      timelineRange: { startSeconds: 5, durationSeconds: 2 }, // Gap of 5s
    });

    const gapIR = gapBuilder.build();
    const gapOtio = OtioExporter.exportToOtioJson(gapIR);
    const { ir: impGap } = OtioImporter.importFromOtioJson(gapOtio);
    assert.equal(impGap.tracks[0].clips[0].timelineRange.startSeconds, 5.0);
    assert.equal(impGap.tracks[0].clips[0].timelineRange.durationSeconds, 2.0);
  });
});
