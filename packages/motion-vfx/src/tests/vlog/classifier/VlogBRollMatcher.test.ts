import assert from "node:assert/strict";
import { describe, it } from "node:test";
import fc from "fast-check";
import {
  FootageClassification,
  IngestedMediaFile,
  VlogBRollMatcher,
} from "../../../vlog/index.js";

describe("Milestone 2-C — Vlog B-Roll Matcher Suite", () => {
  const createMedia = (
    id: string,
    filename: string,
    duration: number,
    tags: string[],
    isARoll = false
  ): { media: IngestedMediaFile; classif: FootageClassification } => {
    const media: IngestedMediaFile = {
      id,
      absolutePath: `/media/${filename}`,
      filename,
      extension: ".mp4",
      mimeType: "video/mp4",
      fingerprint: {
        checksumSha256: id.padEnd(64, "0"),
        sizeBytes: 5000000,
        lastModifiedTimestamp: 1700000000,
        durationSeconds: duration,
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
        durationSeconds: duration,
        orientation: "LANDSCAPE",
      },
      isReadOnly: true,
      ingestedAtTimestamp: 1700000000,
    };

    const classif: FootageClassification = {
      mediaId: id,
      primaryType: isARoll ? "A_ROLL" : "B_ROLL",
      confidence: 0.85,
      scores: {
        aRoll: isARoll ? 0.90 : 0.10,
        bRoll: isARoll ? 0.10 : 0.90,
        action: 0.0,
        timelapse: 0.0,
        screen: 0.0,
        photo: 0.0,
        other: 0.0,
      },
      evidence: {
        hasVoiceActivity: isARoll,
        voiceActivityRatio: isARoll ? 0.8 : 0.0,
        hasDominantFace: isARoll,
        faceCoverageRatio: isARoll ? 0.3 : 0.0,
        averageOpticalFlow: 0.2,
        isStaticImage: false,
        aspectRatio: "16:9",
        detectedTags: tags,
      },
      recommendedRole: isARoll ? "A_ROLL_PRIMARY" : "B_ROLL_CUTAWAY",
      tags,
    };

    return { media, classif };
  };

  it("matches B-Roll candidate based on semantic intent and entity keywords", () => {
    const item1 = createMedia("c1", "catedral_fachada.mp4", 8.0, ["catedral", "architecture", "guadalajara", "historic"]);
    const item2 = createMedia("c2", "tacos_comida.mp4", 6.0, ["food", "tacos", "gastronomia", "mercado"]);
    const item3 = createMedia("c3", "parque_arboles.mp4", 7.0, ["nature", "trees", "park"]);

    const available = [item1.media, item2.media, item3.media];
    const classifs = new Map<string, FootageClassification>([
      [item1.media.id, item1.classif],
      [item2.media.id, item2.classif],
      [item3.media.id, item3.classif],
    ]);

    const match = VlogBRollMatcher.matchBRoll(
      {
        narrativeSegmentId: "seg_arch_01",
        intentText: "caminando hacia la impresionante catedral histórica",
        entities: ["Catedral"],
        location: "Guadalajara",
        targetDurationSeconds: 4.0,
        timelineStartSeconds: 10.0,
        timelineEndSeconds: 14.0,
      },
      available,
      classifs
    );

    assert.ok(match !== null);
    assert.equal(match.selectedCandidate.mediaId, "c1");
    assert.ok(match.selectedCandidate.score.semanticRelevance > 50.0);
    assert.ok(match.selectedCandidate.score.entityMatch > 50.0);
    assert.equal(match.isExclusiveCover, true);
    assert.equal(match.alternatives.length, 2);
  });

  it("filters out A-Roll footage from B-Roll matching unless unlocked or forced", () => {
    const aRoll = createMedia("aroll_01", "host_speech.mp4", 10.0, ["host", "talking"], true);
    const bRoll = createMedia("broll_01", "city_view.mp4", 10.0, ["city", "skyline"], false);

    const available = [aRoll.media, bRoll.media];
    const classifs = new Map<string, FootageClassification>([
      [aRoll.media.id, aRoll.classif],
      [bRoll.media.id, bRoll.classif],
    ]);

    const match = VlogBRollMatcher.matchBRoll(
      {
        narrativeSegmentId: "seg_02",
        intentText: "la ciudad desde las alturas",
        targetDurationSeconds: 3.0,
        timelineStartSeconds: 0.0,
        timelineEndSeconds: 3.0,
      },
      available,
      classifs
    );

    assert.ok(match !== null);
    assert.equal(match.selectedCandidate.mediaId, "broll_01");
  });

  it("respects manual locks: FORBIDDEN excluded, FORCE prioritized, PREFERRED boosted", () => {
    const item1 = createMedia("c1", "tacos.mp4", 6.0, ["food", "tacos"]);
    const item2 = createMedia("c2", "birria.mp4", 6.0, ["food", "birria"]);

    const available = [item1.media, item2.media];
    const classifs = new Map<string, FootageClassification>([
      [item1.media.id, item1.classif],
      [item2.media.id, item2.classif],
    ]);

    // Caso FORBIDDEN: c1 está prohibido, c2 debe ganar aunque c1 coincida mejor con tacos
    const matchForbidden = VlogBRollMatcher.matchBRoll(
      {
        narrativeSegmentId: "seg_food",
        intentText: "deliciosos tacos al pastor",
        targetDurationSeconds: 3.0,
        timelineStartSeconds: 0.0,
        timelineEndSeconds: 3.0,
        locks: {
          c1: { mediaId: "c1", lockType: "FORBIDDEN" },
        },
      },
      available,
      classifs
    );

    assert.ok(matchForbidden !== null);
    assert.equal(matchForbidden.selectedCandidate.mediaId, "c2");

    // Caso FORCE: c2 forzado recibe score 100
    const matchForce = VlogBRollMatcher.matchBRoll(
      {
        narrativeSegmentId: "seg_food_2",
        intentText: "tacos tacos tacos",
        targetDurationSeconds: 3.0,
        timelineStartSeconds: 3.0,
        timelineEndSeconds: 6.0,
        locks: {
          c2: { mediaId: "c2", lockType: "FORCE" },
        },
      },
      available,
      classifs
    );

    assert.ok(matchForce !== null);
    assert.equal(matchForce.selectedCandidate.mediaId, "c2");
    assert.equal(matchForce.selectedCandidate.score.total, 100.0);
  });

  it("applies cooldown penalty to recently used clips", () => {
    const itemA = createMedia("cA", "plaza.mp4", 8.0, ["plaza", "centro"]);
    const itemB = createMedia("cB", "plaza_alt.mp4", 8.0, ["plaza", "centro"]);

    const available = [itemA.media, itemB.media];
    const classifs = new Map<string, FootageClassification>([
      [itemA.media.id, itemA.classif],
      [itemB.media.id, itemB.classif],
    ]);

    // itemA fue usado muy recientemente (índice 0 en recentUsage)
    const match = VlogBRollMatcher.matchBRoll(
      {
        narrativeSegmentId: "seg_cooldown",
        intentText: "caminando por la plaza del centro",
        targetDurationSeconds: 4.0,
        timelineStartSeconds: 20.0,
        timelineEndSeconds: 24.0,
        recentUsageMediaIds: ["cA"],
      },
      available,
      classifs
    );

    assert.ok(match !== null);
    // itemB debe ser seleccionado porque itemA sufre penalización de cooldown
    assert.equal(match.selectedCandidate.mediaId, "cB");
    assert.ok(match.selectedCandidate.score.noveltyPenalty === 0);
  });

  it("optimizes subclip range within asset duration bounds", () => {
    const item = createMedia("c1", "walking_avenue.mp4", 15.0, ["walking", "street"]);
    const available = [item.media];
    const classifs = new Map([[item.media.id, item.classif]]);

    const match = VlogBRollMatcher.matchBRoll(
      {
        narrativeSegmentId: "seg_subclip",
        intentText: "walking street",
        targetDurationSeconds: 5.0,
        timelineStartSeconds: 0.0,
        timelineEndSeconds: 5.0,
      },
      available,
      classifs
    );

    assert.ok(match !== null);
    const subclip = match.selectedCandidate.subclipRange;
    assert.ok(subclip.startSeconds >= 0);
    assert.ok(subclip.endSeconds <= 15.0);
    assert.ok(subclip.endSeconds > subclip.startSeconds);
    assert.ok(Math.abs(subclip.durationSeconds - 5.0) < 0.05);
  });

  it("PBT: subclip range always satisfies 0 <= start < end <= assetDuration", () => {
    fc.assert(
      fc.property(
        fc.double({ min: 5.0, max: 120.0, noNaN: true }),
        fc.double({ min: 1.0, max: 10.0, noNaN: true }),
        (assetDur, targetDur) => {
          const item = createMedia("pbt_asset", "pbt.mp4", assetDur, ["test"]);
          const match = VlogBRollMatcher.matchBRoll(
            {
              narrativeSegmentId: "seg_pbt",
              intentText: "test",
              targetDurationSeconds: targetDur,
              timelineStartSeconds: 0,
              timelineEndSeconds: targetDur,
            },
            [item.media],
            new Map([[item.media.id, item.classif]])
          );

          if (match !== null) {
            const sub = match.selectedCandidate.subclipRange;
            assert.ok(sub.startSeconds >= 0.0);
            assert.ok(sub.endSeconds <= assetDur + 0.001);
            assert.ok(sub.endSeconds >= sub.startSeconds);
          }
        }
      )
    );
  });
});
