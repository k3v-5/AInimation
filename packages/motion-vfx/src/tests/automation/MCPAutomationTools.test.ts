import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { handleTranscribeLocalAudio } from "../../mcp/tools/transcribe-local-audio.js";
import { handleDetectViralClips } from "../../mcp/tools/detect-viral-clips.js";
import { handlePackageSocialRelease } from "../../mcp/tools/package-social-release.js";
import { handleAutoReframeVideo } from "../../mcp/tools/auto-reframe-video.js";

describe("MCP Tools Suite — Automation & Viral Production Handlers", () => {
  it("handles transcribe_local_audio in synthetic mode", async () => {
    const res = await handleTranscribeLocalAudio({
      textFallback: "PRUEBA DETERMINISTA DE TRANSCRIPCION LOCAL",
      totalDurationSec: 5.0,
    });

    assert.equal(res.status, "success");
    assert.equal(res.wordCount, 5);
    assert.equal(res.document.duration, 5.0);
  });

  it("handles detect_viral_clips and returns ranked clips with virality scores", async () => {
    const res = await handleDetectViralClips({
      transcriptText: "EL SECRETO VIRAL DEL MILLONARIO QUE NADIE QUIERE QUE SEPAS EN TIKTOK Y YOUTUBE",
      totalDurationSec: 40.0,
      topK: 2,
    });

    assert.equal(res.status, "success");
    assert.ok(res.viralClips.length >= 1);
    assert.ok(res.viralClips[0].viralityIndex > 0);
  });

  it("handles package_social_release generating YouTube and TikTok payloads", async () => {
    const res = await handlePackageSocialRelease({
      projectName: "Test_Project",
      topic: "Finanzas Personales",
      keywords: ["ahorro", "inversion"],
      viralHookText: "El 99% pierde dinero por este error.",
    });

    assert.equal(res.status, "success");
    assert.ok(res.youtube.recommendedTitle.includes("FINANZAS PERSONALES"));
    assert.ok(res.youtube.descriptionWithTimestamps.includes("MARCAS DE TIEMPO"));
    assert.ok(res.tiktok_reels.hashtags.includes("#fyp"));
  });

  it("handles auto_reframe_video returning 9:16 vertical keyframes", async () => {
    const res = await handleAutoReframeVideo({
      mode: "dynamic_pan_and_scan",
      focalPoints: [{ timeSec: 0, normalizedX: 0.5, confidence: 1.0 }],
      sourceWidth: 1920,
      sourceHeight: 1080,
      targetWidth: 1080,
      targetHeight: 1920,
    });

    assert.equal(res.status, "success");
    assert.equal(res.targetResolution.width, 1080);
    assert.equal(res.targetResolution.height, 1920);
    assert.equal(res.keyframesCount, 1);
  });
});
