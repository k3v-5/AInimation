import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { VlogAudioMixer } from "../../../vlog/audio/vlog-audio-mixer.js";

describe("Milestone 7 — Vlog Audio Mixer Suite", () => {
  it("assigns canonical hierarchical bus levels and calculates ducking on music", () => {
    const descriptors = [
      {
        id: "tr_voice",
        name: "Voiceover_Master",
        type: "VOICE" as const,
        audioFilePath: "audio/vo.wav",
        timelineStartSeconds: 0.0,
        timelineEndSeconds: 10.0,
      },
      {
        id: "tr_music",
        name: "Background_Track",
        type: "MUSIC" as const,
        audioFilePath: "audio/bg.wav",
        timelineStartSeconds: 0.0,
        timelineEndSeconds: 15.0,
      },
      {
        id: "tr_sfx",
        name: "Camera_Shutter",
        type: "CRITICAL_SFX" as const,
        audioFilePath: "audio/shutter.wav",
        timelineStartSeconds: 5.0,
        timelineEndSeconds: 5.2,
      },
      {
        id: "tr_ambience",
        name: "City_Ambience",
        type: "AMBIENCE" as const,
        audioFilePath: "audio/city.wav",
        timelineStartSeconds: 0.0,
        timelineEndSeconds: 15.0,
      },
    ];

    const dialogue = [{ startSeconds: 1.0, endSeconds: 6.0 }];

    const plan = VlogAudioMixer.createMixPlan("proj_mix", "es-MX", descriptors, dialogue);

    // Verificación de configuración maestra
    assert.equal(plan.config.voiceLevelDb, 0.0);
    assert.equal(plan.config.musicLevelDb, -14.0);
    assert.equal(plan.config.sfxLevelDb, -3.0);
    assert.equal(plan.config.ambienceLevelDb, -18.0);
    assert.equal(plan.config.duckingDb, -10.0);
    assert.equal(plan.config.truePeakCeilingDbTP, -1.0);
    assert.equal(plan.config.masterSampleRateHz, 44100);
    assert.equal(plan.config.channels, 2);

    // Verificación de ganancias por pista
    const voice = plan.tracks.find((t) => t.type === "VOICE");
    const music = plan.tracks.find((t) => t.type === "MUSIC");
    const sfx = plan.tracks.find((t) => t.type === "CRITICAL_SFX");
    const amb = plan.tracks.find((t) => t.type === "AMBIENCE");

    assert.equal(voice?.volumeDb, 0.0);
    assert.equal(music?.volumeDb, -14.0);
    assert.equal(sfx?.volumeDb, -3.0);
    assert.equal(amb?.volumeDb, -18.0);

    // Música debe tener envolvente de ducking asociada
    assert.ok(music?.duckingEnvelope !== undefined);
    assert.equal(music?.duckingEnvelope?.targetTrackId, "tr_music");
    assert.ok(music?.duckingEnvelope?.keyframes.length > 2);

    // Checksum determinista presente
    assert.equal(plan.checksumSha256.length, 64);
  });
});
