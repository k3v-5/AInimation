import test from "node:test";
import assert from "node:assert/strict";
import {
  MultiCameraDirector,
  CameraAngleDefinition,
  SpeechTurn,
} from "../../editorial/index.js";

test("Fase 4B — Multi-Camera Director Suite", async (t) => {
  const angles: CameraAngleDefinition[] = [
    {
      angleId: "cam_wide",
      name: "Studio Wide Establishing",
      role: "WIDE",
      scale: "WIDE",
      cameraAzimuthDeg: 0,
    },
    {
      angleId: "cam_host",
      name: "Host Close-Up",
      role: "SPEAKER_PRIMARY",
      assignedSpeakerId: "host_01",
      scale: "MEDIUM_CLOSE",
      cameraAzimuthDeg: 30,
    },
    {
      angleId: "cam_guest",
      name: "Guest Close-Up",
      role: "SPEAKER_SECONDARY",
      assignedSpeakerId: "guest_01",
      scale: "MEDIUM_CLOSE",
      cameraAzimuthDeg: 330,
    },
  ];

  await t.test("switches angle dynamically according to active speaker tracking", () => {
    const turns: SpeechTurn[] = [
      { speakerId: "host_01", startSeconds: 4.0, endSeconds: 10.0 },
      { speakerId: "guest_01", startSeconds: 12.0, endSeconds: 20.0 },
    ];

    const decisions = MultiCameraDirector.planSwitching({ angles, speechTurns: turns });

    // Expect initial wide + host cut + guest cut
    assert.ok(decisions.length >= 3);
    assert.equal(decisions[0].activeAngleId, "cam_wide");
    assert.equal(decisions[1].activeAngleId, "cam_host");
    assert.equal(decisions[2].activeAngleId, "cam_guest");
  });

  await t.test("strictly protects emotional peaks from cutting away during testimony", () => {
    const turns: SpeechTurn[] = [
      { speakerId: "guest_01", startSeconds: 3.0, endSeconds: 8.0 },
      { speakerId: "guest_01", startSeconds: 8.5, endSeconds: 16.0, isEmotionalPeak: true },
    ];

    const decisions = MultiCameraDirector.planSwitching({ angles, speechTurns: turns });
    const emoDecision = decisions.find((d) => d.isEmotionalProtection);
    assert.ok(emoDecision);
    assert.equal(emoDecision.activeAngleId, "cam_guest");
    assert.match(emoDecision.reason, /emotional testimony peak/);
  });

  await t.test("suppresses rapid ping-pong cuts smaller than minShotDurationSeconds", () => {
    const rapidTurns: SpeechTurn[] = [
      { speakerId: "host_01", startSeconds: 4.0, endSeconds: 5.0 },
      { speakerId: "guest_01", startSeconds: 5.2, endSeconds: 6.0 }, // Only 1.2s later -> Suppressed
      { speakerId: "host_01", startSeconds: 6.1, endSeconds: 7.0 }, // Only 0.9s later -> Suppressed
    ];

    const decisions = MultiCameraDirector.planSwitching({
      angles,
      speechTurns: rapidTurns,
      options: { minShotDurationSeconds: 2.5 },
    });

    // Should only have initial wide + the first host cut
    assert.equal(decisions.length, 2);
    assert.equal(decisions[1].activeAngleId, "cam_host");
  });

  await t.test("inserts periodic spatial wide reset after configured interval", () => {
    const longTurns: SpeechTurn[] = [
      { speakerId: "host_01", startSeconds: 3.0, endSeconds: 15.0 },
      { speakerId: "guest_01", startSeconds: 16.0, endSeconds: 40.0 },
      { speakerId: "guest_01", startSeconds: 55.0, endSeconds: 70.0 }, // > 45s since initial wide
    ];

    const decisions = MultiCameraDirector.planSwitching({
      angles,
      speechTurns: longTurns,
      options: { wideResetIntervalSeconds: 45.0 },
    });

    const wideReset = decisions.find((d) => d.reason.includes("Periodic spatial reset"));
    assert.ok(wideReset);
    assert.equal(wideReset.activeAngleId, "cam_wide");
  });
});
