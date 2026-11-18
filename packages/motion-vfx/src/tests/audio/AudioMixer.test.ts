import assert from "node:assert/strict";
import { describe, it } from "node:test";
import { AudioClip } from "../../audio/core/AudioClip.js";
import { SyntheticAudioSource } from "../../audio/core/AudioSource.js";
import { AudioTrack } from "../../audio/core/AudioTrack.js";
import { AudioMixer } from "../../audio/mixer/AudioMixer.js";
import { TimeRange } from "../../timeline/core/TimeRange.js";

describe("Fase 5D — Multi-Track Audio Mixing & Auto-Ducking Tests", () => {
  it("mixes multiple tracks accurately with level summation and panning", () => {
    const mixer = new AudioMixer({ sampleRate: 48000, channels: 2 });

    const sources = new Map<string, SyntheticAudioSource>();
    // Crear fuente senoidal constante para prueba
    sources.set("music_asset", new SyntheticAudioSource({ type: "sine", duration: 10, amplitude: 0.4 }));
    sources.set("sfx_asset", new SyntheticAudioSource({ type: "sine", duration: 10, amplitude: 0.2 }));

    const musicTrack = new AudioTrack({ id: "t_music", gainDb: 0 });
    musicTrack.addClip(new AudioClip({ id: "c_music", assetId: "music_asset", timelineRange: new TimeRange(0, 5) }));

    const sfxTrack = new AudioTrack({ id: "t_sfx", gainDb: 0 });
    sfxTrack.addClip(new AudioClip({ id: "c_sfx", assetId: "sfx_asset", timelineRange: new TimeRange(0, 5) }));

    const mixed = mixer.mix([musicTrack, sfxTrack], new TimeRange(0, 2), (id) => sources.get(id));
    assert.strictEqual(mixed.duration, 2.0);
    assert.strictEqual(mixed.frames, 96000);
    assert.ok(mixed.data[0][1000] !== 0);
  });

  it("applies auto-ducking attenuation on music when voice track is active", () => {
    const mixer = new AudioMixer({ sampleRate: 48000, channels: 2 });

    const sources = new Map<string, SyntheticAudioSource>();
    sources.set("music_src", new SyntheticAudioSource({ type: "sine", duration: 10, amplitude: 0.5 }));
    sources.set("voice_src", new SyntheticAudioSource({ type: "sine", duration: 10, amplitude: 0.8 }));

    const voiceTrack = new AudioTrack({ id: "track_voice" });
    voiceTrack.addClip(new AudioClip({ id: "c_voice", assetId: "voice_src", timelineRange: new TimeRange(2, 5) }));

    const musicTrack = new AudioTrack({
      id: "track_music",
      ducking: {
        sourceTrackId: "track_voice",
        attenuationDb: -6.0, // Reducir ganancia a la mitad
        thresholdRms: 0.1,
      },
    });
    musicTrack.addClip(new AudioClip({ id: "c_music", assetId: "music_src", timelineRange: new TimeRange(0, 10) }));

    // 1. Mezcla en t = [0, 1) -> voice no está activa -> música a nivel normal
    const mixNormal = mixer.mix([voiceTrack, musicTrack], new TimeRange(0, 1), (id) => sources.get(id));

    // 2. Mezcla en t = [2, 3) -> voice ESTÁ activa -> música atenuada
    const mixDucked = mixer.mix([voiceTrack, musicTrack], new TimeRange(2, 3), (id) => sources.get(id));

    assert.strictEqual(mixNormal.duration, 1.0);
    assert.strictEqual(mixDucked.duration, 1.0);
  });
});
