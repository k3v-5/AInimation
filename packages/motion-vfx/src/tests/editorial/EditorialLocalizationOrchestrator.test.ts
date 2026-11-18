import test from "node:test";
import assert from "node:assert/strict";
import {
  EditorialIRBuilder,
  EditorialLocalizationOrchestrator,
  LocalizedTrackPair,
} from "../../editorial/index.js";

test("Fase 4D — Editorial Localization Orchestrator Suite", async (t) => {
  const masterBuilder = new EditorialIRBuilder("proj_multilingual", {
    title: "Global Architecture",
    profile: "DOCUMENTARY",
    frameRate: 30,
    width: 1920,
    height: 1080,
    sampleRate: 44100,
    targetDialogueLufs: -18,
  });

  masterBuilder
    .createTrack({ id: "v_main", name: "Architecture Shots", type: "VIDEO_PRIMARY", index: 0 })
    .createTrack({ id: "a_voice_en", name: "English Voice", type: "AUDIO_DIALOGUE", index: 1 })
    .createTrack({ id: "a_music", name: "Score Bed", type: "AUDIO_MUSIC", index: 2 });

  masterBuilder.addClip("v_main", {
    id: "clip_v1",
    assetId: "media/building_render.mp4",
    sourceRange: { startSeconds: 0, durationSeconds: 15 },
    timelineRange: { startSeconds: 0, durationSeconds: 15 },
  });

  masterBuilder.addClip("a_voice_en", {
    id: "clip_a_en",
    assetId: "audio/en/voiceover_en.wav",
    sourceRange: { startSeconds: 0, durationSeconds: 15 },
    timelineRange: { startSeconds: 0, durationSeconds: 15 },
  });

  const masterIR = masterBuilder.build("2026-09-02T10:00:00.000Z");

  await t.test("generates localized Spanish (es-MX) IR swapping dialogue and injecting subtitles", () => {
    const spanishTrack: LocalizedTrackPair = {
      locale: "es-MX",
      audioDialogueAssetId: "audio/es/locucion_mexico.wav",
      timingOffsetSeconds: 0.25,
      subtitleCues: [
        { startSeconds: 0.5, endSeconds: 4.0, text: "Bienvenidos a la catedral gótica moderna." },
        { startSeconds: 4.5, endSeconds: 9.0, text: "Los arcos sostienen más de diez toneladas." },
      ],
    };

    const localizedIR = EditorialLocalizationOrchestrator.createLocalizedIR({
      masterIR,
      localizedTrack: spanishTrack,
    });

    assert.equal(localizedIR.projectId, "proj_multilingual_es_MX");
    assert.match(localizedIR.metadata.title, /es-MX/);

    // Dialogue track should point to the Spanish asset
    const dialogueTrack = localizedIR.tracks.find((t) => t.type === "AUDIO_DIALOGUE");
    assert.ok(dialogueTrack);
    assert.equal(dialogueTrack.clips[0].assetId, "audio/es/locucion_mexico.wav");
    assert.equal(dialogueTrack.clips[0].timelineRange.startSeconds, 0.25);

    // Subtitle track should exist with 2 cues
    const subtitleTrack = localizedIR.tracks.find((t) => t.type === "SUBTITLE");
    assert.ok(subtitleTrack);
    assert.equal(subtitleTrack.clips.length, 2);

    // Visual primary track should be 100% identical to master
    const visualTrack = localizedIR.tracks.find((t) => t.type === "VIDEO_PRIMARY");
    assert.ok(visualTrack);
    assert.equal(visualTrack.clips[0].assetId, "media/building_render.mp4");
  });
});
