import assert from "node:assert/strict";
import { describe, it } from "node:test";
import fc from "fast-check";
import {
  IngestedMediaFile,
  VlogFootageClassifier,
} from "../../../vlog/index.js";

describe("Milestone 2-B — Vlog Footage Classifier Suite", () => {
  const createMockMedia = (filename: string, ext = ".mp4"): IngestedMediaFile => ({
    id: `asset_${filename}`,
    absolutePath: `/media/${filename}`,
    filename,
    extension: ext,
    mimeType: ext === ".png" ? "image/png" : "video/mp4",
    fingerprint: {
      checksumSha256: "a".repeat(64),
      sizeBytes: 1024000,
      lastModifiedTimestamp: 1700000000,
      durationSeconds: 10.0,
      width: 1920,
      height: 1080,
      fps: 30.0,
    },
    videoStream: {
      codec: "h264",
      width: 1920,
      height: 1080,
      aspectRatio: "16:9",
      fps: 30.0,
      frameRateMode: "CFR",
      durationSeconds: 10.0,
      orientation: "LANDSCAPE",
    },
    audioStream: {
      codec: "aac",
      sampleRateHz: 44100,
      channels: 2,
      durationSeconds: 10.0,
    },
    isReadOnly: true,
    ingestedAtTimestamp: 1700000000,
  });

  it("classifies talking head footage as A_ROLL with high confidence", () => {
    const media = createMockMedia("interview_host.mp4");
    const classification = VlogFootageClassifier.classify(media, {
      hasDominantFace: true,
      faceCoverageRatio: 0.35,
      hasVoiceActivity: true,
      voiceActivityRatio: 0.85,
      averageOpticalFlow: 0.15,
      detectedTags: ["person", "talking", "presentation"],
    });

    assert.equal(classification.primaryType, "A_ROLL");
    assert.ok(classification.confidence > 0.70, `Expected confidence > 0.70, got ${classification.confidence}`);
    assert.equal(classification.recommendedRole, "A_ROLL_PRIMARY");
    assert.ok(classification.scores.aRoll > classification.scores.bRoll);
    assert.equal(classification.evidence.hasDominantFace, true);
    assert.equal(classification.evidence.hasVoiceActivity, true);
  });

  it("classifies landscape/architecture footage as B_ROLL cutaway", () => {
    const media = createMockMedia("catedral_exterior.mp4");
    const classification = VlogFootageClassifier.classify(media, {
      hasDominantFace: false,
      hasVoiceActivity: false,
      averageOpticalFlow: 0.25,
      detectedTags: ["architecture", "building", "city", "street"],
    });

    assert.equal(classification.primaryType, "B_ROLL");
    assert.ok(classification.confidence > 0.50);
    assert.equal(classification.recommendedRole, "B_ROLL_CUTAWAY");
    assert.ok(classification.scores.bRoll > classification.scores.aRoll);
  });

  it("classifies high motion / drone footage as ACTION", () => {
    const media = createMockMedia("fast_drone_chase.mp4");
    const classification = VlogFootageClassifier.classify(media, {
      hasDominantFace: false,
      hasVoiceActivity: false,
      averageOpticalFlow: 0.88, // Muy alto flujo óptico
      detectedTags: ["drone", "fast", "chase", "action"],
    });

    assert.equal(classification.primaryType, "ACTION");
    assert.equal(classification.recommendedRole, "TRANSITION_STINGER");
    assert.ok(classification.scores.action > 0.60);
  });

  it("classifies timelapse tag footage as TIMELAPSE", () => {
    const media = createMockMedia("sunset_hyperlapse.mp4");
    const classification = VlogFootageClassifier.classify(media, {
      hasDominantFace: false,
      hasVoiceActivity: false,
      averageOpticalFlow: 0.45,
      detectedTags: ["timelapse", "sunset", "clouds"],
    });

    assert.equal(classification.primaryType, "TIMELAPSE");
    assert.ok(classification.scores.timelapse > 0.75);
  });

  it("classifies static images as PHOTO", () => {
    const media = createMockMedia("souvenir_polaroid.png", ".png");
    const classification = VlogFootageClassifier.classify(media);

    assert.equal(classification.primaryType, "PHOTO");
    assert.ok(classification.scores.photo > 0.90);
    assert.equal(classification.evidence.isStaticImage, true);
  });

  it("classifies screencast as SCREEN", () => {
    const media = createMockMedia("tutorial_demo.mp4");
    const classification = VlogFootageClassifier.classify(media, {
      detectedTags: ["screen", "desktop", "code", "browser"],
    });

    assert.equal(classification.primaryType, "SCREEN");
    assert.ok(classification.scores.screen > 0.70);
  });

  it("PBT: confidence and all scores are strictly bounded within [0, 1] without NaN or Infinity", () => {
    const media = createMockMedia("random_sample.mp4");

    fc.assert(
      fc.property(
        fc.boolean(),
        fc.double({ noNaN: true }),
        fc.boolean(),
        fc.double({ noNaN: true }),
        fc.double({ noNaN: true }),
        (hasVoice, voiceRatio, hasFace, faceCoverage, opticalFlow) => {
          const res = VlogFootageClassifier.classify(media, {
            hasVoiceActivity: hasVoice,
            voiceActivityRatio: voiceRatio,
            hasDominantFace: hasFace,
            faceCoverageRatio: faceCoverage,
            averageOpticalFlow: opticalFlow,
          });

          // Invariantes matemáticas estrictas
          assert.ok(res.confidence >= 0.0 && res.confidence <= 1.0);
          assert.ok(!isNaN(res.confidence));
          assert.ok(isFinite(res.confidence));

          for (const key of Object.keys(res.scores) as Array<keyof typeof res.scores>) {
            const score = res.scores[key];
            assert.ok(score >= 0.0 && score <= 1.0, `Score '${key}' out of range: ${score}`);
            assert.ok(!isNaN(score));
            assert.ok(isFinite(score));
          }
        }
      )
    );
  });
});
