import { describe, it } from "node:test";
import assert from "node:assert/strict";
import fc from "fast-check";
import {
  handleVlogClassifyFootage,
  handleVlogGenerateJumpCutPlan,
  handleVlogGetStatus,
  handleVlogMatchBRoll,
  handleVlogProduce,
} from "../../mcp/tools/vlog-tools.js";

describe("Milestone 8 & 14 — MCP Vlog Intelligence Tools Suite", () => {
  it("executes vlog_generate_jump_cut_plan and produces valid jump cut metrics", async () => {
    const res = await handleVlogGenerateJumpCutPlan({
      videoPath: "/footage/travel_vlog_day1.mp4",
      transcriptText: "Hola a todos bienvenidos a este nuevo episodio de viaje en Guadalajara.",
      totalDurationSec: 30.0,
      silenceThresholdSec: 0.25,
    });

    assert.equal(res.status, "success");
    assert.equal(res.sourceDuration, 30.0);
    assert.ok(res.editedDuration <= res.sourceDuration);
    assert.ok(res.totalRetainedSegments > 0);
  });

  it("executes vlog_classify_footage and probabilistically identifies A-Roll vs B-Roll", async () => {
    // Talking head with speech and face
    const arollRes = await handleVlogClassifyFootage({
      filePath: "/footage/interview.mp4",
      durationSeconds: 15.0,
      hasSpeech: true,
      hasFace: true,
    });

    assert.equal(arollRes.status, "success");
    assert.equal(arollRes.primaryType, "A_ROLL");
    assert.ok(arollRes.confidence >= 0.5);

    // B-roll landscape with camera motion and no voice
    const brollRes = await handleVlogClassifyFootage({
      filePath: "/footage/landscape.mp4",
      durationSeconds: 8.0,
      hasSpeech: false,
      hasFace: false,
      hasCameraMotion: true,
    });

    assert.equal(brollRes.status, "success");
    assert.equal(brollRes.primaryType, "B_ROLL");
  });

  it("executes vlog_match_broll and ranks available media by semantic relevance", async () => {
    const media = [
      { id: "m_cathedral", filePath: "/media/catedral_historica.mp4", durationSeconds: 6.0 },
      { id: "m_traffic", filePath: "/media/busy_traffic.mp4", durationSeconds: 5.0 },
    ];

    const matchRes = await handleVlogMatchBRoll({
      intentText: "Visitando la hermosa catedral histórica",
      targetDurationSeconds: 4.0,
      availableMedia: media,
    });

    assert.equal(matchRes.status, "success");
    assert.equal(matchRes.matchFound, true);
    assert.ok(matchRes.bestMatch !== null);
    assert.equal(matchRes.bestMatch!.mediaId, "m_cathedral");
  });

  it("executes vlog_produce and queries status through vlog_get_status", async () => {
    const produceRes = await handleVlogProduce({
      projectId: "mcp_vlog_e2e_test",
      scriptText: "Bienvenidos a Guadalajara. Hoy disfrutamos de su arquitectura y cultura.",
      targetLocales: ["es-MX", "en-US"],
      aspectRatios: ["16:9"],
      assets: [
        { id: "aroll_1", name: "Talking.mp4", type: "A_ROLL", durationSeconds: 20.0, filePath: "/media/talking.mp4" },
      ],
    });

    assert.equal(produceRes.status, "success");
    assert.equal(produceRes.projectId, "mcp_vlog_e2e_test");
    assert.ok(produceRes.runId.length > 0);
    assert.equal(produceRes.deliveredLanguages.length, 2);

    const statusRes = await handleVlogGetStatus({ runId: produceRes.runId });
    assert.equal(statusRes.status, "success");
    assert.equal(statusRes.runId, produceRes.runId);
    assert.ok(statusRes.artifacts.length > 0);
  });

  it("PBT: jump cut edited duration is strictly <= source duration", async () => {
    await fc.assert(
      fc.asyncProperty(
        fc.float({ min: 10.0, max: 120.0, noNaN: true }),
        fc.string({ minLength: 10, maxLength: 200 }),
        async (duration, text) => {
          const res = await handleVlogGenerateJumpCutPlan({
            videoPath: "/test/video.mp4",
            transcriptText: text,
            totalDurationSec: duration,
          });

          return res.editedDuration <= res.sourceDuration + 0.001;
        }
      ),
      { numRuns: 20 }
    );
  });
});
